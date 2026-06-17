/**
 * Auto-digitação ergonômica (heurística estilo ChordKit / Cifra Club).
 * Atribui dedos 1–4 e detecta pestanas.
 */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  function pressedDots(frets) {
    var dots = [];
    frets.forEach(function (f, si) {
      if (typeof f === 'number' && f > 0) dots.push({ string: si, fret: f });
    });
    return dots;
  }

  function assignAutoFingers(frets) {
    var fingers = frets.map(function (f) {
      if (f === 'x' || f === 0) return 0;
      return 0;
    });
    var dots = pressedDots(frets);
    if (!dots.length) return fingers;

    var barres = CD.detectBarres(frets);
    var barreStrings = {};
    barres.forEach(function (bar) {
      for (var s = bar.from; s <= bar.to; s++) {
        if (frets[s] === bar.fret) barreStrings[s] = bar.fret;
      }
      for (var b = bar.from; b <= bar.to; b++) {
        if (frets[b] === bar.fret) fingers[b] = 1;
      }
    });

    var remaining = dots.filter(function (d) { return !fingers[d.string]; });
    remaining.sort(function (a, b) {
      if (a.fret !== b.fret) return a.fret - b.fret;
      return a.string - b.string;
    });

    var usedOnFret = {};
    var nextFinger = 2;
    remaining.forEach(function (dot) {
      var fretUsed = usedOnFret[dot.fret] || {};
      var finger = 2;
      while (finger <= 4 && fretUsed[finger]) finger += 1;
      if (finger > 4) finger = 4;
      fingers[dot.string] = finger;
      fretUsed[finger] = true;
      usedOnFret[dot.fret] = fretUsed;
    });

    return fingers;
  }

  function noteAtFret(tuning, stringIdx, fret) {
    var pitch = CD.fretPitch ? CD.fretPitch(tuning, stringIdx, fret) : null;
    if (pitch == null) return '';
    var names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    return names[pitch] || '';
  }

  function noteLabelsForFrets(tuning, frets) {
    return frets.map(function (f, si) {
      if (typeof f !== 'number' || f < 0) return '';
      return noteAtFret(tuning, si, f);
    });
  }

  CD.assignAutoFingers = assignAutoFingers;
  CD.noteLabelsForFrets = noteLabelsForFrets;
})(typeof window !== 'undefined' ? window : globalThis);
