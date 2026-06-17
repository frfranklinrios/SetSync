/**
 * Motor de voicings — busca por backtracking (como Fretboard Explorer / TabV4).
 * Encontra posições tocáveis dentro de 4 casas com todas as notas do acorde.
 */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  var MAX_FRET = 15;
  var MAX_SPAN = 4;
  var MAX_VOICINGS = 12;

  function fretPitch(tuning, stringIdx, fret) {
    if (fret === 'x' || fret == null) return null;
    var oi = CD.noteIndex(tuning[stringIdx]);
    if (oi == null) return null;
    if (fret === 0) return oi;
    return (oi + fret) % 12;
  }

  function uniqueIndices(notes) {
    var seen = {};
    var out = [];
    (notes || []).forEach(function (n) {
      var idx = CD.noteIndex(n);
      if (idx == null || seen[idx]) return;
      seen[idx] = true;
      out.push(idx);
    });
    return out;
  }

  function isPlayableSpan(frets) {
    var nums = frets.filter(function (f) { return typeof f === 'number' && f > 0; });
    if (!nums.length) return frets.indexOf(0) >= 0;
    var minF = Math.min.apply(null, nums);
    var maxF = Math.max.apply(null, nums);
    return (maxF - minF) <= MAX_SPAN;
  }

  function optionsPerString(tuning, chordSet, rootIdx) {
    return tuning.map(function (open, si) {
      var opts = ['x'];
      var oi = CD.noteIndex(open);
      if (oi == null) return opts;
      if (chordSet[oi]) opts.push(0);
      for (var f = 1; f <= MAX_FRET; f++) {
        if (chordSet[(oi + f) % 12]) opts.push(f);
      }
      return opts;
    });
  }

  function validateVoicing(tuning, frets, chordIndices, rootIdx) {
    var played = {};
    var active = 0;
    var lowestString = -1;
    var lowestPitch = null;

    for (var si = 0; si < frets.length; si++) {
      var f = frets[si];
      if (f === 'x') continue;
      active += 1;
      var pitch = fretPitch(tuning, si, f);
      if (pitch == null) return false;
      if (!chordIndices[pitch]) return false;
      played[pitch] = true;
      if (lowestString < 0 || si > lowestString) {
        lowestString = si;
        lowestPitch = pitch;
      }
    }

    if (active < Math.min(2, tuning.length)) return false;
    if (!played[rootIdx]) return false;
    if (!isPlayableSpan(frets)) return false;

    var required = Object.keys(chordIndices).map(function (k) { return parseInt(k, 10); });
    if (required.length <= 4) {
      for (var i = 0; i < required.length; i++) {
        if (!played[required[i]]) return false;
      }
    } else if (Object.keys(played).length < Math.min(required.length, Math.max(3, Math.ceil(required.length * 0.75)))) {
      return false;
    }

    return true;
  }

  function scoreVoicing(tuning, frets, rootIdx) {
    var score = 0;
    var nums = [];
    frets.forEach(function (f, si) {
      if (f === 'x') score += 8;
      else if (f === 0) score -= 6;
      else if (typeof f === 'number') {
        nums.push(f);
        score += f * 2;
        if (fretPitch(tuning, si, f) === rootIdx && si === frets.length - 1) score -= 3;
      }
    });
    if (nums.length) {
      score += (Math.max.apply(null, nums) - Math.min.apply(null, nums)) * 5;
      score += Math.min.apply(null, nums) * 3;
    }
    return score;
  }

  function backtrack(tuning, perString, chordMap, rootIdx, si, current, out, seen) {
    if (out.length >= MAX_VOICINGS) return;
    if (si >= tuning.length) {
      if (!validateVoicing(tuning, current, chordMap, rootIdx)) return;
      var key = current.map(function (f) { return String(f); }).join('');
      if (seen[key]) return;
      seen[key] = true;
      out.push({
        frets: current.slice(),
        score: scoreVoicing(tuning, current, rootIdx),
      });
      return;
    }
    var opts = perString[si];
    for (var i = 0; i < opts.length; i++) {
      current[si] = opts[i];
      backtrack(tuning, perString, chordMap, rootIdx, si + 1, current, out, seen);
      if (out.length >= MAX_VOICINGS) return;
    }
  }

  /**
   * Gera voicings tocáveis para um acorde.
   * @returns {Array<{frets, score}>}
   */
  function discoverVoicings(tuning, notes, limit) {
    var indices = uniqueIndices(notes);
    if (!indices.length) return [];
    var rootIdx = indices[0];
    var chordMap = {};
    indices.forEach(function (idx) { chordMap[idx] = true; });

    var perString = optionsPerString(tuning, chordMap, rootIdx);
    var raw = [];
    var seen = {};
    backtrack(tuning, perString, chordMap, rootIdx, 0, [], raw, seen);

    raw.sort(function (a, b) { return a.score - b.score; });
    var cap = limit || 6;
    return raw.slice(0, cap);
  }

  CD.discoverVoicings = discoverVoicings;
  CD.fretPitch = fretPitch;
})(typeof window !== 'undefined' ? window : globalThis);
