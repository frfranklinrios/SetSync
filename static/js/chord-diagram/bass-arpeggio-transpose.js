/** Transposição de arpejos — formas canônicas do manual */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  var STRING_OPEN = { E: 4, A: 9, D: 2, G: 7 };
  var TUNING = ['E', 'A', 'D', 'G'];

  function semitoneDelta(fromPc, toPc) {
    var d = (toPc - fromPc + 12) % 12;
    return d <= 6 ? d : d - 12;
  }

  function fretsForPc(string, pc, maxFret) {
    maxFret = maxFret || 14;
    var o = STRING_OPEN[string];
    if (o == null) return [];
    var out = [];
    for (var f = 0; f <= maxFret; f++) {
      if ((o + f) % 12 === pc) out.push(f);
    }
    return out;
  }

  function inferQuality(notes) {
    if (!notes || notes.length < 3) return null;
    var rootPc = CD.noteIndex(notes[0]);
    if (rootPc == null) return null;
    var pcs = {};
    notes.forEach(function (n) {
      var p = CD.noteIndex(n);
      if (p != null) pcs[(p - rootPc + 12) % 12] = true;
    });
    function has() {
      for (var i = 0; i < arguments.length; i++) {
        if (!pcs[arguments[i]]) return false;
      }
      return true;
    }
    if (has(0, 3, 6, 10)) return 'm7b5';
    if (has(0, 3, 7, 10)) return 'm7';
    if (has(0, 4, 7, 11)) return 'maj7';
    if (has(0, 4, 7, 10)) return '7';
    if (has(0, 3, 7)) return 'm';
    if (has(0, 4, 7)) return 'maj';
    if (has(0, 3, 6)) return 'dim';
    if (has(0, 4, 8)) return 'aug';
    return null;
  }

  function transposeSteps(steps, templateRoot, targetRoot) {
    if (!steps.length) return [];
    var r0 = CD.noteIndex(templateRoot);
    var rt = CD.noteIndex(targetRoot);
    if (r0 == null || rt == null) return steps.slice();
    var shift = semitoneDelta(r0, rt);
    return steps.map(function (st) {
      var oldPc = CD.noteIndex(st.note);
      if (oldPc == null) return st;
      var newPc = (oldPc + shift + 12) % 12;
      var opts = fretsForPc(st.string, newPc);
      var fret = st.fret;
      if (opts.length) {
        fret = opts.reduce(function (best, f) {
          return Math.abs(f - st.fret) < Math.abs(best - st.fret) ? f : best;
        }, opts[0]);
      }
      var chrom = CD.CHROMATIC || ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
      return {
        string: st.string,
        fret: fret,
        finger: st.finger,
        interval: st.interval,
        note: chrom[newPc],
        isRoot: !!st.isRoot,
        source: st.source,
      };
    });
  }

  function resolveFromQualityTemplates(chord, patternId) {
    if (patternId && patternId !== 'root') return null;
    var bank = CD.BASS_ARPEGGIO_BANK;
    var templates = bank && bank.qualityTemplates;
    if (!templates) return null;
    var notes = chord.notes || [];
    var quality = inferQuality(notes);
    if (!quality || !templates[quality]) return null;
    var template = templates[quality];
    var root = notes[0] || chord.root || 'C';
    var templateRoot = 'C';
    for (var i = 0; i < template.length; i++) {
      if (template[i].isRoot) {
        templateRoot = template[i].note;
        break;
      }
    }
    if (quality === 'm7b5') templateRoot = 'B';
    var steps = transposeSteps(template, templateRoot, root);
    return {
      steps: steps,
      quality: quality,
      label: root + ' ' + quality,
      source: (bank.meta && bank.meta.source) || 'The Bass Guitar Resource Book',
    };
  }

  CD.inferArpeggioQuality = inferQuality;
  CD.transposeArpeggioSteps = transposeSteps;
  CD.resolveFromQualityTemplates = resolveFromQualityTemplates;
})(typeof window !== 'undefined' ? window : globalThis);
