/** Renderização SVG de diagramas de acordes */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var LAYOUT = CD.LAYOUT;

  function dotLabel(fingers, stringIdx, tuning, frets, chord, labelMode) {
    var finger = fingers && fingers[stringIdx];
    if (labelMode === 'dedos' && finger && finger > 0) return String(finger);
    var note = CD.noteAt(tuning, stringIdx, frets[stringIdx]);
    if (!note) return '';
    if (labelMode === 'intervalos' && chord && chord.notes && chord.notes.length) {
      return CD.intervalLabel(chord.notes[0], note) || note;
    }
    if (labelMode === 'notas' || labelMode === 'intervalos') return note;
    if (finger && finger > 0) return String(finger);
    return note;
  }

  function renderChordDiagramSvg(opts) {
    var inst = opts.instrument;
    var chord = opts.chord || {};
    var tuning = CD.TUNINGS[inst] || [];
    var frets = opts.frets || tuning.map(function () { return 'x'; });
    var fingers = opts.fingers || null;
    var notes = chord.notes || [];
    var labelMode = opts.labelMode || 'dedos';
    var leftHanded = !!opts.leftHanded;
    var win = CD.computeWindow(frets, LAYOUT.rows);
    var startFret = win.startFret;
    var rows = win.rows;
    var topMarkerY = LAYOUT.marginY - 14;

    var grid = CD.renderFretboardGrid({
      tuning: tuning,
      rows: rows,
      startFret: startFret,
      leftHanded: leftHanded,
    });

    var rootStr = notes.length ? CD.rootStringIndex(tuning, frets, notes[0]) : -1;
    var barres = CD.detectBarres(frets);
    var chordName = CD.escText(chord.display || chord.input || '');
    var sourceLabel = CD.escText(opts.sourceLabel || 'Shape sugerido');
    var capoHint = opts.capoHint ? '<div class="diagram-capo-hint"><i class="fas fa-ring me-1"></i>' + CD.escText(opts.capoHint) + '</div>' : '';

    var parts = [];
    parts.push(
      '<div class="text-muted mb-2" style="font-size:0.75rem;">' + sourceLabel + '</div>',
      capoHint,
      '<div class="diagram-chord-name">' + chordName + '</div>',
      '<div class="chord-diagram-wrap">',
      '<svg class="diagram-svg" role="img" aria-label="Diagrama do acorde ' + chordName + '" ',
      'width="' + grid.svgW + '" height="' + grid.svgH + '" viewBox="0 0 ' + grid.svgW + ' ' + grid.svgH + '">',
      grid.html
    );

    for (var tt = 0; tt < frets.length; tt++) {
      var fx = CD.stringX(grid.marginX, grid.colGap, tt, tuning.length, leftHanded);
      if (frets[tt] === 'x') {
        parts.push('<text class="diagram-mute" x="' + fx + '" y="' + topMarkerY + '">×</text>');
      } else if (frets[tt] === 0 && startFret === 0) {
        parts.push('<text class="diagram-open" x="' + fx + '" y="' + topMarkerY + '">○</text>');
      }
    }

    barres.forEach(function (bar) {
      var yBar = CD.fretY(grid.marginY, grid.rowGap, bar.fret, startFret);
      if (yBar < grid.marginY - 5 || yBar > grid.marginY + grid.boardH + 5) return;
      var x1 = CD.stringX(grid.marginX, grid.colGap, bar.from, tuning.length, leftHanded);
      var x2 = CD.stringX(grid.marginX, grid.colGap, bar.to, tuning.length, leftHanded);
      parts.push(
        '<line class="diagram-barre" x1="' + x1 + '" y1="' + yBar + '" x2="' + x2 + '" y2="' + yBar + '"></line>'
      );
    });

    for (var dd = 0; dd < frets.length; dd++) {
      var fval = frets[dd];
      if (fval === 'x') continue;
      var fy;
      if (fval === 0 && startFret === 0) {
        fy = topMarkerY + 2;
      } else if (typeof fval === 'number' && fval > 0) {
        fy = CD.fretY(grid.marginY, grid.rowGap, fval, startFret);
        if (fy < grid.marginY || fy > grid.marginY + grid.boardH) continue;
      } else {
        continue;
      }
      var dx = CD.stringX(grid.marginX, grid.colGap, dd, tuning.length, leftHanded);
      var isRoot = dd === rootStr;
      var dotCls = isRoot ? 'diagram-dot diagram-dot-root' : 'diagram-dot';
      var r = isRoot ? LAYOUT.rootDotR : LAYOUT.dotR;
      if (fval === 0) r = 6;
      parts.push('<circle class="' + dotCls + '" cx="' + dx + '" cy="' + fy + '" r="' + r + '"></circle>');
      var text = dotLabel(fingers, dd, tuning, frets, chord, labelMode);
      if (text) {
        var cls = 'diagram-finger-num' + (labelMode === 'notas' ? ' diagram-note-label' : '');
        parts.push('<text class="' + cls + '" x="' + dx + '" y="' + fy + '">' + CD.escText(text) + '</text>');
      }
    }

    parts.push(CD.renderTuningLabels(tuning, grid, leftHanded));
    parts.push('</svg></div>');
    return parts.join('');
  }

  function renderChordDiagram(inst, chord, shapeOption, renderOpts) {
    renderOpts = renderOpts || {};
    var tuning = CD.TUNINGS[inst];
    var frets = shapeOption && shapeOption.frets
      ? shapeOption.frets
      : CD.buildAutoShape(tuning, chord.notes || []);
    var capoHint = '';
    if (shapeOption && shapeOption.label && /casa|pestana/i.test(shapeOption.label)) {
      capoHint = shapeOption.label;
    }
    return renderChordDiagramSvg({
      instrument: inst,
      chord: chord,
      frets: frets,
      fingers: shapeOption && shapeOption.fingers,
      sourceLabel: (shapeOption && shapeOption.source) || 'Cifra clássica',
      labelMode: renderOpts.labelMode || 'dedos',
      leftHanded: renderOpts.leftHanded,
      capoHint: capoHint,
    });
  }

  CD.renderChordDiagramSvg = renderChordDiagramSvg;
  CD.renderChordDiagram = renderChordDiagram;
})(typeof window !== 'undefined' ? window : globalThis);
