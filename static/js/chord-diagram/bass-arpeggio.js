/** Diagrama de arpejo para baixo — padrões do Bass Guitar Resource Book */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  function normalizeSymbol(symbol) {
    if (CD.normalizedChordKey) {
      return CD.normalizedChordKey(symbol) || String(symbol || '').replace(/\s+/g, '');
    }
    return String(symbol || '').replace(/\s+/g, '');
  }

  function bankLookupKeys(chord) {
    var display = (chord && (chord.display || chord.input)) || '';
    var input = (chord && chord.input) || '';
    var keys = [];
    function push(k) {
      if (k && keys.indexOf(k) < 0) keys.push(k);
    }
    if (CD.chordKeyCandidates) {
      CD.chordKeyCandidates(display).forEach(push);
      if (input && input !== display) CD.chordKeyCandidates(input).forEach(push);
    }
    push(display.replace(/\s+/g, ''));
    push(input.replace(/\s+/g, ''));
    push(normalizeSymbol(display));
    push(normalizeSymbol(input));
    return keys;
  }

  function lookupBankPattern(chord, patternId) {
    var bank = CD.BASS_ARPEGGIO_BANK;
    if (!bank || !bank.patterns) return null;
    var map = bank.patterns;
    var keys = bankLookupKeys(chord);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (!k || !map[k]) continue;
      var list = map[k];
      for (var j = 0; j < list.length; j++) {
        if (list[j].pattern === patternId) return list[j];
      }
      if (patternId === 'root' && list.length) return list[0];
    }
    return null;
  }

  function stepsFromBank(entry) {
    return (entry.steps || []).map(function (s) {
      return {
        note: s.note,
        string: s.string,
        fret: s.fret,
        finger: s.finger,
        interval: s.interval,
        isRoot: !!s.isRoot,
        source: entry.source || 'The Bass Guitar Resource Book',
      };
    });
  }

  function buildArpeggio(chord, tuning, patternId) {
    if (patternId && patternId !== 'root') {
      return [];
    }

    if (CD.resolveFromQualityTemplates) {
      var resolved = CD.resolveFromQualityTemplates(chord, patternId || 'root');
      if (resolved && resolved.steps && resolved.steps.length) {
        return resolved.steps.map(function (s) {
          return {
            note: s.note,
            string: s.string,
            fret: s.fret,
            finger: s.finger,
            interval: s.interval,
            isRoot: !!s.isRoot,
            source: resolved.source,
          };
        });
      }
    }

    var bankEntry = lookupBankPattern(chord, patternId || 'root');
    if (bankEntry && bankEntry.steps && bankEntry.steps.length) {
      return stepsFromBank(bankEntry);
    }

    return [];
  }

  function computeArpWindow(steps, baseCols) {
    baseCols = baseCols || (CD.LAYOUT && CD.LAYOUT.bassCols) || 6;
    var positiveFrets = steps.map(function (s) { return s.fret; }).filter(function (f) { return f > 0; });
    var hasOpen = steps.some(function (s) { return s.fret === 0; });
    if (!positiveFrets.length) {
      return { startFret: 0, cols: baseCols, showNut: true };
    }
    var minF = Math.min.apply(null, positiveFrets);
    var maxF = Math.max.apply(null, positiveFrets);
    var span = maxF - minF + 1;
    var cols = Math.max(baseCols, span + (hasOpen ? 0 : 1));
    var startFret = 0;
    if (!hasOpen) {
      startFret = Math.max(0, minF - 1);
      if (maxF - startFret + 1 > cols) {
        startFret = Math.max(0, maxF - cols + 1);
      }
      if (minF <= startFret) {
        startFret = Math.max(0, minF - 1);
      }
    }
    return { startFret: startFret, cols: cols, showNut: startFret === 0 || hasOpen };
  }

  function normalizeArpSteps(steps) {
    return (steps || []).map(function (s) {
      return {
        note: s.note,
        string: s.string,
        fret: s.fret,
        finger: s.finger,
        interval: s.interval,
        isRoot: !!s.isRoot,
        source: s.source,
      };
    });
  }

  function renderBassArpeggioDiagram(steps, tuning) {
    var L = CD.LAYOUT;
    var win = computeArpWindow(steps, L.bassCols || 6);
    var grid = CD.renderHorizontalFretboardGrid({
      tuning: tuning,
      cols: win.cols,
      startFret: win.startFret,
    });

    var parts = [
      '<div class="chord-diagram-wrap">',
      '<svg class="diagram-svg diagram-bass-svg" role="img" aria-label="Arpejo de baixo" ',
      'width="' + grid.svgW + '" height="' + grid.svgH + '" viewBox="0 0 ' + grid.svgW + ' ' + grid.svgH + '">',
      CD.renderDiagramDefs(),
      grid.html,
    ];

    for (var i = 0; i < steps.length; i++) {
      var st = steps[i];
      var yPos = CD.horizontalStringY(grid, st.string);
      if (yPos == null) continue;

      if (st.fret === 0) {
        var openX = CD.horizontalFretX(grid, 0);
        parts.push(
          '<circle class="diagram-open-mark" cx="' + openX + '" cy="' + yPos + '" r="' + L.openR + '"><title>' +
          CD.escText(st.note) + ' (casa 0)</title></circle>',
          '<text class="diagram-string-mark" x="' + openX + '" y="' + yPos + '">' +
          CD.escText(st.interval || '?') + '</text>'
        );
        continue;
      }

      if (!CD.fretVisible(st.fret, grid.startFret, grid.cols)) continue;
      var xPos = CD.horizontalFretX(grid, st.fret);
      var dotCls = st.isRoot ? 'diagram-dot diagram-dot-root' : 'diagram-dot';
      parts.push(
        '<circle class="' + dotCls + '" cx="' + xPos + '" cy="' + yPos + '" r="' + L.dotR + '"><title>' +
        CD.escText(st.note) + ' · ' + CD.escText(st.string) + ' corda · casa ' + st.fret + '</title></circle>',
        '<text class="diagram-finger-num diagram-note-label" fill="#fff" x="' + xPos + '" y="' + yPos + '">' +
        CD.escText(st.interval || '?') + '</text>'
      );
    }

    parts.push('</svg></div>');
    return parts.join('');
  }

  function renderArpeggio(chord, tuning, patternId, opts) {
    opts = opts || {};
    var steps = opts.steps && opts.steps.length
      ? normalizeArpSteps(opts.steps)
      : buildArpeggio(chord, tuning, patternId);
    if (!steps.length) return '<div class="text-muted">Não foi possível gerar arpejo.</div>';
    var source = (steps[0] && steps[0].source) || 'The Bass Guitar Resource Book';
    var bankEntry = opts.meta || lookupBankPattern(chord, patternId || 'root');
    var resolved = CD.resolveFromQualityTemplates && CD.resolveFromQualityTemplates(chord, patternId || 'root');
    var label = (bankEntry && bankEntry.label) || (resolved && resolved.label) || 'Arpejo sugerido';
    var html = '<div class="arpeggio-box">';
    html += '<div class="text-muted mb-2" style="font-size:0.85rem;">' + CD.escText(label) + ' · ' + CD.escText(source) + '</div>';
    html += renderBassArpeggioDiagram(steps, tuning);
    html += '<div class="arp-steps mt-2">';
    steps.forEach(function (st) {
      html += '<span class="arp-step">' + (st.interval || '?') + ' · ' + st.note + ' · ' + st.string + ' corda · casa ' + st.fret + '</span>';
    });
    html += '</div></div>';
    return html;
  }

  CD.buildArpeggio = buildArpeggio;
  CD.lookupBankPattern = lookupBankPattern;
  CD.computeArpWindow = computeArpWindow;
  CD.renderBassArpeggioDiagram = renderBassArpeggioDiagram;
  CD.renderArpeggio = renderArpeggio;
})(typeof window !== 'undefined' ? window : globalThis);
