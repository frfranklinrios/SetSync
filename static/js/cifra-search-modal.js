/**
 * Modal de busca, preview e importação de cifras para o repertório da banda.
 */
(function () {
  "use strict";

  var modalEl = document.getElementById("cifraSearchModal");
  if (!modalEl) return;

  var bandId = modalEl.getAttribute("data-band-id");
  var bsModal = window.bootstrap && bootstrap.Modal
    ? bootstrap.Modal.getOrCreateInstance(modalEl)
    : null;

  var stepSearch = document.getElementById("cifra-search-step-search");
  var stepPreview = document.getElementById("cifra-search-step-preview");
  var queryInput = document.getElementById("cifra-modal-query");
  var statusEl = document.getElementById("cifra-modal-status");
  var resultsEl = document.getElementById("cifra-modal-results");
  var importBtn = document.getElementById("cifra-modal-import-btn");
  var previewTitle = document.getElementById("cifra-modal-preview-title");
  var previewMeta = document.getElementById("cifra-modal-preview-meta");
  var previewBody = document.getElementById("cifra-modal-preview-body");
  var backBtn = document.getElementById("cifra-modal-back");

  var currentPayload = null;
  var debounceTimer = null;

  function csrfHeaders() {
    var token =
      document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") ||
      document.querySelector('input[name="csrf_token"]')?.value;
    var headers = { "Content-Type": "application/json" };
    if (token) headers["X-CSRFToken"] = token;
    return headers;
  }

  function setStatus(text, isError) {
    if (!statusEl) return;
    statusEl.textContent = text || "";
    statusEl.classList.toggle("text-danger", !!isError);
    statusEl.classList.toggle("text-muted", !isError);
  }

  function showSearchStep() {
    if (stepSearch) stepSearch.classList.remove("d-none");
    if (stepPreview) stepPreview.classList.add("d-none");
    if (importBtn) importBtn.classList.add("d-none");
    currentPayload = null;
  }

  function showPreviewStep() {
    if (stepSearch) stepSearch.classList.add("d-none");
    if (stepPreview) stepPreview.classList.remove("d-none");
    if (importBtn) importBtn.classList.remove("d-none");
  }

  function renderResults(items) {
    if (!resultsEl) return;
    resultsEl.innerHTML = "";
    if (!items || !items.length) {
      resultsEl.classList.add("d-none");
      return;
    }
    items.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cifra-modal-result";
      btn.innerHTML =
        '<div><div class="cifra-modal-result-title">' +
        (item.title || "Sem título") +
        '</div><div class="cifra-modal-result-artist">' +
        (item.artist || "") +
        '</div></div><span class="badge ' +
        (item.cached ? "text-bg-success" : "text-bg-secondary") +
        '">' +
        (item.cached ? "Pronta" : "Índice") +
        "</span>";
      btn.addEventListener("click", function () {
        loadPreview(item, btn);
      });
      resultsEl.appendChild(btn);
    });
    resultsEl.classList.remove("d-none");
  }

  function fetchImport(item) {
    var scrape = item.cached ? "0" : "1";
    return fetch(
      "/cifras/import/api/api-cifras/" +
        encodeURIComponent(item.artist_slug) +
        "/" +
        encodeURIComponent(item.song_slug) +
        "?scrape=" +
        scrape,
      { credentials: "same-origin" }
    ).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error((data && data.detail) || "Falha ao carregar cifra.");
        return data;
      });
    });
  }

  function fetchPreviewHtml(payload) {
    return fetch("/cifras/import/api/preview", {
      method: "POST",
      credentials: "same-origin",
      headers: csrfHeaders(),
      body: JSON.stringify(payload),
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error((data && data.detail) || "Falha no preview.");
        return data;
      });
    });
  }

  function loadPreview(item, btn) {
    var prev = btn ? btn.textContent : "";
    if (btn) {
      btn.disabled = true;
      btn.style.opacity = "0.6";
    }
    setStatus("Carregando cifra…");
    fetchImport(item)
      .then(function (data) {
        currentPayload = data;
        return fetchPreviewHtml(data);
      })
      .then(function (preview) {
        if (previewTitle) previewTitle.textContent = preview.titulo || currentPayload.titulo;
        if (previewMeta) {
          previewMeta.textContent =
            (preview.artista || currentPayload.artista || "") +
            (preview.tom_original ? " · Tom " + preview.tom_original : "");
        }
        if (previewBody) previewBody.innerHTML = preview.html || "<p class='text-muted'>Sem conteúdo.</p>";
        showPreviewStep();
        setStatus("");
      })
      .catch(function (err) {
        setStatus(err.message || String(err), true);
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.style.opacity = "";
        }
      });
  }

  function runSearch() {
    var q = (queryInput && queryInput.value || "").trim();
    if (q.length < 2) {
      setStatus("Digite pelo menos 2 caracteres.", true);
      renderResults([]);
      return;
    }
    setStatus("Buscando…");
    fetch("/cifras/import/api/buscar?q=" + encodeURIComponent(q) + "&limit=20", {
      credentials: "same-origin",
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error((data && data.detail) || "Busca falhou.");
          return data;
        });
      })
      .then(function (data) {
        var items = data.items || [];
        if (!items.length) {
          setStatus("Nenhum resultado para «" + q + "».");
          renderResults([]);
          return;
        }
        setStatus(items.length + " resultado(s). Toque para visualizar.");
        renderResults(items);
      })
      .catch(function (err) {
        setStatus(err.message || String(err), true);
        renderResults([]);
      });
  }

  function importToBand() {
    if (!currentPayload || !bandId) return;
    importBtn.disabled = true;
    var prev = importBtn.innerHTML;
    importBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Importando…';
    fetch("/cifras/import/api/para-banda/" + encodeURIComponent(bandId), {
      method: "POST",
      credentials: "same-origin",
      headers: csrfHeaders(),
      body: JSON.stringify(currentPayload),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) {
            if (res.status === 402 && window.SetSyncUpgradeModal) {
              SetSyncUpgradeModal.show(data.detail);
            }
            throw new Error((data && data.detail) || "Falha ao importar.");
          }
          return data;
        });
      })
      .then(function (data) {
        if (bsModal) bsModal.hide();
        window.location.href = data.view_url || data.edit_url || window.location.href;
      })
      .catch(function (err) {
        alert(err.message || String(err));
      })
      .finally(function () {
        importBtn.disabled = false;
        importBtn.innerHTML = prev;
      });
  }

  document.getElementById("cifra-modal-search-btn")?.addEventListener("click", runSearch);
  queryInput?.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") {
      ev.preventDefault();
      runSearch();
    }
  });
  queryInput?.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(runSearch, 400);
  });
  backBtn?.addEventListener("click", showSearchStep);
  importBtn?.addEventListener("click", importToBand);

  modalEl.addEventListener("hidden.bs.modal", function () {
    showSearchStep();
    if (queryInput) queryInput.value = "";
    setStatus("");
    renderResults([]);
  });

  document.querySelectorAll("[data-open-cifra-search]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (bsModal) bsModal.show();
      setTimeout(function () {
        queryInput?.focus();
      }, 200);
    });
  });

  window.SetSyncCifraSearchModal = { open: function () { if (bsModal) bsModal.show(); } };
})();
