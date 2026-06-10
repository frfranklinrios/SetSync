/** Renderização visual do chord sheet (compartilhado entre index e embed). */
(function (global) {
  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderBar(acordes) {
    const cells = (acordes || []).map((a) => {
      const t = String(a || "").trim();
      if (t === "%") return '<span class="chord repeat">%</span>';
      return `<span class="chord">${esc(t)}</span>`;
    });
    return `<span class="grade-bar">${cells.join('<span class="sep">·</span>')}</span>`;
  }

  function renderBloco(compassos) {
    const bars = compassos.map((c) => renderBar(c.acordes)).join("");
    return `<div class="grade-bloco">${bars}</div>`;
  }

  function renderGradeView(el, partes, compasso) {
    if (!el) return;
    if (!partes || !partes.length) {
      el.innerHTML = '<div class="grade-panel-header">Sem chord sheet para exibir.</div>';
      return;
    }

    let header = "Chord sheet";
    if (compasso) header += ` · Compasso ${esc(compasso)}`;
    let html = `<div class="grade-panel-header">${header}</div>`;

    partes.forEach((parte) => {
      html += `<div class="grade-parte"><div class="grade-parte-nome">${esc(parte.nome)}</div>`;
      let bloco = [];
      (parte.compassos || []).forEach((c) => {
        if (c.secao) {
          if (bloco.length) {
            html += renderBloco(bloco);
            bloco = [];
          }
          html += `<div class="grade-secao">${esc(c.secao)}</div>`;
        }
        bloco.push(c);
      });
      if (bloco.length) html += renderBloco(bloco);
      html += "</div>";
    });

    el.innerHTML = html;
  }

  global.CifrasGradeRender = { esc, renderGradeView, renderBloco, renderBar };
})(window);
