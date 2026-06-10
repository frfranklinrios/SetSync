/** Escalas musicais para diagramas no braço */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  CD.SCALE_TYPES = {
    major: { id: 'major', label: 'Maior', intervals: [0, 2, 4, 5, 7, 9, 11] },
    minor: { id: 'minor', label: 'Menor natural', intervals: [0, 2, 3, 5, 7, 8, 10] },
    pent_major: { id: 'pent_major', label: 'Pentatônica maior', intervals: [0, 2, 4, 7, 9] },
    pent_minor: { id: 'pent_minor', label: 'Pentatônica menor', intervals: [0, 3, 5, 7, 10] },
    blues: { id: 'blues', label: 'Blues', intervals: [0, 3, 5, 6, 7, 10] },
    mixolydian: { id: 'mixolydian', label: 'Mixolídio', intervals: [0, 2, 4, 5, 7, 9, 10] },
    dorian: { id: 'dorian', label: 'Dórico', intervals: [0, 2, 3, 5, 7, 9, 10] },
  };

  function scaleNotes(rootNote, scaleId) {
    var def = CD.SCALE_TYPES[scaleId];
    if (!def) return [];
    var ri = CD.noteIndex(rootNote);
    if (ri == null) return [];
    var chrom = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    return def.intervals.map(function (iv) {
      return chrom[(ri + iv) % 12];
    });
  }

  function chordRootNote(chord) {
    if (!chord) return null;
    if (chord.notes && chord.notes.length) return chord.notes[0];
    var key = CD.normalizedChordKey(chord.display || chord.input || '');
    if (!key) return null;
    var m = key.match(/^([A-G](?:#|b)?)/);
    return m ? m[1] : null;
  }

  function suggestScalesForChord(chord) {
    var root = chordRootNote(chord);
    if (!root) return [];
    var key = CD.normalizedChordKey(chord.display || chord.input || '') || '';
    var ql = key.replace(/^[A-G](?:#|b)?/, '').toLowerCase();
    var ids = [];

    if (!ql || ql === 'maj' || ql === 'maj7') {
      ids = ['major', 'pent_major', 'mixolydian'];
    } else if (ql === 'm' || ql === 'min' || ql === 'm7' || ql === 'dim') {
      ids = ['minor', 'pent_minor', 'blues', 'dorian'];
    } else if (ql === '7' || ql === '9' || ql === '7sus4') {
      ids = ['mixolydian', 'pent_minor', 'blues', 'major'];
    } else if (ql.indexOf('sus') >= 0) {
      ids = ['major', 'mixolydian', 'pent_major'];
    } else {
      ids = ['major', 'minor', 'pent_major', 'pent_minor'];
    }

    var seen = {};
    return ids.filter(function (id) {
      if (seen[id]) return false;
      seen[id] = true;
      return !!CD.SCALE_TYPES[id];
    }).map(function (id) {
      return {
        id: id,
        label: CD.SCALE_TYPES[id].label,
        root: root,
        notes: scaleNotes(root, id),
      };
    });
  }

  /**
   * Pontos da escala numa janela do braço (corda, casa, é tônica).
   */
  function buildScaleFretPoints(tuning, rootNote, scaleId, windowFrets) {
    var notes = scaleNotes(rootNote, scaleId);
    if (!notes.length) return { startFret: 1, points: [] };

    var noteSet = {};
    notes.forEach(function (n) {
      var i = CD.noteIndex(n);
      if (i != null) noteSet[i] = n;
    });
    var rootIdx = CD.noteIndex(rootNote);

    var anchor = null;
    tuning.forEach(function (open, si) {
      var oi = CD.noteIndex(open);
      if (oi == null || rootIdx == null) return;
      for (var f = 0; f <= 14; f++) {
        if ((oi + f) % 12 === rootIdx) {
          if (!anchor || f < anchor.fret || (f === anchor.fret && si < anchor.string)) {
            anchor = { string: si, fret: f };
          }
          break;
        }
      }
    });

    var start = anchor ? Math.max(0, anchor.fret - 1) : 0;
    if (start > 0 && start + windowFrets > 15) start = Math.max(0, 15 - windowFrets);
    var end = start + windowFrets;

    var points = [];
    tuning.forEach(function (open, si) {
      var oi = CD.noteIndex(open);
      if (oi == null) return;
      for (var f = start; f <= end; f++) {
        var pc = (oi + f) % 12;
        if (!noteSet.hasOwnProperty(pc)) continue;
        points.push({
          string: si,
          fret: f,
          note: noteSet[pc],
          isRoot: pc === rootIdx,
        });
      }
    });

    return { startFret: start, points: points, scaleNotes: notes };
  }

  CD.scaleNotes = scaleNotes;
  CD.chordRootNote = chordRootNote;
  CD.suggestScalesForChord = suggestScalesForChord;
  CD.buildScaleFretPoints = buildScaleFretPoints;
})(typeof window !== 'undefined' ? window : globalThis);
