/** Teoria e resolução de shapes automáticos */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var NOTE_IDX = CD.NOTE_IDX;
  var ROOT_ALIAS = CD.ROOT_ALIAS;

  function normalizeNote(n) {
    if (!n) return null;
    var s = String(n).trim().replace('♯', '#').replace('♭', 'b');
    return Object.prototype.hasOwnProperty.call(NOTE_IDX, s) ? s : null;
  }

  function noteIndex(n) {
    var key = normalizeNote(n);
    return key == null ? null : NOTE_IDX[key];
  }

  function sanitizeChordText(text) {
    if (!text) return '';
    return String(text).replace(/\s+/g, ' ').replace(/^\[|\]$/g, '').trim();
  }

  function normalizedChordKey(chordDisplay) {
    var text = sanitizeChordText(chordDisplay).replace(/\s+/g, '');
    text = text.replace(/[()[\]{}]/g, '');
    var m = text.match(/^([A-G](?:#|b)?)(.*)$/);
    if (!m) return null;
    var root = ROOT_ALIAS[m[1]] || m[1];
    var q = (m[2] || '').replace(/\/.*$/, '');
    if (!q || q.toLowerCase() === 'maj') return root;

    var ql = q.toLowerCase();
    if (ql === 'm' || ql === 'min') return root + 'm';
    if (ql === '7') return root + '7';
    if (ql === 'm7' || ql === 'min7') return root + 'm7';
    if (ql === 'maj7' || ql === '7+' || q === 'M7' || ql === 'm7+') return root + 'maj7';
    if (ql === 'sus4') return root + 'sus4';
    if (ql === '7sus4') return root + '7sus4';
    if (ql === 'sus2') return root;
    if (ql === 'dim' || ql === 'o' || ql === 'º' || ql === '°') return root + 'dim';
    if (ql === 'dim7' || ql === 'm7b5' || ql === 'ø') return root + 'm7b5';
    if (ql === 'aug' || ql === '+') return root + 'aug';
    if (ql === '6') return root + '6';
    if (ql === 'm6' || ql === 'min6') return root + 'm6';
    if (ql === '9') return root + '9';
    if (ql === 'm9' || ql === 'min9') return root + 'm9';
    if (ql === 'maj9' || ql === 'M9') return root + 'maj9';
    if (ql === 'add9') return root + 'add9';
    if (ql === '11') return root + '11';
    if (ql === 'm11') return root + 'm11';
    if (ql === '13') return root + '13';
    if (ql === '5') return root + '5';
    return root + q;
  }

  function chordKeyCandidates(chordDisplay) {
    var k = normalizedChordKey(chordDisplay);
    if (!k) return [];
    var list = [k];
    if (/7sus4$/.test(k)) list.push(k.replace(/7sus4$/, '7'));
    if (/sus4$/.test(k) && !/7sus4$/.test(k)) list.push(k.replace(/sus4$/, ''));
    return list;
  }

  function getPreferredShape(inst, chordDisplay) {
    var positions = getChordPositions(inst, chordDisplay);
    if (positions.length) return positions[0];
    return null;
  }

  function getChordPositions(inst, chordDisplay) {
    var bankInst = inst === 'cavaco' ? 'violao' : inst;
    var dbBank = (CD.CHORDS_DB_SHAPES && CD.CHORDS_DB_SHAPES[bankInst]) || {};
    var keys = chordKeyCandidates(chordDisplay);
    for (var d = 0; d < keys.length; d++) {
      if (dbBank[keys[d]] && dbBank[keys[d]].length) {
        var list = dbBank[keys[d]].slice();
        if (inst === 'cavaco') {
          return list.map(function (pos) {
            var a = adaptVoicingForStrings(pos.frets, pos.fingers, pos.barres, 4);
            return {
              label: pos.label,
              frets: a.frets,
              fingers: a.fingers,
              barres: a.barres,
              source: pos.source || 'chords-db',
            };
          });
        }
        return list;
      }
    }
    return [];
  }

  function fretsKey(frets) {
    return (frets || []).map(function (f) { return String(f); }).join('');
  }

  function fretsLabel(frets) {
    return (frets || []).map(function (f) { return String(f); }).join(' ');
  }

  function buildAutoShape(tuning, notes) {
    return buildAutoShapes(tuning, notes, 1)[0] || tuning.map(function () { return 'x'; });
  }

  function buildAutoShapes(tuning, notes, limit) {
    var noteSet = {};
    notes.forEach(function (n) {
      var idx = noteIndex(n);
      if (idx != null) noteSet[idx] = true;
    });

    var candidates = [];
    for (var base = 0; base <= 12; base++) {
      var frets = [];
      var active = 0;
      var muteCount = 0;
      tuning.forEach(function (open) {
        var oi = noteIndex(open);
        var chosen = null;
        if (oi != null && base === 0 && noteSet[(oi + 0) % 12]) chosen = 0;
        for (var f = Math.max(1, base); f <= base + 4; f++) {
          if (oi != null && noteSet[(oi + f) % 12]) {
            chosen = f;
            break;
          }
        }
        if (chosen == null) {
          frets.push('x');
          muteCount += 1;
        } else {
          frets.push(chosen);
          active += 1;
        }
      });

      if (active < Math.min(3, tuning.length)) continue;
      var numeric = frets.filter(function (f) { return typeof f === 'number' && f > 0; });
      var minF = numeric.length ? Math.min.apply(null, numeric) : 0;
      var maxF = numeric.length ? Math.max.apply(null, numeric) : 0;
      var span = maxF - minF;
      var score = (span * 10) + (muteCount * 7) + base;
      candidates.push({ frets: frets, score: score });
    }

    candidates.sort(function (a, b) { return a.score - b.score; });
    var out = [];
    var seen = {};
    for (var i = 0; i < candidates.length; i++) {
      var k = fretsKey(candidates[i].frets);
      if (seen[k]) continue;
      seen[k] = true;
      out.push(candidates[i].frets);
      if (out.length >= (limit || 3)) break;
    }
    if (!out.length) out.push(tuning.map(function () { return 'x'; }));
    return out;
  }

  function intervalFromDistance(d) {
    var map = {
      0: '1', 1: 'b2', 2: '2', 3: 'b3', 4: '3', 5: '4', 6: 'b5',
      7: '5', 8: '#5', 9: '6', 10: 'b7', 11: '7',
    };
    return Object.prototype.hasOwnProperty.call(map, d) ? map[d] : '?';
  }

  function hasInterval(chord, candidates) {
    var notes = (chord && chord.notes) || [];
    if (!notes.length) return false;
    var rootIdx = noteIndex(notes[0]);
    if (rootIdx == null) return false;
    var found = {};
    notes.forEach(function (n) {
      var ni = noteIndex(n);
      if (ni == null) return;
      var iv = intervalFromDistance((ni - rootIdx + 12) % 12);
      found[iv] = true;
    });
    for (var i = 0; i < candidates.length; i++) {
      if (found[candidates[i]]) return true;
    }
    return false;
  }

  function availableBassPatterns(chord) {
    var list = [{ id: 'root', label: 'Fundamental' }];
    if (hasInterval(chord, ['3', 'b3'])) list.push({ id: 'inv1', label: '1ª inversão' });
    if (hasInterval(chord, ['5'])) list.push({ id: 'inv2', label: '2ª inversão' });
    if (hasInterval(chord, ['7', 'b7'])) list.push({ id: 'inv3', label: '3ª inversão' });
    return list;
  }

  function rootStringIndex(tuning, frets, rootNote) {
    var ri = noteIndex(rootNote);
    if (ri == null) return -1;
    for (var i = 0; i < tuning.length; i++) {
      var oi = noteIndex(tuning[i]);
      var f = frets[i];
      if (oi == null) continue;
      if (f === 0 && ri === oi) return i;
      if (typeof f === 'number' && f > 0 && ri === (oi + f) % 12) return i;
    }
    return -1;
  }

  function barreAllowedOnString(frets, stringIdx, barreFret) {
    for (var g = 0; g < stringIdx; g++) {
      var fg = frets[g];
      if (typeof fg === 'number' && fg > 0 && fg < barreFret) {
        return false;
      }
    }
    return true;
  }

  function detectBarresContiguous(frets) {
    var barres = [];
    var n = frets.length;
    var i = 0;
    while (i < n) {
      var f = frets[i];
      if (typeof f !== 'number' || f <= 0) {
        i += 1;
        continue;
      }
      var j = i + 1;
      while (j < n && frets[j] === f) {
        j += 1;
      }
      var s = i;
      while (s < j) {
        if (!barreAllowedOnString(frets, s, f)) {
          s += 1;
          continue;
        }
        var e = s + 1;
        while (e < j && barreAllowedOnString(frets, e, f)) {
          e += 1;
        }
        if (e - s >= 2) {
          barres.push({
            fret: f,
            from: s,
            to: e - 1,
          });
        }
        s = e;
      }
      i = j;
    }
    return barres;
  }

  function coerceFret(fval) {
    if (fval === 'x' || fval === 'X') return null;
    if (typeof fval === 'number') return fval > 0 ? fval : null;
    if (typeof fval === 'string' && fval.trim() !== '') {
      var n = parseInt(fval, 10);
      return isNaN(n) || n <= 0 ? null : n;
    }
    return null;
  }

  function barreSpanFromFrets(frets, barreFret) {
    if (!barreFret) return null;
    var from = -1;
    var to = -1;
    for (var i = 0; i < frets.length; i++) {
      var f = coerceFret(frets[i]);
      if (f === null || f < barreFret) continue;
      if (from < 0) from = i;
      to = i;
    }
    if (from < 0 || to <= from) return null;
    return { fret: barreFret, from: from, to: to };
  }

  function detectBarresFromFingers(frets, fingers) {
    if (!fingers || !fingers.length) return [];
    var byFret = {};
    for (var i = 0; i < frets.length; i++) {
      var f = coerceFret(frets[i]);
      if (f === null) continue;
      if (Number(fingers[i]) !== 1) continue;
      if (!byFret[f]) byFret[f] = [];
      byFret[f].push(i);
    }
    var barres = [];
    Object.keys(byFret).forEach(function (key) {
      var fret = parseInt(key, 10);
      var span = barreSpanFromFrets(frets, fret);
      if (!span) return;
      var strings = byFret[fret];
      if (strings.length < 2) return;
      var valid = true;
      for (var s = span.from; s <= span.to; s++) {
        if (frets[s] === 'x' || frets[s] === 'X') continue;
        var fs = coerceFret(frets[s]);
        if (fs !== null && fs < fret) {
          valid = false;
          break;
        }
        if (!barreAllowedOnString(frets, s, fret)) {
          valid = false;
          break;
        }
      }
      if (valid) barres.push(span);
    });
    barres.sort(function (a, b) { return a.fret - b.fret; });
    return barres;
  }

  function detectBarres(frets, fingers, explicitBarres) {
    var fromExplicit = normalizeShapeBarres(explicitBarres);
    if (fromExplicit.length) return fromExplicit;
    var fromFingers = detectBarresFromFingers(frets, fingers);
    if (fromFingers.length) return fromFingers;
    return detectBarresContiguous(frets);
  }

  function normalizeShapeBarres(barres) {
    if (!barres || !barres.length) return [];
    return barres.map(function (b) {
      if (b.from != null && b.to != null) {
        return { fret: b.fret, from: b.from, to: b.to };
      }
      return {
        fret: b.fret,
        from: (b.startString != null ? b.startString : 1) - 1,
        to: (b.endString != null ? b.endString : 1) - 1,
      };
    }).filter(function (b) { return b.to > b.from; });
  }

  var GUITAR_TO_CAVACO_IDX = [2, 3, 4, 5];

  function adaptVoicingForStrings(frets, fingers, barres, stringCount) {
    if (!frets || frets.length <= stringCount) {
      return {
        frets: frets,
        fingers: fingers,
        barres: normalizeShapeBarres(barres),
      };
    }
    if (frets.length === 6 && stringCount === 4) {
      var nf = GUITAR_TO_CAVACO_IDX.map(function (i) { return frets[i]; });
      var nfi = fingers ? GUITAR_TO_CAVACO_IDX.map(function (i) { return fingers[i]; }) : null;
      return { frets: nf, fingers: nfi, barres: detectBarres(nf, nfi, []) };
    }
    var trimmed = frets.slice(0, stringCount);
    var tf = fingers ? fingers.slice(0, stringCount) : null;
    return {
      frets: trimmed,
      fingers: tf,
      barres: detectBarres(trimmed, tf, normalizeShapeBarres(barres)),
    };
  }

  function barreDrawRange(bar, frets, stringCount) {
    var from = Math.max(0, bar.from);
    var to = Math.min(bar.to, stringCount - 1);
    while (from <= to && frets[from] === 'x') from += 1;
    while (to >= from && frets[to] === 'x') to -= 1;
    if (from >= to) return null;
    return { from: from, to: to };
  }

  function barreFingerLabel(bar, frets, fingers) {
    for (var s = bar.from; s <= bar.to; s++) {
      if (frets[s] !== bar.fret) continue;
      if (fingers && fingers[s] === 1) return '1';
      if (fingers && fingers[s] > 0) return String(fingers[s]);
    }
    return '1';
  }

  function stringOnBarre(stringIdx, frets, barres) {
    var fval = frets[stringIdx];
    for (var b = 0; b < barres.length; b++) {
      var bar = barres[b];
      if (stringIdx >= bar.from && stringIdx <= bar.to && fval === bar.fret) {
        return bar;
      }
    }
    return null;
  }

  function buildShapeOptions(instrument, chord) {
    if (!chord || instrument === 'baixo') return [];

    var display = chord.display || chord.input || '';
    var positions = getChordPositions(instrument, display);

    if (positions.length) {
      return positions.map(function (pos) {
        return {
          frets: pos.frets,
          fingers: pos.fingers,
          barres: pos.barres || [],
          label: pos.label || 'Padrão',
          source: pos.source || 'chords-db',
        };
      });
    }

    return [];
  }

  CD.normalizeNote = normalizeNote;
  CD.noteIndex = noteIndex;
  CD.sanitizeChordText = sanitizeChordText;
  CD.normalizedChordKey = normalizedChordKey;
  CD.chordKeyCandidates = chordKeyCandidates;
  CD.getPreferredShape = getPreferredShape;
  CD.getChordPositions = getChordPositions;
  CD.fretsKey = fretsKey;
  CD.fretsLabel = fretsLabel;
  CD.buildAutoShape = buildAutoShape;
  CD.buildAutoShapes = buildAutoShapes;
  CD.intervalFromDistance = intervalFromDistance;
  CD.hasInterval = hasInterval;
  CD.availableBassPatterns = availableBassPatterns;
  CD.rootStringIndex = rootStringIndex;
  CD.detectBarres = detectBarres;
  CD.stringOnBarre = stringOnBarre;
  CD.adaptVoicingForStrings = adaptVoicingForStrings;
  CD.barreDrawRange = barreDrawRange;
  CD.barreFingerLabel = barreFingerLabel;
  CD.buildShapeOptions = buildShapeOptions;
})(typeof window !== 'undefined' ? window : globalThis);
