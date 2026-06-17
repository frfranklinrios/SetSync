/** Escalas musicais para diagramas no braço */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  CD.SCALE_TYPES = {
    major: { id: 'major', label: 'Maior (jóia)', intervals: [0, 2, 4, 5, 7, 9, 11] },
    minor: { id: 'minor', label: 'Menor natural', intervals: [0, 2, 3, 5,  7, 8, 10] },
    harmonic_minor: { id: 'harmonic_minor', label: 'Menor harmônica', intervals: [0, 2, 3, 5, 7, 8, 11] },
    melodic_minor: { id: 'melodic_minor', label: 'Menor melódica', intervals: [0, 2, 3, 5, 7, 9, 11] },
    pent_major: { id: 'pent_major', label: 'Pentatônica maior', intervals: [0, 2, 4, 7, 9] },
    pent_minor: { id: 'pent_minor', label: 'Pentatônica menor', intervals: [0, 3, 5, 7, 10] },
    blues: { id: 'blues', label: 'Blues', intervals: [0, 3, 5, 6, 7, 10] },
    mixolydian: { id: 'mixolydian', label: 'Mixolídio', intervals: [0, 2, 4, 5, 7, 9, 10] },
    dorian: { id: 'dorian', label: 'Dórico', intervals: [0, 2, 3, 5, 7, 9, 10] },
    phrygian: { id: 'phrygian', label: 'Frígio', intervals: [0, 1, 3, 5, 7, 8, 10] },
    lydian: { id: 'lydian', label: 'Lídio', intervals: [0, 2, 4, 6, 7, 9, 11] },
    locrian: { id: 'locrian', label: 'Lócrio', intervals: [0, 1, 3, 5, 6, 8, 10] },
    aeolian: { id: 'aeolian', label: 'Eólio', intervals: [0, 2, 3, 5, 7, 8, 10] },
  };

  function scaleNotes(rootNote, scaleId) {
    var def = CD.SCALE_TYPES[scaleId];
    if (!def) return [];
    var ri = CD.noteIndex(rootNote);
    if (ri == null) return [];
    return def.intervals.map(function (iv) {
      return CD.CHROMATIC[(ri + iv) % 12];
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

  function chordToneSet(chord) {
    var set = {};
    (chord && chord.notes || []).forEach(function (n) {
      var i = CD.noteIndex(n);
      if (i != null) set[i] = true;
    });
    return set;
  }

  function suggestScalesForChord(chord) {
    var root = chordRootNote(chord);
    if (!root) return [];
    var key = CD.normalizedChordKey(chord.display || chord.input || '') || '';
    var ql = key.replace(/^[A-G](?:#|b)?/, '').toLowerCase();
    var ids = [];

    if (!ql || ql === 'maj' || ql === 'maj7' || ql === 'maj9') {
      ids = ['major', 'pent_major', 'mixolydian', 'lydian'];
    } else if (ql === 'm' || ql === 'min') {
      ids = ['minor', 'pent_minor', 'dorian', 'aeolian'];
    } else if (ql === 'm7' || ql === 'min7') {
      ids = ['dorian', 'minor', 'pent_minor', 'blues'];
    } else if (ql.indexOf('dim') >= 0 || ql === 'm7b5') {
      ids = ['locrian', 'phrygian', 'harmonic_minor'];
    } else if (ql === '7' || ql === '9' || ql === '13') {
      ids = ['mixolydian', 'blues', 'pent_minor', 'dorian'];
    } else if (ql.indexOf('sus') >= 0) {
      ids = ['mixolydian', 'major', 'pent_major'];
    } else if (ql.indexOf('m') === 0) {
      ids = ['minor', 'harmonic_minor', 'melodic_minor', 'blues'];
    } else {
      ids = ['major', 'minor', 'pent_major', 'pent_minor', 'mixolydian'];
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

  function buildScaleFretPoints(tuning, rootNote, scaleId, startFret, windowFrets) {
    var notes = scaleNotes(rootNote, scaleId);
    if (!notes.length) return { startFret: 0, points: [], scaleNotes: [] };

    var noteSet = {};
    notes.forEach(function (n) {
      var i = CD.noteIndex(n);
      if (i != null) noteSet[i] = n;
    });
    var rootIdx = CD.noteIndex(rootNote);
    var start = Math.max(0, startFret || 0);
    var end = start + (windowFrets || 11);

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

    return { startFret: start, points: points, scaleNotes: notes, endFret: end };
  }

  function defaultScaleStart(tuning, rootNote) {
    var rootIdx = CD.noteIndex(rootNote);
    if (rootIdx == null) return 0;
    for (var si = 0; si < tuning.length; si++) {
      var oi = CD.noteIndex(tuning[si]);
      if (oi == null) continue;
      for (var f = 0; f <= 12; f++) {
        if ((oi + f) % 12 === rootIdx) return Math.max(0, f - 1);
      }
    }
    return 0;
  }

  CD.scaleNotes = scaleNotes;
  CD.chordRootNote = chordRootNote;
  CD.chordToneSet = chordToneSet;
  CD.suggestScalesForChord = suggestScalesForChord;
  CD.buildScaleFretPoints = buildScaleFretPoints;
  CD.defaultScaleStart = defaultScaleStart;
})(typeof window !== 'undefined' ? window : globalThis);
