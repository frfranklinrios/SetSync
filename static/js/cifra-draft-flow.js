/**
 * Fluxo de rascunho pessoal: salvar edição privada e decidir publicar na banda.
 */
(function () {
  "use strict";

  var form = document.getElementById("cifra-form");
  var shareModalEl = document.getElementById("cifraShareModal");
  if (!form || !shareModalEl) return;

  var cifraId = shareModalEl.getAttribute("data-cifra-id");
  var canPublish = shareModalEl.getAttribute("data-can-publish") === "1";
  var bsShare = window.bootstrap && bootstrap.Modal
    ? bootstrap.Modal.getOrCreateInstance(shareModalEl)
    : null;

  function csrfHeaders() {
    var token =
      document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") ||
      document.querySelector('input[name="csrf_token"]')?.value;
    var headers = { "Content-Type": "application/json" };
    if (token) headers["X-CSRFToken"] = token;
    return headers;
  }

  function collectPayload() {
    var ta = document.getElementById("conteudo");
    var payload = {
      titulo: form.querySelector('[name="titulo"]')?.value || "",
      artista: form.querySelector('[name="artista"]')?.value || "",
      tom_original: form.querySelector('[name="tom_original"]')?.value || "",
      conteudo: ta ? ta.value : "",
    };
    var cj = document.getElementById("cifra_json_hidden");
    var gj = document.getElementById("grade_json_hidden");
    if (cj && cj.value) {
      try { payload.cifra_json = JSON.parse(cj.value); } catch (e) {}
    }
    if (gj && gj.value) {
      try { payload.grade_json = JSON.parse(gj.value); } catch (e) {}
    }
    return payload;
  }

  function prepareFormBeforeSave() {
    var ta = document.getElementById("conteudo");
    if (window.SetSyncCifraClubPaste && SetSyncCifraClubPaste.normalizarColagem && ta) {
      ta.value = SetSyncCifraClubPaste.normalizarColagem(ta.value);
    }
    if (window.SetSyncChordPro && ta && ta.value.trim()) {
      ta.value = SetSyncChordPro.toChordPro(ta.value, {
        titulo: form.querySelector('[name="titulo"]').value,
        artista: form.querySelector('[name="artista"]').value,
        key: form.querySelector('[name="tom_original"]').value,
      });
    }
    if (typeof parseConteudo === "function" && ta) {
      var parsed = parseConteudo(ta.value);
      if (parsed.length > 0) {
        document.getElementById("cifra_json_hidden").value = JSON.stringify(parsed);
      }
    }
  }

  function saveDraft() {
    prepareFormBeforeSave();
    return fetch("/cifras/" + encodeURIComponent(cifraId) + "/api/rascunho", {
      method: "PUT",
      credentials: "same-origin",
      headers: csrfHeaders(),
      body: JSON.stringify(collectPayload()),
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error((data && data.detail) || "Falha ao salvar rascunho.");
        return data;
      });
    });
  }

  form.addEventListener("submit", function (ev) {
    if (form.getAttribute("data-draft-flow") !== "1") return;
    ev.preventDefault();
    var submitBtn = form.querySelector('[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    saveDraft()
      .then(function () {
        if (bsShare) bsShare.show();
      })
      .catch(function (err) {
        alert(err.message || String(err));
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
  });

  document.getElementById("cifra-share-keep-private")?.addEventListener("click", function () {
    if (bsShare) bsShare.hide();
    window.location.href = "/cifras/" + encodeURIComponent(cifraId) + "?versao=minha";
  });

  document.getElementById("cifra-share-publish")?.addEventListener("click", function () {
    if (!canPublish) return;
    var btn = this;
    btn.disabled = true;
    fetch("/cifras/" + encodeURIComponent(cifraId) + "/api/rascunho/publicar", {
      method: "POST",
      credentials: "same-origin",
      headers: csrfHeaders(),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error((data && data.detail) || "Falha ao publicar.");
          return data;
        });
      })
      .then(function (data) {
        window.location.href = data.redirect || "/cifras/" + encodeURIComponent(cifraId);
      })
      .catch(function (err) {
        alert(err.message || String(err));
        btn.disabled = false;
      });
  });
})();
