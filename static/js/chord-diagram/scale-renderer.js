/** Renderização SVG de escalas no braço */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var LAYOUT = CD.LAYOUT;

  function renderScaleDiagram(inst, rootNote, scaleId, scaleMeta) {
    var tuning = CD.TUNINGS[inst] || [];
    var def = CD.SCALE_TYPES[scaleId];
    if (!def || !tuning.length) {
      return '<div class="text-muted">Escala não disponível.</div>';
    }

    var windowFrets = LAYOUT.rows;
    var data = CD.buildScaleFretPoints(tuning, rootNote, scaleId, windowFrets);
    var startFret = data.startFret;
    var points = data.points;
    var rows = LAYOUT.rows;
    var colGap = LAYOUT.colGap;
    var rowGap = LAYOUT.rowGap;
    var marginX = LAYOUT.marginX;
    var marginY = LAYOUT.marginY;
    var boardW = (tuning.length - 1) * colGap;
    var boardH = rows * rowGap;
    var svgW = marginX * 2 + boardW;
    var svgH = marginY + boardH + 18;
    var title = CD.escText((scaleMeta && scaleMeta.label) || def.label);
    var rootLabel = CD.escText(rootNote);
    var notesLine = CD.escText((data.scaleNotes || []).join(' · '));

    var parts = [];
    parts.push(
      '<div class="text-muted mb-2" style="font-size:0.75rem;">Escala de ' + rootLabel + ' · ' + title + '</div>',
      '<div class="diagram-chord-name diagram-scale-name">' + title + '</div>',
      '<div class="chord-notes mb-2">Notas: ' + notesLine + '</div>',
      '<div class="chord-diagram-wrap">',
      '<svg class="diagram-svg diagram-scale-svg" role="img" aria-label="Escala ' + title + ' em ' + rootLabel + '" ',
      'width="' + svgW + '" height="' + svgH + '" viewBox="0 0 ' + svgW + ' ' + svgH + '">'
    );

    for (var rr = 0; rr <= rows; rr++) {
      var y = marginY + (rr * rowGap);
      var cls = (rr === 0 && startFret === 0) ? 'diagram-nut' : 'diagram-grid';
      parts.push(
        '<line class="' + cls + '" x1="' + marginX + '" y1="' + y + '" x2="' + (marginX + boardW) + '" y2="' + y + '"></line>'
      );
    }

    for (var ss = 0; ss < tuning.length; ss++) {
      var x = marginX + (ss * colGap);
      parts.push(
        '<line class="diagram-grid" x1="' + x + '" y1="' + marginY + '" x2="' + x + '" y2="' + (marginY + boardH) + '"></line>'
      );
    }

    if (startFret > 0) {
      parts.push(
        '<text class="diagram-fret-text" x="' + (marginX - 8) + '" y="' + (marginY + rowGap / 2) + '">' + startFret + 'fr</text>'
      );
    }

    var topY = marginY - 12;
    points.forEach(function (pt) {
      var dx = marginX + (pt.string * colGap);
      if (pt.fret === 0 && startFret === 0) {
        var openCls = pt.isRoot ? 'diagram-scale-dot diagram-scale-root diagram-scale-open' : 'diagram-scale-dot diagram-scale-open';
        parts.push('<circle class="' + openCls + '" cx="' + dx + '" cy="' + topY + '" r="' + (pt.isRoot ? 7 : 5) + '"></circle>');
        return;
      }
      var relFret = pt.fret - startFret;
      if (relFret < 0 || relFret > rows) return;
      var fy = marginY + ((relFret + 0.5) * rowGap);
      if (pt.isRoot) {
        parts.push('<circle class="diagram-scale-dot diagram-scale-root" cx="' + dx + '" cy="' + fy + '" r="8"></circle>');
      } else {
        parts.push('<circle class="diagram-scale-dot" cx="' + dx + '" cy="' + fy + '" r="6"></circle>');
      }
    });

    parts.push('</svg></div>');
    return parts.join('');
  }

  CD.renderScaleDiagram = renderScaleDiagram;
})(typeof window !== 'undefined' ? window : globalThis);
