/** Diagrama de arpejo para baixo — padrões do Bass Guitar Resource Book */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  function normalizeSymbol(symbol) {
    if (CD.normalizedChordKey) {
      return CD.normalizedChordKey(symbol) || String(symbol || '').replace(/\s+/g, '');
    }
    return String(symbol || '').replace(/\s+/g, '');
  }

  function lookupBankPattern(chord, patternId) {
    var bank = CD.BASS_ARPEGGIO_BANK;
    if (!bank || !bank.patterns) return null;
    var display = (chord && (chord.display || chord.input)) || '';
    var keys = [display.replace(/\s+/g, ''), normalizeSymbol(display)];
    var map = bank.patterns;
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
    var bankEntry = lookupBankPattern(chord, patternId || 'root');
    if (bankEntry && bankEntry.steps && bankEntry.steps.length) {
      return stepsFromBank(bankEntry);
    }

    var notes = (chord.notes || []).slice();
    if (!notes.length) return [];
    var steps = [];
    var lastFret = 3;
    var root = notes[0];
    var allowedPatterns = CD.availableBassPatterns(chord).map(function (x) { return x.id; });
    var activePattern = allowedPatterns.indexOf(patternId) >= 0 ? patternId : 'root';

    function intervalLabel(note, rootNote, isOctaveReturn) {
      var ni = CD.noteIndex(note);
      var ri = CD.noteIndex(rootNote);
      if (ni == null || ri == null) return '?';
      var d = (ni - ri + 12) % 12;
      var base = CD.intervalFromDistance(d);
      if (isOctaveReturn && d === 0) return '1';
      return base;
    }

    var byInterval = {};
    notes.forEach(function (n) {
      var lbl = intervalLabel(n, root, false);
      byInterval[lbl] = n;
    });
    byInterval['1'] = root;
    byInterval['8'] = root;

    function pickInterval(candidates) {
      for (var i = 0; i < candidates.length; i++) {
        if (byInterval[candidates[i]]) return candidates[i];
      }
      return null;
    }

    function buildPattern() {
      var recipe;
      if (activePattern === 'inv1') recipe = [['3', 'b3'], ['5'], ['7', 'b7'], ['1']];
      else if (activePattern === 'inv2') recipe = [['5'], ['7', 'b7'], ['1'], ['3', 'b3']];
      else if (activePattern === 'inv3') recipe = [['7', 'b7'], ['1'], ['3', 'b3'], ['5']];
      else recipe = [['1'], ['3', 'b3'], ['5'], ['7', 'b7'], ['1']];

      var out = [];
      recipe.forEach(function (alts) {
        var iv = pickInterval(alts);
        if (iv) out.push({ interval: iv, note: byInterval[iv] });
      });
      if (!out.length) {
        out = notes.map(function (n) {
          return { interval: intervalLabel(n, root, false), note: n };
        });
        out.push({ interval: '8', note: root });
      }
      return out;
    }

    buildPattern().forEach(function (item) {
      var target = CD.noteIndex(item.note);
      var best = null;
      for (var s = 0; s < tuning.length; s++) {
        var oi = CD.noteIndex(tuning[s]);
        if (oi == null || target == null) continue;
        for (var f = 0; f <= 12; f++) {
          if (((oi + f) % 12) === target) {
            var dist = Math.abs(f - lastFret);
            var score = dist + (s * 0.2);
            var cand = { note: item.note, string: tuning[s], fret: f, score: score };
            if (!best || cand.score < best.score) best = cand;
            break;
          }
        }
      }
      if (best) {
        best.interval = item.interval;
        steps.push(best);
        lastFret = best.fret;
      }
    });
    return steps;
  }

  function renderBassArpeggioDiagram(steps, tuning) {
    var rows = tuning.slice().reverse();
    var rowIndex = {};
    rows.forEach(function (s, i) { rowIndex[s] = i; });
    var positiveFrets = steps.map(function (s) { return s.fret; }).filter(function (f) { return f > 0; });

    var startFret = 0;
    if (positiveFrets.length) {
      var minF = Math.min.apply(null, positiveFrets);
      var maxF = Math.max.apply(null, positiveFrets);
      startFret = maxF <= 4 ? 0 : Math.max(0, minF - 1);
      while (maxF > startFret + 5) startFret += 1;
    }

    var cols = 6;
    var colGap = 52;
    var rowGap = 40;
    var marginLeft = 42;
    var marginTop = 18;
    var boardW = cols * colGap;
    var boardH = (rows.length - 1) * rowGap;
    var svgW = marginLeft + boardW + 18;
    var svgH = marginTop + boardH + 34;

    var html = '<div class="bass-arp-wrap"><svg class="bass-arp-svg" width="' + svgW + '" height="' + svgH + '" viewBox="0 0 ' + svgW + ' ' + svgH + '">';

    for (var r = 0; r < rows.length; r++) {
      var y = marginTop + (r * rowGap);
      html += '<line class="bass-grid" x1="' + marginLeft + '" y1="' + y + '" x2="' + (marginLeft + boardW) + '" y2="' + y + '"></line>';
      html += '<text class="bass-string-label" x="18" y="' + y + '">' + rows[r] + '</text>';
    }

    for (var c = 0; c <= cols; c++) {
      var x = marginLeft + (c * colGap);
      var cls = (c === 0 && startFret === 0) ? 'bass-nut' : 'bass-grid';
      html += '<line class="' + cls + '" x1="' + x + '" y1="' + marginTop + '" x2="' + x + '" y2="' + (marginTop + boardH) + '"></line>';
    }

    if (startFret > 0) {
      html += '<text class="bass-fret-label" x="' + (marginLeft + colGap / 2) + '" y="' + (marginTop + boardH + 18) + '">' + (startFret + 1) + 'fr</text>';
    } else if (positiveFrets.length && Math.min.apply(null, positiveFrets) === 1) {
      html += '<text class="bass-fret-label" x="' + (marginLeft + colGap / 2) + '" y="' + (marginTop + boardH + 18) + '">1</text>';
    }

    for (var i = 0; i < steps.length; i++) {
      var st = steps[i];
      var ridx = rowIndex[st.string];
      if (ridx == null) continue;
      var yPos = marginTop + (ridx * rowGap);

      if (st.fret === 0) {
        var openX = marginLeft - 16;
        html += '<circle class="bass-dot-open" cx="' + openX + '" cy="' + yPos + '" r="12"><title>' + st.note + ' (casa 0)</title></circle>';
        html += '<text class="bass-step-num-open" x="' + openX + '" y="' + yPos + '">' + (st.interval || '?') + '</text>';
        continue;
      }

      if (st.fret <= startFret || st.fret > startFret + cols) continue;
      var xPos = marginLeft + ((st.fret - startFret - 0.5) * colGap);
      html += '<circle class="bass-dot-fill" cx="' + xPos + '" cy="' + yPos + '" r="13"><title>' + st.note + ' · ' + st.string + ' corda · casa ' + st.fret + '</title></circle>';
      html += '<text class="bass-step-num" x="' + xPos + '" y="' + yPos + '">' + (st.interval || '?') + '</text>';
    }

    html += '</svg></div>';
    return html;
  }

  function renderArpeggio(chord, tuning, patternId) {
    var steps = buildArpeggio(chord, tuning, patternId);
    if (!steps.length) return '<div class="text-muted">Não foi possível gerar arpejo.</div>';
    var source = (steps[0] && steps[0].source) || 'fallback';
    var bankEntry = lookupBankPattern(chord, patternId || 'root');
    var label = bankEntry && bankEntry.label ? bankEntry.label : 'Arpejo sugerido';
    var html = '<div class="arpeggio-box">';
    html += '<div class="text-muted mb-2" style="font-size:0.85rem;">' + CD.escText(label) + ' · ' + CD.escText(source) + '</div>';
    html += '<div class="text-muted mb-2" style="font-size:0.82rem;">' + tuning.slice().reverse().join(' · ') + '</div>';
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
  CD.renderBassArpeggioDiagram = renderBassArpeggioDiagram;
  CD.renderArpeggio = renderArpeggio;
})(typeof window !== 'undefined' ? window : globalThis);
