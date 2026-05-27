/**
 * Ponte entre o iframe da ferramenta integrada (cifras_tool) e o formulário add/edit.
 */
(function () {
  function toolUrl() {
    var modalEl = document.getElementById("cifrasToolModal");
    if (modalEl && modalEl.dataset.toolUrl) {
      return modalEl.dataset.toolUrl.replace(/\/+$/, "");
    }
    return "/cifras/import/tool";
  }

  function openCifrasToolModal() {
    var frame = document.getElementById("cifrasToolFrame");
    var modalEl = document.getElementById("cifrasToolModal");
    if (!frame || !modalEl) return;

    frame.src = toolUrl();
    var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  }

  function buildEditableTextFromCifraJson(data) {
    if (!Array.isArray(data) || !data.length) return "";
    var lines = [];
    var lastGroup = null;
    data.forEach(function (item) {
      var g = item.group != null ? item.group : 0;
      if (lastGroup !== null && g !== lastGroup) lines.push("");
      lastGroup = g;
      var ac = item.acorde ? "[" + item.acorde + "]" : "";
      lines.push(ac + (item.texto_letra || ""));
    });
    return lines.join("\n");
  }

  function applyCifrasToolResult(payload) {
    if (!payload || payload.type !== "setsync-cifras-apply") return;

    var set = function (name, val) {
      var el = document.querySelector('[name="' + name + '"]');
      if (el && val != null && val !== "") el.value = val;
    };

    set("titulo", payload.titulo);
    set("artista", payload.artista);
    set("tom_original", payload.tom_original);

    var conteudo = payload.conteudo || "";
    if (!conteudo && payload.cifra_json && payload.cifra_json.length) {
      conteudo = buildEditableTextFromCifraJson(payload.cifra_json);
    }
    var ta = document.getElementById("conteudo");
    if (ta) ta.value = conteudo;

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
    if (payload.bpm != null) set("bpm", payload.bpm);
    if (payload.duracao_seg != null) {
      var ds = document.getElementById("duracao_seg_hidden");
      if (ds) ds.value = payload.duracao_seg;
    }

    if (typeof renderPreview === "function" && payload.cifra_json) {
      renderPreview(payload.cifra_json);
    } else if (typeof renderPreview === "function" && conteudo) {
      if (typeof parseConteudo === "function") renderPreview(parseConteudo(conteudo));
    }

    var modalEl = document.getElementById("cifrasToolModal");
    if (modalEl) {
      var modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }
  }

  window.openCifrasToolModal = openCifrasToolModal;
  window.applyCifrasToolResult = applyCifrasToolResult;

  window.addEventListener("message", function (ev) {
    if (!ev.data || ev.data.type !== "setsync-cifras-apply") return;
    applyCifrasToolResult(ev.data);
  });
})();
