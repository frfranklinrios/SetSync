/** Renderização SVG de diagramas de acordes */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var LAYOUT = CD.LAYOUT;

  function escText(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * Gera SVG do diagrama de acordes.
   * @param {object} opts - { instrument, chord, frets, sourceLabel }
   */
  function renderChordDiagramSvg(opts) {
    var inst = opts.instrument;
    var chord = opts.chord || {};
    var tuning = CD.TUNINGS[inst] || [];
    var frets = opts.frets || tuning.map(function () { return 'x'; });
    var fingers = opts.fingers || null;
    var notes = chord.notes || [];
    var played = frets.filter(function (f) { return typeof f === 'number' && f > 0; });
    var startFret = played.length ? Math.min.apply(null, played) : 1;
    if (startFret < 1) startFret = 1;

    var rows = LAYOUT.rows;
    var colGap = LAYOUT.colGap;
    var rowGap = LAYOUT.rowGap;
    var marginX = LAYOUT.marginX;
    var marginY = LAYOUT.marginY;
    var topMarkerY = marginY - 14;
    var boardW = (tuning.length - 1) * colGap;
    var boardH = rows * rowGap;
    var svgW = marginX * 2 + boardW;
    var svgH = marginY + boardH + 18;
    var rootStr = notes.length ? CD.rootStringIndex(tuning, frets, notes[0]) : -1;
    var barres = CD.detectBarres(frets);
    var chordName = escText(chord.display || chord.input || '');
    var sourceLabel = escText(opts.sourceLabel || 'Shape sugerido');

    var parts = [];
    parts.push(
      '<div class="text-muted mb-2" style="font-size:0.75rem;">' + sourceLabel + '</div>',
      '<div class="diagram-chord-name">' + chordName + '</div>',
      '<div class="chord-diagram-wrap">',
      '<svg class="diagram-svg" role="img" aria-label="Diagrama do acorde ' + chordName + '" ',
      'width="' + svgW + '" height="' + svgH + '" viewBox="0 0 ' + svgW + ' ' + svgH + '">'
    );

    for (var rr = 0; rr <= rows; rr++) {
      var y = marginY + (rr * rowGap);
      var cls = (rr === 0 && startFret === 1) ? 'diagram-nut' : 'diagram-grid';
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

    if (startFret > 1) {
      parts.push(
        '<text class="diagram-fret-text" x="' + (marginX - 8) + '" y="' + (marginY + rowGap / 2) + '">' + startFret + 'fr</text>'
      );
    }

    for (var tt = 0; tt < frets.length; tt++) {
      var fx = marginX + (tt * colGap);
      if (frets[tt] === 'x') {
        parts.push('<text class="diagram-mute" x="' + fx + '" y="' + topMarkerY + '">X</text>');
      } else if (frets[tt] === 0) {
        parts.push('<text class="diagram-open" x="' + fx + '" y="' + topMarkerY + '">O</text>');
      }
    }

    barres.forEach(function (bar) {
      var yBar = marginY + ((bar.fret - startFret + 0.5) * rowGap);
      if (yBar < marginY || yBar > marginY + boardH) return;
      var x1 = marginX + (bar.from * colGap);
      var x2 = marginX + (bar.to * colGap);
      parts.push(
        '<line class="diagram-barre" x1="' + x1 + '" y1="' + yBar + '" x2="' + x2 + '" y2="' + yBar + '"></line>'
      );
    });

    for (var dd = 0; dd < frets.length; dd++) {
      var fval = frets[dd];
      if (typeof fval !== 'number' || fval <= 0) continue;
      var fy = marginY + ((fval - startFret + 0.5) * rowGap);
      if (fy < marginY || fy > marginY + boardH) continue;
      var dx = marginX + (dd * colGap);
      var dotCls = dd === rootStr ? 'diagram-dot diagram-dot-root' : 'diagram-dot';
      var r = dd === rootStr ? LAYOUT.rootDotR : LAYOUT.dotR;
      parts.push('<circle class="' + dotCls + '" cx="' + dx + '" cy="' + fy + '" r="' + r + '"></circle>');
      var finger = fingers && fingers[dd];
      if (finger && typeof finger === 'number' && finger > 0) {
        parts.push(
          '<text class="diagram-finger-num" x="' + dx + '" y="' + fy + '">' + finger + '</text>'
        );
      }
    }

    parts.push('</svg></div>');
    return parts.join('');
  }

  function renderChordDiagram(inst, chord, shapeOption) {
    var tuning = CD.TUNINGS[inst];
    var frets = shapeOption && shapeOption.frets
      ? shapeOption.frets
      : CD.buildAutoShape(tuning, chord.notes || []);
    return renderChordDiagramSvg({
      instrument: inst,
      chord: chord,
      frets: frets,
      fingers: shapeOption && shapeOption.fingers,
      sourceLabel: (shapeOption && shapeOption.source) || 'Cifra clássica',
    });
  }

  CD.escText = escText;
  CD.renderChordDiagramSvg = renderChordDiagramSvg;
  CD.renderChordDiagram = renderChordDiagram;
})(typeof window !== 'undefined' ? window : globalThis);
