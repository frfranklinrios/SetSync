/** Renderização SVG de diagramas de acordes */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var LAYOUT = CD.LAYOUT;

  function renderMuteMarker(x, y) {
    return '<text class="diagram-string-mark" x="' + x + '" y="' + y + '">X</text>';
  }

  function renderOpenMarker(x, y) {
    return '<text class="diagram-string-mark" x="' + x + '" y="' + y + '">o</text>';
  }

  function renderBarrePill(x1, x2, y) {
    var h = LAYOUT.barreHeight || 18;
    var left = Math.min(x1, x2) - h / 2;
    var w = Math.abs(x2 - x1) + h;
    return '<rect class="diagram-barre" x="' + left + '" y="' + (y - h / 2) + '" width="' + w + '" height="' + h + '" rx="' + (h / 2) + '"></rect>';
  }

  function renderBarreLabels(barres, fingers, tuning, grid, startFret, leftHanded, labelMode, frets) {
    if (labelMode !== 'dedos' || !barres.length) return '';
    var parts = [];
    barres.forEach(function (bar) {
      var y = CD.fretY(grid.marginY, grid.rowGap, bar.fret, startFret);
      if (y < grid.marginY - 5 || y > grid.marginY + grid.boardH + 5) return;
      var span = CD.barreDrawRange(bar, frets, tuning.length);
      if (!span) return;
      var x1 = CD.stringX(grid.marginX, grid.colGap, span.from, tuning.length, leftHanded);
      var x2 = CD.stringX(grid.marginX, grid.colGap, span.to, tuning.length, leftHanded);
      var finger = CD.barreFingerLabel(bar, frets, fingers);
      parts.push(
        '<text class="diagram-finger-num diagram-barre-num" fill="#fff" x="' + ((x1 + x2) / 2) + '" y="' + y + '">' +
        CD.escText(finger) + '</text>'
      );
    });
    return parts.join('');
  }

  function renderDotLabels(frets, fingers, tuning, chord, labelMode, grid, startFret, leftHanded, barres) {
    var parts = [];
    for (var dd = 0; dd < frets.length; dd++) {
      if (CD.stringOnBarre(dd, frets, barres)) continue;
      var fval = frets[dd];
      if (fval === 'x' || (fval === 0 && startFret === 0)) continue;
      if (typeof fval !== 'number' || fval <= 0) continue;
      var fy = CD.fretY(grid.marginY, grid.rowGap, fval, startFret);
      if (fy < grid.marginY || fy > grid.marginY + grid.boardH) continue;
      var text = dotLabel(fingers, dd, tuning, frets, chord, labelMode);
      if (!text) continue;
      var dx = CD.stringX(grid.marginX, grid.colGap, dd, tuning.length, leftHanded);
      var cls = 'diagram-finger-num';
      if (labelMode === 'notas' || labelMode === 'intervalos') cls += ' diagram-note-label';
      parts.push('<text class="' + cls + '" fill="#fff" x="' + dx + '" y="' + fy + '">' + CD.escText(text) + '</text>');
    }
    return parts.join('');
  }

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

  function resolveBarres(frets, fingers, explicitBarres) {
    return CD.detectBarres(frets, fingers, explicitBarres);
  }

  function renderChordDiagramSvg(opts) {
    var inst = opts.instrument;
    var chord = opts.chord || {};
    var tuning = CD.TUNINGS[inst] || [];
    var adapted = CD.adaptVoicingForStrings(
      opts.frets || tuning.map(function () { return 'x'; }),
      opts.fingers || null,
      opts.barres,
      tuning.length
    );
    var frets = adapted.frets;
    var fingers = adapted.fingers;
    var labelMode = opts.labelMode || 'dedos';
    var leftHanded = !!opts.leftHanded;
    var win = CD.computeWindow(frets, LAYOUT.rows);
    var startFret = win.startFret;
    var rows = win.rows;

    var grid = CD.renderFretboardGrid({
      tuning: tuning,
      rows: rows,
      startFret: startFret,
      leftHanded: leftHanded,
    });
    var topMarkerY = grid.marginY - 13;

    var barres = resolveBarres(frets, fingers, adapted.barres);
    var chordName = CD.escText(chord.display || chord.input || '');
    var sourceLabel = CD.escText(opts.sourceLabel || 'Shape sugerido');
    var capoHint = opts.capoHint ? '<div class="diagram-capo-hint"><i class="fas fa-ring me-1"></i>' + CD.escText(opts.capoHint) + '</div>' : '';

    var parts = [];
    parts.push(
      '<div class="text-muted mb-2" style="font-size:0.85rem;">' + sourceLabel + '</div>',
      capoHint,
      '<div class="diagram-chord-name">' + chordName + '</div>',
      '<div class="chord-diagram-wrap">',
      '<svg class="diagram-svg" role="img" aria-label="Diagrama do acorde ' + chordName + '" ',
      'width="' + grid.svgW + '" height="' + grid.svgH + '" viewBox="0 0 ' + grid.svgW + ' ' + grid.svgH + '">',
      CD.renderDiagramDefs(),
      grid.html
    );

    barres.forEach(function (bar) {
      var yBar = CD.fretY(grid.marginY, grid.rowGap, bar.fret, startFret);
      if (yBar < grid.marginY - 2 || yBar > grid.marginY + grid.boardH + 2) return;
      var span = CD.barreDrawRange(bar, frets, tuning.length);
      if (!span) return;
      var x1 = CD.stringX(grid.marginX, grid.colGap, span.from, tuning.length, leftHanded);
      var x2 = CD.stringX(grid.marginX, grid.colGap, span.to, tuning.length, leftHanded);
      parts.push(renderBarrePill(x1, x2, yBar));
    });

    for (var tt = 0; tt < frets.length; tt++) {
      var fx = CD.stringX(grid.marginX, grid.colGap, tt, tuning.length, leftHanded);
      if (frets[tt] === 'x') {
        parts.push(renderMuteMarker(fx, topMarkerY));
      } else if (frets[tt] === 0 && startFret === 0) {
        parts.push(renderOpenMarker(fx, topMarkerY));
      }
    }

    for (var dd = 0; dd < frets.length; dd++) {
      if (CD.stringOnBarre(dd, frets, barres)) continue;
      var fval = frets[dd];
      if (fval === 'x' || (fval === 0 && startFret === 0)) continue;
      if (typeof fval !== 'number' || fval <= 0) continue;
      var fy = CD.fretY(grid.marginY, grid.rowGap, fval, startFret);
      if (fy < grid.marginY || fy > grid.marginY + grid.boardH) continue;
      var dx = CD.stringX(grid.marginX, grid.colGap, dd, tuning.length, leftHanded);
      parts.push(
        '<circle class="diagram-dot" cx="' + dx + '" cy="' + fy + '" r="' + LAYOUT.dotR + '"></circle>'
      );
    }

    parts.push(renderBarreLabels(barres, fingers, tuning, grid, startFret, leftHanded, labelMode, frets));
    parts.push(renderDotLabels(frets, fingers, tuning, chord, labelMode, grid, startFret, leftHanded, barres));
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
      barres: shapeOption && shapeOption.barres,
      sourceLabel: (shapeOption && shapeOption.source) || 'chords-db',
      labelMode: renderOpts.labelMode || 'dedos',
      leftHanded: renderOpts.leftHanded,
      capoHint: capoHint,
    });
  }

  CD.renderChordDiagramSvg = renderChordDiagramSvg;
  CD.renderChordDiagram = renderChordDiagram;
})(typeof window !== 'undefined' ? window : globalThis);
