/**
 * Calculadora Inteligente de Capotraste — Uníssono.
 * Inspirado nas melhores bibliotecas open-source de teoria musical e violão (sepandhaghighi/capo & Capoless).
 * Permite que o músico toque em formas fáceis (CAGED: C, A, G, E, D) afinando no tom real da banda.
 */
(function (global) {
  'use strict';

  var CHROMATIC_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  var CHROMATIC_FLAT  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];

  var NOTE_TO_INDEX = {
    'C': 0, 'B#': 0,
    'C#': 1, 'DB': 1,
    'D': 2,
    'D#': 3, 'EB': 3,
    'E': 4, 'FB': 4,
    'F': 5, 'E#': 5,
    'F#': 6, 'GB': 6,
    'G': 7,
    'G#': 8, 'AB': 8,
    'A': 9,
    'A#': 10, 'BB': 10,
    'B': 11, 'CB': 11
  };

  // Formatos abertos mais confortáveis no violão (Sistema CAGED + menores abertos)
  var OPEN_SHAPES_MAJOR = { 'G': 10, 'D': 9, 'C': 9, 'E': 8, 'A': 8 };
  var OPEN_SHAPES_MINOR = { 'EM': 10, 'AM': 10, 'DM': 8, 'BM': 6 };

  function parseRootAndSuffix(keyStr) {
    if (!keyStr || typeof keyStr !== 'string') return { root: 'C', isMinor: false };
    var clean = keyStr.trim().replace(/^Tom\s+/i, '');
    var m = clean.match(/^([A-Ga-g][#b]?)(.*)$/);
    if (!m) return { root: 'C', isMinor: false };
    var note = m[1].toUpperCase();
    if (note.length === 2) {
      note = note[0] + (m[1][1] === '#' ? '#' : 'b');
    }
    var suffix = (m[2] || '').toLowerCase();
    var isMinor = suffix.indexOf('m') === 0 && suffix.indexOf('maj') !== 0;
    return { root: note, isMinor: isMinor, suffix: suffix };
  }

  function getNoteIndex(note) {
    if (!note) return 0;
    var norm = note.toUpperCase();
    return NOTE_TO_INDEX.hasOwnProperty(norm) ? NOTE_TO_INDEX[norm] : 0;
  }

  function indexToNote(idx, useFlat) {
    idx = ((idx % 12) + 12) % 12;
    return useFlat ? CHROMATIC_FLAT[idx] : CHROMATIC_SHARP[idx];
  }

  /**
   * Calcula o formato de acorde tocado dado o tom real e a casa do Capo.
   * Acorde_tocado = Tom_real - Capo_fret
   */
  function calculateCapo(rootKey, capoFret) {
    capoFret = Math.max(0, Math.min(11, parseInt(capoFret, 10) || 0));
    var info = parseRootAndSuffix(rootKey);
    var rootIdx = getNoteIndex(info.root);
    var playedIdx = ((rootIdx - capoFret) % 12 + 12) % 12;

    var useFlat = (info.root.indexOf('b') !== -1 || info.root === 'F');
    var playedNote = indexToNote(playedIdx, useFlat);
    var playedKey = playedNote + (info.isMinor ? 'm' : '');

    return {
      rootKey: rootKey,
      capoFret: capoFret,
      playedKey: playedKey,
      semitonesOffset: -capoFret, // transposição visual aplicada na cifra
      isMinor: info.isMinor,
    };
  }

  /**
   * Retorna as melhores sugestões de Capo (casas de 1 a 7) para o tom real,
   * pontuando de acordo com a facilidade dos acordes no violão.
   */
  function getSuggestions(rootKey) {
    var info = parseRootAndSuffix(rootKey);
    var suggestions = [];

    for (var fret = 1; fret <= 7; fret++) {
      var calc = calculateCapo(rootKey, fret);
      var playedNote = calc.playedKey.toUpperCase();
      var score = 0;
      var label = '';

      if (info.isMinor) {
        var baseMinor = playedNote;
        if (OPEN_SHAPES_MINOR[baseMinor]) {
          score = OPEN_SHAPES_MINOR[baseMinor];
          label = 'Formas abertas de ' + calc.playedKey;
        }
      } else {
        var baseMajor = calc.playedKey.replace(/m.*$/i, '').toUpperCase();
        if (OPEN_SHAPES_MAJOR[baseMajor]) {
          score = OPEN_SHAPES_MAJOR[baseMajor];
          label = 'Formas abertas de ' + calc.playedKey;
        }
      }

      if (score > 0) {
        suggestions.push({
          fret: fret,
          playedKey: calc.playedKey,
          score: score,
          label: label,
          semitones: -fret,
        });
      }
    }

    suggestions.sort(function (a, b) { return b.score - a.score; });
    return suggestions;
  }

  global.SetSyncCapo = {
    calculateCapo: calculateCapo,
    getSuggestions: getSuggestions,
    parseRootAndSuffix: parseRootAndSuffix,
  };
})(window);
