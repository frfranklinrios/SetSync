/**
 * Núcleo SVG do braço — compartilhado entre acordes e escalas.
 */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  var CHROMATIC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

  function computeWindow(frets, rows) {
    rows = rows || (CD.LAYOUT && CD.LAYOUT.rows) || 5;
    var nums = [];
    var hasOpen = false;
    (frets || []).forEach(function (f) {
      if (f === 0) hasOpen = true;
      else if (typeof f === 'number' && f > 0) nums.push(f);
    });
    if (!nums.length) {
      return { startFret: hasOpen ? 0 : 1, rows: rows, showNut: hasOpen || !nums.length };
    }
    var minF = Math.min.apply(null, nums);
    var maxF = Math.max.apply(null, nums);
    // Uma casa mais grave que a primeira nota (estilo Cifra Club)
    var start = hasOpen ? 0 : Math.max(0, minF - 1);
    if (!hasOpen && maxF - start + 1 > rows) {
      start = Math.max(0, maxF - rows + 1);
    }
    return {
      startFret: start,
      rows: rows,
      showNut: start === 0,
      endFret: start + rows - (start === 0 ? 0 : 1),
    };
  }

  function fretY(marginY, rowGap, fret, startFret) {
    if (fret === 0 && startFret === 0) return marginY - 12;
    if (startFret === 0) {
      return marginY + ((fret - 0.5) * rowGap);
    }
    return marginY + ((fret - startFret + 0.5) * rowGap);
  }

  function renderDiagramDefs() {
    return '';
  }

  function stringX(marginX, colGap, stringIdx, stringCount, leftHanded) {
    var idx = leftHanded ? (stringCount - 1 - stringIdx) : stringIdx;
    return marginX + (idx * colGap);
  }

  function mirrorString(stringIdx, stringCount, leftHanded) {
    return leftHanded ? (stringCount - 1 - stringIdx) : stringIdx;
  }

  function renderFretboardGrid(opts) {
    var L = CD.LAYOUT;
    var tuning = opts.tuning || [];
    var rows = opts.rows || L.rows;
    var startFret = opts.startFret || 0;
    var leftHanded = !!opts.leftHanded;
    var marginX = opts.marginX != null ? opts.marginX : L.marginX;
    var marginY = opts.marginY != null ? opts.marginY : L.marginY;
    var colGap = L.colGap;
    var rowGap = L.rowGap;
    var boardW = (tuning.length - 1) * colGap;
    var boardH = rows * rowGap;
    var padX = L.boardPad || 8;
    var padY = L.boardPad || 8;
    var boardRadius = L.boardRadius || 10;
    var parts = [];

    parts.push(
      '<rect class="diagram-board" x="' + (marginX - padX) + '" y="' + (marginY - padY) + '" ',
      'width="' + (boardW + padX * 2) + '" height="' + (boardH + padY * 2) + '" rx="' + boardRadius + '"></rect>'
    );

    for (var rr = 0; rr <= rows; rr++) {
      var y = marginY + (rr * rowGap);
      var isNut = rr === 0 && startFret === 0;
      parts.push(
        '<line class="' + (isNut ? 'diagram-nut' : 'diagram-fret') + '" x1="' + (marginX - 2) + '" y1="' + y +
        '" x2="' + (marginX + boardW + 2) + '" y2="' + y + '"></line>'
      );
    }

    for (var ss = 0; ss < tuning.length; ss++) {
      var x = stringX(marginX, colGap, ss, tuning.length, leftHanded);
      parts.push(
        '<line class="diagram-string" x1="' + x + '" y1="' + marginY + '" x2="' + x + '" y2="' + (marginY + boardH) + '"></line>'
      );
    }

    for (var fr = 0; fr < rows; fr++) {
      var fretNum = startFret === 0 ? fr + 1 : startFret + fr;
      parts.push(
        '<text class="diagram-fret-side" x="' + (marginX - 18) + '" y="' + (marginY + fr * rowGap + rowGap / 2) + '">' +
        fretNum + '</text>'
      );
    }

    return {
      html: parts.join(''),
      boardW: boardW,
      boardH: boardH,
      marginX: marginX,
      marginY: marginY,
      colGap: colGap,
      rowGap: rowGap,
      svgW: marginX * 2 + boardW,
      svgH: marginY + boardH + (L.bottomPad || 48),
    };
  }

  /** Grade horizontal — arpejos de baixo (cordas em linhas, trastes em colunas). */
  function renderHorizontalFretboardGrid(opts) {
    var L = CD.LAYOUT;
    var tuning = opts.tuning || [];
    var rows = tuning.slice().reverse();
    var cols = opts.cols || L.bassCols || 6;
    var startFret = opts.startFret || 0;
    var marginLeft = opts.marginLeft != null ? opts.marginLeft : L.marginX;
    var marginTop = opts.marginTop != null ? opts.marginTop : L.marginY;
    var colGap = L.colGap;
    var rowGap = L.rowGap;
    var boardW = cols * colGap;
    var boardH = (rows.length - 1) * rowGap;
    var padX = L.boardPad || 8;
    var padY = L.boardPad || 8;
    var boardRadius = L.boardRadius || 10;
    var labelX = L.sideLabelX || 18;
    var parts = [];

    parts.push(
      '<rect class="diagram-board" x="' + (marginLeft - padX) + '" y="' + (marginTop - padY) + '" ',
      'width="' + (boardW + padX * 2) + '" height="' + (boardH + padY * 2) + '" rx="' + boardRadius + '"></rect>'
    );

    for (var r = 0; r < rows.length; r++) {
      var y = marginTop + (r * rowGap);
      parts.push(
        '<line class="diagram-string" x1="' + marginLeft + '" y1="' + y + '" x2="' + (marginLeft + boardW) + '" y2="' + y + '"></line>',
        '<text class="diagram-side-label diagram-string-side" x="' + labelX + '" y="' + y + '">' + CD.escText(rows[r]) + '</text>'
      );
    }

    for (var c = 0; c <= cols; c++) {
      var x = marginLeft + (c * colGap);
      var isNut = c === 0 && startFret === 0;
      parts.push(
        '<line class="' + (isNut ? 'diagram-nut' : 'diagram-fret') + '" x1="' + x + '" y1="' + marginTop + '" x2="' + x + '" y2="' + (marginTop + boardH) + '"></line>'
      );
    }

    var labelY = marginTop + boardH + 18;
    for (var fc = 0; fc < cols; fc++) {
      var fretNum = startFret + fc + 1;
      parts.push(
        '<text class="diagram-tuning diagram-fret-bottom" x="' + (marginLeft + fc * colGap + colGap / 2) + '" y="' + labelY + '">' + fretNum + '</text>'
      );
    }

    return {
      html: parts.join(''),
      rows: rows,
      rowIndex: rows.reduce(function (acc, s, i) { acc[s] = i; return acc; }, {}),
      boardW: boardW,
      boardH: boardH,
      marginLeft: marginLeft,
      marginTop: marginTop,
      colGap: colGap,
      rowGap: rowGap,
      cols: cols,
      startFret: startFret,
      svgW: marginLeft + boardW + (L.marginX - padX),
      svgH: marginTop + boardH + (L.bottomPad || 48),
    };
  }

  function horizontalFretX(grid, fret) {
    if (fret === 0) return grid.marginLeft - (CD.LAYOUT.openR || 7) - 6;
    return grid.marginLeft + ((fret - grid.startFret - 0.5) * grid.colGap);
  }

  function horizontalStringY(grid, stringName) {
    var idx = grid.rowIndex[stringName];
    if (idx == null) return null;
    return grid.marginTop + (idx * grid.rowGap);
  }

  function fretVisible(fret, startFret, cols) {
    return fret > startFret && fret <= startFret + cols;
  }

  function renderTuningLabels(tuning, layout, leftHanded) {
    var parts = [];
    var y = layout.marginY + layout.boardH + 18;
    for (var tu = 0; tu < tuning.length; tu++) {
      var tx = stringX(layout.marginX, layout.colGap, tu, tuning.length, leftHanded);
      parts.push('<text class="diagram-tuning" x="' + tx + '" y="' + y + '">' + CD.escText(tuning[tu]) + '</text>');
    }
    return parts.join('');
  }

  function intervalLabel(rootNote, note) {
    var ri = CD.noteIndex(rootNote);
    var ni = CD.noteIndex(note);
    if (ri == null || ni == null) return '';
    var d = (ni - ri + 12) % 12;
    var map = {
      0: 'R', 1: 'b2', 2: '2', 3: 'b3', 4: '3', 5: '4', 6: 'b5',
      7: '5', 8: '#5', 9: '6', 10: 'b7', 11: '7',
    };
    return map[d] || '';
  }

  function noteAt(tuning, stringIdx, fret) {
    if (fret === 'x') return null;
    var oi = CD.noteIndex(tuning[stringIdx]);
    if (oi == null) return null;
    if (fret === 0) return CHROMATIC[oi];
    return CHROMATIC[(oi + fret) % 12];
  }

  CD.computeWindow = computeWindow;
  CD.renderDiagramDefs = renderDiagramDefs;
  CD.fretY = fretY;
  CD.stringX = stringX;
  CD.mirrorString = mirrorString;
  CD.renderFretboardGrid = renderFretboardGrid;
  CD.renderHorizontalFretboardGrid = renderHorizontalFretboardGrid;
  CD.horizontalFretX = horizontalFretX;
  CD.horizontalStringY = horizontalStringY;
  CD.fretVisible = fretVisible;
  CD.renderTuningLabels = renderTuningLabels;
  CD.intervalLabel = intervalLabel;
  CD.noteAt = noteAt;
  CD.CHROMATIC = CHROMATIC;
})(typeof window !== 'undefined' ? window : globalThis);
