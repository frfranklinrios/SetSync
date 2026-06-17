/** Renderização SVG de escalas no braço */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var LAYOUT = CD.LAYOUT;

  function renderScaleDiagram(inst, rootNote, scaleId, scaleMeta, renderOpts) {
    renderOpts = renderOpts || {};
    var tuning = CD.TUNINGS[inst] || [];
    var def = CD.SCALE_TYPES[scaleId];
    if (!def || !tuning.length) {
      return '<div class="text-muted">Escala não disponível.</div>';
    }

    var windowFrets = renderOpts.scaleRows || 12;
    var startFret = renderOpts.scaleStart != null
      ? renderOpts.scaleStart
      : CD.defaultScaleStart(tuning, rootNote);
    var leftHanded = !!renderOpts.leftHanded;
    var showNotes = renderOpts.scaleShowNotes !== false;
    var chordTones = renderOpts.chordTones || null;

    var data = CD.buildScaleFretPoints(tuning, rootNote, scaleId, startFret, windowFrets);
    var rows = windowFrets;
    var grid = CD.renderFretboardGrid({
      tuning: tuning,
      rows: rows,
      startFret: startFret,
      leftHanded: leftHanded,
      marginX: 32,
    });

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
      'width="' + grid.svgW + '" height="' + grid.svgH + '" viewBox="0 0 ' + grid.svgW + ' ' + grid.svgH + '">',
      CD.renderDiagramDefs(),
      grid.html
    );

    data.points.forEach(function (pt) {
      var dx = CD.stringX(grid.marginX, grid.colGap, pt.string, tuning.length, leftHanded);
      var fy;
      if (pt.fret === 0 && startFret === 0) {
        fy = grid.marginY - 10;
      } else {
        fy = CD.fretY(grid.marginY, grid.rowGap, pt.fret, startFret);
        if (fy < grid.marginY || fy > grid.marginY + grid.boardH) return;
      }
      var isChordTone = false;
      if (chordTones) {
        var pi = CD.noteIndex(pt.note);
        isChordTone = pi != null && chordTones[pi];
      }
      var cls = 'diagram-scale-dot';
      if (pt.isRoot) cls += ' diagram-scale-root';
      else if (isChordTone) cls += ' diagram-scale-chord-tone';
      var r = pt.isRoot ? 8 : (isChordTone ? 7 : 5.5);
      parts.push('<circle class="' + cls + '" cx="' + dx + '" cy="' + fy + '" r="' + r + '"></circle>');
      if (showNotes) {
        parts.push(
          '<text class="diagram-scale-note-label" x="' + dx + '" y="' + fy + '">' + CD.escText(pt.note) + '</text>'
        );
      }
    });

    parts.push(CD.renderTuningLabels(tuning, grid, leftHanded));
    parts.push('</svg></div>');
    return parts.join('');
  }

  CD.renderScaleDiagram = renderScaleDiagram;
})(typeof window !== 'undefined' ? window : globalThis);
