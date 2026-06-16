/**
 * Busca cifras na API local (api-cifras) e preenche o formulário add/edit.
 */
(function () {
  "use strict";

  var debounceTimer = null;

  function csrfHeaders() {
    var token =
      document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") ||
      document.querySelector('input[name="csrf_token"]')?.value;
    var headers = { "Content-Type": "application/json" };
    if (token) headers["X-CSRFToken"] = token;
    return headers;
  }

  function setStatus(el, text, isError) {
    if (!el) return;
    el.textContent = text || "";
    el.classList.toggle("text-danger", !!isError);
    el.classList.toggle("text-muted", !isError);
  }

  function renderResults(container, items, onPick) {
    if (!container) return;
    container.innerHTML = "";
    if (!items || !items.length) {
      container.classList.add("d-none");
      return;
    }
    items.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "api-cifras-result";
      btn.dataset.artistSlug = item.artist_slug || "";
      btn.dataset.songSlug = item.song_slug || "";
      btn.dataset.cached = item.cached ? "1" : "0";
      btn.dataset.url = item.url || "";

      var main = document.createElement("div");
      var title = document.createElement("div");
      title.className = "api-cifras-result-title";
      title.textContent = item.title || "Sem título";
      var artist = document.createElement("div");
      artist.className = "api-cifras-result-artist";
      artist.textContent = item.artist || "";
      main.appendChild(title);
      main.appendChild(artist);
      btn.appendChild(main);

      var badge = document.createElement("span");
      badge.className =
        "badge " + (item.cached ? "text-bg-success" : "text-bg-secondary");
      badge.textContent = item.cached ? "Pronta" : "Índice";
      btn.appendChild(badge);

      btn.addEventListener("click", function () {
        onPick(item, btn);
      });
      container.appendChild(btn);
    });
    container.classList.remove("d-none");
  }

  function buildReferenciaSnapshot(payload) {
    return {
      source: "api-cifras",
      titulo: payload.titulo || "",
      artista: payload.artista || "",
      tom_original: payload.tom_original || payload.tom || "",
      conteudo: payload.conteudo || "",
      cifra_json: payload.cifra_json || null,
      grade_json: payload.grade_json || null,
      meta: {
        artist_slug: payload.artist_slug || "",
        song_slug: payload.song_slug || "",
        url_cifra: payload.url_cifra || "",
        cached: !!payload.cached,
        imported_at: new Date().toISOString(),
      },
    };
  }

  function setReferenciaSnapshot(payload) {
    var hidden = document.getElementById("referencia_json_hidden");
    if (!hidden || !payload) return;
    hidden.value = JSON.stringify(buildReferenciaSnapshot(payload));
  }

  function applyPayload(payload) {
    if (window.applyCifrasToolResult) {
      window.applyCifrasToolResult({
        type: "setsync-cifras-apply",
        titulo: payload.titulo,
        artista: payload.artista,
        tom_original: payload.tom_original,
        conteudo: payload.conteudo,
        cifra_json: payload.cifra_json,
        grade_json: payload.grade_json,
        bpm: payload.bpm,
        duracao_seg: payload.duracao_seg,
      });
      return;
    }

    var set = function (name, val) {
      var el = document.querySelector('[name="' + name + '"]');
      if (el && val != null && val !== "") el.value = val;
    };
    set("titulo", payload.titulo);
    set("artista", payload.artista);
    set("tom_original", payload.tom_original);

    var ta = document.getElementById("conteudo");
    if (ta && payload.conteudo) ta.value = payload.conteudo;

    if (payload.cifra_json) {
      var cj = document.getElementById("cifra_json_hidden");
      if (cj) cj.value = JSON.stringify(payload.cifra_json);
    }
    if (payload.grade_json) {
      var gj = document.getElementById("grade_json_hidden");
      if (gj) gj.value = JSON.stringify(payload.grade_json);
      var gradeTa = document.getElementById("grade_text");
      if (gradeTa && window.SetSyncGradeVisual) {
        gradeTa.value = SetSyncGradeVisual.jsonToText(payload.grade_json);
      }
    }

    if (typeof renderPreview === "function") {
      if (payload.cifra_json) renderPreview(payload.cifra_json);
      else if (typeof parseConteudo === "function" && ta)
        renderPreview(parseConteudo(ta.value));
    }
  }

  function importCifra(item, statusEl, btn) {
    if (!item.artist_slug || !item.song_slug) return;

    var prev = btn.textContent;
    btn.disabled = true;
    setStatus(statusEl, "Importando cifra…");

    var scrape = item.cached ? "0" : "1";
    fetch(
      "/cifras/import/api/api-cifras/" +
        encodeURIComponent(item.artist_slug) +
        "/" +
        encodeURIComponent(item.song_slug) +
        "?scrape=" +
        scrape,
      { credentials: "same-origin" }
    )
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error((data && data.detail) || "Falha ao importar.");
          return data;
        });
      })
      .then(function (data) {
        applyPayload(data);
        setReferenciaSnapshot(data);
        setStatus(
          statusEl,
          data.cached
            ? "Cifra importada do cache local."
            : "Cifra baixada online (ainda não estava no cache local)."
        );
      })
      .catch(function (err) {
        setStatus(statusEl, err.message || String(err), true);
      })
      .finally(function () {
        btn.disabled = false;
      });
  }

  function runSearch(root) {
    var input = root.querySelector("[data-api-cifras-input]");
    var statusEl = root.querySelector("[data-api-cifras-status]");
    var resultsEl = root.querySelector("[data-api-cifras-results]");
    var q = (input && input.value || "").trim();
    if (q.length < 2) {
      setStatus(statusEl, "Digite pelo menos 2 caracteres.", true);
      renderResults(resultsEl, [], function () {});
      return;
    }

    setStatus(statusEl, "Buscando…");
    fetch(
      "/cifras/import/api/buscar?q=" + encodeURIComponent(q) + "&limit=20",
      { credentials: "same-origin" }
    )
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error((data && data.detail) || "Busca falhou.");
          return data;
        });
      })
      .then(function (data) {
        var items = data.items || [];
        if (!items.length) {
          setStatus(statusEl, "Nenhum resultado para «" + q + "».");
          renderResults(resultsEl, [], function () {});
          return;
        }
        setStatus(statusEl, items.length + " resultado(s). Toque para importar.");
        renderResults(resultsEl, items, function (item, btn) {
          importCifra(item, statusEl, btn);
        });
      })
      .catch(function (err) {
        setStatus(statusEl, err.message || String(err), true);
        renderResults(resultsEl, [], function () {});
      });
  }

  function attach(root) {
    if (!root || root.dataset.apiCifrasBound) return;
    root.dataset.apiCifrasBound = "1";

    var input = root.querySelector("[data-api-cifras-input]");
    var submit = root.querySelector("[data-api-cifras-submit]");

    function scheduleSearch() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        runSearch(root);
      }, 350);
    }

    if (submit) {
      submit.addEventListener("click", function () {
        runSearch(root);
      });
    }
    if (input) {
      input.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter") {
          ev.preventDefault();
          runSearch(root);
        }
      });
      input.addEventListener("input", scheduleSearch);
    }
  }

  document.querySelectorAll("[data-api-cifras-search]").forEach(attach);
})();
