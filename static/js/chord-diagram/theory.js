/** Teoria e resolução de shapes automáticos */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var NOTE_IDX = CD.NOTE_IDX;
  var ROOT_ALIAS = CD.ROOT_ALIAS;
  var COMMON_SHAPES = CD.COMMON_SHAPES;

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
    if (ql === 'dim' || ql === 'o' || ql === 'º' || ql === '°') return root + 'm';
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
    var realBank = (CD.REAL_SHAPES && CD.REAL_SHAPES[inst]) || {};
    var legacyBank = (COMMON_SHAPES && COMMON_SHAPES[inst]) || {};
    var keys = chordKeyCandidates(chordDisplay);
    for (var i = 0; i < keys.length; i++) {
      if (realBank[keys[i]] && realBank[keys[i]].length) {
        return realBank[keys[i]].slice();
      }
    }
    for (var j = 0; j < keys.length; j++) {
      if (legacyBank[keys[j]]) {
        return [CD.migrateLegacyShape(legacyBank[keys[j]], 'Padrão')];
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

  function detectBarres(frets) {
    var groups = {};
    frets.forEach(function (f, i) {
      if (typeof f === 'number' && f > 0) {
        if (!groups[f]) groups[f] = [];
        groups[f].push(i);
      }
    });
    var barres = [];
    Object.keys(groups).forEach(function (fretKey) {
      var idxs = groups[fretKey];
      if (idxs.length >= 2) {
        barres.push({
          fret: parseInt(fretKey, 10),
          from: Math.min.apply(null, idxs),
          to: Math.max.apply(null, idxs),
        });
      }
    });
    barres.sort(function (a, b) { return a.fret - b.fret; });
    return barres;
  }

  function buildShapeOptions(instrument, chord) {
    if (!chord || instrument === 'baixo') return [];

    var tuning = CD.TUNINGS[instrument];
    var display = chord.display || chord.input || '';
    var real = getChordPositions(instrument, display);

    if (real.length) {
      return real.map(function (pos) {
        return {
          frets: pos.frets,
          fingers: pos.fingers,
          label: pos.label || 'Padrão',
          source: pos.source || 'Cifra clássica',
        };
      });
    }

    var autos = buildAutoShapes(tuning, chord.notes || [], 3);
    if (autos.length) {
      return autos.map(function (f, idx) {
        return {
          frets: f,
          fingers: null,
          label: 'Sugerido ' + (idx + 1),
          source: 'Posição sugerida',
        };
      });
    }

    return [{
      frets: buildAutoShape(tuning, chord.notes || []),
      fingers: null,
      label: 'Sugerido',
      source: 'Posição sugerida',
    }];
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
  CD.buildShapeOptions = buildShapeOptions;
})(typeof window !== 'undefined' ? window : globalThis);
