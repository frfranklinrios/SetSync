/** Posições importadas de tombatossals/chords-db — gerado por scripts/build_chords_db_shapes.py */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  function P(label, frets, fingers, source, barres) {
    return { label: label, frets: frets, fingers: fingers || null, source: source || 'chords-db', barres: barres || [] };
  }
  CD.CHORDS_DB_SHAPES = {
    violao: {
      'A': [
      P('Abertura', ["x", 0, 2, 2, 2, 0], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 0, 2, 2, 2, 5], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 7, 6, 5, 5], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'A/Ab': [
      P('2ª casa (pestana)', [4, 4, 2, 2, 2, 5], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [4, 4, 2, 2, 5, 5], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 6, 6, 5, 5], [0, 0, 2, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'A/B': [
      P('Padrão', ["x", 2, 2, 2, 2, 0], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 2, 2, 2, 2, 5], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 7, 9, 10, 9], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'A/Bb': [
      P('Padrão', ["x", 1, 2, 2, 2, 0], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", "x", 8, 6, 5, 5], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 8, 9, 10, 9], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'A/C': [
      P('Padrão', ["x", 3, 2, 2, 2, 0], [0, 4, 1, 2, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 3, 2, 2, 2, 5], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', ["x", "x", 10, 9, 10, 9], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'A/C#': [
      P('2ª casa (pestana)', ["x", 4, 2, 2, 2, 5], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 4, 2, 2, 5, 5], [0, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [9, 12, 11, 9, 10, 9], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'A/D': [
      P('Abertura', ["x", "x", 0, 2, 2, 0], [0, 0, 0, 1, 2, 0], 'chords-db', []),
      P('5ª casa', ["x", "x", 0, 6, 5, 5], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 7, 6, 5, 5], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'A/E': [
      P('Abertura', [0, 0, 2, 2, 2, 0], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('2ª casa', [0, 4, 2, 2, 2, 5], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa', [0, 4, 2, 2, 5, 5], [0, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}])
      ],
      'A/Eb': [
      P('Padrão', ["x", "x", 1, 2, 2, 0], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 7, 6, 5, 5], [0, 2, 4, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('Padrão', ["x", 6, 7, 6, 5, "x"], [0, 2, 4, 3, 1, 0], 'chords-db', [])
      ],
      'A/F': [
      P('Abertura', [1, 0, 2, 2, 2, 0], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 2, 2, 0], [0, 0, 3, 1, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 6, 5, 5], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'A/F#': [
      P('Abertura', [2, 0, 2, 2, 2, 0], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 2, 2, 0], [0, 0, 4, 1, 2, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 4, 2, 2, 2, 5], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'A/G': [
      P('Abertura', [3, 0, 2, 2, 2, 0], [4, 0, 1, 2, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [3, 4, 2, 2, 2, 5], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [3, 4, 2, 2, 5, 5], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'A/G#': [
      P('2ª casa', [4, 4, 2, 2, 5, 5], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa', [4, 4, 2, 2, 2, 5], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('5ª casa', ["x", "x", 6, 6, 5, 5], [0, 0, 2, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'A11': [
      P('Abertura', ["x", 0, 0, 0, 2, 0], [0, 0, 0, 0, 2, 0], 'chords-db', []),
      P('Abertura', [5, 4, 0, 0, 0, 3], [3, 2, 0, 0, 0, 1], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 6, 5, 5], [1, 1, 1, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'A13': [
      P('Abertura', ["x", 0, 2, 0, 2, 2], [0, 0, 1, 0, 2, 3], 'chords-db', []),
      P('Abertura', [5, 4, 4, 0, 3, 0], [4, 2, 3, 0, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 6, 7, 5], [1, 3, 1, 2, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'A5': [
      P('Padrão', [5, 7, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 0, 2, "x", "x", "x"], [0, 0, 1, 0, 0, 0], 'chords-db', []),
      P('Padrão', [5, 7, 7, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'A6': [
      P('2ª casa', ["x", 0, 2, 2, 2, 2], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('Padrão', [5, "x", 4, 6, 5, "x"], [2, 0, 1, 4, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, "x", 6, 7, 5], [1, 3, 0, 2, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'A69': [
      P('2ª casa', ["x", 0, 4, 4, 2, 2], [0, 0, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', [5, 4, 4, 4, 5, 5], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', ["x", 7, 7, 6, 7, 7], [0, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'A7': [
      P('Abertura', ["x", 0, 2, 0, 2, 0], [0, 0, 2, 0, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 0, 2, 2, 2, 3], [0, 0, 1, 1, 1, 2], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 5, 6, 5, 5], [1, 3, 1, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'A7#9': [
      P('[5, 8]ª casa (pestana)', [5, 7, 5, 6, 8, 8], [1, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}, {"fret": 8, "from": 4, "to": 5}]),
      P('Padrão', ["x", "x", 7, 6, 8, 8], [0, 0, 2, 1, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 0, 10, 9, 8, 9], [0, 0, 4, 2, 1, 3], 'chords-db', [])
      ],
      'A7b5': [
      P('Padrão', ["x", 0, 1, 2, 2, 3], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 0, 5, 6, 4, 5], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 7, 8, 8, 9], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'A7b9': [
      P('2ª casa', ["x", 0, 2, 3, 2, 3], [0, 0, 1, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 5, 6, 5, 6], [1, 4, 1, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 7, 6, 8, 6], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'A7sus4': [
      P('Abertura', ["x", 0, 2, 0, 3, 0], [0, 0, 2, 0, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 7, 5, 5], [1, 3, 1, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', ["x", 0, 7, 9, 8, 10], [0, 0, 1, 3, 2, 4], 'chords-db', [])
      ],
      'A9': [
      P('Abertura', [5, 4, 2, 0, 0, 0], [4, 3, 1, 0, 0, 0], 'chords-db', []),
      P('2ª casa', ["x", 0, 2, 4, 2, 3], [0, 0, 1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 5, 6, 5, 7], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'A9#11': [
      P('Abertura', ["x", 0, 1, 0, 2, 0], [0, 0, 1, 0, 3, 0], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 5, 4, 4, 5], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 7, 8, 8, 9], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'A9b5': [
      P('Padrão', ["x", 0, 1, 4, 2, 3], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 5, 4, 4, 5], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('8ª casa', ["x", 0, 9, 8, 8, 9], [0, 0, 2, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Aadd11': [
      P('7ª casa', ["x", 0, 7, 7, 10, 9], [0, 0, 1, 1, 4, 3], 'chords-db', [{"fret": 7, "from": 2, "to": 5}]),
      P('10ª casa', ["x", 0, 11, 9, 10, 10], [0, 0, 3, 1, 2, 2], 'chords-db', [{"fret": 10, "from": 2, "to": 5}]),
      P('9ª casa', ["x", 0, 12, 9, 10, 9], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'Aadd9': [
      P('Abertura', ["x", 0, 2, 4, 2, 0], [0, 0, 1, 3, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 7, 6, 5, 7], [0, 0, 3, 2, 1, 4], 'chords-db', []),
      P('9ª casa (pestana)', ["x", 12, 11, 9, 12, 9], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Aalt': [
      P('Padrão', ["x", 0, 1, 2, 2, "x"], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 0, 7, 6, 4, 5], [0, 0, 4, 3, 1, 2], 'chords-db', []),
      P('Padrão', ["x", 0, 11, 8, 10, 9], [0, 0, 4, 1, 3, 2], 'chords-db', [])
      ],
      'Aaug': [
      P('Padrão', ["x", 0, 3, 2, 2, 1], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('2ª casa (pestana)', [5, 4, 3, 2, 2, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 2, "from": 0, "to": 4}]),
      P('5ª casa (pestana)', [5, "x", 7, 6, 6, 5], [1, 0, 4, 2, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Aaug7': [
      P('Abertura', ["x", 0, 3, 0, 2, 1], [0, 0, 3, 0, 2, 1], 'chords-db', []),
      P('2ª casa', ["x", 0, 3, 2, 2, 3], [0, 0, 2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', ["x", 0, 5, 6, 6, 5], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'Aaug9': [
      P('Padrão', ["x", 0, 3, 4, 2, 3], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('Abertura', [5, 4, 3, 0, 0, 5], [3, 2, 1, 0, 0, 4], 'chords-db', []),
      P('Padrão', ["x", 0, 5, 6, 6, 7], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'Ab': [
      P('1ª casa (pestana)', [4, 3, 1, 1, 1, "x"], [3, 2, 1, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('4ª casa (pestana)', [4, 6, 6, 5, 4, 4], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 9, 8], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ab/A': [
      P('1ª casa', ["x", 0, 1, 1, 1, 4], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa', ["x", 0, 6, 5, 4, 4], [0, 0, 3, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 7, 5, 4, 4], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Ab/B': [
      P('1ª casa (pestana)', ["x", 2, 1, 1, 1, 4], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 9, 8, 9, 8], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}]),
      P('1ª casa (pestana)', ["x", 2, 1, 1, 1, "x"], [0, 2, 1, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 1, "to": 4}])
      ],
      'Ab/Bb': [
      P('1ª casa (pestana)', ["x", 1, 1, 1, 1, 4], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 8, 9, 8], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 8, 8, 9, 8], [0, 0, 1, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Ab/C': [
      P('1ª casa (pestana)', ["x", 3, 1, 1, 1, 4], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", 3, 1, 1, 4, 4], [0, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [8, 11, 10, 8, 9, 8], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Ab/C#': [
      P('4ª casa (pestana)', ["x", 4, 6, 5, 4, 4], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 11, 8, 9, 8], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", "x", 11, 13, 13, 11], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 11, "from": 2, "to": 5}])
      ],
      'Ab/D': [
      P('4ª casa', ["x", "x", 0, 5, 4, 4], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', ["x", 5, 6, 5, 4, 4], [0, 2, 4, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa', ["x", "x", 0, 8, 9, 8], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 3, "to": 5}])
      ],
      'Ab/E': [
      P('1ª casa', [0, 3, 1, 1, 1, 4], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa', [0, 3, 1, 1, 4, 4], [0, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 2, 5, 4, 4], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'Ab/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 1, 1, 4], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 6, 5, 4, 4], [0, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 9, 8], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ab/F': [
      P('1ª casa (pestana)', [1, 3, 1, 1, 1, 4], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [1, 3, 1, 1, 4, 4], [1, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 5, 4, 4], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'Ab/F#': [
      P('1ª casa (pestana)', [2, 3, 1, 1, 1, 4], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [2, 3, 1, 1, 4, 4], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 5, 4, 4], [0, 0, 1, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Ab/G': [
      P('1ª casa (pestana)', [3, 3, 1, 1, 1, 4], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [3, 3, 1, 1, 4, 4], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 5, 5, 4, 4], [0, 0, 2, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Ab11': [
      P('4ª casa (pestana)', [4, 4, 4, 5, 4, 4], [1, 1, 1, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 6, 7, 8], [1, 1, 1, 1, 2, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', ["x", 11, 10, 11, 9, 9], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Ab13': [
      P('1ª casa (pestana)', [4, 1, 3, 1, 1, 2], [4, 1, 3, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 4, 5, 6, 4], [1, 3, 1, 2, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 4, 5, 6, 6], [1, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'Ab5': [
      P('Padrão', [4, 6, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 11, 13, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [4, 6, 6, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'Ab6': [
      P('1ª casa (pestana)', ["x", 3, 1, 1, 1, 1], [0, 3, 1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', [4, "x", 3, 5, 4, "x"], [2, 0, 1, 4, 3, 0], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 6, 8], [0, 1, 1, 3, 1, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ab69': [
      P('1ª casa (pestana)', ["x", 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', [4, 3, 3, 3, 4, 4], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 5, 6, 6], [0, 0, 2, 1, 3, 4], 'chords-db', [])
      ],
      'Ab7': [
      P('1ª casa (pestana)', ["x", "x", 1, 1, 1, 2], [0, 0, 1, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 4, 5, 4, 4], [1, 3, 1, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 7, 8], [0, 1, 1, 3, 2, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ab7#9': [
      P('4ª casa', [4, 3, 4, 4, 4, 4], [2, 1, 3, 3, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('[4, 7]ª casa (pestana)', [4, 6, 4, 5, 7, 7], [1, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}, {"fret": 7, "from": 4, "to": 5}]),
      P('7ª casa', ["x", "x", 6, 5, 7, 7], [0, 0, 3, 1, 4, 4], 'chords-db', [{"fret": 7, "from": 4, "to": 5}])
      ],
      'Ab7b5': [
      P('Padrão', [4, "x", 4, 5, 3, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 7, 7, 8], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('9ª casa (pestana)', ["x", 9, 10, 11, 9, 10], [0, 1, 2, 4, 1, 3], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Ab7b9': [
      P('1ª casa', ["x", 0, 1, 1, 1, 2], [0, 0, 1, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa', ["x", "x", 4, 5, 4, 5], [1, 0, 1, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 6, 5, 7, 5], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'Ab7sus4': [
      P('[1, 2]ª casa (pestana)', ["x", "x", 1, 1, 2, 2], [0, 0, 1, 1, 2, 2], 'chords-db', [{"fret": 1, "from": 2, "to": 5}, {"fret": 2, "from": 4, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 4, 6, 4, 4], [1, 3, 1, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', ["x", 11, 11, 11, 9, 9], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Ab9': [
      P('3ª casa (pestana)', [4, 3, 4, 3, 4, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}]),
      P('4ª casa (pestana)', [4, 6, 4, 5, 4, 6], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 5, 7, 6], [0, 0, 2, 1, 4, 3], 'chords-db', [])
      ],
      'Ab9#11': [
      P('Padrão', [4, "x", 4, 5, 3, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 7, 7, 8], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('10ª casa (pestana)', ["x", 11, 10, 11, 11, 10], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'Ab9b5': [
      P('Padrão', [4, 3, 0, 3, "x", 2], [4, 2, 0, 3, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [4, 3, 4, 3, 3, 4], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 5, 4, 5, "x", 6], [1, 2, 1, 3, 0, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'Abadd11': [
      P('9ª casa', ["x", 11, 10, 8, 9, 9], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 9, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', [4, 3, 1, 1, 2, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('6ª casa', [4, 3, 6, 6, "x", "x"], [2, 1, 4, 4, 0, 0], 'chords-db', [{"fret": 6, "from": 2, "to": 3}])
      ],
      'Abadd9': [
      P('Padrão', [4, 3, "x", 3, 4, "x"], [3, 1, 0, 2, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 5, 4, 6], [0, 0, 3, 2, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 11, 10, 8, 11, 8], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Abalt': [
      P('Padrão', ["x", "x", 6, 5, 3, 4], [0, 0, 4, 3, 1, 2], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 7, 9, 8], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('[10, 13]ª casa (pestana)', ["x", 11, 10, 13, 13, 10], [0, 2, 1, 4, 4, 1], 'chords-db', [{"fret": 10, "from": 1, "to": 5}, {"fret": 13, "from": 3, "to": 4}])
      ],
      'Abaug': [
      P('1ª casa (pestana)', [4, 3, 2, 1, 1, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('Padrão', [4, "x", 6, 5, 5, "x"], [1, 0, 4, 2, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", "x", 6, 5, 5, "x"], [0, 0, 2, 1, 1, 0], 'chords-db', [{"fret": 5, "from": 2, "to": 4}])
      ],
      'Abaug7': [
      P('Padrão', [4, "x", 4, 5, 5, 0], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 9, 7, 8], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 11, 10, 11, 9, 0], [0, 3, 2, 4, 1, 0], 'chords-db', [])
      ],
      'Abaug9': [
      P('1ª casa (pestana)', [2, 1, 2, 1, 1, 2], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa', [4, 3, 4, 3, 5, 0], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}]),
      P('Padrão', ["x", "x", 4, 5, 5, 6], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'Abdim': [
      P('Padrão', [4, 2, "x", 4, 3, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 7, "x", 7], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 11, 9, "x", 9, 10], [0, 4, 1, 0, 2, 3], 'chords-db', [])
      ],
      'Abdim7': [
      P('Abertura', ["x", "x", 0, 1, 0, 1], [0, 0, 0, 1, 0, 2], 'chords-db', []),
      P('3ª casa (pestana)', [4, "x", 3, 4, 3, 4], [2, 0, 1, 3, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 7, 6, 7], [0, 0, 1, 3, 2, 4], 'chords-db', [])
      ],
      'Abm': [
      P('4ª casa (pestana)', [4, 6, 6, 4, 4, 4], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 8, 9, 7], [0, 0, 1, 3, 4, 2], 'chords-db', []),
      P('Padrão', ["x", "x", 9, 8, 9, 7], [0, 0, 3, 2, 4, 1], 'chords-db', [])
      ],
      'Abm/A': [
      P('Abertura', ["x", 0, 1, 1, 0, 4], [0, 0, 1, 2, 0, 4], 'chords-db', []),
      P('4ª casa', ["x", 0, 1, 4, 4, 4], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa', ["x", 0, 6, 4, 4, 4], [0, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Abm/B': [
      P('1ª casa (pestana)', ["x", 2, 1, 1, 4, 4], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa', ["x", 2, 1, 4, 4, 4], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', [7, 6, 6, 4, 4, 4], [4, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'Abm/Bb': [
      P('1ª casa (pestana)', ["x", 1, 1, 4, 4, 4], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [6, 6, 6, 4, 4, 4], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 8, 9, 7], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Abm/C': [
      P('4ª casa', ["x", 3, 1, 4, 4, 4], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 10, 8, 9, 7], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 10, 13, 12, 11], [0, 0, 1, 4, 3, 2], 'chords-db', [])
      ],
      'Abm/C#': [
      P('4ª casa (pestana)', ["x", 4, 6, 4, 4, 4], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 6, 4, 4, 7], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('11ª casa (pestana)', ["x", "x", 11, 13, 12, 11], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 11, "from": 2, "to": 5}])
      ],
      'Abm/D': [
      P('4ª casa', ["x", "x", 0, 4, 4, 4], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', ["x", 5, 6, 4, 4, 4], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 5, 6, 4, 4, 7], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'Abm/E': [
      P('1ª casa', [0, 2, 1, 1, 4, 4], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa', [0, 2, 1, 4, 4, 4], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa', ["x", "x", 2, 4, 4, 4], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 4, "from": 3, "to": 5}])
      ],
      'Abm/Eb': [
      P('Padrão', ["x", "x", 1, 1, 0, 4], [0, 0, 1, 2, 0, 4], 'chords-db', []),
      P('4ª casa', ["x", "x", 1, 4, 4, 4], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 6, 4, 4, 4], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'Abm/F': [
      P('1ª casa (pestana)', [1, 2, 1, 1, 4, 4], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [1, 2, 1, 4, 4, 4], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa', ["x", "x", 3, 4, 4, 4], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 4, "from": 3, "to": 5}])
      ],
      'Abm/F#': [
      P('4ª casa (pestana)', ["x", "x", 4, 4, 4, 4], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('Padrão', [2, 2, 1, 1, 0, "x"], [3, 4, 1, 2, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 9, 9, 8, 9, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', [])
      ],
      'Abm/G': [
      P('1ª casa (pestana)', [3, 2, 1, 1, 4, 4], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa', [3, 2, 1, 4, 4, 4], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 5, 4, 4, 4], [0, 0, 2, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Abm11': [
      P('2ª casa (pestana)', [4, 2, 4, 3, 2, 2], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 4, 4, 4, 6], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 6, 7, 7], [0, 0, 1, 1, 2, 3], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Abm6': [
      P('Padrão', [4, "x", 3, 4, 4, "x"], [2, 0, 1, 3, 4, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 6, 4, 6, 4], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 6, 7], [0, 1, 1, 3, 1, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Abm69': [
      P('4ª casa', [4, "x", 3, 4, 4, 6], [2, 0, 1, 3, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('[4, 6]ª casa (pestana)', [4, 6, 6, 4, 6, 6], [1, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}, {"fret": 6, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [7, 6, 6, 8, 6, 6], [2, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Abm7': [
      P('Padrão', [4, "x", 4, 4, 4, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 4, 4, 4, 4], [1, 3, 1, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 7, 7], [0, 1, 1, 4, 2, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Abm7b5': [
      P('Abertura', ["x", "x", 0, 1, 0, 2], [0, 0, 0, 1, 0, 3], 'chords-db', []),
      P('Padrão', [4, "x", 4, 4, 3, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('7ª casa', ["x", "x", 6, 7, 7, 7], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 7, "from": 3, "to": 5}])
      ],
      'Abm9': [
      P('1ª casa', [4, 1, 1, 1, 0, 2], [4, 1, 1, 2, 0, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 4, 4, 4, 6], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('8ª casa', [7, 9, 8, 8, 9, 7], [1, 3, 2, 2, 4, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 4}])
      ],
      'Abm9/B': [
      P('6ª casa (pestana)', [7, 6, 6, 8, 7, 6], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [7, "x", 6, 8, 7, 6], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Abm9/F#': [
      P('6ª casa (pestana)', ["x", 9, 6, 8, 7, 6], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('11ª casa (pestana)', [14, 11, 13, 11, 11, 11], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 5}]),
      P('11ª casa (pestana)', [14, 11, 13, 13, 11, 11], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 5}])
      ],
      'Abmadd9': [
      P('Padrão', [4, 2, "x", 3, 4, "x"], [3, 1, 0, 2, 4, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", "x", 6, 4, 4, 6], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 6, 4, 4, 6], [1, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'Abmaj11': [
      P('Padrão', [4, 3, 1, 0, 2, "x"], [4, 3, 1, 0, 2, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 5, 5, 4, 4], [1, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 6, 8, 8], [0, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Abmaj13': [
      P('3ª casa (pestana)', [4, 3, 3, 3, 4, 3], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 5, 5, 6, 4], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 11, 10, 10, 8, 8], [0, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Abmaj7': [
      P('4ª casa (pestana)', [4, 6, 5, 5, 4, 4], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 8, 8], [0, 1, 1, 3, 3, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('Padrão', ["x", 11, 10, 12, 9, "x"], [0, 3, 2, 4, 1, 0], 'chords-db', [])
      ],
      'Abmaj7#5': [
      P('Abertura', [4, 3, 2, 0, 1, 0], [4, 3, 2, 0, 1, 0], 'chords-db', []),
      P('Abertura', [4, 3, 5, 0, 5, 0], [2, 1, 3, 0, 4, 0], 'chords-db', []),
      P('8ª casa (pestana)', [8, 11, 10, 9, 8, 8], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Abmaj7b5': [
      P('3ª casa (pestana)', [4, 3, 5, 5, 3, 3], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', [4, 5, 5, 5, "x", "x"], [1, 2, 3, 4, 0, 0], 'chords-db', []),
      P('8ª casa (pestana)', [0, 0, 6, 7, 8, 8], [0, 0, 1, 2, 3, 4], 'chords-db', [{"fret": 8, "from": 4, "to": 5}])
      ],
      'Abmaj7sus2': [
      P('3ª casa (pestana)', ["x", "x", 6, 3, 4, 3], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 8, 8, 6], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", 11, 13, 12, 11, 11], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 11, "from": 1, "to": 5}])
      ],
      'Abmaj9': [
      P('1ª casa (pestana)', ["x", 1, 1, 1, 1, 3], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', [4, 3, 5, 3, 4, 3], [2, 1, 4, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 5, 5, 4, 6], [1, 3, 2, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'Abmmaj11': [
      P('4ª casa (pestana)', [4, 4, 5, 4, 4, 6], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 6, 8, 7], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', ["x", 11, 9, 12, 11, 9], [0, 2, 1, 4, 3, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Abmmaj7': [
      P('1ª casa (pestana)', ["x", 2, 1, 1, 4, 3], [0, 2, 1, 1, 4, 3], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 5, 4, 4, 4], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 8, 7], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Abmmaj7b5': [
      P('4ª casa (pestana)', [4, 5, 5, 4, "x", 4], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 7, 8, 7], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('12ª casa', [10, 11, 12, 12, 12, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 12, "from": 2, "to": 4}])
      ],
      'Abmmaj9': [
      P('Padrão', [4, "x", 5, 3, 0, 4], [2, 0, 4, 1, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 5, 4, 4, 6], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 8, 8, 7], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Absus': [
      P('4ª casa (pestana)', [4, 4, 6, 6, 4, 4], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 6, 6, 4, 4], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 6, 6, 4, 4], [0, 0, 3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Absus2': [
      P('Padrão', [4, "x", "x", 3, 4, 4], [2, 0, 0, 1, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 6, "x", 4, 6], [1, 2, 3, 0, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 8, 9, 6], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Absus4': [
      P('1ª casa (pestana)', ["x", "x", 1, 1, 2, 4], [0, 0, 1, 1, 2, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 6, 6, 4, 4], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 9, 9], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Adim': [
      P('Padrão', ["x", 0, 1, 2, 1, "x"], [0, 0, 1, 3, 2, 0], 'chords-db', []),
      P('Padrão', [5, 3, "x", 4, 3, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 7, 8, "x", 8], [0, 0, 1, 2, 0, 3], 'chords-db', [])
      ],
      'Adim7': [
      P('Padrão', ["x", 0, 1, 2, 1, 2], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('4ª casa (pestana)', [5, "x", 4, 5, 4, "x"], [2, 0, 1, 3, 1, 0], 'chords-db', [{"fret": 4, "from": 0, "to": 4}]),
      P('5ª casa (pestana)', [5, 6, 7, 5, 7, 5], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Am': [
      P('Abertura', ["x", 0, 2, 2, 1, 0], [0, 0, 2, 3, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 0, 2, 5, 5, 5], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 7, 5, 5, 5], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Am/Ab': [
      P('2ª casa (pestana)', [4, 3, 2, 2, 5, 5], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('5ª casa', [4, 3, 2, 5, 5, 5], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 6, 5, 5, 5], [0, 0, 2, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'Am/B': [
      P('Padrão', ["x", 2, 2, 2, 1, 0], [0, 2, 3, 4, 1, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 2, 2, 5, 5, 5], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', [7, 7, 7, 5, 5, 5], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Am/Bb': [
      P('Padrão', ["x", 1, 2, 2, 1, 0], [0, 1, 3, 4, 2, 0], 'chords-db', []),
      P('5ª casa (pestana)', [6, 7, 7, 5, 5, 5], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 8, 5, 5, 5], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'Am/C': [
      P('Padrão', ["x", 3, 2, 2, 1, 0], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 3, 2, 2, 5, 5], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa', ["x", 3, 2, 5, 5, 5], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 5, "from": 3, "to": 5}])
      ],
      'Am/C#': [
      P('5ª casa', ["x", 4, 2, 5, 5, 5], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 11, 9, 10, 8], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 11, 14, 13, 12], [0, 0, 1, 4, 3, 2], 'chords-db', [])
      ],
      'Am/D': [
      P('Abertura', ["x", "x", 0, 2, 1, 0], [0, 0, 0, 2, 1, 0], 'chords-db', []),
      P('5ª casa', ["x", "x", 0, 5, 5, 5], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 7, 5, 5, 5], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Am/E': [
      P('Abertura', [0, 0, 2, 2, 1, 0], [0, 0, 2, 3, 1, 0], 'chords-db', []),
      P('Abertura', [0, 3, 2, 2, 1, 0], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('2ª casa', [0, 3, 2, 2, 5, 5], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}])
      ],
      'Am/Eb': [
      P('Padrão', ["x", "x", 1, 2, 1, 0], [0, 0, 1, 3, 2, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 7, 5, 5, 5], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 6, 7, 5, 5, 8], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Am/F': [
      P('Padrão', ["x", "x", 3, 2, 1, 0], [0, 0, 3, 2, 1, 0], 'chords-db', []),
      P('5ª casa', ["x", "x", 3, 5, 5, 5], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', ["x", 8, 7, 5, 5, 5], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Am/F#': [
      P('Abertura', [2, 0, 2, 2, 1, 0], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 2, 1, 0], [0, 0, 4, 2, 1, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 3, 2, 2, 5, 5], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'Am/G': [
      P('Abertura', [3, 0, 2, 2, 1, 0], [4, 0, 2, 3, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", "x", 5, 5, 5, 5], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('Padrão', [3, 0, 2, 2, 1, "x"], [4, 0, 2, 3, 1, 0], 'chords-db', [])
      ],
      'Am/G#': [
      P('5ª casa', [4, 3, 2, 5, 5, 5], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('2ª casa', [4, 3, 2, 2, 5, 5], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'Am11': [
      P('Abertura', ["x", 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', [5, 3, 5, 4, 3, 3], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', [5, 5, 5, 5, 5, 7], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Am6': [
      P('Padrão', ["x", 0, 2, 2, 1, 2], [0, 0, 2, 3, 1, 4], 'chords-db', []),
      P('5ª casa', [5, "x", 4, 5, 5, 5], [2, 0, 1, 3, 3, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 7, 5, 7, 5], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Am69': [
      P('Abertura', ["x", 0, 4, 5, 0, 0], [0, 0, 2, 4, 0, 0], 'chords-db', []),
      P('[5, 7]ª casa (pestana)', [5, 7, 7, 5, 7, 7], [1, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}, {"fret": 7, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [8, 0, 7, 9, 7, 7], [2, 0, 1, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Am7': [
      P('Abertura', ["x", 0, 2, 0, 1, 0], [0, 0, 2, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", 0, 2, 2, 1, 3], [0, 0, 2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [5, "x", 5, 5, 5, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', [])
      ],
      'Am7b5': [
      P('Abertura', ["x", 0, 1, 0, 1, "x"], [0, 0, 2, 0, 3, 0], 'chords-db', []),
      P('Padrão', [5, "x", 5, 5, 4, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 6, 7, 5, 8, 5], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Am9': [
      P('Padrão', ["x", 0, 2, 4, 1, 3], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 5, 5, 7], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Abertura', [8, 0, 9, 0, 8, 0], [1, 0, 3, 0, 2, 0], 'chords-db', [])
      ],
      'Am9/C': [
      P('7ª casa (pestana)', [8, 7, 7, 9, 8, 7], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [8, "x", 7, 9, 8, 7], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Am9/G': [
      P('Abertura', [3, 0, 2, 0, 0, 0], [2, 0, 1, 0, 0, 0], 'chords-db', []),
      P('Abertura', [3, 0, 2, 0, 0, 3], [2, 0, 1, 0, 0, 3], 'chords-db', []),
      P('Abertura', [3, 0, 2, 2, 0, 0], [3, 0, 1, 2, 0, 0], 'chords-db', [])
      ],
      'Amadd9': [
      P('Abertura', ["x", 0, 2, 4, 1, 0], [0, 0, 2, 4, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", "x", 7, 5, 5, 7], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 7, 9, 0, 8], [0, 0, 1, 3, 0, 2], 'chords-db', [])
      ],
      'Amaj11': [
      P('Abertura', ["x", 0, 0, 1, 2, 0], [0, 0, 0, 1, 2, 0], 'chords-db', []),
      P('2ª casa', ["x", 0, 0, 2, 2, 4], [0, 0, 0, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('5ª casa', [5, 5, 6, 6, 5, 7], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Amaj13': [
      P('Padrão', ["x", 0, 2, 1, 2, 2], [0, 0, 2, 1, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 4, 4, 5, 4], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa', ["x", 0, 6, 6, 7, 7], [0, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Amaj7': [
      P('Abertura', ["x", 0, 2, 1, 2, 0], [0, 0, 2, 1, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 0, 2, 2, 2, 4], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 7, 6, 6, 5, 5], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Amaj7#5': [
      P('1ª casa', ["x", 0, 3, 1, 2, 1], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('2ª casa', ["x", 0, 3, 2, 2, 4], [0, 0, 2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 6, 6, 6, 5], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'Amaj7b5': [
      P('1ª casa', ["x", 0, 1, 1, 2, 4], [0, 0, 1, 1, 2, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('2ª casa', ["x", 0, 1, 2, 2, 4], [0, 0, 1, 2, 2, 4], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('Padrão', [5, 6, 6, 6, "x", "x"], [1, 2, 3, 4, 0, 0], 'chords-db', [])
      ],
      'Amaj7sus2': [
      P('Abertura', ["x", 0, 2, 1, 0, 0], [0, 0, 2, 1, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 1, 0, 4], [0, 0, 2, 1, 0, 4], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 2, 0, 4], [0, 0, 1, 2, 0, 4], 'chords-db', [])
      ],
      'Amaj9': [
      P('2ª casa', ["x", 0, 2, 4, 2, 4], [0, 0, 1, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('4ª casa', [5, 4, 6, 4, 5, 0], [2, 1, 4, 1, 3, 0], 'chords-db', [{"fret": 4, "from": 0, "to": 4}]),
      P('Padrão', ["x", 0, 6, 6, 5, 7], [0, 0, 2, 3, 1, 4], 'chords-db', [])
      ],
      'Ammaj11': [
      P('Abertura', ["x", 0, 0, 1, 1, 0], [0, 0, 0, 1, 2, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 6, 5, 5, 7], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('7ª casa', ["x", 0, 7, 7, 9, 8], [0, 0, 1, 1, 3, 2], 'chords-db', [{"fret": 7, "from": 2, "to": 5}])
      ],
      'Ammaj7': [
      P('Abertura', ["x", 0, 2, 1, 1, 0], [0, 0, 3, 1, 2, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 6, 5, 5, 5], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', ["x", 7, 7, 9, 9, 8], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Ammaj7b5': [
      P('1ª casa', ["x", 0, 1, 1, 1, 4], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 6, 6, 5, "x", 5], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 7, 8, 9, 8], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'Ammaj9': [
      P('Abertura', [5, 3, 6, 4, 0, 0], [3, 1, 4, 2, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 6, 5, 0, 4], [0, 0, 3, 2, 0, 1], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 6, 5, 5, 7], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Asus': [
      P('Abertura', ["x", 0, 0, 2, 3, 0], [0, 0, 0, 1, 2, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 2, 3, 0], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('2ª casa', ["x", 0, 2, 2, 3, 5], [0, 0, 1, 1, 2, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'Asus2': [
      P('Abertura', ["x", 0, 2, 2, 0, 0], [0, 0, 2, 3, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 4, 0, 0], [0, 0, 1, 4, 0, 0], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 7, 9, 10, 7], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Asus2sus4': [
      P('Abertura', ["x", 0, 0, 2, 0, 0], [0, 0, 0, 1, 0, 0], 'chords-db', []),
      P('[5]ª casa (pestana)', [5, 5, 7, 7, 5, 7], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', [5, 5, 2, 4, "x", "x"], [3, 4, 1, 2, 0, 0], 'chords-db', [])
      ],
      'Asus4': [
      P('Abertura', ["x", 0, 2, 2, 3, 0], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 0, "x", 3, 0], [0, 0, 0, 0, 1, 0], 'chords-db', []),
      P('[5, 7]ª casa (pestana)', [5, 7, 7, 7, 5, 5], [1, 3, 3, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}, {"fret": 7, "from": 1, "to": 3}])
      ],
      'B': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 4, 2], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 4, 7], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 9, 8, 7, 7], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'B/A': [
      P('Abertura', ["x", 0, 1, 4, 0, 2], [0, 0, 1, 4, 0, 2], 'chords-db', []),
      P('Padrão', ["x", 0, 4, 4, 4, 2], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('4ª casa', ["x", 0, 4, 4, 4, 7], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'B/Ab': [
      P('4ª casa (pestana)', [4, 6, 4, 4, 4, 7], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 6, 4, 4, 7, 7], [1, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 8, 7, 7], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'B/Bb': [
      P('4ª casa (pestana)', [6, 6, 4, 4, 4, 7], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [6, 6, 4, 4, 7, 7], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', ["x", "x", 8, 8, 7, 7], [0, 0, 2, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 2, "to": 5}])
      ],
      'B/C': [
      P('Padrão', ["x", 3, 1, 4, 0, 2], [0, 3, 1, 4, 0, 2], 'chords-db', []),
      P('7ª casa (pestana)', ["x", "x", 10, 8, 7, 7], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 10, 11, 12, 11], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'B/C#': [
      P('4ª casa (pestana)', ["x", 4, 4, 4, 4, 7], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 9, 11, 12, 11], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 9, "from": 0, "to": 5}]),
      P('11ª casa (pestana)', ["x", "x", 11, 11, 12, 11], [0, 0, 1, 1, 2, 1], 'chords-db', [{"fret": 11, "from": 2, "to": 5}])
      ],
      'B/D': [
      P('Padrão', ["x", "x", 0, 4, 4, 2], [0, 0, 0, 3, 4, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 5, 4, 4, 4, 7], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('7ª casa', ["x", "x", 0, 8, 7, 7], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 3, "to": 5}])
      ],
      'B/E': [
      P('2ª casa', [0, 2, 4, 4, 4, 2], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 2, 4, 4, 2], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('4ª casa', [0, 6, 4, 4, 4, 7], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'B/Eb': [
      P('Padrão', ["x", "x", 1, 4, 0, 2], [0, 0, 1, 4, 0, 2], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 6, 4, 4, 4, 7], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 4, 4, 7, 7], [0, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'B/F': [
      P('Padrão', ["x", "x", 3, 4, 4, 2], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 8, 9, 8, 7, 7], [0, 2, 4, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}]),
      P('4ª casa', [1, 2, 4, 4, 4, "x"], [1, 2, 4, 4, 4, 0], 'chords-db', [{"fret": 4, "from": 2, "to": 4}])
      ],
      'B/F#': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 4, 2], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 4, 4, 2], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 4, 7], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'B/G': [
      P('Padrão', ["x", "x", 5, 4, 4, 2], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 8, 7, 7], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 10, 9, 8, 7, 7], [0, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'B11': [
      P('Abertura', ["x", 2, 1, 2, 0, 0], [0, 2, 1, 3, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 2, 4, 2], [1, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 7, 8, 7, 7], [1, 1, 1, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'B13': [
      P('4ª casa', ["x", 2, 1, 2, 4, 4], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 4, "from": 4, "to": 5}]),
      P('2ª casa (pestana)', [2, 2, 2, 2, 4, 4], [1, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [7, 4, 6, 4, 4, 5], [4, 1, 3, 1, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'B5': [
      P('Padrão', [7, 9, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 2, 4, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [7, 9, 9, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'B6': [
      P('Padrão', ["x", 2, 1, 1, 0, "x"], [0, 3, 1, 2, 0, 0], 'chords-db', []),
      P('4ª casa', ["x", 2, 4, 4, 4, 4], [0, 1, 3, 3, 3, 3], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('Padrão', [7, "x", 9, 8, 9, "x"], [1, 0, 3, 2, 4, 0], 'chords-db', [])
      ],
      'B69': [
      P('1ª casa (pestana)', ["x", 2, 1, 1, 2, 2], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [7, 6, 6, 6, 7, 7], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('9ª casa', ["x", 9, 9, 8, 9, 9], [0, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'B7': [
      P('Padrão', ["x", 2, 1, 2, 0, 2], [0, 2, 1, 3, 0, 4], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 4, 2, 4, 2], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 4, 5], [0, 0, 1, 1, 1, 2], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'B7#9': [
      P('Padrão', ["x", 2, 1, 2, 3, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', []),
      P('Abertura', [7, 6, 0, 7, 0, 5], [3, 2, 0, 4, 0, 1], 'chords-db', []),
      P('[7, 10]ª casa (pestana)', [7, 9, 7, 8, 10, 10], [1, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}, {"fret": 10, "from": 4, "to": 5}])
      ],
      'B7b5': [
      P('Padrão', ["x", 2, 1, 2, 0, 1], [0, 3, 1, 4, 0, 2], 'chords-db', []),
      P('Padrão', ["x", 2, 3, 2, 4, "x"], [0, 1, 2, 1, 3, 0], 'chords-db', []),
      P('Padrão', [7, "x", 7, 8, 6, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', [])
      ],
      'B7b9': [
      P('1ª casa (pestana)', ["x", 2, 1, 2, 1, 2], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', [7, 6, 7, 5, "x", "x"], [3, 2, 4, 1, 0, 0], 'chords-db', []),
      P('7ª casa (pestana)', [7, "x", 7, 8, 7, 8], [1, 0, 1, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'B7sus4': [
      P('Abertura', ["x", 2, 2, 2, 0, 0], [0, 1, 2, 3, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 4, 2, 5, 2], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('[4, 5]ª casa (pestana)', ["x", "x", 4, 4, 5, 5], [0, 0, 1, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 2, "to": 5}, {"fret": 5, "from": 4, "to": 5}])
      ],
      'B9': [
      P('2ª casa', ["x", 2, 1, 2, 2, 2], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [7, 4, 4, 6, 4, 5], [4, 1, 1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 7, 8, 7, 9], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'B9#11': [
      P('1ª casa (pestana)', ["x", 2, 1, 2, 2, 1], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 2, 3, 2, 4, 2], [0, 1, 2, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', [7, "x", 7, 8, 6, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', [])
      ],
      'B9b5': [
      P('1ª casa (pestana)', ["x", 2, 1, 2, 2, 1], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [7, 6, 7, 6, 6, 7], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 8, 7, 8, "x", 9], [1, 2, 1, 3, 0, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Badd11': [
      P('Abertura', ["x", 2, 1, 4, 0, 0], [0, 2, 1, 4, 0, 0], 'chords-db', []),
      P('12ª casa', ["x", 14, 13, 11, 12, 12], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 12, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [7, 6, 4, 4, 5, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 4, "from": 0, "to": 4}])
      ],
      'Badd9': [
      P('Padrão', ["x", 2, 1, "x", 2, 2], [0, 2, 1, 0, 3, 4], 'chords-db', []),
      P('7ª casa', [7, 6, "x", 6, 7, 7], [3, 1, 0, 2, 4, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 9, 8, 7, 9], [0, 0, 3, 2, 1, 4], 'chords-db', [])
      ],
      'Balt': [
      P('Padrão', ["x", 2, 3, 4, 4, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 9, 8, 6, 7], [0, 0, 4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [7, 8, 9, 8, 0, "x"], [1, 2, 4, 3, 0, 0], 'chords-db', [])
      ],
      'Baug': [
      P('Abertura', ["x", 2, 1, 0, 0, "x"], [0, 2, 1, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 4, 4, 3], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [7, "x", 9, 8, 8, "x"], [1, 0, 4, 2, 3, 0], 'chords-db', [])
      ],
      'Baug7': [
      P('Padrão', ["x", 2, 1, 2, 0, 3], [0, 2, 1, 3, 0, 4], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 2, 5, 2, 4, 3], [0, 0, 2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', [7, "x", 7, 8, 8, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Baug9': [
      P('2ª casa', ["x", 2, 1, 2, 2, 3], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [5, 4, 5, 4, 4, 5], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [7, 6, 7, 6, 8, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 6, "from": 0, "to": 4}])
      ],
      'Bb': [
      P('1ª casa (pestana)', ["x", 1, 3, 3, 3, 1], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', [6, 5, 3, 3, 3, "x"], [4, 3, 1, 1, 1, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}]),
      P('6ª casa (pestana)', [6, 8, 8, 7, 6, 6], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bb/A': [
      P('Abertura', ["x", 0, 0, 3, 3, 1], [0, 0, 0, 3, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 0, 3, 3, 3, 1], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('3ª casa', ["x", 0, 3, 3, 3, 6], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'Bb/Ab': [
      P('3ª casa (pestana)', [4, 5, 3, 3, 3, 6], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [4, 5, 3, 3, 6, 6], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 7, 6, 6], [0, 0, 1, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Bb/B': [
      P('Padrão', ["x", 2, 0, 3, 3, 1], [0, 2, 0, 3, 4, 1], 'chords-db', []),
      P('6ª casa (pestana)', ["x", "x", 9, 7, 6, 6], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 9, 10, 11, 10], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'Bb/C': [
      P('Padrão', ["x", 3, 0, 3, 3, 1], [0, 2, 0, 3, 4, 1], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 3, 3, 3, 6], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 8, 10, 11, 10], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Bb/C#': [
      P('Padrão', ["x", 4, 0, 3, 3, 1], [0, 4, 0, 2, 3, 1], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 4, 3, 3, 3, 6], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', ["x", "x", 11, 10, 11, 10], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}])
      ],
      'Bb/D': [
      P('Padrão', ["x", "x", 0, 3, 3, 1], [0, 0, 0, 3, 4, 1], 'chords-db', []),
      P('6ª casa', ["x", "x", 0, 3, 6, 6], [0, 0, 0, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 4, "to": 5}]),
      P('3ª casa (pestana)', ["x", 5, 3, 3, 3, 6], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Bb/E': [
      P('1ª casa', [0, 1, 3, 3, 3, 1], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 2, 3, 3, 1], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('3ª casa', [0, 5, 3, 3, 3, 6], [0, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Bb/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 3, 3, 1], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 7, 6, 6], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', ["x", "x", 13, 10, 11, 10], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}])
      ],
      'Bb/F': [
      P('1ª casa (pestana)', [1, 1, 3, 3, 3, 1], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 3, 3, 1], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 3, 6], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'Bb/F#': [
      P('Padrão', ["x", "x", 4, 3, 3, 1], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 7, 6, 6], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 9, 8, 7, 6, 6], [0, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Bb/G': [
      P('3ª casa (pestana)', [3, 5, 3, 3, 3, 6], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 5, 3, 3, 6, 6], [1, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 7, 6, 6], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'Bb11': [
      P('1ª casa (pestana)', ["x", 1, 1, 1, 3, 1], [0, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [6, 5, 0, 5, 4, 4], [4, 2, 0, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 8, 8, 9, 10], [1, 1, 1, 1, 2, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Bb13': [
      P('3ª casa', ["x", 1, 0, 1, 3, 3], [0, 1, 0, 2, 4, 4], 'chords-db', [{"fret": 3, "from": 4, "to": 5}]),
      P('4ª casa', [6, 5, 0, 0, 4, 4], [3, 2, 0, 0, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 7, 8, 8], [1, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bb5': [
      P('Padrão', [6, 8, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 1, 3, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [6, 8, 8, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'Bb6': [
      P('3ª casa', ["x", 1, 3, 3, 3, 3], [0, 1, 3, 3, 3, 3], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('Abertura', [6, 5, 0, 0, 6, 6], [2, 1, 0, 0, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, "x", 7, 8, 6], [1, 3, 0, 2, 4, 0], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bb69': [
      P('Abertura', ["x", 1, 0, 0, 1, 1], [0, 1, 0, 0, 2, 3], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 5, 5, 6, 6], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('8ª casa', ["x", 8, 8, 7, 8, 8], [0, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Bb7': [
      P('1ª casa (pestana)', ["x", 1, 3, 1, 3, 1], [0, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 6, 7, 6, 6], [1, 3, 1, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 8, 10, 9, 10], [0, 1, 1, 3, 2, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Bb7#9': [
      P('Padrão', ["x", 1, 0, 1, 2, "x"], [0, 1, 0, 2, 3, 0], 'chords-db', []),
      P('[6, 9]ª casa (pestana)', [6, 8, 6, 7, 9, 9], [1, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}, {"fret": 9, "from": 4, "to": 5}]),
      P('Padrão', ["x", "x", 8, 7, 9, 9], [0, 0, 2, 1, 3, 4], 'chords-db', [])
      ],
      'Bb7b5': [
      P('1ª casa (pestana)', ["x", 1, 2, 1, 3, "x"], [0, 1, 2, 1, 3, 0], 'chords-db', [{"fret": 1, "from": 1, "to": 4}]),
      P('Padrão', [6, "x", 6, 7, 5, 0], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 9, 9, 10], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'Bb7b9': [
      P('Abertura', ["x", 1, 0, 1, 0, 1], [0, 1, 0, 2, 0, 3], 'chords-db', []),
      P('Padrão', [6, 5, 6, 4, "x", "x"], [3, 2, 4, 1, 0, 0], 'chords-db', []),
      P('6ª casa (pestana)', [6, "x", 6, 7, 6, 7], [1, 0, 1, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bb7sus4': [
      P('1ª casa (pestana)', ["x", 1, 3, 1, 4, 1], [0, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('[3, 4]ª casa (pestana)', ["x", "x", 3, 3, 4, 4], [0, 0, 1, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 2, "to": 5}, {"fret": 4, "from": 4, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 6, 8, 6, 6], [1, 3, 1, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bb9': [
      P('Padrão', ["x", 1, 0, 1, 1, 1], [0, 1, 0, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 6, 5, 6, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 4}]),
      P('6ª casa (pestana)', [6, 8, 6, 7, 6, 8], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bb9#11': [
      P('Abertura', ["x", 1, 0, 1, 1, 0], [0, 1, 0, 2, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 6, 5, 5, "x"], [2, 1, 3, 1, 1, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 4}]),
      P('Padrão', ["x", "x", 8, 9, 9, 10], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'Bb9b5': [
      P('Abertura', ["x", 1, 0, 1, 1, 0], [0, 1, 0, 2, 3, 0], 'chords-db', []),
      P('Padrão', [6, "x", 0, 5, 5, 4], [4, 0, 0, 2, 3, 1], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 6, 5, 5, 6], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Bbadd11': [
      P('11ª casa', ["x", 13, 12, 10, 11, 11], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 11, "from": 1, "to": 5}]),
      P('Padrão', ["x", 1, 0, 3, 4, "x"], [0, 1, 0, 3, 4, 0], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 3, 3, 4, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}])
      ],
      'Bbadd9': [
      P('Padrão', ["x", 1, 0, 3, 1, 1], [0, 1, 0, 4, 2, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 7, 6, 8], [0, 0, 3, 2, 1, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 7, "x", 8], [0, 0, 2, 1, 0, 3], 'chords-db', [])
      ],
      'Bbalt': [
      P('Padrão', ["x", 1, 2, 3, 3, 0], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('Abertura', [6, 7, 0, 7, 5, 0], [2, 3, 0, 4, 1, 0], 'chords-db', []),
      P('Padrão', [6, 7, 0, 7, "x", 6], [1, 3, 0, 4, 0, 2], 'chords-db', [])
      ],
      'Bbaug': [
      P('Padrão', ["x", 1, 4, 3, 3, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 4, 3, 3, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}]),
      P('Padrão', ["x", "x", 8, 7, 7, 6], [0, 0, 4, 2, 3, 1], 'chords-db', [])
      ],
      'Bbaug7': [
      P('1ª casa (pestana)', ["x", 1, 4, 1, 3, 2], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', [6, "x", 6, 7, 7, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 11, 9, 10], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'Bbaug9': [
      P('Padrão', ["x", 1, 0, 1, 1, 2], [0, 1, 0, 2, 3, 4], 'chords-db', []),
      P('3ª casa (pestana)', [4, 3, 4, 3, 3, 4], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', [6, 5, 6, 5, 7, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 4}])
      ],
      'Bbdim': [
      P('Padrão', ["x", 1, 2, 3, 2, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', []),
      P('Padrão', [6, 4, "x", 6, 5, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 9, "x", 9], [0, 0, 1, 2, 0, 3], 'chords-db', [])
      ],
      'Bbdim7': [
      P('Abertura', ["x", 1, 2, 0, 2, 0], [0, 1, 2, 0, 3, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 3, 2, 3], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 7, 8, 6, 8, 6], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbm': [
      P('1ª casa (pestana)', ["x", 1, 3, 3, 2, 1], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 8, 6, 6, 6], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 8, 6, 6, 6], [0, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Bbm/A': [
      P('Padrão', ["x", 0, 3, 3, 2, 1], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('6ª casa', ["x", 0, 3, 6, 6, 6], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 6, "from": 3, "to": 5}]),
      P('3ª casa (pestana)', [5, 4, 3, 3, 6, 6], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'Bbm/Ab': [
      P('6ª casa (pestana)', ["x", "x", 6, 6, 6, 6], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('Padrão', ["x", 11, 11, 10, 11, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', []),
      P('3ª casa (pestana)', [4, 4, 3, 3, "x", "x"], [2, 3, 1, 1, 0, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Bbm/B': [
      P('6ª casa (pestana)', [7, 8, 8, 6, 6, 6], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 9, 6, 6, 6], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", "x", 9, 10, 11, 9], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'Bbm/C': [
      P('3ª casa (pestana)', ["x", 3, 3, 6, 6, 6], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [8, 8, 8, 6, 6, 6], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 8, 10, 11, 9], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Bbm/C#': [
      P('3ª casa (pestana)', ["x", 4, 3, 3, 6, 6], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa', ["x", 4, 3, 6, 6, 6], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 6, "from": 3, "to": 5}]),
      P('6ª casa (pestana)', [9, 8, 8, 6, 6, 6], [4, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbm/D': [
      P('Padrão', ["x", "x", 0, 3, 2, 1], [0, 0, 0, 3, 2, 1], 'chords-db', []),
      P('6ª casa', ["x", 5, 3, 6, 6, 6], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 6, "from": 3, "to": 5}]),
      P('6ª casa', ["x", "x", 0, 6, 6, 6], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 3, "to": 5}])
      ],
      'Bbm/E': [
      P('1ª casa', [0, 1, 3, 3, 2, 1], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 2, 3, 2, 1], [0, 0, 2, 4, 3, 1], 'chords-db', []),
      P('3ª casa', [0, 4, 3, 3, 6, 6], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Bbm/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 3, 2, 1], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 6, 6, 6], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 6, 6, 9], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Bbm/F': [
      P('1ª casa (pestana)', [1, 1, 3, 3, 2, 1], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 3, 2, 1], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('6ª casa', ["x", "x", 3, 6, 6, 6], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 6, "from": 3, "to": 5}])
      ],
      'Bbm/F#': [
      P('Padrão', ["x", "x", 4, 3, 2, 1], [0, 0, 4, 3, 2, 1], 'chords-db', []),
      P('6ª casa', ["x", "x", 4, 6, 6, 6], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 6, "from": 3, "to": 5}]),
      P('6ª casa (pestana)', ["x", 9, 8, 6, 6, 6], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Bbm/G': [
      P('3ª casa (pestana)', [3, 4, 3, 3, 6, 6], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 4, 3, 6, 6, 6], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('6ª casa', ["x", "x", 5, 6, 6, 6], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 6, "from": 3, "to": 5}])
      ],
      'Bbm11': [
      P('4ª casa (pestana)', [6, 4, 6, 5, 4, 4], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 6, 6, 8], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 8, 8, 9, 9], [0, 0, 1, 1, 2, 3], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Bbm6': [
      P('Padrão', ["x", 1, 3, "x", 2, 3], [0, 1, 3, 0, 2, 4], 'chords-db', []),
      P('Padrão', ["x", 4, 5, 3, 6, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', []),
      P('6ª casa', [6, "x", 5, 6, 6, 6], [2, 0, 1, 3, 3, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbm69': [
      P('6ª casa', [6, "x", 5, 6, 6, 8], [2, 0, 1, 3, 3, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, "x", 8, 6, 8, 8], [1, 0, 2, 1, 3, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [9, "x", 8, 10, 8, 8], [2, 0, 1, 4, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Bbm7': [
      P('Padrão', [5, "x", 5, 5, 5, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('1ª casa (pestana)', ["x", 1, 3, 1, 2, 1], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 3, 3, 2, 4], [0, 0, 2, 3, 1, 4], 'chords-db', [])
      ],
      'Bbm7b5': [
      P('Padrão', ["x", 1, 2, 1, 2, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", "x", 2, 3, 2, 4], [0, 0, 1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('Padrão', [6, "x", 6, 6, 5, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', [])
      ],
      'Bbm9': [
      P('Padrão', ["x", "x", 3, 5, 2, 4], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('4ª casa (pestana)', [6, 4, "x", 5, 6, 4], [3, 1, 0, 2, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 6, 6, 6, 8], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbm9/Ab': [
      P('1ª casa (pestana)', [4, 1, 3, 1, 1, 1], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [4, 1, 3, 3, 1, 1], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 11, 8, 10, 9, 8], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Bbm9/C#': [
      P('8ª casa (pestana)', [9, 8, 8, 10, 9, 8], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [9, "x", 8, 10, 9, 8], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Bbmadd9': [
      P('Padrão', ["x", 4, 3, 3, 1, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('Padrão', [6, 4, "x", 5, 6, "x"], [3, 1, 0, 2, 4, 0], 'chords-db', []),
      P('6ª casa (pestana)', ["x", "x", 8, 6, 6, 8], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Bbmaj11': [
      P('1ª casa (pestana)', ["x", 1, 1, 2, 3, 1], [0, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', [6, "x", 0, 5, 4, 5], [4, 0, 0, 2, 1, 3], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 7, 7, 6, 6], [1, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbmaj13': [
      P('1ª casa (pestana)', ["x", 1, 1, 2, 3, 3], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', [6, 5, 5, 5, 6, 5], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 7, 7, 8, 6], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbmaj7': [
      P('1ª casa (pestana)', ["x", 1, 3, 2, 3, 1], [0, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 3, 5], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 7, 7, 6, 6], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbmaj7#5': [
      P('Padrão', ["x", 1, 0, 2, 3, 2], [0, 1, 0, 2, 4, 3], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 4, 3, 3, 5], [0, 0, 2, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('Padrão', [6, "x", 7, 7, 7, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Bbmaj7b5': [
      P('Padrão', ["x", 1, 2, 2, 3, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 7, 7, 5, 5], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', [6, 7, 7, 7, "x", 0], [1, 2, 3, 4, 0, 0], 'chords-db', [])
      ],
      'Bbmaj7sus2': [
      P('1ª casa (pestana)', ["x", 1, 3, 2, 1, 1], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 8, 5, 6, 5], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 8, 10, 10, 8], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Bbmaj9': [
      P('1ª casa', [1, 1, 0, 2, 1, "x"], [1, 1, 0, 3, 2, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('3ª casa (pestana)', [6, 3, 3, 3, 3, 5], [4, 1, 1, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', [6, 5, 7, 5, 6, "x"], [2, 1, 4, 1, 3, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 4}])
      ],
      'Bbmmaj11': [
      P('1ª casa (pestana)', ["x", 1, 1, 2, 2, 1], [0, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 7, 6, 6, 8], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 8, 8, 10, 9], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Bbmmaj7': [
      P('1ª casa (pestana)', ["x", 1, 3, 2, 2, 1], [0, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 7, 6, 6, 6], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 8, 10, 10, 9], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Bbmmaj7b5': [
      P('Padrão', ["x", 1, 2, 2, 2, 0], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('5ª casa (pestana)', [6, 7, "x", 6, 5, 5], [2, 4, 0, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 7, 7, 6, "x", 6], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbmmaj9': [
      P('5ª casa', [6, 4, "x", 5, 6, 5], [3, 1, 0, 2, 4, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', [6, 4, 7, 5, "x", "x"], [3, 1, 4, 2, 0, 0], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, 7, 6, 6, 8], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbsus': [
      P('1ª casa (pestana)', ["x", 1, 1, 3, 4, 1], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", 1, 3, 3, 4, 1], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 8, 8, 6, 6], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bbsus2': [
      P('1ª casa (pestana)', [1, 1, 3, 3, 1, 1], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [6, 3, 3, 5, 6, "x"], [3, 1, 1, 2, 4, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}]),
      P('8ª casa (pestana)', [8, 8, 8, 10, 11, 8], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Bbsus2sus4': [
      P('[1]ª casa (pestana)', ["x", 1, 1, 3, 1, 1], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('[6]ª casa (pestana)', [6, 6, 8, 8, 6, 8], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('Padrão', [6, 6, 3, 5, "x", "x"], [3, 4, 1, 2, 0, 0], 'chords-db', [])
      ],
      'Bbsus4': [
      P('1ª casa (pestana)', ["x", 1, 3, 3, 4, 1], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 4, 6], [0, 0, 1, 1, 2, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 8, 8, 6, 6], [1, 3, 3, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Bdim': [
      P('Abertura', ["x", 2, 0, "x", 0, 1], [0, 3, 0, 0, 0, 2], 'chords-db', []),
      P('Padrão', ["x", 2, 3, 4, 3, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', []),
      P('Padrão', [7, 5, "x", 7, 6, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', [])
      ],
      'Bdim7': [
      P('1ª casa (pestana)', ["x", 2, 3, 1, 3, 1], [0, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 3, 4, 3, 4], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, "x", 6, 7, 6, "x"], [3, 0, 1, 4, 2, 0], 'chords-db', [])
      ],
      'Bm': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 3, 2], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 9, 7, 7, 7], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 9, 11, 12, 10], [0, 0, 1, 3, 4, 2], 'chords-db', [])
      ],
      'Bm/A': [
      P('Padrão', ["x", 0, 4, 4, 3, 2], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('Abertura', ["x", 0, 0, 4, 0, 2], [0, 0, 0, 3, 0, 1], 'chords-db', []),
      P('Abertura', ["x", 0, 0, 4, 3, 2], [0, 0, 0, 3, 2, 1], 'chords-db', [])
      ],
      'Bm/Ab': [
      P('Padrão', [4, "x", 4, 4, 3, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 5, 4, 4, 7, 7], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 5, 4, 7, 7, 7], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'Bm/Bb': [
      P('Abertura', ["x", 1, 0, 4, 0, 2], [0, 1, 0, 4, 0, 2], 'chords-db', []),
      P('4ª casa (pestana)', [6, 5, 4, 4, 7, 7], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('7ª casa', [6, 5, 4, 7, 7, 7], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 7, "from": 3, "to": 5}])
      ],
      'Bm/C': [
      P('Abertura', ["x", 3, 0, 4, 0, 2], [0, 2, 0, 3, 0, 1], 'chords-db', []),
      P('Padrão', ["x", 3, 0, 4, 3, 2], [0, 2, 0, 4, 3, 1], 'chords-db', []),
      P('7ª casa (pestana)', [8, 9, 9, 7, 7, 7], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bm/C#': [
      P('Abertura', ["x", 4, 0, 4, 0, 2], [0, 3, 0, 4, 0, 1], 'chords-db', []),
      P('Padrão', ["x", 4, 0, 4, 3, 2], [0, 3, 0, 4, 2, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 4, 7, 7, 7], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'Bm/D': [
      P('Abertura', ["x", "x", 0, 4, 0, 2], [0, 0, 0, 3, 0, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 4, 3, 2], [0, 0, 0, 3, 2, 1], 'chords-db', []),
      P('7ª casa', ["x", "x", 0, 4, 7, 7], [0, 0, 0, 1, 4, 4], 'chords-db', [{"fret": 7, "from": 4, "to": 5}])
      ],
      'Bm/E': [
      P('Abertura', [0, 2, 0, 4, 0, 2], [0, 1, 0, 4, 0, 2], 'chords-db', []),
      P('2ª casa', [0, 2, 4, 4, 3, 2], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 2, 4, 3, 2], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'Bm/Eb': [
      P('Padrão', ["x", "x", 1, 4, 3, 2], [0, 0, 1, 4, 3, 2], 'chords-db', []),
      P('7ª casa', ["x", 6, 4, 7, 7, 7], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 7, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 13, 11, 12, 10], [0, 0, 4, 2, 3, 1], 'chords-db', [])
      ],
      'Bm/F': [
      P('Padrão', ["x", "x", 3, 4, 3, 2], [0, 0, 2, 4, 3, 1], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 8, 9, 7, 7, 7], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', ["x", 8, 9, 7, 7, 10], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Bm/F#': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 3, 2], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 4, 3, 2], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('7ª casa', ["x", "x", 4, 7, 7, 7], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 7, "from": 3, "to": 5}])
      ],
      'Bm/G': [
      P('Padrão', ["x", "x", 5, 4, 3, 2], [0, 0, 4, 3, 2, 1], 'chords-db', []),
      P('7ª casa', ["x", "x", 5, 7, 7, 7], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 7, "from": 3, "to": 5}]),
      P('7ª casa (pestana)', ["x", 10, 9, 7, 7, 7], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Bm11': [
      P('Abertura', ["x", 2, 0, 2, 2, 0], [0, 1, 0, 2, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', [7, 5, 7, 6, 5, 5], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 7, 7, 7, 9], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bm6': [
      P('Abertura', [2, 2, 0, 1, 0, 2], [2, 3, 0, 1, 0, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 4, 3, 4], [0, 0, 2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [7, "x", 6, 7, 7, "x"], [2, 0, 1, 3, 4, 0], 'chords-db', [])
      ],
      'Bm69': [
      P('Padrão', ["x", 2, 0, 1, 2, 2], [0, 2, 0, 1, 3, 4], 'chords-db', []),
      P('[6, 7]ª casa', ["x", 5, 6, 6, 7, 7], [0, 1, 2, 2, 3, 3], 'chords-db', [{"fret": 6, "from": 2, "to": 5}, {"fret": 7, "from": 4, "to": 5}]),
      P('[7, 9]ª casa (pestana)', [7, 9, 9, 7, 9, 9], [1, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}, {"fret": 9, "from": 1, "to": 5}])
      ],
      'Bm7': [
      P('Padrão', [7, "x", 7, 7, 7, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 4, 2, 3, 2], [1, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 4, 3, 5], [0, 0, 2, 3, 1, 4], 'chords-db', [])
      ],
      'Bm7b5': [
      P('Padrão', ["x", 2, 3, 2, 3, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('Padrão', [7, "x", 7, 7, 6, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('7ª casa (pestana)', [7, 8, 9, 7, 10, 7], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bm9': [
      P('Padrão', ["x", 2, 0, 2, 2, 2], [0, 1, 0, 2, 3, 4], 'chords-db', []),
      P('4ª casa', ["x", 4, 4, 4, 3, 5], [0, 2, 3, 3, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 7, 7, 7, 9], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bm9/A': [
      P('2ª casa (pestana)', [5, 2, 4, 2, 2, 2], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [5, 2, 4, 4, 2, 2], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', ["x", 12, 9, 11, 10, 9], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Bm9/D': [
      P('9ª casa (pestana)', [10, 9, 9, 11, 10, 9], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', [10, "x", 9, 11, 10, 9], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Bmadd9': [
      P('Padrão', ["x", 5, 4, 4, 2, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('Padrão', [7, 5, 0, 6, 7, "x"], [3, 1, 0, 2, 4, 0], 'chords-db', []),
      P('7ª casa (pestana)', ["x", "x", 9, 7, 7, 9], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 2, "to": 5}])
      ],
      'Bmaj11': [
      P('Abertura', ["x", 2, 1, 3, 0, 0], [0, 2, 1, 3, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 3, 4, 2], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 8, 8, 7, 9], [1, 1, 2, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bmaj13': [
      P('2ª casa (pestana)', ["x", 2, 2, 3, 4, 4], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [7, 6, 6, 6, 7, 6], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 8, 8, 9, 7], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bmaj7': [
      P('2ª casa (pestana)', [2, 2, 4, 3, 4, 2], [1, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 4, 6], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 8, 8, 7, 7], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bmaj7#5': [
      P('Padrão', ["x", 2, 1, 3, 0, 3], [0, 2, 1, 3, 0, 4], 'chords-db', []),
      P('Padrão', ["x", 2, 5, 3, 4, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', []),
      P('Padrão', [7, 6, 8, 0, 8, "x"], [2, 1, 3, 0, 3, 0], 'chords-db', [])
      ],
      'Bmaj7b5': [
      P('Padrão', ["x", 2, 3, 3, 4, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('6ª casa (pestana)', [7, 6, 8, 8, 6, 6], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('Padrão', [7, 8, 8, 8, 0, "x"], [1, 2, 3, 4, 0, 0], 'chords-db', [])
      ],
      'Bmaj7sus2': [
      P('2ª casa (pestana)', ["x", 2, 4, 3, 2, 2], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 9, 6, 7, 6], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", "x", 9, 11, 11, 9], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'Bmaj9': [
      P('2ª casa', [2, 2, 1, 3, 2, "x"], [2, 2, 1, 4, 3, 0], 'chords-db', [{"fret": 2, "from": 0, "to": 4}]),
      P('4ª casa (pestana)', ["x", "x", 4, 6, 4, 6], [0, 0, 1, 3, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('6ª casa', [7, 6, 8, 6, 7, "x"], [2, 1, 4, 1, 3, 0], 'chords-db', [{"fret": 6, "from": 0, "to": 4}])
      ],
      'Bmmaj11': [
      P('Abertura', ["x", 2, 0, 3, 2, 0], [0, 1, 0, 3, 2, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 3, 3, 2], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 8, 7, 7, 9], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bmmaj7': [
      P('Abertura', ["x", 2, 0, 3, 0, 2], [0, 1, 0, 3, 0, 2], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 4, 3, 3, 2], [1, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 8, 7, 7, 7], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bmmaj7b5': [
      P('Padrão', ["x", 2, 3, 3, 3, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('6ª casa (pestana)', [7, 8, "x", 7, 6, 6], [2, 4, 0, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 8, 8, 7, "x", 7], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bmmaj9': [
      P('Padrão', ["x", 2, 0, 3, 2, 2], [0, 1, 0, 4, 2, 3], 'chords-db', []),
      P('Padrão', [7, 5, 8, 6, 0, "x"], [3, 1, 4, 2, 0, 0], 'chords-db', []),
      P('7ª casa (pestana)', [7, 9, 8, 7, 7, 9], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Bsus': [
      P('Abertura', ["x", 2, 4, 4, 0, 0], [0, 1, 3, 4, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 2, 2, 4, 5, 2], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 2, 4, 4, 5, 2], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}])
      ],
      'Bsus2': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 2, 2], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', [7, "x", "x", 6, 7, 7], [2, 0, 0, 1, 3, 4], 'chords-db', []),
      P('9ª casa (pestana)', [9, 9, 9, 11, 12, 9], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Bsus2sus4': [
      P('[2]ª casa (pestana)', ["x", 2, 2, 4, 2, 2], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('[7]ª casa (pestana)', [7, 7, 9, 9, 7, 9], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('Padrão', [7, 7, 4, 6, "x", "x"], [3, 4, 1, 2, 0, 0], 'chords-db', [])
      ],
      'Bsus4': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 5, 2], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 5, 7], [0, 0, 1, 1, 2, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 9, 9, 7, 7], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'C': [
      P('Abertura', ["x", 3, 2, 0, 1, 0], [0, 3, 2, 0, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 5, 5, 5, 3], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('5ª casa', ["x", "x", 5, 5, 5, 8], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'C#': [
      P('1ª casa', ["x", 4, 3, 1, 2, 1], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 6, 6, 6, 4], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa', [9, 8, 6, 6, 6, 9], [3, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#/A': [
      P('1ª casa', ["x", 0, 3, 1, 2, 1], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 3, 1, 2, 4], [0, 0, 3, 1, 2, 4], 'chords-db', []),
      P('Padrão', ["x", 0, 6, 6, 6, 4], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'C#/Ab': [
      P('4ª casa (pestana)', [4, 4, 6, 6, 6, 4], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 6, 6, 4], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('6ª casa (pestana)', ["x", "x", 6, 6, 6, 9], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'C#/B': [
      P('1ª casa (pestana)', ["x", 2, 3, 1, 2, 1], [0, 2, 4, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [7, 8, 6, 6, 6, 9], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [7, 8, 6, 6, 9, 9], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#/Bb': [
      P('1ª casa (pestana)', ["x", 1, 3, 1, 2, 1], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", 1, 3, 1, 2, 4], [0, 1, 3, 1, 2, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 6, 6, 6, 9], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#/C': [
      P('1ª casa (pestana)', ["x", 3, 3, 1, 2, 1], [0, 3, 4, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [8, 8, 6, 6, 6, 9], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [8, 8, 6, 6, 9, 9], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#/D': [
      P('1ª casa', ["x", "x", 0, 1, 2, 1], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 0, 6, 6, 4], [0, 0, 0, 3, 4, 1], 'chords-db', []),
      P('9ª casa', ["x", "x", 0, 10, 9, 9], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 9, "from": 3, "to": 5}])
      ],
      'C#/E': [
      P('1ª casa', [0, 4, 3, 1, 2, 1], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 2, 1, 2, 1], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa', [0, 4, 6, 6, 6, 4], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'C#/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 1, 2, 1], [0, 0, 1, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 6, 6, 9], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('11ª casa (pestana)', [11, 11, 11, 13, 14, 13], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 11, "from": 0, "to": 5}])
      ],
      'C#/F': [
      P('1ª casa (pestana)', [1, 4, 3, 1, 2, 1], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [1, "x", "x", 1, 2, 1], [1, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 3, 1, 2, 1], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}])
      ],
      'C#/F#': [
      P('1ª casa (pestana)', ["x", "x", 4, 1, 2, 1], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 6, 6, 4], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", 9, 11, 10, 9, 9], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'C#/G': [
      P('Padrão', ["x", "x", 5, 6, 6, 4], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('9ª casa (pestana)', ["x", 10, 11, 10, 9, 9], [0, 2, 4, 3, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}]),
      P('6ª casa', [3, 4, 6, 6, 6, "x"], [1, 2, 4, 4, 4, 0], 'chords-db', [{"fret": 6, "from": 2, "to": 4}])
      ],
      'C#11': [
      P('Abertura', ["x", 4, 3, 0, 0, 4], [0, 2, 1, 0, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 5, 4, 6, 4], [0, 1, 2, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [9, 8, 9, 8, 8, 9], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C#13': [
      P('Padrão', ["x", 4, 3, 3, 0, 2], [0, 4, 2, 3, 0, 1], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 4, 6, 6], [1, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('8ª casa', [9, 8, 8, 8, 9, 7], [3, 2, 2, 2, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 4}])
      ],
      'C#5': [
      P('Padrão', [9, 11, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 4, 6, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [9, 11, 11, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'C#6': [
      P('Padrão', ["x", 4, 3, 3, 2, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('6ª casa', ["x", 4, 6, 6, 6, 6], [0, 1, 3, 3, 3, 3], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', [9, 8, 8, 6, 6, 6], [4, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#69': [
      P('1ª casa (pestana)', ["x", 4, 1, 3, 2, 1], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 4, 3, 3, 4, 4], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [9, 8, 8, 8, 9, 9], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C#7': [
      P('Padrão', ["x", 4, 3, 4, 2, "x"], [0, 3, 2, 4, 1, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 6, 4, 6, 4], [0, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [9, 8, 6, 6, 6, 7], [4, 3, 1, 1, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#7#9': [
      P('Padrão', ["x", 4, 3, 4, 2, 0], [0, 3, 2, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", 4, 3, 4, 5, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', []),
      P('9ª casa', ["x", 8, 9, 9, 9, 9], [0, 1, 2, 2, 3, 4], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'C#7b5': [
      P('Abertura', ["x", 4, 3, 0, 0, 1], [0, 4, 3, 0, 0, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 5, 4, 6, "x"], [0, 1, 2, 1, 3, 0], 'chords-db', [{"fret": 4, "from": 1, "to": 4}]),
      P('Padrão', [9, "x", 9, 10, 8, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', [])
      ],
      'C#7b9': [
      P('3ª casa (pestana)', ["x", 4, 3, 4, 3, 4], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 4, 0, 4, 6, 7], [0, 1, 0, 2, 3, 4], 'chords-db', []),
      P('Padrão', [9, 8, 9, 7, 0, "x"], [3, 2, 4, 1, 0, 0], 'chords-db', [])
      ],
      'C#7sus4': [
      P('2ª casa (pestana)', ["x", 4, 4, 4, 2, 2], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 6, 4, 7, 4], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", "x", 6, 7, 7], [0, 0, 0, 1, 2, 3], 'chords-db', [])
      ],
      'C#9': [
      P('4ª casa', [4, 4, 3, 4, 4, 4], [2, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', [9, 8, 9, 8, "x", "x"], [3, 1, 4, 2, 0, 0], 'chords-db', []),
      P('9ª casa (pestana)', [9, 11, 9, 10, 9, 11], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#9#11': [
      P('Abertura', ["x", 3, 2, 0, 0, 3], [0, 2, 1, 0, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 5, 4, 6, 4], [0, 1, 2, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [9, 8, 9, 8, 8, 9], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C#9b5': [
      P('3ª casa (pestana)', ["x", 4, 3, 4, 4, 3], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [9, 8, 9, 8, 8, 9], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('Padrão', [9, 10, "x", 10, 0, 11], [1, 2, 0, 3, 0, 4], 'chords-db', [])
      ],
      'C#add11': [
      P('2ª casa', ["x", 4, 3, 1, 2, 2], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [9, 8, 6, 6, 7, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 6, "from": 0, "to": 4}]),
      P('11ª casa', [9, 8, 11, 11, "x", "x"], [2, 1, 4, 4, 0, 0], 'chords-db', [{"fret": 11, "from": 2, "to": 3}])
      ],
      'C#add9': [
      P('1ª casa (pestana)', ["x", 4, 3, 1, 4, 1], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", 4, 3, "x", 4, 4], [0, 2, 1, 0, 3, 4], 'chords-db', []),
      P('Padrão', [9, 8, "x", 8, 9, "x"], [3, 1, 0, 2, 4, 0], 'chords-db', [])
      ],
      'C#alt': [
      P('Padrão', ["x", 4, 3, 0, 2, 1], [0, 4, 3, 0, 2, 1], 'chords-db', []),
      P('Padrão', ["x", 4, 5, 0, 6, 3], [0, 2, 3, 0, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 4, 5, 6, 6, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'C#aug': [
      P('2ª casa (pestana)', ["x", 4, 4, 4, 2, 2], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 6, 4, 7, 4], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [9, 8, 7, 6, 6, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 6, "from": 0, "to": 4}])
      ],
      'C#aug7': [
      P('Padrão', ["x", 4, 3, 2, 0, 1], [0, 4, 3, 2, 0, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 7, 4, 6, 5], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', [9, 8, 7, "x", 0, 7], [4, 3, 1, 0, 0, 2], 'chords-db', [])
      ],
      'C#aug9': [
      P('4ª casa', ["x", 4, 3, 4, 4, 5], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', [9, 8, 7, 8, 0, "x"], [4, 2, 1, 3, 0, 0], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 9, 8, 10, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 8, "from": 0, "to": 4}])
      ],
      'C#dim': [
      P('Padrão', ["x", 4, 2, "x", 2, 3], [0, 4, 1, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 4, 5, 6, 5, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', []),
      P('Padrão', [9, 7, "x", 9, 8, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', [])
      ],
      'C#dim7': [
      P('Padrão', ["x", "x", 2, 3, 2, 3], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 4, 5, 3, 5, 3], [0, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa', [9, "x", 8, 9, 8, "x"], [2, 0, 1, 3, 1, 0], 'chords-db', [{"fret": 8, "from": 0, "to": 4}])
      ],
      'C#m': [
      P('Padrão', ["x", 4, 2, 1, 2, "x"], [0, 4, 2, 1, 3, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 6, 6, 5, 4], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa', [9, 7, 6, 6, "x", 9], [3, 2, 1, 1, 0, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#m/A': [
      P('Abertura', ["x", 0, 2, 1, 2, 0], [0, 0, 2, 1, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 0, 6, 6, 5, 4], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 7, 6, 5, 4], [0, 0, 4, 3, 2, 1], 'chords-db', [])
      ],
      'C#m/Ab': [
      P('4ª casa (pestana)', [4, 4, 6, 6, 5, 4], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 6, 5, 4], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('9ª casa', ["x", "x", 6, 9, 9, 9], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 9, "from": 3, "to": 5}])
      ],
      'C#m/B': [
      P('Padrão', ["x", 2, 2, 1, 2, 0], [0, 2, 3, 1, 4, 0], 'chords-db', []),
      P('9ª casa (pestana)', ["x", "x", 9, 9, 9, 9], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}]),
      P('Padrão', ["x", 2, 2, 1, 2, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', [])
      ],
      'C#m/Bb': [
      P('Padrão', ["x", 1, 2, 1, 2, 0], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('6ª casa (pestana)', [6, 7, 6, 6, 9, 9], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 7, 6, 9, 9, 9], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C#m/C': [
      P('Padrão', ["x", 3, 2, 1, 2, 0], [0, 4, 2, 1, 3, 0], 'chords-db', []),
      P('6ª casa (pestana)', [8, 7, 6, 6, 9, 9], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('9ª casa', [8, 7, 6, 9, 9, 9], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 9, "from": 3, "to": 5}])
      ],
      'C#m/D': [
      P('Abertura', ["x", "x", 0, 1, 2, 0], [0, 0, 0, 1, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 6, 5, 4], [0, 0, 0, 3, 2, 1], 'chords-db', []),
      P('9ª casa', ["x", "x", 0, 9, 9, 9], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 3, "to": 5}])
      ],
      'C#m/E': [
      P('Padrão', ["x", "x", 2, 1, 2, 0], [0, 0, 2, 1, 3, 0], 'chords-db', []),
      P('4ª casa', [0, 4, 6, 6, 5, 4], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa', [0, 7, 6, 6, 9, 9], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'C#m/Eb': [
      P('Padrão', ["x", "x", 1, 1, 2, 0], [0, 0, 1, 2, 3, 0], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 6, 9, 9, 9], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [11, 11, 11, 9, 9, 9], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#m/F': [
      P('Padrão', ["x", "x", 3, 1, 2, 0], [0, 0, 3, 1, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 6, 5, 4], [0, 0, 1, 4, 3, 2], 'chords-db', []),
      P('9ª casa', ["x", 8, 6, 9, 9, 9], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 9, "from": 3, "to": 5}])
      ],
      'C#m/F#': [
      P('Padrão', ["x", "x", 4, 1, 2, 0], [0, 0, 4, 1, 2, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", "x", 4, 6, 5, 4], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", 9, 11, 9, 9, 9], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'C#m/G': [
      P('Padrão', ["x", "x", 5, 6, 5, 4], [0, 0, 2, 4, 3, 1], 'chords-db', []),
      P('9ª casa (pestana)', ["x", 10, 11, 9, 9, 9], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', ["x", 10, 11, 9, 9, 12], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'C#m11': [
      P('2ª casa (pestana)', ["x", 4, 2, 4, 2, 2], [0, 2, 1, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [9, 7, 9, 8, 7, 7], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 9, 9, 9, 11], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#m6': [
      P('2ª casa (pestana)', ["x", 4, 2, 3, 2, 4], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 6, 6, 5, 6], [0, 0, 2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [9, "x", 8, 9, 9, "x"], [2, 0, 1, 3, 4, 0], 'chords-db', [])
      ],
      'C#m69': [
      P('Padrão', ["x", 4, 1, 3, 2, 0], [0, 4, 1, 3, 2, 0], 'chords-db', []),
      P('Padrão', ["x", 4, 2, 3, 4, "x"], [0, 3, 1, 2, 4, 0], 'chords-db', []),
      P('Padrão', [9, 7, 8, 8, "x", 0], [4, 1, 2, 3, 0, 0], 'chords-db', [])
      ],
      'C#m7': [
      P('Padrão', [9, "x", 9, 9, 9, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 6, 4, 5, 4], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 6, 6, 5, 7], [0, 0, 2, 3, 1, 4], 'chords-db', [])
      ],
      'C#m7b5': [
      P('Padrão', ["x", 4, 5, 4, 5, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", "x", 5, 6, 5, 7], [0, 0, 1, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('Padrão', [9, "x", 9, 9, 8, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', [])
      ],
      'C#m9': [
      P('4ª casa', ["x", 4, 2, 4, 4, 4], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa', ["x", 6, 6, 6, 5, 7], [0, 2, 2, 3, 1, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('9ª casa', ["x", 7, 9, 8, 9, 9], [0, 1, 3, 2, 4, 4], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'C#m9/B': [
      P('4ª casa (pestana)', [7, 4, 6, 4, 4, 4], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [7, 4, 6, 6, 4, 4], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('11ª casa (pestana)', ["x", 14, 11, 13, 12, 11], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 11, "from": 1, "to": 5}])
      ],
      'C#m9/E': [
      P('11ª casa (pestana)', [12, 11, 11, 13, 12, 11], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 5}]),
      P('11ª casa (pestana)', [12, "x", 11, 13, 12, 11], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 5}])
      ],
      'C#madd9': [
      P('Padrão', ["x", 4, 2, 1, 4, "x"], [0, 3, 2, 1, 4, 0], 'chords-db', []),
      P('Padrão', ["x", 4, 6, 6, 4, 0], [0, 1, 3, 4, 2, 0], 'chords-db', []),
      P('Padrão', [9, 7, "x", 8, 9, 0], [3, 1, 0, 2, 4, 0], 'chords-db', [])
      ],
      'C#maj11': [
      P('2ª casa (pestana)', ["x", 4, 3, 5, 2, 2], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 4, 5, 6, 4], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', [9, 8, "x", "x", 7, 8], [4, 2, 0, 0, 1, 3], 'chords-db', [])
      ],
      'C#maj13': [
      P('Padrão', ["x", 4, 1, 3, 1, 1], [0, 4, 2, 3, 0, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 4, 5, 6, 6], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [9, 8, 8, 8, 9, 8], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C#maj7': [
      P('1ª casa (pestana)', ["x", 4, 3, 1, 1, 1], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 6, 5, 6, 4], [1, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa', ["x", "x", "x", 6, 6, 8], [0, 0, 0, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 3, "to": 5}])
      ],
      'C#maj7#5': [
      P('1ª casa (pestana)', [1, 4, 3, 2, 1, 1], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", 4, 7, 5, 6, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 11, 10, 10, 8], [0, 0, 4, 2, 3, 1], 'chords-db', [])
      ],
      'C#maj7b5': [
      P('3ª casa (pestana)', ["x", 4, 3, 5, 6, 3], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 4, 5, 5, 6, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 10, 10, 8, 8], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C#maj7sus2': [
      P('4ª casa (pestana)', ["x", 4, 6, 5, 4, 4], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 11, 8, 9, 8], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", "x", 11, 13, 13, 11], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 11, "from": 2, "to": 5}])
      ],
      'C#maj9': [
      P('1ª casa (pestana)', ["x", 4, 1, 1, 1, 1], [0, 4, 1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", 4, 3, 5, 4, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 10, 8, 9, 8], [2, 1, 4, 1, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C#mmaj11': [
      P('2ª casa (pestana)', ["x", 4, 2, 5, 4, 2], [0, 3, 1, 4, 3, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 4, 5, 5, 4], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 10, 9, 9, 11], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#mmaj7': [
      P('1ª casa', ["x", 4, 2, 1, 1, "x"], [0, 4, 2, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 1, "to": 4}]),
      P('4ª casa (pestana)', [4, 4, 6, 5, 5, 4], [1, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', [9, 11, 10, 9, 9, 9], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#mmaj7b5': [
      P('Abertura', ["x", 4, 2, 0, 1, 0], [0, 4, 2, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", 4, 5, 5, 5, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('9ª casa (pestana)', [9, 10, 10, 9, "x", 9], [1, 2, 2, 1, 0, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#mmaj9': [
      P('1ª casa (pestana)', ["x", 4, 1, 1, 1, 0], [0, 4, 1, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 1, "to": 4}]),
      P('Padrão', ["x", 4, 2, 5, 4, 0], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('4ª casa', [4, 4, 6, 5, 4, 0], [1, 1, 4, 3, 2, 0], 'chords-db', [{"fret": 4, "from": 0, "to": 4}])
      ],
      'C#sus': [
      P('4ª casa (pestana)', ["x", 4, 4, 6, 7, 4], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 6, 6, 7, 4], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 11, 11, 9, 9], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#sus2': [
      P('4ª casa (pestana)', [4, 4, 6, 6, 4, 4], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [9, 6, 6, 8, 9, "x"], [0, 1, 0, 0, 2, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 4}]),
      P('9ª casa (pestana)', [9, 11, 11, "x", 9, 11], [1, 2, 3, 0, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#sus2sus4': [
      P('[4]ª casa (pestana)', ["x", 4, 4, 6, 4, 4], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('[9]ª casa (pestana)', [9, 9, 11, 11, 9, 11], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'C#sus4': [
      P('Padrão', ["x", 4, 4, 1, 2, "x"], [0, 3, 4, 1, 2, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 6, 6, 7, 4], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', [9, "x", 6, 6, 7, 9], [2, 3, 0, 0, 1, 4], 'chords-db', [])
      ],
      'C/A': [
      P('Abertura', ["x", 0, 2, 0, 1, 0], [0, 0, 2, 0, 1, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 0, 1, 3], [0, 0, 2, 0, 1, 3], 'chords-db', []),
      P('Padrão', ["x", 0, 5, 5, 5, 3], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'C/Ab': [
      P('Abertura', [4, 3, 2, 0, 1, 0], [4, 3, 2, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 5, 5, 3], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 9, 8, 8], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'C/B': [
      P('Abertura', ["x", 2, 2, 0, 1, 0], [0, 2, 3, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", 2, 2, 0, 1, 3], [0, 2, 3, 0, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [7, 7, 5, 5, 5, 8], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'C/Bb': [
      P('Abertura', ["x", 1, 2, 0, 1, 0], [0, 1, 3, 0, 2, 0], 'chords-db', []),
      P('Padrão', ["x", 1, 2, 0, 1, 3], [0, 1, 3, 0, 2, 4], 'chords-db', []),
      P('5ª casa (pestana)', [6, 7, 5, 5, 5, 8], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'C/C#': [
      P('Abertura', ["x", 4, 2, 0, 1, 0], [0, 4, 2, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", 4, 2, 0, 1, 3], [0, 4, 2, 0, 1, 3], 'chords-db', []),
      P('8ª casa (pestana)', ["x", "x", 11, 9, 8, 8], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'C/D': [
      P('Abertura', ["x", "x", 0, 0, 1, 0], [0, 0, 0, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 5, 5, 3], [0, 0, 0, 3, 4, 1], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 5, 5, 5, 5, 8], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'C/E': [
      P('Abertura', [0, 3, 2, 0, 1, 0], [0, 3, 2, 0, 1, 0], 'chords-db', []),
      P('Abertura', [0, 3, 2, 0, 1, 3], [0, 3, 2, 0, 1, 4], 'chords-db', []),
      P('Abertura', ["x", "x", 2, 0, 1, 0], [0, 0, 2, 0, 1, 0], 'chords-db', [])
      ],
      'C/Eb': [
      P('Abertura', ["x", "x", 1, 0, 1, 0], [0, 0, 1, 0, 2, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 5, 5, 5, 8], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 6, 5, 5, 5, "x"], [0, 2, 1, 1, 1, 0], 'chords-db', [{"fret": 5, "from": 1, "to": 4}])
      ],
      'C/F': [
      P('Abertura', ["x", "x", 3, 0, 1, 0], [0, 0, 3, 0, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 3, 5, 5, 3], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 10, 9, 8, 8], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'C/F#': [
      P('Abertura', [2, 3, 2, 0, 1, 0], [2, 4, 3, 0, 1, 0], 'chords-db', []),
      P('Abertura', ["x", "x", 4, 0, 1, 0], [0, 0, 4, 0, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 5, 5, 3], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'C/G': [
      P('Abertura', [3, 3, 2, 0, 1, 0], [3, 4, 2, 0, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 5, 5, 3], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 5, 5, 3], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'C11': [
      P('1ª casa (pestana)', ["x", 3, 2, 3, 1, 1], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 3, 5, 3], [0, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa', [8, 7, 0, 0, 6, 6], [3, 2, 0, 0, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'C13': [
      P('5ª casa', ["x", 3, 2, 3, 5, 5], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 5, "from": 4, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 3, 3, 5, 5], [1, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('7ª casa', [8, 7, 7, 7, 8, 6], [3, 2, 2, 2, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 4}])
      ],
      'C5': [
      P('Padrão', [8, 10, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 3, 5, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [8, 10, 10, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'C6': [
      P('Padrão', ["x", 3, 2, 2, 1, 0], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('5ª casa', ["x", 3, 5, 5, 5, 5], [0, 1, 3, 3, 3, 4], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('Padrão', [8, "x", 7, 9, 8, "x"], [2, 0, 1, 4, 3, 0], 'chords-db', [])
      ],
      'C69': [
      P('2ª casa (pestana)', ["x", 3, 2, 2, 3, 3], [0, 3, 1, 1, 3, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Abertura', ["x", 3, 0, 0, 5, 5], [0, 1, 0, 0, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 7, 7, 8, 8], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'C7': [
      P('Padrão', ["x", 3, 2, 3, 1, 0], [0, 3, 2, 4, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 5, 3, 5, 3], [0, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 5, 5, 5, 6], [0, 0, 1, 1, 1, 2], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'C7#9': [
      P('Padrão', ["x", 3, 2, 3, 4, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', []),
      P('3ª casa', ["x", 3, 5, 3, 4, 0], [0, 1, 3, 1, 2, 0], 'chords-db', [{"fret": 3, "from": 1, "to": 4}]),
      P('8ª casa (pestana)', [8, 10, 8, 9, 8, 11], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C7/G': [
      P('Padrão', [3, 3, 2, 3, "x", "x"], [2, 3, 1, 4, 0, 0], 'chords-db', []),
      P('Abertura', [3, 1, 2, 0, 1, 0], [4, 2, 3, 0, 1, 0], 'chords-db', []),
      P('3ª casa', [3, 3, 5, 3, 5, 3], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'C7b5': [
      P('Padrão', ["x", "x", 2, 3, 1, 2], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('3ª casa', ["x", 3, 4, 3, 5, "x"], [0, 1, 2, 1, 3, 0], 'chords-db', [{"fret": 3, "from": 1, "to": 4}]),
      P('Padrão', [8, "x", 8, 9, 7, 0], [2, 0, 3, 4, 1, 0], 'chords-db', [])
      ],
      'C7b9': [
      P('2ª casa (pestana)', ["x", 3, 2, 3, 2, 3], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', [8, 7, 8, 6, "x", "x"], [3, 2, 4, 1, 0, 0], 'chords-db', []),
      P('8ª casa (pestana)', [8, "x", 8, 9, 8, 9], [1, 0, 1, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'C7sus4': [
      P('1ª casa (pestana)', ["x", 3, 3, 3, 1, 1], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 5, 3, 6, 3], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 5, 5, 6, 6], [0, 0, 1, 1, 2, 3], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'C9': [
      P('Abertura', [0, 3, 2, 0, 3, 0], [0, 2, 3, 0, 4, 0], 'chords-db', []),
      P('3ª casa', [3, 3, 2, 3, 3, 3], [2, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [8, 7, 8, 7, 8, 8], [2, 1, 3, 1, 4, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'C9#11': [
      P('2ª casa (pestana)', ["x", 3, 2, 3, 3, 2], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 4, 3, 5, 3], [0, 1, 2, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [8, 7, 8, 7, 7, 8], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'C9b5': [
      P('2ª casa (pestana)', ["x", 3, 2, 3, 3, 2], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", 3, 4, 3, 3, 0], [0, 1, 4, 2, 3, 0], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 8, 7, 7, 8], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Cadd11': [
      P('1ª casa', ["x", 3, 2, 0, 1, 1], [0, 3, 2, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', [8, 7, 5, 5, 6, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 4}]),
      P('10ª casa', [8, 7, 10, 10, "x", "x"], [2, 1, 4, 4, 0, 0], 'chords-db', [{"fret": 10, "from": 2, "to": 3}])
      ],
      'Cadd9': [
      P('Abertura', ["x", 3, 2, 0, 3, 0], [0, 2, 1, 0, 3, 0], 'chords-db', []),
      P('Abertura', ["x", 3, 0, 0, 3, 0], [0, 1, 0, 0, 3, 0], 'chords-db', []),
      P('Abertura', [8, 7, 0, 0, 8, 0], [2, 1, 0, 0, 3, 0], 'chords-db', [])
      ],
      'Calt': [
      P('2ª casa (pestana)', ["x", 3, 2, 5, 5, 2], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", 3, 4, 5, 5, 0], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 10, 9, 7, 8], [0, 0, 4, 3, 1, 2], 'chords-db', [])
      ],
      'Caug': [
      P('1ª casa', ["x", 3, 2, 1, 1, "x"], [0, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 1, "to": 4}]),
      P('Padrão', ["x", 3, 6, 5, 5, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', []),
      P('5ª casa', [8, 7, 6, 5, 5, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 4}])
      ],
      'Caug7': [
      P('Padrão', ["x", 3, 2, 3, "x", 4], [0, 2, 1, 3, 0, 4], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 6, 3, 5, 4], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', [8, "x", 8, 9, 9, 0], [1, 0, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Caug9': [
      P('3ª casa', ["x", 3, 2, 3, 3, 4], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 3, 0, 3, 5, 4], [0, 1, 0, 2, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 6, 5, 5, 6], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Cdim': [
      P('Padrão', ["x", 3, 1, "x", 1, 2], [0, 4, 1, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 3, 4, 5, 4, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', []),
      P('Padrão', [8, 6, "x", 8, 7, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', [])
      ],
      'Cdim7': [
      P('Padrão', ["x", "x", 1, 2, 1, 2], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 3, 4, 2, 4, 2], [0, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa', [8, "x", 7, 8, 7, "x"], [2, 0, 1, 3, 1, 0], 'chords-db', [{"fret": 7, "from": 0, "to": 4}])
      ],
      'Cm': [
      P('Padrão', ["x", 3, 1, 0, 1, 3], [0, 3, 2, 0, 1, 4], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 5, 4, 3], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa', [8, 6, 5, 5, "x", "x"], [4, 2, 1, 1, 0, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Cm/A': [
      P('Abertura', ["x", 0, 1, 0, 1, 3], [0, 0, 1, 0, 2, 4], 'chords-db', []),
      P('Padrão', ["x", 0, 5, 5, 4, 3], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('8ª casa', ["x", 0, 5, 8, 8, 8], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 8, "from": 3, "to": 5}])
      ],
      'Cm/Ab': [
      P('Padrão', ["x", "x", 6, 5, 4, 3], [0, 0, 4, 3, 2, 1], 'chords-db', []),
      P('8ª casa', ["x", "x", 6, 8, 8, 8], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 8, "from": 3, "to": 5}]),
      P('8ª casa (pestana)', ["x", 11, 10, 8, 8, 8], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Cm/B': [
      P('Padrão', ["x", 2, 1, 0, 1, 3], [0, 3, 1, 0, 2, 4], 'chords-db', []),
      P('5ª casa (pestana)', [7, 6, 5, 5, 8, 8], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('8ª casa', [7, 6, 5, 8, 8, 8], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 8, "from": 3, "to": 5}])
      ],
      'Cm/Bb': [
      P('8ª casa (pestana)', ["x", "x", 8, 8, 8, 8], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}]),
      P('Padrão', ["x", 1, 1, 0, 1, "x"], [0, 1, 2, 0, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', [6, 6, 5, 5, "x", "x"], [2, 3, 1, 1, 0, 0], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Cm/C#': [
      P('8ª casa (pestana)', [9, 10, 10, 8, 8, 8], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 11, 8, 8, 8], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", "x", 11, 12, 13, 11], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 11, "from": 2, "to": 5}])
      ],
      'Cm/D': [
      P('Padrão', ["x", "x", 0, 5, 4, 3], [0, 0, 0, 3, 2, 1], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 5, 5, 8, 8, 8], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('8ª casa', ["x", "x", 0, 8, 8, 8], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 3, "to": 5}])
      ],
      'Cm/E': [
      P('Padrão', ["x", "x", 2, 5, 4, 3], [0, 0, 1, 4, 3, 2], 'chords-db', []),
      P('3ª casa', [0, 3, 5, 5, 4, 3], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('5ª casa', [0, 6, 5, 5, 8, 8], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Cm/Eb': [
      P('Padrão', ["x", "x", 1, 0, 1, 3], [0, 0, 1, 0, 2, 4], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 5, 5, 8, 8], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('8ª casa', ["x", 6, 5, 8, 8, 8], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 8, "from": 3, "to": 5}])
      ],
      'Cm/F': [
      P('3ª casa (pestana)', ["x", "x", 3, 5, 4, 3], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 10, 8, 8, 8], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 10, 8, 8, 11], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Cm/F#': [
      P('Padrão', ["x", "x", 4, 5, 4, 3], [0, 0, 2, 4, 3, 1], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 9, 10, 8, 8, 8], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", 9, 10, 8, 8, 11], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Cm/G': [
      P('3ª casa (pestana)', [3, 3, 5, 5, 4, 3], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 5, 4, 3], [0, 0, 3, 4, 2, 1], 'chords-db', []),
      P('8ª casa', ["x", "x", 5, 8, 8, 8], [0, 0, 1, 4, 4, 4], 'chords-db', [{"fret": 8, "from": 3, "to": 5}])
      ],
      'Cm11': [
      P('1ª casa (pestana)', ["x", 3, 1, 3, 3, 1], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 3, 4, 3], [0, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [8, 6, 8, 7, 6, 6], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Cm6': [
      P('1ª casa (pestana)', ["x", 3, 1, 2, 1, 3], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", 3, 5, "x", 4, 5], [0, 1, 3, 0, 2, 4], 'chords-db', []),
      P('8ª casa', [8, "x", 7, 8, 8, 8], [2, 0, 1, 3, 3, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Cm69': [
      P('3ª casa', ["x", 3, 1, 2, 3, 3], [0, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Abertura', ["x", 3, 0, 0, 4, 5], [0, 1, 0, 0, 2, 4], 'chords-db', []),
      P('Padrão', [8, 6, 7, 7, "x", "x"], [4, 1, 2, 3, 0, 0], 'chords-db', [])
      ],
      'Cm7': [
      P('Padrão', [8, "x", 8, 8, 8, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 3, 1, 3, 4, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 3, 4, 3], [1, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'Cm7b5': [
      P('Padrão', ["x", 3, 4, 3, 4, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", "x", 4, 5, 4, 6], [0, 0, 1, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', [8, 9, 10, 8, 11, 8], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Cm9': [
      P('3ª casa', ["x", 3, 1, 3, 3, 3], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 3, 0, 3, 4, 3], [0, 1, 0, 2, 4, 3], 'chords-db', []),
      P('8ª casa', ["x", 6, 8, 7, 8, 8], [0, 1, 3, 2, 4, 4], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Cm9/Bb': [
      P('3ª casa (pestana)', [6, 3, 5, 3, 3, 3], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [6, 3, 5, 5, 3, 3], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('10ª casa (pestana)', ["x", 13, 10, 12, 11, 10], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'Cm9/Eb': [
      P('10ª casa (pestana)', [11, 10, 10, 12, 11, 10], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 5}]),
      P('10ª casa (pestana)', [11, "x", 10, 12, 11, 10], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 5}])
      ],
      'Cmadd9': [
      P('Padrão', ["x", 3, 1, 0, 3, 3], [0, 2, 1, 0, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 3, 0, 5, 4, 3], [0, 1, 0, 4, 3, 2], 'chords-db', []),
      P('8ª casa', [8, 6, 0, 7, 8, 8], [3, 1, 0, 2, 4, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Cmaj11': [
      P('Abertura', ["x", 3, 2, 0, 0, 1], [0, 3, 2, 0, 0, 1], 'chords-db', []),
      P('3ª casa', ["x", 3, 3, 0, 0, 0], [0, 1, 1, 0, 0, 0], 'chords-db', [{"fret": 3, "from": 1, "to": 2}]),
      P('Abertura', [8, 7, 9, 0, 6, 0], [3, 2, 4, 0, 1, 0], 'chords-db', [])
      ],
      'Cmaj13': [
      P('Padrão', ["x", 3, 2, 2, 0, 1], [0, 4, 2, 3, 0, 1], 'chords-db', []),
      P('3ª casa', ["x", 3, 3, 4, 5, 5], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [8, 7, 7, 7, 8, 7], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Cmaj7': [
      P('Abertura', [3, 3, 2, 0, 0, 0], [2, 3, 1, 0, 0, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 4, 5, 3], [1, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 5, 5, 5, 7], [0, 0, 1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'Cmaj7#5': [
      P('Abertura', ["x", 3, 2, 1, 0, 0], [0, 3, 2, 1, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 3, 6, 4, 5, 0], [0, 1, 4, 2, 3, 0], 'chords-db', []),
      P('Abertura', [8, 7, 6, 5, 0, 0], [4, 3, 2, 1, 0, 0], 'chords-db', [])
      ],
      'Cmaj7b5': [
      P('Padrão', ["x", 3, 2, 4, 0, 2], [0, 3, 1, 4, 0, 2], 'chords-db', []),
      P('Padrão', ["x", 3, 4, 4, 5, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 9, 9, 7, 7], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Cmaj7sus2': [
      P('Padrão', ["x", 3, 0, 4, 1, 3], [0, 2, 0, 4, 1, 3], 'chords-db', []),
      P('Abertura', ["x", 3, 0, 0, 0, 3], [0, 1, 0, 0, 0, 2], 'chords-db', []),
      P('Abertura', ["x", 3, 0, 4, 0, 3], [0, 1, 0, 3, 0, 2], 'chords-db', [])
      ],
      'Cmaj9': [
      P('Abertura', ["x", 3, 0, 0, 0, 0], [0, 3, 0, 0, 0, 0], 'chords-db', []),
      P('3ª casa', [3, 3, 2, 4, 3, "x"], [2, 2, 1, 4, 3, 0], 'chords-db', [{"fret": 3, "from": 0, "to": 4}]),
      P('5ª casa (pestana)', [0, 5, 5, 5, 5, 7], [0, 1, 1, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Cmmaj11': [
      P('Abertura', ["x", 3, 1, 0, 0, 1], [0, 3, 1, 0, 0, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 3, 4, 4, 3], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 9, 8, 8, 10], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Cmmaj7': [
      P('Abertura', ["x", 3, 1, 0, 0, "x"], [0, 3, 1, 0, 0, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 4, 4, 3], [1, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 10, 9, 8, 8, 8], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Cmmaj7b5': [
      P('Padrão', ["x", 3, "x", 4, 4, 2], [0, 2, 0, 3, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 3, 4, 4, 4, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('8ª casa (pestana)', [8, 9, 9, 8, "x", 8], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Cmmaj9': [
      P('Padrão', ["x", 3, 1, 4, 3, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 3, 0, 4, 4, 3], [0, 1, 0, 3, 4, 2], 'chords-db', []),
      P('Padrão', [8, 6, "x", 7, 0, 8], [3, 1, 0, 2, 0, 4], 'chords-db', [])
      ],
      'Csus': [
      P('1ª casa', ["x", 3, 3, 0, 1, 1], [0, 3, 4, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", 3, 3, 0, 1, 3], [0, 2, 3, 0, 1, 4], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 3, 5, 6, 3], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Csus2': [
      P('Abertura', ["x", 3, 0, 0, 1, 3], [0, 3, 0, 0, 1, 4], 'chords-db', []),
      P('Abertura', ["x", 3, 0, 0, 3, 3], [0, 1, 0, 0, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 5, 3, 3], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'Csus2sus4': [
      P('Padrão', ["x", 3, 3, 0, 3, 3], [0, 1, 2, 0, 3, 4], 'chords-db', []),
      P('[1]ª casa', ["x", 3, 0, 0, 1, 1], [0, 3, 0, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('[3]ª casa (pestana)', ["x", 3, 3, 5, 3, 3], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Csus4': [
      P('1ª casa', ["x", 3, 3, 0, 1, 1], [0, 3, 4, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 5, 5, 6, 3], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', [8, 8, "x", 0, 6, 8], [2, 3, 0, 0, 1, 4], 'chords-db', [])
      ],
      'D': [
      P('Padrão', ["x", "x", 0, 2, 3, 2], [0, 0, 0, 1, 3, 2], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 5, 4, 2, 3, 2], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 7, 7, 7, 5], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'D/A': [
      P('2ª casa', ["x", 0, 0, 2, 3, 2], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('2ª casa', ["x", 0, 4, 2, 3, 2], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 4, 2, 3, 5], [0, 0, 3, 1, 2, 4], 'chords-db', [])
      ],
      'D/Ab': [
      P('2ª casa', [4, 0, 0, 2, 3, 2], [3, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa', [4, 0, 4, 2, 3, 2], [3, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 7, 7, 5], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'D/B': [
      P('2ª casa (pestana)', ["x", 2, 4, 2, 3, 2], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 2, 4, 2, 3, 5], [0, 1, 3, 1, 2, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [7, 9, 7, 7, 7, 10], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'D/Bb': [
      P('Padrão', ["x", 1, 0, 2, 3, 2], [0, 1, 0, 2, 4, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 7, 7, 5], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 11, 10, 10], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'D/C': [
      P('2ª casa', ["x", 3, 0, 2, 3, 2], [0, 2, 0, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 3, 4, 2, 3, 2], [0, 2, 4, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [8, 9, 7, 7, 7, 10], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'D/C#': [
      P('2ª casa', ["x", 4, 0, 2, 3, 2], [0, 3, 0, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 4, 4, 2, 3, 2], [0, 3, 4, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [9, 9, 7, 7, 7, 10], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'D/E': [
      P('2ª casa', [0, 0, 0, 2, 3, 2], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('2ª casa', [0, 0, 4, 2, 3, 2], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('2ª casa', [0, 5, 4, 2, 3, 2], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}])
      ],
      'D/Eb': [
      P('Padrão', ["x", "x", 1, 2, 3, 2], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('10ª casa (pestana)', ["x", "x", 13, 11, 10, 10], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}]),
      P('7ª casa', ["x", 6, 7, 7, 7, "x"], [0, 1, 2, 2, 2, 0], 'chords-db', [{"fret": 7, "from": 2, "to": 4}])
      ],
      'D/F': [
      P('Abertura', [1, 0, 0, 2, 3, 2], [1, 0, 0, 2, 4, 3], 'chords-db', []),
      P('2ª casa (pestana)', ["x", "x", 3, 2, 3, 2], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', ["x", 8, 7, 7, 7, 10], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'D/F#': [
      P('2ª casa (pestana)', [2, 5, 4, 2, 3, 2], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [2, "x", "x", 2, 3, 2], [1, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 4, 2, 3, 2], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'D/G': [
      P('2ª casa', [3, 0, 0, 2, 3, 2], [2, 0, 0, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa', [3, 0, 4, 2, 3, 2], [2, 0, 4, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 5, 2, 3, 2], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'D11': [
      P('Abertura', ["x", "x", 0, 0, 1, 2], [0, 0, 0, 0, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 5, 4, 5, 3, 3], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 5, 7, 5], [0, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'D13': [
      P('Padrão', ["x", "x", 0, 4, 1, 2], [0, 0, 0, 4, 1, 2], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 5, 7, 7], [1, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Abertura', [10, 9, 0, 9, 0, 8], [4, 2, 0, 3, 0, 1], 'chords-db', [])
      ],
      'D5': [
      P('Padrão', [10, 12, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 5, 7, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [10, 12, 12, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'D6': [
      P('Abertura', ["x", "x", 0, 2, 0, 2], [0, 0, 0, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 5, 4, 4, 3, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('7ª casa', ["x", 5, 7, 7, 7, 7], [0, 1, 3, 3, 3, 4], 'chords-db', [{"fret": 7, "from": 2, "to": 5}])
      ],
      'D69': [
      P('Abertura', ["x", 5, 4, 2, 0, 0], [0, 4, 3, 1, 0, 0], 'chords-db', []),
      P('4ª casa', ["x", 5, 4, 4, 5, 5], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [10, 9, 9, 9, 10, 10], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'D7': [
      P('Padrão', ["x", "x", 0, 2, 1, 2], [0, 0, 0, 2, 1, 3], 'chords-db', []),
      P('Padrão', ["x", 5, 4, 5, 3, "x"], [0, 3, 2, 4, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 7, 5, 7, 5], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'D7#9': [
      P('Padrão', ["x", 5, 4, 5, 6, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', []),
      P('Abertura', [0, 0, 0, 10, 7, 8], [0, 0, 0, 4, 1, 2], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 8, 7, 7, 7, 8], [0, 2, 1, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'D7b5': [
      P('1ª casa', ["x", "x", 0, 1, 1, 2], [0, 0, 0, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 3, 4], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('5ª casa', ["x", 5, 6, 5, 7, "x"], [0, 1, 2, 1, 3, 0], 'chords-db', [{"fret": 5, "from": 1, "to": 4}])
      ],
      'D7b9': [
      P('Padrão', ["x", "x", 0, 5, 4, 2], [0, 0, 0, 4, 3, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 5, 4, 5, 4, 5], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('5ª casa', ["x", 6, 0, 5, 7, 5], [0, 2, 0, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'D7sus4': [
      P('Padrão', ["x", "x", 0, 2, 1, 3], [0, 0, 0, 2, 1, 4], 'chords-db', []),
      P('Padrão', ["x", 5, 5, 5, 3, "x"], [0, 2, 3, 4, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 7, 5, 8, 5], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'D9': [
      P('5ª casa', [5, 5, 4, 5, 5, 5], [2, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', ["x", 7, 0, 7, 7, 8], [0, 1, 0, 2, 3, 4], 'chords-db', []),
      P('9ª casa (pestana)', [10, 9, 10, 9, 10, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 9, "from": 0, "to": 4}])
      ],
      'D9#11': [
      P('Padrão', ["x", "x", 0, 1, 1, 2], [0, 0, 0, 1, 2, 3], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 5, 4, 5, 5, 4], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", 9, 0, 7, 9, 8], [0, 3, 0, 1, 4, 2], 'chords-db', [])
      ],
      'D9b5': [
      P('4ª casa (pestana)', ["x", 5, 4, 5, 5, 4], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", 5, 6, 5, 7, 0], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('9ª casa (pestana)', [10, 9, 10, 9, 9, 10], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Dadd11': [
      P('3ª casa', ["x", 5, 4, 2, 3, 3], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 0, 11, 8, 10], [0, 0, 0, 4, 1, 3], 'chords-db', []),
      P('7ª casa (pestana)', [10, 9, 7, 7, 8, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 7, "from": 0, "to": 4}])
      ],
      'Dadd9': [
      P('2ª casa', ["x", 5, 4, 2, 5, 2], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", 5, 7, 7, 7, 0], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 9, 7, 10], [0, 0, 0, 3, 1, 4], 'chords-db', [])
      ],
      'Dalt': [
      P('Padrão', ["x", "x", 0, 1, 3, 2], [0, 0, 0, 1, 3, 2], 'chords-db', []),
      P('Padrão', ["x", 5, 4, "x", 3, 4], [0, 4, 2, 0, 1, 3], 'chords-db', []),
      P('Padrão', ["x", 5, 6, 7, 7, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Daug': [
      P('Padrão', ["x", "x", 0, 3, 3, 2], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('3ª casa', ["x", 5, 4, 3, 3, "x"], [0, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 3, "from": 1, "to": 4}]),
      P('7ª casa', [10, 9, 8, 7, 7, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 7, "from": 0, "to": 4}])
      ],
      'Daug7': [
      P('Padrão', ["x", "x", 0, 3, 1, 2], [0, 0, 0, 4, 1, 2], 'chords-db', []),
      P('Padrão', ["x", 5, 4, 5, "x", 6], [0, 2, 1, 3, 0, 4], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 5, 8, 5, 7, 6], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Daug9': [
      P('5ª casa', ["x", 5, 4, 5, 5, 6], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('Padrão', ["x", 7, 0, 5, 7, 6], [0, 3, 0, 1, 4, 2], 'chords-db', []),
      P('9ª casa (pestana)', [10, 9, 10, 9, 11, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 9, "from": 0, "to": 4}])
      ],
      'Ddim': [
      P('Padrão', ["x", "x", 0, 1, "x", 1], [0, 0, 0, 1, 0, 2], 'chords-db', []),
      P('Padrão', ["x", 5, 3, "x", 3, 4], [0, 4, 1, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 5, 6, 7, 6, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', [])
      ],
      'Ddim7': [
      P('Abertura', ["x", "x", 0, 1, 0, 1], [0, 0, 0, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 5, 6, 4, 6, 4], [0, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", 8, 0, 10, 9, 7], [0, 2, 0, 4, 3, 1], 'chords-db', [])
      ],
      'Dm': [
      P('Padrão', ["x", "x", 0, 2, 3, 1], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 7, 7, 6, 5], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', ["x", 8, 7, 7, 6, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', [])
      ],
      'Dm/A': [
      P('Abertura', ["x", 0, 0, 2, 3, 1], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", 0, 3, 2, 3, 1], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 0, 7, 7, 6, 5], [0, 0, 3, 4, 2, 1], 'chords-db', [])
      ],
      'Dm/Ab': [
      P('Abertura', [4, 0, 0, 2, 3, 1], [4, 0, 0, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 7, 6, 5], [0, 0, 2, 4, 3, 1], 'chords-db', []),
      P('10ª casa (pestana)', ["x", 11, 12, 10, 10, 10], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'Dm/B': [
      P('Padrão', ["x", 2, 0, 2, 3, 1], [0, 2, 0, 3, 4, 1], 'chords-db', []),
      P('7ª casa (pestana)', [7, 8, 7, 7, 10, 10], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [7, 8, 7, 10, 10, 10], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Dm/Bb': [
      P('1ª casa (pestana)', ["x", 1, 3, 2, 3, 1], [0, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 8, 7, 6, 5], [0, 0, 4, 3, 2, 1], 'chords-db', []),
      P('10ª casa', ["x", "x", 8, 10, 10, 10], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 10, "from": 3, "to": 5}])
      ],
      'Dm/C': [
      P('Padrão', ["x", 3, 0, 2, 3, 1], [0, 3, 0, 2, 4, 1], 'chords-db', []),
      P('10ª casa (pestana)', ["x", "x", 10, 10, 10, 10], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}]),
      P('Padrão', ["x", 3, 3, 2, 3, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', [])
      ],
      'Dm/C#': [
      P('Padrão', ["x", 4, 0, 2, 3, 1], [0, 4, 0, 2, 3, 1], 'chords-db', []),
      P('7ª casa (pestana)', [9, 8, 7, 7, 10, 10], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('10ª casa', [9, 8, 7, 10, 10, 10], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 10, "from": 3, "to": 5}])
      ],
      'Dm/E': [
      P('Abertura', [0, 0, 0, 2, 3, 1], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('Abertura', [0, 0, 3, 2, 3, 1], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 2, 3, 1], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'Dm/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 2, 3, 1], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('10ª casa (pestana)', [11, 12, 12, 10, 10, 10], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 5}]),
      P('10ª casa (pestana)', ["x", "x", 13, 10, 10, 10], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}])
      ],
      'Dm/F': [
      P('Padrão', ["x", "x", 3, 2, 3, 1], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 8, 7, 7, 10, 10], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}]),
      P('10ª casa', ["x", 8, 7, 10, 10, 10], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 10, "from": 3, "to": 5}])
      ],
      'Dm/F#': [
      P('Abertura', [2, 0, 0, 2, 3, 1], [2, 0, 0, 3, 4, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 2, 3, 1], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 7, 6, 5], [0, 0, 1, 4, 3, 2], 'chords-db', [])
      ],
      'Dm/G': [
      P('Abertura', [3, 0, 0, 2, 3, 1], [3, 0, 0, 2, 4, 1], 'chords-db', []),
      P('5ª casa (pestana)', ["x", "x", 5, 7, 6, 5], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('10ª casa (pestana)', ["x", 10, 12, 10, 10, 10], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'Dm11': [
      P('1ª casa (pestana)', ["x", "x", 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 4, "to": 5}]),
      P('3ª casa (pestana)', ["x", 5, 3, 5, 5, 3], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [10, 8, 10, 9, 8, 8], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Dm6': [
      P('Abertura', ["x", "x", 0, 2, 0, 1], [0, 0, 0, 2, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 5, 3, 4, 3, 5], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 5, 7, "x", 6, 7], [0, 1, 3, 0, 2, 4], 'chords-db', [])
      ],
      'Dm69': [
      P('Abertura', ["x", 5, 3, 2, 0, 0], [0, 4, 2, 1, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 5, 3, 4, 5, 0], [0, 3, 1, 2, 4, 0], 'chords-db', []),
      P('Padrão', ["x", 7, 0, 7, 6, 7], [0, 2, 0, 3, 1, 4], 'chords-db', [])
      ],
      'Dm7': [
      P('Padrão', [10, "x", 10, 10, 10, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('1ª casa', ["x", "x", 0, 2, 1, 1], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 3, "to": 5}]),
      P('5ª casa', ["x", 5, 7, 5, 6, 5], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Dm7b5': [
      P('1ª casa', ["x", "x", 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 3, "to": 5}]),
      P('3ª casa', ["x", 5, 3, 5, 3, 4], [0, 3, 1, 4, 1, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 5, 6, 5, 6, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', [])
      ],
      'Dm9': [
      P('Abertura', [1, 0, 0, 2, 1, 0], [1, 0, 0, 3, 2, 0], 'chords-db', []),
      P('5ª casa', ["x", 5, 3, 5, 5, 5], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('Padrão', ["x", 5, 7, 5, 6, 0], [0, 1, 4, 2, 3, 0], 'chords-db', [])
      ],
      'Dm9/C': [
      P('Abertura', ["x", 3, 0, 2, 1, 0], [0, 3, 0, 2, 1, 0], 'chords-db', []),
      P('Abertura', ["x", 3, 0, 2, 3, 0], [0, 2, 0, 1, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', [8, 5, 7, 5, 5, 5], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Dm9/F': [
      P('Abertura', [1, 0, 0, 2, 1, 0], [1, 0, 0, 3, 2, 0], 'chords-db', []),
      P('Abertura', [1, 3, 0, 2, 3, 0], [1, 3, 0, 2, 4, 0], 'chords-db', []),
      P('Abertura', [1, "x", 0, 2, 1, 0], [1, 0, 0, 3, 2, 0], 'chords-db', [])
      ],
      'Dmadd9': [
      P('Padrão', ["x", 5, 3, 2, 3, 0], [0, 4, 2, 1, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 5, 3, 2, 5, "x"], [0, 3, 2, 1, 4, 0], 'chords-db', []),
      P('Padrão', ["x", 5, 7, 7, 6, 0], [0, 1, 3, 4, 2, 0], 'chords-db', [])
      ],
      'Dmaj11': [
      P('2ª casa', ["x", "x", 0, 0, 2, 2], [0, 0, 0, 0, 1, 1], 'chords-db', [{"fret": 2, "from": 4, "to": 5}]),
      P('5ª casa (pestana)', [5, 5, 5, 6, 7, 5], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', ["x", 9, 0, 7, 8, 9], [0, 3, 0, 1, 2, 4], 'chords-db', [])
      ],
      'Dmaj13': [
      P('2ª casa', ["x", "x", 0, 4, 2, 2], [0, 0, 0, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('Padrão', ["x", 5, 4, 4, 2, 0], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('5ª casa', ["x", 5, 5, 6, 7, 7], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Dmaj7': [
      P('2ª casa (pestana)', ["x", "x", 0, 2, 2, 2], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('2ª casa (pestana)', ["x", 5, 4, 2, 2, 2], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', [5, 5, 7, 6, 7, 5], [1, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Dmaj7#5': [
      P('Padrão', ["x", "x", 0, 3, 2, 2], [0, 0, 0, 4, 2, 3], 'chords-db', []),
      P('2ª casa (pestana)', [2, 5, 4, 3, 2, 2], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", 5, 0, 6, 7, 6], [0, 1, 0, 2, 4, 3], 'chords-db', [])
      ],
      'Dmaj7b5': [
      P('Padrão', ["x", "x", 0, 1, 2, 2], [0, 0, 0, 1, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 5, 6, 6, 7, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', []),
      P('9ª casa (pestana)', [10, 9, 11, 11, 9, 9], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Dmaj7sus2': [
      P('Abertura', ["x", "x", 0, 2, 2, 0], [0, 0, 0, 1, 2, 0], 'chords-db', []),
      P('5ª casa', ["x", "x", 0, 6, 5, 5], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 7, 6, 5, 5], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Dmaj9': [
      P('2ª casa (pestana)', ["x", 5, 2, 2, 2, 2], [0, 4, 1, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", 5, 4, 6, 4, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 9, 0, 9, 7, 9], [0, 2, 0, 3, 1, 4], 'chords-db', [])
      ],
      'Dmmaj11': [
      P('Abertura', ["x", "x", 0, 0, 2, 1], [0, 0, 0, 0, 2, 1], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 5, 3, 6, 5, 3], [0, 2, 1, 4, 3, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', [5, 5, 5, 7, 7, 5], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Dmmaj7': [
      P('Padrão', ["x", "x", 0, 2, 2, 1], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('2ª casa', ["x", 5, 3, 2, 2, 0], [0, 4, 2, 1, 1, 0], 'chords-db', [{"fret": 2, "from": 1, "to": 4}]),
      P('5ª casa (pestana)', [5, 5, 7, 6, 6, 5], [1, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Dmmaj7b5': [
      P('Padrão', ["x", "x", 0, 1, 2, 1], [0, 0, 0, 1, 3, 2], 'chords-db', []),
      P('6ª casa', [4, 5, 6, 6, 6, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 6, "from": 2, "to": 4}]),
      P('Padrão', ["x", 5, 6, 6, 6, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Dmmaj9': [
      P('Padrão', ["x", 5, 3, 6, 5, 0], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 7, 0, 6, 6, 5], [0, 4, 0, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", 8, 0, 9, 10, 9], [0, 1, 0, 2, 4, 3], 'chords-db', [])
      ],
      'Dsus': [
      P('3ª casa', ["x", "x", 0, 2, 3, 3], [0, 0, 0, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 4, "to": 5}]),
      P('Padrão', ["x", "x", 0, 7, 8, 5], [0, 0, 0, 3, 4, 1], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 5, 5, 7, 8, 5], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Dsus2': [
      P('Abertura', ["x", "x", 0, 2, 3, 0], [0, 0, 0, 2, 3, 0], 'chords-db', []),
      P('2ª casa', ["x", "x", 2, 2, 3, 5], [0, 0, 1, 1, 2, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', [5, 5, 7, 7, 5, 5], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Dsus2sus4': [
      P('[5]ª casa (pestana)', ["x", 5, 5, 7, 5, 5], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('[2, 3]ª casa', ["x", 5, 2, 2, 3, 3], [0, 4, 1, 1, 2, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 5}, {"fret": 3, "from": 1, "to": 5}]),
      P('[10]ª casa (pestana)', [10, 10, 12, 12, 10, 12], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 10, "from": 0, "to": 5}])
      ],
      'Dsus4': [
      P('Padrão', ["x", "x", 0, 2, 3, 3], [0, 0, 0, 1, 2, 3], 'chords-db', []),
      P('Abertura', ["x", 5, 0, 0, 3, 5], [0, 3, 0, 0, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 7, 7, 8, 5], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'E': [
      P('Abertura', [0, 2, 2, 1, 0, 0], [0, 2, 3, 1, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 4, 5, 4], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 7, 6, 4, 5, 4], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'E/A': [
      P('Abertura', ["x", 0, 2, 1, 0, 0], [0, 0, 2, 1, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 1, 0, 4], [0, 0, 2, 1, 0, 4], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 4, 0, 4], [0, 0, 1, 3, 0, 4], 'chords-db', [])
      ],
      'E/Ab': [
      P('4ª casa (pestana)', [4, 7, 6, 4, 5, 4], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, "x", "x", 4, 5, 4], [1, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 6, 4, 5, 4], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'E/B': [
      P('Abertura', ["x", 2, 2, 1, 0, 0], [0, 2, 3, 1, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 2, 2, 4, 5, 4], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 9, 9, 9, 7], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'E/Bb': [
      P('Abertura', ["x", 1, 2, 1, 0, 0], [0, 1, 3, 2, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 9, 9, 7], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 1, 2, 1, 0, "x"], [0, 1, 3, 2, 0, 0], 'chords-db', [])
      ],
      'E/C': [
      P('Abertura', ["x", 3, 2, 1, 0, 0], [0, 3, 2, 1, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 3, 2, 1, 0, 4], [0, 3, 2, 1, 0, 4], 'chords-db', []),
      P('Padrão', ["x", 3, 2, 4, 0, 4], [0, 2, 1, 3, 0, 4], 'chords-db', [])
      ],
      'E/C#': [
      P('Abertura', ["x", 4, 2, 1, 0, 0], [0, 4, 2, 1, 0, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 4, 6, 4, 5, 4], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 6, 4, 5, 7], [0, 1, 3, 1, 2, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'E/D': [
      P('Abertura', ["x", "x", 0, 1, 0, 0], [0, 0, 0, 1, 0, 0], 'chords-db', []),
      P('4ª casa', ["x", "x", 0, 4, 5, 4], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', ["x", 5, 6, 4, 5, 4], [0, 2, 4, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'E/D#': [
      P('Abertura', ["x", "x", 1, 1, 0, 0], [0, 0, 1, 2, 0, 0], 'chords-db', []),
      P('4ª casa', ["x", 6, 6, 4, 5, 4], [0, 3, 4, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa', [11, 11, 9, 9, 12, 12], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'E/Eb': [
      P('Abertura', ["x", "x", 1, 1, 0, 0], [0, 0, 1, 2, 0, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 6, 6, 4, 5, 4], [0, 3, 4, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [11, 11, 9, 9, 9, 12], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'E/F': [
      P('Abertura', [1, 2, 2, 1, 0, 0], [1, 3, 4, 2, 0, 0], 'chords-db', []),
      P('Abertura', ["x", "x", 3, 1, 0, 0], [0, 0, 3, 1, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 4, 5, 4], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'E/F#': [
      P('Abertura', [2, 2, 2, 1, 0, 0], [2, 3, 4, 1, 0, 0], 'chords-db', []),
      P('Abertura', ["x", "x", 4, 1, 0, 0], [0, 0, 4, 1, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 4, 5, 4], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'E/G': [
      P('Abertura', [3, 2, 2, 1, 0, 0], [4, 2, 3, 1, 0, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", "x", 5, 4, 5, 4], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", 10, 9, 9, 9, 12], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'E/G#': [
      P('Abertura', ["x", "x", "x", 1, 0, 0], [0, 0, 0, 1, 0, 0], 'chords-db', []),
      P('Abertura', [4, 2, 2, 1, 0, 0], [4, 2, 3, 1, 0, 0], 'chords-db', []),
      P('4ª casa', [4, 7, 6, 4, 5, 4], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'E11': [
      P('Abertura', [0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0], 'chords-db', []),
      P('Abertura', [0, 0, 4, 4, 3, 4], [0, 0, 2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 7, 6, 7, 5, 5], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'E13': [
      P('Abertura', [0, 2, 0, 1, 2, 0], [0, 2, 0, 1, 3, 0], 'chords-db', []),
      P('Abertura', [0, 0, 0, 1, 2, 2], [0, 0, 0, 1, 2, 3], 'chords-db', []),
      P('Abertura', [0, 5, 6, 6, 5, 0], [0, 1, 3, 4, 2, 0], 'chords-db', [])
      ],
      'E5': [
      P('Padrão', [12, 14, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 7, 9, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [12, 14, 14, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'E6': [
      P('Abertura', [0, 2, 2, 1, 2, 0], [0, 2, 3, 1, 4, 0], 'chords-db', []),
      P('2ª casa (pestana)', [0, 2, 2, 4, 2, 4], [0, 1, 1, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", 7, 6, 6, 5, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', [])
      ],
      'E69': [
      P('2ª casa', [0, 2, 2, 1, 2, 2], [0, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 7, 6, 6, 7, 7], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', ["x", 9, 9, 9, 9, 9], [0, 1, 1, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'E7': [
      P('Abertura', [0, 2, 0, 1, 0, 0], [0, 2, 0, 1, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 7, 6, 7, 5, "x"], [0, 3, 2, 4, 1, 0], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 9, 7, 9, 7], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'E7#9': [
      P('Abertura', [0, 2, 0, 1, 0, 3], [0, 2, 0, 1, 0, 4], 'chords-db', []),
      P('Abertura', [0, 5, 0, 0, 3, 4], [0, 3, 0, 0, 1, 2], 'chords-db', []),
      P('Padrão', ["x", 7, 6, 7, 8, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', [])
      ],
      'E7b5': [
      P('Abertura', [0, 1, 0, 1, 3, 0], [0, 1, 0, 2, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 3, 3, 4], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 7, 5, 6], [0, 0, 2, 4, 1, 3], 'chords-db', [])
      ],
      'E7b9': [
      P('Abertura', [0, 2, 0, 1, 0, 1], [0, 3, 0, 1, 0, 2], 'chords-db', []),
      P('4ª casa', [0, 5, 0, 4, 6, 4], [0, 3, 0, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 7, 6, 7, 6, 7], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'E7sus4': [
      P('Abertura', [0, 2, 0, 2, 0, 0], [0, 2, 0, 3, 0, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 7, 7, 7, 5, 5], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 9, 7, 10, 7], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'E9': [
      P('Abertura', [0, 2, 0, 1, 0, 2], [0, 2, 0, 1, 0, 3], 'chords-db', []),
      P('2ª casa', [4, "x", 2, 4, 3, 2], [3, 0, 1, 4, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa', [7, 7, 6, 7, 7, 7], [2, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'E9#11': [
      P('Abertura', [0, 1, 0, 1, 0, 0], [0, 1, 0, 2, 0, 0], 'chords-db', []),
      P('Abertura', [0, 5, 0, 3, 5, 4], [0, 3, 0, 1, 4, 2], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 7, 6, 7, 7, 6], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'E9b5': [
      P('1ª casa', [0, 1, 2, 1, 3, 2], [0, 1, 2, 1, 4, 3], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa', [0, 5, 4, 3, 3, 4], [0, 4, 2, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 7, 6, 7, 7, 6], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Eadd11': [
      P('2ª casa', [0, 2, 2, 2, 5, 4], [0, 1, 1, 1, 4, 3], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa', [0, 7, 6, 4, 5, 5], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('5ª casa', ["x", 7, 6, 4, 5, 5], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Eadd9': [
      P('Abertura', [0, 2, 2, 1, 0, 2], [0, 2, 3, 1, 0, 4], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 7, 6, 4, 7, 4], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", 7, 6, "x", 7, 7], [0, 2, 1, 0, 3, 4], 'chords-db', [])
      ],
      'Ealt': [
      P('Padrão', [0, 1, 2, 1, "x", "x"], [0, 1, 3, 2, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 3, 5, 4], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [0, 7, 6, "x", 5, 6], [0, 4, 2, 0, 1, 3], 'chords-db', [])
      ],
      'Eaug': [
      P('Abertura', [0, 3, 2, 1, 1, 0], [0, 4, 3, 1, 2, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 7, 6, 5, 5, "x"], [0, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 5, "from": 1, "to": 4}]),
      P('Padrão', ["x", 7, 10, 9, 9, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [])
      ],
      'Eaug7': [
      P('Abertura', [0, 3, 0, 1, 1, 0], [0, 4, 0, 1, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 5, 3, 4], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 7, 10, 7, 9, 8], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Eaug9': [
      P('Abertura', [0, 3, 0, 1, 3, 2], [0, 3, 0, 1, 4, 2], 'chords-db', []),
      P('4ª casa', [0, 5, 4, 5, 5, 4], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('7ª casa', ["x", 7, 6, 7, 7, 8], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Eb': [
      P('Padrão', ["x", "x", 1, 3, 4, 3], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('3ª casa', ["x", 6, 5, 3, 4, 3], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 8, 8, 6], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Eb/A': [
      P('Padrão', ["x", 0, 1, 3, 4, 3], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('3ª casa', ["x", 0, 5, 3, 4, 3], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 5, 3, 4, 6], [0, 0, 3, 1, 2, 4], 'chords-db', [])
      ],
      'Eb/Ab': [
      P('3ª casa (pestana)', ["x", "x", 6, 3, 4, 3], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 8, 8, 6], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", 11, 13, 12, 11, 11], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 11, "from": 1, "to": 5}])
      ],
      'Eb/B': [
      P('Padrão', ["x", "x", 9, 8, 8, 6], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 9, 12, 11, 11], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('11ª casa (pestana)', ["x", 14, 13, 12, 11, 11], [0, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 11, "from": 1, "to": 5}])
      ],
      'Eb/Bb': [
      P('1ª casa (pestana)', ["x", 1, 1, 3, 4, 3], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 8, 8, 8, 6], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 8, 8, 8, 6], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'Eb/C': [
      P('3ª casa (pestana)', ["x", 3, 5, 3, 4, 3], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 5, 3, 4, 6], [0, 1, 3, 1, 2, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [8, 10, 8, 8, 8, 11], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Eb/C#': [
      P('3ª casa (pestana)', ["x", 4, 5, 3, 4, 3], [0, 2, 4, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [9, 10, 8, 8, 8, 11], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [9, 10, 8, 8, 11, 11], [2, 3, 1, 1, 4, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Eb/D': [
      P('3ª casa', ["x", "x", 0, 3, 4, 3], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa (pestana)', ["x", 5, 5, 3, 4, 3], [0, 3, 4, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 0, 8, 8, 6], [0, 0, 0, 3, 4, 1], 'chords-db', [])
      ],
      'Eb/E': [
      P('1ª casa', [0, 1, 1, 3, 4, 3], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 2, 3, 4, 3], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('3ª casa', [0, 6, 5, 3, 4, 3], [0, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Eb/F': [
      P('1ª casa (pestana)', [1, 1, 1, 3, 4, 3], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 4, 3], [0, 0, 1, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 8, 8, 8, 11], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Eb/F#': [
      P('3ª casa (pestana)', ["x", "x", 4, 3, 4, 3], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", 9, 8, 8, 8, 11], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", 9, 8, 8, 8, "x"], [0, 2, 1, 1, 1, 0], 'chords-db', [{"fret": 8, "from": 1, "to": 4}])
      ],
      'Eb/G': [
      P('3ª casa (pestana)', [3, 6, 5, 3, 4, 3], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, "x", "x", 3, 4, 3], [1, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 5, 3, 4, 3], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'Eb11': [
      P('1ª casa (pestana)', [1, 1, 1, 1, 2, 3], [1, 1, 1, 1, 2, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 5, 6, 4, 4], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [0, 6, 6, 6, 8, 6], [0, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Eb13': [
      P('8ª casa', ["x", 6, 5, 6, 8, 8], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 8, "from": 4, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 6, 8, 8], [1, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('9ª casa', [11, 10, 10, 0, 9, 9], [4, 2, 3, 0, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Eb5': [
      P('Padrão', [11, 13, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 6, 8, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [11, 13, 13, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'Eb6': [
      P('1ª casa', ["x", "x", 1, 3, 1, 3], [0, 0, 1, 3, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 6, 5, 5, 4, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', []),
      P('8ª casa', ["x", 6, 8, 8, 8, 8], [0, 1, 3, 3, 3, 3], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Eb69': [
      P('Padrão', ["x", "x", 1, 0, 1, 1], [0, 0, 2, 0, 3, 4], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 3, 3, 4, 3], [0, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 6, 5, 5, 6, 6], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Eb7': [
      P('Padrão', ["x", "x", 1, 3, 2, 3], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 8, 6, 8, 6], [0, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 8, 8, 8, 9], [0, 0, 1, 1, 1, 2], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Eb7#9': [
      P('Padrão', ["x", "x", 1, 0, 2, 2], [0, 0, 2, 0, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 6, 5, 6, 7, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 9, 8, 8, 8, 9], [0, 2, 1, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Eb7b5': [
      P('Padrão', ["x", "x", 1, 2, 2, 3], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 6, 4, 5], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 7, 6, 8, 6], [0, 1, 2, 1, 3, 0], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Eb7b9': [
      P('Abertura', ["x", "x", 1, 0, 2, 0], [0, 0, 2, 0, 4, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 5, 6, 5, 6], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('6ª casa', ["x", 6, 8, 6, 8, 0], [0, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 6, "from": 1, "to": 4}])
      ],
      'Eb7sus4': [
      P('Padrão', ["x", "x", 1, 3, 2, 4], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 6, 6, 6, 4, 4], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 8, 6, 9, 6], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Eb9': [
      P('Padrão', ["x", "x", 1, 0, 2, 1], [0, 0, 1, 0, 3, 2], 'chords-db', []),
      P('6ª casa', ["x", 6, 5, 6, 6, 6], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('Padrão', [11, 10, 11, 10, "x", "x"], [3, 1, 4, 2, 0, 0], 'chords-db', [])
      ],
      'Eb9#11': [
      P('Padrão', ["x", "x", 1, 2, 2, 3], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 5, 6, 6, 5], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 7, 6, 8, "x"], [0, 1, 2, 1, 3, 0], 'chords-db', [{"fret": 6, "from": 1, "to": 4}])
      ],
      'Eb9b5': [
      P('5ª casa (pestana)', ["x", 6, 5, 6, 6, 5], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('Padrão', ["x", 6, 7, 0, 6, 9], [0, 1, 3, 0, 2, 4], 'chords-db', []),
      P('10ª casa (pestana)', [11, 10, 11, 10, 10, 11], [1, 2, 0, 3, 0, 4], 'chords-db', [{"fret": 10, "from": 0, "to": 5}])
      ],
      'Ebadd11': [
      P('4ª casa', ["x", "x", 1, 0, 4, 4], [0, 0, 1, 0, 4, 4], 'chords-db', [{"fret": 4, "from": 4, "to": 5}]),
      P('4ª casa', ["x", 6, 5, 3, 4, 4], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [11, 10, 8, 8, 9, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 8, "from": 0, "to": 4}])
      ],
      'Ebadd9': [
      P('3ª casa (pestana)', ["x", 6, 5, 3, 6, 3], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 6, 5, 0, 6, 6], [0, 2, 1, 0, 3, 4], 'chords-db', []),
      P('Padrão', [11, 10, "x", 10, 11, "x"], [3, 1, 0, 2, 4, 0], 'chords-db', [])
      ],
      'Ebalt': [
      P('Padrão', ["x", "x", 1, 2, 4, 3], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('Padrão', ["x", 6, 5, 0, 4, 5], [0, 4, 2, 0, 1, 3], 'chords-db', []),
      P('Padrão', ["x", 6, 7, 0, 8, "x"], [0, 1, 2, 0, 3, 0], 'chords-db', [])
      ],
      'Ebaug': [
      P('Padrão', ["x", "x", 5, 4, 4, 3], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('4ª casa (pestana)', ["x", 6, 5, 4, 4, "x"], [0, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 4, "from": 1, "to": 4}]),
      P('8ª casa (pestana)', [11, 10, 9, 8, 8, "x"], [4, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 8, "from": 0, "to": 4}])
      ],
      'Ebaug7': [
      P('Padrão', ["x", "x", 1, 4, 2, 3], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 9, 6, 8, 7], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('Abertura', [11, 10, 11, 0, 0, 9], [3, 2, 4, 0, 0, 1], 'chords-db', [])
      ],
      'Ebaug9': [
      P('3ª casa (pestana)', [3, 4, 3, 4, 4, 3], [1, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('6ª casa', ["x", 6, 5, 6, 6, 7], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('Padrão', [11, 10, "x", 10, 0, 9], [4, 2, 0, 3, 0, 1], 'chords-db', [])
      ],
      'Ebdim': [
      P('Padrão', ["x", "x", 1, 2, "x", 2], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 6, 4, "x", 4, 5], [0, 4, 1, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 6, 7, 8, 7, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', [])
      ],
      'Ebdim7': [
      P('Padrão', ["x", "x", 1, 2, 1, 2], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 6, 7, 5, 7, 5], [0, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 7, 8, 7, 8], [0, 0, 1, 3, 2, 4], 'chords-db', [])
      ],
      'Ebm': [
      P('Padrão', ["x", "x", 1, 3, 4, 2], [0, 0, 1, 3, 4, 2], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 3, 4, 2], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 8, 8, 7, 6], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Ebm/A': [
      P('Padrão', ["x", 0, 1, 3, 4, 2], [0, 0, 1, 3, 4, 2], 'chords-db', []),
      P('Padrão', ["x", 0, 4, 3, 4, 2], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 0, 8, 8, 7, 6], [0, 0, 3, 4, 2, 1], 'chords-db', [])
      ],
      'Ebm/Ab': [
      P('6ª casa (pestana)', ["x", "x", 6, 8, 7, 6], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", 11, 13, 11, 11, 11], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 11, "from": 1, "to": 5}]),
      P('11ª casa (pestana)', ["x", 11, 13, 11, 11, 14], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 11, "from": 1, "to": 5}])
      ],
      'Ebm/B': [
      P('2ª casa (pestana)', ["x", 2, 4, 3, 4, 2], [0, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 9, 8, 7, 6], [0, 0, 4, 3, 2, 1], 'chords-db', []),
      P('11ª casa', ["x", "x", 9, 11, 11, 11], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 11, "from": 3, "to": 5}])
      ],
      'Ebm/Bb': [
      P('1ª casa (pestana)', ["x", 1, 1, 3, 4, 2], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 8, 8, 7, 6], [1, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 8, 8, 7, 6], [0, 0, 3, 4, 2, 1], 'chords-db', [])
      ],
      'Ebm/C': [
      P('8ª casa (pestana)', [8, 9, 8, 8, 11, 11], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 9, 8, 11, 11, 11], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('11ª casa', ["x", "x", 10, 11, 11, 11], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 11, "from": 3, "to": 5}])
      ],
      'Ebm/C#': [
      P('11ª casa (pestana)', ["x", "x", 11, 11, 11, 11], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 11, "from": 2, "to": 5}]),
      P('Padrão', ["x", 4, 4, 3, 4, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', []),
      P('8ª casa (pestana)', [9, 9, 8, 8, "x", "x"], [2, 3, 1, 1, 0, 0], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ebm/D': [
      P('Padrão', ["x", "x", 0, 3, 4, 2], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 8, 7, 6], [0, 0, 0, 3, 2, 1], 'chords-db', []),
      P('8ª casa (pestana)', [10, 9, 8, 8, 11, 11], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Ebm/E': [
      P('1ª casa', [0, 1, 1, 3, 4, 2], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 2, 3, 4, 2], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('6ª casa', [0, 6, 8, 8, 7, 6], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ebm/F': [
      P('1ª casa (pestana)', [1, 1, 1, 3, 4, 2], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 3, 4, 2], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 8, 8, 11, 11, 11], [0, 1, 1, 4, 4, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Ebm/F#': [
      P('Padrão', ["x", "x", 4, 3, 4, 2], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 9, 8, 8, 11, 11], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}]),
      P('11ª casa', ["x", 9, 8, 11, 11, 11], [0, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 11, "from": 3, "to": 5}])
      ],
      'Ebm/G': [
      P('Padrão', ["x", "x", 5, 3, 4, 2], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 8, 7, 6], [0, 0, 1, 4, 3, 2], 'chords-db', []),
      P('11ª casa', ["x", 10, 8, 11, 11, 11], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 11, "from": 3, "to": 5}])
      ],
      'Ebm11': [
      P('1ª casa (pestana)', ["x", "x", 1, 1, 2, 2], [0, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 4, 6, 6, 4], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [11, 9, 11, 10, 9, 9], [3, 1, 4, 2, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Ebm6': [
      P('1ª casa (pestana)', ["x", 1, 1, 3, 1, 2], [0, 1, 1, 3, 1, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 4, 5, 4, 6], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 8, 8, 7, 8], [0, 0, 2, 3, 1, 4], 'chords-db', [])
      ],
      'Ebm69': [
      P('1ª casa', [2, "x", 1, 3, 1, 1], [2, 0, 1, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", 6, 4, 5, 6, "x"], [0, 3, 1, 2, 4, 0], 'chords-db', []),
      P('9ª casa (pestana)', [11, 9, 10, 10, 9, 9], [4, 1, 2, 3, 0, 0], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'Ebm7': [
      P('Padrão', [11, "x", 11, 11, 11, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 1, 3, 2, 2], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 8, 6, 7, 6], [1, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Ebm7b5': [
      P('2ª casa', ["x", "x", 1, 2, 2, 2], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('Padrão', ["x", 6, 7, 6, 7, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('7ª casa', ["x", "x", 7, 8, 7, 9], [0, 0, 1, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 2, "to": 5}])
      ],
      'Ebm9': [
      P('6ª casa', ["x", 6, 4, 6, 6, 6], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 8, 10, 7, 9], [0, 0, 2, 4, 1, 3], 'chords-db', []),
      P('11ª casa', ["x", 9, 11, 10, 11, 11], [0, 1, 3, 2, 4, 4], 'chords-db', [{"fret": 11, "from": 2, "to": 5}])
      ],
      'Ebm9/C#': [
      P('1ª casa (pestana)', ["x", 4, 1, 3, 2, 1], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [9, 6, 8, 6, 6, 6], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [9, 6, 8, 8, 6, 6], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Ebm9/F#': [
      P('1ª casa (pestana)', [2, 1, 1, 3, 2, 1], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [2, "x", 1, 3, 2, 1], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}])
      ],
      'Ebmadd9': [
      P('Padrão', ["x", "x", 4, 3, 4, 1], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 6, 4, 3, 6, "x"], [0, 3, 2, 1, 4, 0], 'chords-db', []),
      P('Padrão', ["x", 6, 4, "x", 6, 6], [0, 2, 1, 0, 3, 4], 'chords-db', [])
      ],
      'Ebmaj11': [
      P('1ª casa', ["x", "x", 1, 1, 3, 3], [0, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 5, 7, 4, 4], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 7, 8, 6], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Ebmaj13': [
      P('Padrão', ["x", 3, 1, 0, 3, "x"], [0, 3, 1, 0, 4, 0], 'chords-db', []),
      P('3ª casa', ["x", 6, 5, 5, 3, 3], [0, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 7, 8, 8], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ebmaj7': [
      P('[1, 3]ª casa (pestana)', ["x", 1, 1, 3, 3, 3], [0, 1, 1, 3, 3, 3], 'chords-db', [{"fret": 1, "from": 1, "to": 5}, {"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa', ["x", 6, 5, 3, 3, 3], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 8, 7, 8, 6], [1, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Ebmaj7#5': [
      P('3ª casa', [3, 6, 5, 4, 3, 3], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", 6, 5, 7, "x", 7], [0, 2, 1, 3, 0, 4], 'chords-db', []),
      P('Padrão', ["x", 6, 9, 7, 8, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', [])
      ],
      'Ebmaj7b5': [
      P('Padrão', ["x", "x", 1, 2, 3, 3], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 7, 7, 8, 6], [0, 1, 2, 2, 4, 0], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', [11, 10, 12, 12, 10, 10], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 5}])
      ],
      'Ebmaj7sus2': [
      P('1ª casa (pestana)', ["x", "x", 1, 3, 3, 1], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 7, 6, 6], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', ["x", "x", 13, 10, 11, 10], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}])
      ],
      'Ebmaj9': [
      P('3ª casa', ["x", 6, 3, 3, 3, 3], [0, 4, 1, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 6, 5, 7, 6, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 8, 8, 8, 8, 10], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Ebmmaj11': [
      P('1ª casa (pestana)', ["x", 1, 1, 1, 3, 2], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 4, 7, 6, 4], [0, 3, 1, 4, 3, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 6, 7, 7, 6], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'Ebmmaj7': [
      P('Padrão', ["x", "x", 1, 3, 3, 2], [0, 0, 1, 3, 4, 2], 'chords-db', []),
      P('Padrão', ["x", 6, 4, 3, 3, "x"], [0, 4, 3, 1, 2, 0], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 8, 7, 7, 6], [0, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ebmmaj7b5': [
      P('Padrão', ["x", "x", 1, 2, 3, 2], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('7ª casa', [5, 6, 7, 7, 7, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 7, "from": 2, "to": 4}]),
      P('Padrão', ["x", 6, 7, 7, 7, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Ebmmaj9': [
      P('Padrão', ["x", 6, 4, 7, 6, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', []),
      P('6ª casa (pestana)', [6, 9, 8, 7, 6, 6], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('Padrão', [11, 9, 12, 10, "x", "x"], [3, 1, 4, 2, 0, 0], 'chords-db', [])
      ],
      'Ebsus': [
      P('4ª casa', ["x", "x", 1, 3, 4, 4], [0, 0, 1, 3, 4, 4], 'chords-db', [{"fret": 4, "from": 4, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 6, 8, 9, 6], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 8, 9, 6], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Ebsus2': [
      P('1ª casa (pestana)', [1, 1, 1, 3, 4, 1], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 6, 8, 8, 6, 6], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [11, 8, 8, 10, 11, "x"], [3, 1, 1, 2, 4, 0], 'chords-db', [{"fret": 8, "from": 0, "to": 4}])
      ],
      'Ebsus2sus4': [
      P('[6]ª casa (pestana)', ["x", 6, 6, 8, 6, 6], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('[3, 4]ª casa', ["x", 6, 3, 3, 4, 4], [0, 4, 1, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 5}, {"fret": 4, "from": 1, "to": 5}]),
      P('[11]ª casa (pestana)', [11, 11, 13, 13, 11, 13], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 11, "from": 0, "to": 5}])
      ],
      'Ebsus4': [
      P('Padrão', ["x", "x", 1, 3, 4, 4], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 8, 8, 9, 6], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa', ["x", "x", 8, 8, 9, "x"], [0, 0, 1, 1, 2, 0], 'chords-db', [{"fret": 8, "from": 2, "to": 4}])
      ],
      'Edim': [
      P('Padrão', ["x", "x", 2, 3, "x", 3], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 7, 5, "x", 5, 6], [0, 4, 1, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 7, 8, 9, 8, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', [])
      ],
      'Edim7': [
      P('Abertura', [0, 1, 2, 0, 2, 0], [0, 1, 2, 0, 3, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 3, 2, 3], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('Padrão', ["x", 7, 8, 6, 8, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', [])
      ],
      'Em': [
      P('Abertura', [0, 2, 2, 0, 0, 0], [0, 2, 3, 0, 0, 0], 'chords-db', []),
      P('2ª casa', [0, 2, 2, 4, 5, 3], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', ["x", 7, 9, 9, 8, 7], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Em/A': [
      P('Abertura', ["x", 0, 2, 0, 0, 0], [0, 0, 1, 0, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 0, 0, 3], [0, 0, 1, 0, 0, 2], 'chords-db', []),
      P('Abertura', ["x", 0, 2, 4, 0, 3], [0, 0, 1, 3, 0, 2], 'chords-db', [])
      ],
      'Em/Ab': [
      P('Abertura', [4, 2, 2, 0, 0, 0], [4, 1, 2, 0, 0, 0], 'chords-db', []),
      P('Abertura', [4, 2, 2, 0, 0, 3], [4, 1, 2, 0, 0, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 6, 4, 5, 3], [0, 0, 4, 2, 3, 1], 'chords-db', [])
      ],
      'Em/B': [
      P('Abertura', ["x", 2, 2, 0, 0, 0], [0, 1, 2, 0, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 2, 2, 0, 0, 3], [0, 1, 2, 0, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 2, 2, 4, 0, 3], [0, 1, 2, 4, 0, 3], 'chords-db', [])
      ],
      'Em/Bb': [
      P('Abertura', ["x", 1, 2, 0, 0, 0], [0, 1, 2, 0, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 1, 2, 0, 0, 3], [0, 1, 2, 0, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 1, 2, 4, 0, 3], [0, 1, 2, 4, 0, 3], 'chords-db', [])
      ],
      'Em/C': [
      P('Abertura', ["x", 3, 2, 0, 0, 0], [0, 2, 1, 0, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 3, 2, 0, 0, 3], [0, 2, 1, 0, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 3, 2, 4, 0, 3], [0, 2, 1, 4, 0, 3], 'chords-db', [])
      ],
      'Em/C#': [
      P('Abertura', ["x", 4, 2, 0, 0, 0], [0, 3, 1, 0, 0, 0], 'chords-db', []),
      P('Abertura', ["x", 4, 2, 0, 0, 3], [0, 3, 1, 0, 0, 2], 'chords-db', []),
      P('Padrão', ["x", 4, 2, 4, 0, 3], [0, 3, 1, 4, 0, 2], 'chords-db', [])
      ],
      'Em/D': [
      P('Abertura', ["x", "x", 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 4, 5, 3], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 9, 8, 7], [0, 0, 0, 3, 2, 1], 'chords-db', [])
      ],
      'Em/D#': [
      P('Abertura', ["x", "x", 1, 0, 0, 0], [0, 0, 1, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 6, 5, 4, 5, "x"], [0, 4, 2, 1, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 6, 9, 9, 8, "x"], [0, 1, 3, 4, 2, 0], 'chords-db', [])
      ],
      'Em/Eb': [
      P('Abertura', ["x", "x", 1, 0, 0, 0], [0, 0, 1, 0, 0, 0], 'chords-db', []),
      P('9ª casa (pestana)', [11, 10, 9, 9, 12, 12], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}]),
      P('12ª casa', [11, 10, 9, 12, 12, 12], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 12, "from": 3, "to": 5}])
      ],
      'Em/F': [
      P('Abertura', [1, 2, 2, 0, 0, 0], [1, 2, 3, 0, 0, 0], 'chords-db', []),
      P('Abertura', [1, 2, 2, 0, 0, 3], [1, 2, 3, 0, 0, 4], 'chords-db', []),
      P('Abertura', ["x", "x", 3, 0, 0, 0], [0, 0, 1, 0, 0, 0], 'chords-db', [])
      ],
      'Em/F#': [
      P('Abertura', [2, 2, 2, 0, 0, 0], [1, 2, 3, 0, 0, 0], 'chords-db', []),
      P('Abertura', [2, 2, 2, 0, 0, 3], [1, 2, 3, 0, 0, 4], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 4, 5, 3], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'Em/G': [
      P('Abertura', [3, 2, 2, 0, 0, 0], [3, 1, 2, 0, 0, 0], 'chords-db', []),
      P('Abertura', [3, 2, 2, 0, 0, 3], [3, 1, 2, 0, 0, 4], 'chords-db', []),
      P('Abertura', [3, 2, 2, 4, 0, 0], [3, 1, 2, 4, 0, 0], 'chords-db', [])
      ],
      'Em/G#': [
      P('Abertura', [4, 2, 2, 0, 0, 0], [4, 1, 2, 0, 0, 0], 'chords-db', []),
      P('4ª casa', [4, 7, 5, 4, 5, "x"], [1, 4, 2, 1, 3, 0], 'chords-db', [{"fret": 4, "from": 0, "to": 4}]),
      P('Padrão', ["x", "x", 6, 4, 5, 3], [0, 0, 4, 2, 3, 1], 'chords-db', [])
      ],
      'Em11': [
      P('Abertura', [0, 0, 0, 0, 0, 2], [0, 0, 0, 0, 0, 1], 'chords-db', []),
      P('Abertura', [0, 0, 5, 4, 3, 0], [0, 0, 3, 2, 1, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 7, 5, 7, 7, 5], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Em6': [
      P('Abertura', [0, 2, 2, 0, 2, 0], [0, 1, 2, 0, 3, 0], 'chords-db', []),
      P('2ª casa', [0, 2, 2, 4, 2, 3], [0, 1, 1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 7, 5, 6, 5, 7], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Em69': [
      P('2ª casa', [0, 2, 2, 0, 2, 2], [0, 1, 1, 0, 2, 3], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa', [3, "x", 2, 4, 2, 2], [2, 0, 1, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa', ["x", 7, 5, 6, 7, 7], [0, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Em7': [
      P('Abertura', [0, "x", 0, 0, 0, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('Padrão', [12, "x", 12, 12, 12, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('Abertura', [0, 2, 2, 0, 3, 0], [0, 2, 3, 0, 4, 0], 'chords-db', [])
      ],
      'Em7b5': [
      P('3ª casa', [0, 1, 2, 3, 3, 3], [0, 1, 2, 3, 3, 3], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('Padrão', ["x", 7, 8, 7, 8, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', []),
      P('8ª casa (pestana)', ["x", "x", 8, 9, 8, 10], [0, 0, 1, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Em9': [
      P('Abertura', [0, 2, 0, 0, 0, 2], [0, 2, 0, 0, 0, 4], 'chords-db', []),
      P('Abertura', [0, 2, 2, 0, 3, 2], [0, 1, 2, 0, 4, 3], 'chords-db', []),
      P('7ª casa', ["x", 7, 5, 7, 7, 7], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Em9/D': [
      P('2ª casa (pestana)', ["x", 5, 2, 4, 3, 2], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [10, 7, 9, 7, 7, 7], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [10, 7, 9, 9, 7, 7], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Em9/G': [
      P('2ª casa (pestana)', [3, 2, 2, 4, 3, 2], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', [3, "x", 2, 0, 3, 2], [3, 0, 1, 0, 4, 2], 'chords-db', []),
      P('2ª casa (pestana)', [3, "x", 2, 4, 3, 2], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'Emadd9': [
      P('1ª casa (pestana)', ["x", "x", 3, 1, 1, 3], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 8, 6, 5, 8, "x"], [0, 3, 2, 1, 4, 0], 'chords-db', []),
      P('Padrão', ["x", 8, 6, 0, 6, 8], [0, 3, 1, 0, 2, 4], 'chords-db', [])
      ],
      'Emaj11': [
      P('Abertura', [0, 0, 1, 1, 0, 0], [0, 0, 1, 2, 0, 0], 'chords-db', []),
      P('4ª casa', [0, 0, 6, 4, 4, 5], [0, 0, 3, 1, 1, 2], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 7, 8, 9, 7], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Emaj13': [
      P('1ª casa', [0, 2, 1, 1, 2, 2], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa', ["x", 7, 6, 6, 4, 4], [0, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', ["x", 7, 7, 8, 9, 9], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Emaj7': [
      P('Abertura', [0, 2, 1, 1, 0, 0], [0, 3, 1, 2, 0, 0], 'chords-db', []),
      P('4ª casa', ["x", "x", 2, 4, 4, 4], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('4ª casa (pestana)', ["x", 7, 6, 4, 4, 4], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'Emaj7#5': [
      P('4ª casa', [0, 3, 2, 1, 4, 4], [0, 3, 2, 1, 4, 4], 'chords-db', [{"fret": 4, "from": 4, "to": 5}]),
      P('4ª casa (pestana)', [4, 7, 6, 5, 4, 4], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('Padrão', ["x", 7, 10, 8, 9, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', [])
      ],
      'Emaj7b5': [
      P('1ª casa', [0, 1, 1, 1, 4, 0], [0, 1, 1, 1, 4, 0], 'chords-db', [{"fret": 1, "from": 1, "to": 4}]),
      P('Padrão', ["x", "x", 2, 3, 4, 4], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 7, 8, 8, 9, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Emaj7sus2': [
      P('2ª casa', [0, 2, 2, 4, 4, 2], [0, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa', [0, 2, 4, 4, 4, 2], [0, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 2, 4, 4, 2], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'Emaj9': [
      P('Abertura', [0, 2, 1, 1, 0, 2], [0, 3, 1, 2, 0, 4], 'chords-db', []),
      P('2ª casa (pestana)', [4, 2, 2, 4, 4, 2], [2, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", 7, 6, 8, 7, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', [])
      ],
      'Emmaj11': [
      P('Abertura', [0, 0, 1, 0, 0, 2], [0, 0, 1, 0, 0, 3], 'chords-db', []),
      P('2ª casa (pestana)', ["x", 2, 2, 2, 4, 3], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", 7, 5, 8, 7, 5], [0, 2, 1, 4, 3, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Emmaj7': [
      P('Abertura', [0, 2, 1, 0, 0, 0], [0, 2, 1, 0, 0, 0], 'chords-db', []),
      P('2ª casa', [0, 2, 2, 4, 4, 3], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 7, 5, 4, 4, "x"], [0, 4, 2, 1, 1, 0], 'chords-db', [{"fret": 4, "from": 1, "to": 4}])
      ],
      'Emmaj7b5': [
      P('Abertura', [0, 1, 1, 0, "x", 0], [0, 1, 2, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 3, 4, 3], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('8ª casa', [6, 7, 8, 8, 8, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 8, "from": 2, "to": 4}])
      ],
      'Emmaj9': [
      P('Abertura', [0, 2, 1, 0, 0, 2], [0, 2, 1, 0, 0, 3], 'chords-db', []),
      P('4ª casa', [0, "x", 4, 4, 4, 3], [0, 0, 2, 2, 4, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 4}]),
      P('Abertura', [0, 10, 9, 8, 7, 0], [0, 4, 3, 2, 1, 0], 'chords-db', [])
      ],
      'Esus': [
      P('Abertura', [0, 0, 2, 2, 0, 0], [0, 0, 1, 2, 0, 0], 'chords-db', []),
      P('Abertura', [0, 0, 2, 4, 0, 0], [0, 0, 1, 3, 0, 0], 'chords-db', []),
      P('Abertura', [0, 2, 2, 2, 0, 0], [0, 1, 2, 3, 0, 0], 'chords-db', [])
      ],
      'Esus2': [
      P('2ª casa (pestana)', [2, 2, 2, 4, 5, 2], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', [0, 7, 9, 9, 7, 7], [0, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}]),
      P('Abertura', [0, 9, 9, 9, 0, 0], [0, 1, 2, 3, 0, 0], 'chords-db', [])
      ],
      'Esus2sus4': [
      P('Abertura', [0, 0, 2, 2, 0, 2], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Abertura', [0, 2, 2, 2, 0, 2], [0, 1, 2, 3, 0, 4], 'chords-db', []),
      P('[7]ª casa (pestana)', ["x", 7, 7, 9, 7, 7], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Esus4': [
      P('Abertura', [0, 2, 2, 2, 0, 0], [0, 2, 3, 4, 0, 0], 'chords-db', []),
      P('2ª casa', [0, 2, 2, 4, 5, 5], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', [7, 7, 9, 9, 10, 7], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'F': [
      P('1ª casa (pestana)', [1, 3, 3, 2, 1, 1], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa', ["x", "x", 3, 2, 1, 1], [0, 0, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 3, 5, 6, 5], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'F#': [
      P('2ª casa (pestana)', [2, 4, 4, 3, 2, 2], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 7, 6], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', [6, 9, 8, 6, 7, 6], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}])
      ],
      'F#/A': [
      P('2ª casa', ["x", 0, 4, 3, 2, 2], [0, 0, 3, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 4, 6, 7, 6], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('6ª casa', ["x", 0, 8, 6, 7, 6], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'F#/Ab': [
      P('4ª casa (pestana)', [4, 4, 4, 6, 7, 6], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 6, 7, 6], [0, 0, 1, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', ["x", 11, 11, 11, 11, 14], [0, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 11, "from": 1, "to": 5}])
      ],
      'F#/B': [
      P('2ª casa (pestana)', ["x", 2, 4, 3, 2, 2], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 9, 6, 7, 6], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", "x", 9, 11, 11, 9], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'F#/Bb': [
      P('6ª casa (pestana)', [6, 9, 8, 6, 7, 6], [1, 4, 3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, "x", "x", 6, 7, 6], [1, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 8, 6, 7, 6], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'F#/C': [
      P('2ª casa (pestana)', ["x", 3, 4, 3, 2, 2], [0, 2, 4, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 10, 11, 11, 9], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 3, 4, 3, 2, "x"], [0, 2, 4, 3, 1, 0], 'chords-db', [])
      ],
      'F#/C#': [
      P('2ª casa (pestana)', ["x", 4, 4, 3, 2, 2], [0, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 7, 6], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 11, 11, 11, 9], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'F#/D': [
      P('2ª casa', ["x", "x", 0, 3, 2, 2], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('2ª casa (pestana)', ["x", 5, 4, 3, 2, 2], [0, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('6ª casa', ["x", "x", 0, 6, 7, 6], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 3, "to": 5}])
      ],
      'F#/E': [
      P('2ª casa', [0, 4, 4, 3, 2, 2], [0, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 2, 3, 2, 2], [0, 0, 1, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('4ª casa', [0, 4, 4, 6, 7, 6], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'F#/Eb': [
      P('Padrão', ["x", "x", 1, 3, 2, 2], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 8, 6, 7, 6], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 6, 7, 9], [0, 1, 3, 1, 2, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'F#/F': [
      P('2ª casa (pestana)', ["x", "x", 3, 3, 2, 2], [0, 0, 2, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 8, 8, 6, 7, 6], [0, 3, 4, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('11ª casa (pestana)', [13, 13, 11, 11, 11, 14], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 11, "from": 0, "to": 5}])
      ],
      'F#/G': [
      P('2ª casa (pestana)', ["x", "x", 5, 3, 2, 2], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 5, 6, 7, 6], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('11ª casa', ["x", 10, 11, 11, 11, "x"], [0, 1, 2, 2, 2, 0], 'chords-db', [{"fret": 11, "from": 2, "to": 4}])
      ],
      'F#11': [
      P('Abertura', [2, 1, 2, 1, 0, 0], [3, 1, 4, 2, 0, 0], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 4, 5, 6], [1, 1, 1, 1, 2, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', ["x", 9, 8, 9, 7, 7], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F#13': [
      P('Abertura', [2, 2, 1, 3, 0, 0], [2, 3, 1, 4, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 3, 4, 4], [1, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", 9, 8, 8, 7, 0], [0, 4, 2, 3, 1, 0], 'chords-db', [])
      ],
      'F#5': [
      P('Padrão', [2, 4, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 9, 11, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 4, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'F#6': [
      P('Padrão', [2, "x", 1, 3, 2, "x"], [2, 0, 1, 4, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, "x", 4, 3, 4, 2], [1, 0, 3, 2, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 4, 6], [0, 1, 1, 3, 1, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'F#69': [
      P('1ª casa (pestana)', [2, 1, 1, 1, 2, 2], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 3, 4, 4], [0, 0, 2, 1, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 6, 6, 6, 7, 6], [0, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'F#7': [
      P('2ª casa (pestana)', [2, 4, 2, 3, 2, 2], [1, 3, 1, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 5, 6], [0, 1, 1, 3, 2, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", 9, 8, 9, 7, "x"], [0, 3, 2, 4, 1, 0], 'chords-db', [])
      ],
      'F#7#9': [
      P('2ª casa', [2, 1, 2, 2, 2, 2], [2, 1, 3, 3, 3, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [2, 4, 2, 3, 2, 5], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 3, 5, 5], [0, 0, 2, 1, 3, 4], 'chords-db', [])
      ],
      'F#7b5': [
      P('Padrão', [2, "x", 2, 3, 1, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 5, 5, 6], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 7, 8, 9, 7, 8], [0, 1, 2, 4, 1, 3], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F#7b9': [
      P('Abertura', [2, 1, 2, 0, 2, 0], [2, 1, 3, 0, 4, 0], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 4, 3, 5, 3], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", 9, 8, 9, 8, 9], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'F#7sus4': [
      P('2ª casa (pestana)', [2, 4, 2, 4, 2, 2], [1, 3, 1, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 6, 5, 7], [0, 0, 1, 3, 2, 4], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 9, 9, 9, 7, 7], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F#9': [
      P('2ª casa (pestana)', [2, 4, 2, 3, 2, 4], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 3, 5, 4], [0, 0, 2, 1, 4, 3], 'chords-db', []),
      P('9ª casa', [9, 9, 8, 9, 9, 9], [2, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'F#9#11': [
      P('1ª casa (pestana)', [2, 1, 2, 1, 1, 2], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 5, 6], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 9, 8, 9, 9, 8], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'F#9b5': [
      P('1ª casa (pestana)', [2, 1, 2, 1, 1, 2], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa', [2, 1, 2, 1, 1, 0], [2, 1, 3, 1, 1, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('3ª casa (pestana)', ["x", 3, 4, 3, 5, 4], [0, 1, 2, 1, 4, 3], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'F#add11': [
      P('7ª casa', ["x", 9, 8, 6, 7, 7], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 7, "from": 1, "to": 5}]),
      P('Padrão', [2, 1, 4, 3, 0, "x"], [2, 1, 4, 3, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 4, 3, 0, "x"], [1, 3, 4, 2, 0, 0], 'chords-db', [])
      ],
      'F#add9': [
      P('2ª casa', [2, 1, "x", 1, 2, 2], [3, 1, 0, 2, 4, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 3, 2, 4], [0, 0, 3, 2, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 9, 8, 6, 9, 6], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'F#alt': [
      P('Padrão', ["x", "x", 4, 3, 1, 2], [0, 0, 4, 3, 1, 2], 'chords-db', []),
      P('2ª casa (pestana)', [2, 3, 4, 3, "x", 2], [1, 2, 4, 3, 0, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 7, 6], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'F#aug': [
      P('Padrão', ["x", "x", 4, 3, 3, 2], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 4, 3, 3, "x"], [0, 0, 2, 1, 1, 0], 'chords-db', [{"fret": 3, "from": 2, "to": 4}]),
      P('7ª casa (pestana)', ["x", 9, 8, 7, 7, "x"], [0, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 7, "from": 1, "to": 4}])
      ],
      'F#aug7': [
      P('Padrão', [2, "x", 2, 3, 3, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 7, 5, 6], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 9, 8, 7, 7, 0], [0, 4, 3, 1, 2, 0], 'chords-db', [])
      ],
      'F#aug9': [
      P('1ª casa', [2, 1, 2, 1, 3, 0], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('Padrão', ["x", 9, 8, 7, 9, 0], [0, 3, 2, 1, 4, 0], 'chords-db', []),
      P('9ª casa', ["x", 9, 8, 9, 9, 10], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'F#dim': [
      P('Padrão', [2, 0, "x", 2, 1, "x"], [2, 0, 0, 3, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 4, 5, "x", 5], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 9, 7, "x", 7, 8], [0, 4, 1, 0, 2, 3], 'chords-db', [])
      ],
      'F#dim7': [
      P('1ª casa (pestana)', [2, "x", 1, 2, 1, "x"], [2, 0, 1, 3, 1, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 4}]),
      P('2ª casa (pestana)', [2, 3, 4, 2, 4, 2], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 4, 5], [0, 0, 1, 3, 2, 4], 'chords-db', [])
      ],
      'F#m': [
      P('2ª casa (pestana)', [2, 4, 4, 2, 2, 2], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 7, 5], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 7, 6, 7, 5], [0, 0, 3, 2, 4, 1], 'chords-db', [])
      ],
      'F#m/A': [
      P('2ª casa', ["x", 0, 4, 2, 2, 2], [0, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('2ª casa', ["x", 0, 4, 2, 2, 5], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('2ª casa (pestana)', [5, 4, 4, 2, 2, 2], [4, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'F#m/Ab': [
      P('2ª casa', [4, 0, 4, 2, 2, 2], [3, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [4, 4, 4, 2, 2, 2], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [4, 4, 4, 6, 7, 5], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'F#m/B': [
      P('2ª casa (pestana)', ["x", 2, 4, 2, 2, 2], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 2, 4, 2, 2, 5], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', ["x", "x", 9, 11, 10, 9], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 9, "from": 2, "to": 5}])
      ],
      'F#m/Bb': [
      P('Padrão', ["x", "x", 8, 6, 7, 5], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 8, 11, 10, 9], [0, 0, 1, 4, 3, 2], 'chords-db', []),
      P('14ª casa', ["x", 13, 11, 14, 14, 14], [0, 3, 1, 4, 4, 4], 'chords-db', [{"fret": 14, "from": 3, "to": 5}])
      ],
      'F#m/C': [
      P('2ª casa (pestana)', ["x", 3, 4, 2, 2, 2], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 3, 4, 2, 2, 5], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 10, 11, 10, 9], [0, 0, 2, 4, 3, 1], 'chords-db', [])
      ],
      'F#m/C#': [
      P('2ª casa (pestana)', ["x", 4, 4, 2, 2, 2], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa (pestana)', ["x", 4, 4, 2, 2, 5], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 7, 5], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'F#m/D': [
      P('2ª casa', ["x", "x", 0, 2, 2, 2], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('2ª casa (pestana)', ["x", 5, 4, 2, 2, 2], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 0, 6, 7, 5], [0, 0, 0, 2, 3, 1], 'chords-db', [])
      ],
      'F#m/E': [
      P('2ª casa', [0, 0, 4, 2, 2, 2], [0, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('2ª casa', [0, 4, 4, 2, 2, 2], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('2ª casa', [0, 4, 4, 2, 2, 5], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}])
      ],
      'F#m/Eb': [
      P('2ª casa', ["x", "x", 1, 2, 2, 2], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 2, "from": 3, "to": 5}]),
      P('11ª casa (pestana)', [11, 12, 11, 11, 14, 14], [1, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 11, "from": 0, "to": 5}]),
      P('11ª casa (pestana)', [11, 12, 11, 14, 14, 14], [1, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 11, "from": 0, "to": 5}])
      ],
      'F#m/F': [
      P('2ª casa (pestana)', ["x", "x", 3, 2, 2, 2], [0, 0, 2, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('11ª casa (pestana)', [13, 12, 11, 11, 14, 14], [3, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 11, "from": 0, "to": 5}]),
      P('14ª casa', [13, 12, 11, 14, 14, 14], [3, 2, 1, 4, 4, 4], 'chords-db', [{"fret": 14, "from": 3, "to": 5}])
      ],
      'F#m/G': [
      P('2ª casa', [3, 0, 4, 2, 2, 2], [2, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [3, 4, 4, 2, 2, 2], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 5, 2, 2, 2], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'F#m11': [
      P('Abertura', [2, 0, 2, 1, 0, 0], [2, 0, 3, 1, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 2, 2, 4], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 5, 5], [0, 0, 1, 1, 2, 3], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'F#m6': [
      P('2ª casa', [2, "x", 1, 2, 2, 2], [2, 0, 1, 3, 3, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 4, 5], [0, 1, 1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', ["x", 9, 7, 8, 7, 9], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F#m69': [
      P('1ª casa', [2, 0, 1, 1, 2, 2], [2, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa', [2, 4, 4, 2, 4, 4], [1, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', [5, 4, 4, 6, 4, 4], [2, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'F#m7': [
      P('Padrão', [2, "x", 2, 2, 2, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('Padrão', [14, "x", 14, 14, 14, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 4, 2, 2, 2, 2], [1, 3, 1, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'F#m7b5': [
      P('Abertura', [2, 0, 2, 2, 1, 0], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('5ª casa', ["x", "x", 4, 5, 5, 5], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('Padrão', ["x", 9, 10, 9, 10, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', [])
      ],
      'F#m9': [
      P('Abertura', [2, 0, 2, 1, 2, 0], [2, 0, 3, 1, 4, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 4, 2, 2, 2, 4], [1, 2, 1, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('9ª casa', ["x", 9, 7, 9, 9, 9], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'F#m9/A': [
      P('4ª casa (pestana)', [5, 4, 4, 6, 5, 4], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', [5, "x", 4, 6, 5, 4], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}])
      ],
      'F#m9/E': [
      P('2ª casa', [0, 0, 4, 2, 2, 4], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('2ª casa', [0, 4, 4, 2, 2, 4], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 7, 4, 6, 5, 4], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}])
      ],
      'F#madd9': [
      P('2ª casa (pestana)', ["x", "x", 4, 2, 2, 4], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('2ª casa (pestana)', [2, 4, 4, 2, 2, 4], [1, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", 9, 7, 6, 9, "x"], [0, 3, 2, 1, 4, 0], 'chords-db', [])
      ],
      'F#maj11': [
      P('2ª casa (pestana)', [2, 2, 3, 3, 2, 2], [1, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 4, 6, 6], [0, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('Padrão', ["x", 9, 8, 10, 0, 9], [0, 2, 1, 4, 0, 3], 'chords-db', [])
      ],
      'F#maj13': [
      P('1ª casa (pestana)', [2, 1, 1, 1, 2, 1], [2, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 6, 4, 4, 6, 6], [0, 2, 1, 1, 3, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa', ["x", 9, 8, 8, 6, 6], [0, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'F#maj7': [
      P('2ª casa (pestana)', [2, 4, 3, 3, 2, 2], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 6, 6], [0, 1, 1, 3, 3, 3], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 9, 8, 6, 6, 6], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'F#maj7#5': [
      P('Padrão', [2, "x", 3, 3, 3, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('6ª casa (pestana)', [6, 9, 8, 7, 6, 6], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('Padrão', ["x", 9, 12, 10, 11, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', [])
      ],
      'F#maj7b5': [
      P('1ª casa (pestana)', [2, 1, 3, 3, 1, 1], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 6, 6], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 9, 8, 10, 11, 8], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'F#maj7sus2': [
      P('1ª casa (pestana)', ["x", "x", 4, 1, 2, 1], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 6, 6, 4], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}]),
      P('9ª casa (pestana)', ["x", 9, 11, 10, 9, 9], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'F#maj9': [
      P('1ª casa (pestana)', [2, 1, 3, 1, 2, 1], [2, 1, 4, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [2, "x", 3, 3, 2, 4], [1, 0, 2, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 3, 6, 4], [0, 0, 2, 1, 4, 3], 'chords-db', [])
      ],
      'F#mmaj11': [
      P('2ª casa (pestana)', [2, 2, 3, 2, 2, 4], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 4, 6, 5], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('7ª casa (pestana)', ["x", 9, 7, 10, 9, 7], [0, 2, 1, 4, 3, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F#mmaj7': [
      P('2ª casa (pestana)', [2, 4, 3, 2, 2, 2], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 6, 5], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 9, 7, 6, 6, "x"], [0, 4, 2, 1, 1, 0], 'chords-db', [{"fret": 6, "from": 1, "to": 4}])
      ],
      'F#mmaj7b5': [
      P('2ª casa (pestana)', [2, 3, 3, 2, "x", 2], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 6, 5], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('10ª casa', [8, 9, 10, 10, 10, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 10, "from": 2, "to": 4}])
      ],
      'F#mmaj9': [
      P('1ª casa', [2, 0, 3, 1, 2, 1], [2, 0, 4, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', [2, 0, 3, 1, 2, "x"], [2, 0, 4, 1, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 4, 3, 2, 2, 4], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}])
      ],
      'F#sus': [
      P('2ª casa (pestana)', [2, 2, 4, 4, 2, 2], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', [2, 4, 4, 4, 2, 2], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 4, 4, 2, 2], [0, 0, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}])
      ],
      'F#sus2': [
      P('Padrão', [2, "x", "x", 1, 2, 2], [2, 0, 0, 1, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 6, 7, 4], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 11, 11, 9, 9], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'F#sus2sus4': [
      P('2ª casa', [2, 2, 4, 4, 2, 4], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('9ª casa', ["x", 9, 9, 11, 9, 9], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}]),
      P('[6, 7]ª casa', ["x", 9, 6, 6, 7, 7], [0, 4, 1, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 5}, {"fret": 7, "from": 1, "to": 5}])
      ],
      'F#sus4': [
      P('2ª casa (pestana)', [2, 4, 4, 4, 2, 2], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 4, 6, 7, 7], [0, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('9ª casa (pestana)', [9, 9, 11, 11, 12, 9], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 5}])
      ],
      'F/A': [
      P('1ª casa', ["x", 0, 3, 2, 1, 1], [0, 0, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 3, 5, 6, 5], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('5ª casa', ["x", 0, 7, 5, 6, 5], [0, 0, 3, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'F/Ab': [
      P('1ª casa', [4, 0, 3, 2, 1, 1], [4, 0, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 6, 5, 6, 5], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('10ª casa (pestana)', ["x", 11, 10, 10, 10, 13], [0, 2, 1, 1, 1, 4], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'F/B': [
      P('1ª casa (pestana)', ["x", 2, 3, 2, 1, 1], [0, 2, 4, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 9, 10, 10, 8], [0, 0, 2, 3, 4, 1], 'chords-db', []),
      P('Padrão', ["x", 2, 3, 2, 1, "x"], [0, 2, 4, 3, 1, 0], 'chords-db', [])
      ],
      'F/Bb': [
      P('1ª casa (pestana)', ["x", 1, 3, 2, 1, 1], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 8, 5, 6, 5], [0, 0, 4, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 8, 10, 10, 8], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'F/C': [
      P('1ª casa (pestana)', ["x", 3, 3, 2, 1, 1], [0, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 5, 6, 5], [0, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 10, 10, 10, 8], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'F/C#': [
      P('1ª casa (pestana)', ["x", 4, 3, 2, 1, 1], [0, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 11, 10, 10, 8], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 11, 14, 13, 13], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'F/D': [
      P('1ª casa', ["x", "x", 0, 2, 1, 1], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 3, "to": 5}]),
      P('5ª casa', ["x", "x", 0, 5, 6, 5], [0, 0, 0, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 3, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 7, 5, 6, 5], [0, 1, 3, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'F/D#': [
      P('1ª casa', ["x", "x", 1, 2, 1, 1], [0, 0, 1, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('5ª casa', ["x", 6, 7, 5, 6, 5], [0, 2, 4, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('5ª casa', ["x", 6, 3, 5, 6, 5], [0, 3, 1, 2, 4, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'F/E': [
      P('1ª casa', [0, 0, 3, 2, 1, 1], [0, 0, 3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('1ª casa', [0, 3, 3, 2, 1, 1], [0, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 2, 2, 1, 1], [0, 0, 2, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}])
      ],
      'F/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 2, 1, 1], [0, 0, 1, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('5ª casa (pestana)', ["x", 6, 7, 5, 6, 5], [0, 2, 4, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', [11, 12, 10, 10, 10, 13], [2, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 10, "from": 0, "to": 5}])
      ],
      'F/F#': [
      P('1ª casa', [2, 0, 3, 2, 1, 1], [2, 0, 4, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 4, 2, 1, 1], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 4, 5, 6, 5], [0, 0, 1, 2, 4, 3], 'chords-db', [])
      ],
      'F/G': [
      P('1ª casa', [3, 0, 3, 2, 1, 1], [3, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 3, 5, 6, 5], [1, 1, 1, 2, 4, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 5, 5, 6, 5], [0, 0, 1, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'F11': [
      P('1ª casa (pestana)', [1, 1, 1, 2, 1, 1], [1, 1, 1, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 3, 3, 4, 5], [1, 1, 1, 1, 2, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', ["x", 8, 7, 8, 6, 6], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'F13': [
      P('1ª casa (pestana)', [1, 3, 1, 2, 3, 1], [1, 3, 1, 2, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [1, 1, 1, 2, 3, 3], [1, 1, 1, 2, 3, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('10ª casa', ["x", 8, 7, 8, 10, 10], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 10, "from": 4, "to": 5}])
      ],
      'F5': [
      P('Padrão', [1, 3, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 8, 10, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [1, 3, 3, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'F6': [
      P('1ª casa (pestana)', [1, "x", 3, 2, 3, 1], [1, 0, 3, 2, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 5, 3, 5], [0, 1, 1, 3, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", 8, 7, 7, 6, "x"], [0, 4, 2, 3, 1, 0], 'chords-db', [])
      ],
      'F69': [
      P('Abertura', [1, 0, 0, 0, 1, 1], [1, 0, 0, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 2, 3, 3], [0, 0, 2, 1, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 5, 5, 5, 6, 5], [0, 1, 1, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'F7': [
      P('1ª casa (pestana)', [1, 3, 1, 2, 1, 1], [1, 3, 1, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 5, 4, 5], [0, 1, 1, 3, 2, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 10, 8, 10, 8], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'F7#9': [
      P('1ª casa (pestana)', [1, 3, 1, 2, 1, 4], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 2, 4, 4], [0, 0, 2, 1, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 8, 7, 8, 9, "x"], [0, 2, 1, 3, 4, 0], 'chords-db', [])
      ],
      'F7b5': [
      P('Abertura', [1, 0, 1, 2, 0, 1], [1, 0, 2, 4, 0, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 4, 4, 5], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 7, 8, 6, 7], [0, 0, 2, 4, 1, 3], 'chords-db', [])
      ],
      'F7b9': [
      P('1ª casa (pestana)', [1, 3, 1, 2, 1, 2], [1, 4, 1, 2, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('2ª casa (pestana)', ["x", "x", 3, 2, 4, 2], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', ["x", 8, 7, 8, 7, 8], [0, 2, 1, 3, 1, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F7sus4': [
      P('1ª casa (pestana)', [1, 3, 1, 3, 1, 1], [1, 3, 1, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('6ª casa (pestana)', [6, 8, 8, 8, 6, 6], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 10, 8, 11, 8], [1, 1, 3, 1, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'F9': [
      P('1ª casa (pestana)', [1, 3, 1, 2, 1, 3], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 2, 4, 3], [0, 0, 2, 1, 4, 3], 'chords-db', []),
      P('8ª casa', [8, 8, 7, 8, 8, 8], [2, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'F9#11': [
      P('Abertura', [1, 0, 1, 0, 0, 1], [1, 0, 2, 0, 0, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 4, 4, 5], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 8, 7, 8, 8, 7], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'F9b5': [
      P('Abertura', [1, 0, 1, 0, 0, 1], [1, 0, 2, 0, 0, 3], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 8, 7, 8, 8, 7], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}]),
      P('Padrão', ["x", 8, 9, 0, 10, 11], [0, 1, 2, 0, 3, 4], 'chords-db', [])
      ],
      'Fadd11': [
      P('6ª casa', ["x", 8, 7, 5, 6, 6], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', [13, 12, 10, 10, 11, "x"], [4, 3, 1, 1, 2, 0], 'chords-db', [{"fret": 10, "from": 0, "to": 4}])
      ],
      'Fadd9': [
      P('Padrão', ["x", "x", 3, 2, 1, 3], [0, 0, 3, 2, 1, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 0, 6, 5], [0, 0, 1, 0, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 8, 7, 5, 8, 5], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Falt': [
      P('Padrão', [1, 2, 3, 2, 0, "x"], [1, 2, 4, 3, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 4, 0, 5], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 8, 9, 10, 10, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Faug': [
      P('Padrão', ["x", "x", 3, 2, 2, 1], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('6ª casa (pestana)', ["x", 8, 7, 6, 6, "x"], [0, 3, 2, 1, 1, 0], 'chords-db', [{"fret": 6, "from": 1, "to": 4}]),
      P('Padrão', ["x", 8, "x", 10, 10, 9], [0, 1, 0, 3, 4, 2], 'chords-db', [])
      ],
      'Faug7': [
      P('Padrão', [1, 0, 1, 2, 2, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 6, 4, 5], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 8, 11, 8, 10, 9], [0, 1, 4, 1, 3, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Faug9': [
      P('Abertura', [1, 0, 1, 0, 2, 1], [1, 0, 2, 0, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 6, 5, 6, 6, 5], [1, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('8ª casa', ["x", 8, 7, 8, 8, 9], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Fdim': [
      P('Padrão', ["x", "x", 3, 4, "x", 4], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 8, 6, "x", 6, 7], [0, 4, 1, 0, 2, 3], 'chords-db', []),
      P('Padrão', ["x", 8, 9, 10, 9, "x"], [0, 1, 2, 4, 3, 0], 'chords-db', [])
      ],
      'Fdim7': [
      P('Abertura', [1, "x", 0, 1, 0, 1], [1, 0, 0, 2, 0, 3], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 3, 4, 3, 4], [0, 0, 1, 3, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('7ª casa (pestana)', [7, 8, 9, 7, 9, 7], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Fm': [
      P('1ª casa (pestana)', [1, 3, 3, 1, 1, 1], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 5, 6, 4], [0, 0, 1, 3, 4, 2], 'chords-db', []),
      P('8ª casa (pestana)', ["x", 8, 10, 10, 9, 8], [0, 1, 3, 4, 2, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Fm/A': [
      P('1ª casa', ["x", 0, 3, 1, 1, 1], [0, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('1ª casa', ["x", 0, 3, 1, 1, 4], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 0, 3, 5, 6, 4], [0, 0, 1, 3, 4, 2], 'chords-db', [])
      ],
      'Fm/Ab': [
      P('1ª casa (pestana)', [4, 3, 3, 1, 1, 1], [4, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 6, 5, 6, 4], [0, 0, 3, 2, 4, 1], 'chords-db', []),
      P('10ª casa (pestana)', ["x", 11, 10, 10, 13, 13], [0, 2, 1, 1, 4, 4], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'Fm/B': [
      P('1ª casa (pestana)', ["x", 2, 3, 1, 1, 1], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", 2, 3, 1, 1, 4], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 9, 10, 9, 8], [0, 0, 2, 4, 3, 1], 'chords-db', [])
      ],
      'Fm/Bb': [
      P('1ª casa (pestana)', ["x", 1, 3, 1, 1, 1], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", 1, 3, 1, 1, 4], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", "x", 8, 10, 9, 8], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 8, "from": 2, "to": 5}])
      ],
      'Fm/C': [
      P('1ª casa (pestana)', ["x", 3, 3, 1, 1, 1], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", 3, 3, 1, 1, 4], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 5, 6, 4], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Fm/C#': [
      P('1ª casa (pestana)', ["x", 4, 3, 1, 1, 1], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('4ª casa (pestana)', ["x", 4, 6, 5, 6, 4], [0, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 4, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 11, 10, 9, 8], [0, 0, 4, 3, 2, 1], 'chords-db', [])
      ],
      'Fm/D': [
      P('1ª casa', ["x", "x", 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 0, 5, 6, 4], [0, 0, 0, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 0, 10, 9, 8], [0, 0, 0, 3, 2, 1], 'chords-db', [])
      ],
      'Fm/E': [
      P('1ª casa', [0, 3, 3, 1, 1, 1], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa', [0, 3, 3, 1, 1, 4], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 2, 1, 1, 1], [0, 0, 2, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}])
      ],
      'Fm/Eb': [
      P('1ª casa (pestana)', ["x", "x", 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 6, 6, 5, 6, "x"], [0, 2, 3, 1, 4, 0], 'chords-db', []),
      P('10ª casa (pestana)', [11, 11, 10, 10, "x", "x"], [2, 3, 1, 1, 0, 0], 'chords-db', [{"fret": 10, "from": 0, "to": 3}])
      ],
      'Fm/F#': [
      P('1ª casa (pestana)', [2, 3, 3, 1, 1, 1], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 4, 1, 1, 1], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 4, 5, 6, 4], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'Fm/G': [
      P('1ª casa (pestana)', [3, 3, 3, 1, 1, 1], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 3, 5, 6, 4], [1, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 5, 6, 4], [0, 0, 2, 3, 4, 1], 'chords-db', [])
      ],
      'Fm11': [
      P('1ª casa (pestana)', [1, 1, 1, 1, 1, 3], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 4, 4], [0, 0, 1, 1, 2, 3], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 8, 6, 8, 8, 6], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Fm6': [
      P('Padrão', [1, "x", 0, 1, 1, 1], [1, 0, 0, 2, 3, 4], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 3, 5, 3, 4], [0, 0, 1, 3, 1, 2], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", 8, 6, 7, 6, 8], [0, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Fm69': [
      P('[1, 3]ª casa (pestana)', [1, 3, 3, 1, 3, 3], [1, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}, {"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', [4, "x", 3, 5, 3, 3], [2, 0, 1, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", 8, 6, 7, 8, "x"], [0, 3, 1, 2, 4, 0], 'chords-db', [])
      ],
      'Fm7': [
      P('Padrão', [1, "x", 1, 1, 1, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('Padrão', [13, "x", 13, 13, 13, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('1ª casa (pestana)', [1, 3, 1, 1, 1, 1], [1, 3, 1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}])
      ],
      'Fm7b5': [
      P('Padrão', [1, "x", 1, 1, 0, "x"], [1, 0, 2, 3, 0, 0], 'chords-db', []),
      P('4ª casa', ["x", "x", 3, 4, 4, 4], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 4, "from": 3, "to": 5}]),
      P('Padrão', ["x", 8, 9, 8, 9, "x"], [0, 1, 3, 2, 4, 0], 'chords-db', [])
      ],
      'Fm9': [
      P('1ª casa (pestana)', [1, 3, 1, 1, 1, 3], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", 3, 3, 0, 4, 4], [0, 1, 2, 0, 3, 4], 'chords-db', []),
      P('8ª casa', ["x", 8, 6, 8, 8, 8], [0, 2, 1, 3, 4, 4], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Fm9/Ab': [
      P('3ª casa (pestana)', [4, 3, 3, 5, 4, 3], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [4, "x", 3, 5, 4, 3], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'Fm9/Eb': [
      P('3ª casa (pestana)', ["x", 6, 3, 5, 4, 3], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', [11, 8, 10, 8, 8, 8], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [11, 8, 10, 10, 8, 8], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Fmadd9': [
      P('1ª casa (pestana)', ["x", "x", 3, 1, 1, 3], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 2, "to": 5}]),
      P('Padrão', ["x", 8, 6, 5, 8, "x"], [0, 3, 2, 1, 4, 0], 'chords-db', []),
      P('Padrão', ["x", 8, 6, 0, 6, 8], [0, 3, 1, 0, 2, 4], 'chords-db', [])
      ],
      'Fmaj11': [
      P('1ª casa (pestana)', [1, 1, 2, 2, 1, 1], [1, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 5, 5], [0, 0, 1, 1, 3, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 8, 9, 10, 8], [1, 1, 1, 2, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Fmaj13': [
      P('Abertura', [1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 2, 3, 0], [0, 0, 2, 1, 3, 0], 'chords-db', []),
      P('5ª casa', ["x", 8, 7, 7, 5, 5], [0, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Fmaj7': [
      P('Padrão', ["x", "x", 3, 2, 1, 0], [0, 0, 3, 2, 1, 0], 'chords-db', []),
      P('1ª casa (pestana)', [1, 3, 2, 2, 1, 1], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 5, 5, 5], [0, 1, 1, 3, 3, 3], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Fmaj7#5': [
      P('Abertura', [1, 0, 2, 2, 2, 0], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 7, 6, 5, 5], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('Padrão', ["x", 8, 11, 9, 10, "x"], [0, 1, 4, 2, 3, 0], 'chords-db', [])
      ],
      'Fmaj7b5': [
      P('Abertura', [1, 0, 2, 2, 0, 0], [1, 0, 2, 3, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 4, 5, 5], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 8, 9, 9, 10, "x"], [0, 1, 2, 3, 4, 0], 'chords-db', [])
      ],
      'Fmaj7sus2': [
      P('Abertura', ["x", "x", 3, 0, 1, 0], [0, 0, 3, 0, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 3, 5, 5, 3], [0, 0, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('8ª casa (pestana)', ["x", 8, 10, 9, 8, 8], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Fmaj9': [
      P('Abertura', [1, 0, 2, 0, 1, 0], [1, 0, 3, 0, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 2, 2, 1, 3], [0, 0, 2, 3, 1, 4], 'chords-db', []),
      P('Padrão', ["x", 8, 7, 9, 8, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', [])
      ],
      'Fmmaj11': [
      P('1ª casa (pestana)', [1, 1, 2, 1, 1, 3], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 3, 3, 5, 4], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 8, 6, 9, 8, 6], [0, 2, 1, 4, 3, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Fmmaj7': [
      P('1ª casa (pestana)', [1, 3, 2, 1, 1, 1], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 5, 5, 4], [0, 0, 1, 3, 4, 2], 'chords-db', []),
      P('8ª casa (pestana)', [8, 8, 10, 9, 9, 8], [1, 1, 4, 2, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Fmmaj7b5': [
      P('1ª casa', [1, 2, 2, 1, 0, 0], [1, 2, 3, 1, 0, 0], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', ["x", "x", 3, 4, 5, 4], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('9ª casa', [7, 8, 9, 9, 9, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 9, "from": 2, "to": 4}])
      ],
      'Fmmaj9': [
      P('1ª casa (pestana)', [1, 3, 2, 1, 1, 3], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 0, 5, 4], [0, 0, 1, 0, 4, 2], 'chords-db', []),
      P('Padrão', ["x", 8, 6, 9, 8, "x"], [0, 2, 1, 4, 3, 0], 'chords-db', [])
      ],
      'Fsus': [
      P('1ª casa (pestana)', [1, 1, 3, 3, 1, 1], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', [1, 3, 3, 3, 1, 1], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('1ª casa (pestana)', ["x", "x", 3, 3, 1, 1], [0, 0, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 2, "to": 5}])
      ],
      'Fsus2': [
      P('1ª casa (pestana)', [1, 3, 3, "x", 1, 3], [1, 2, 3, 0, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 3, 3, 5, 6, 3], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', [8, 8, 10, 10, 8, 8], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'Fsus2sus4': [
      P('[1]ª casa', [1, 1, 3, 3, 1, 3], [1, 1, 2, 3, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('[8]ª casa', ["x", 8, 8, 10, 8, 8], [0, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}]),
      P('[5, 6]ª casa', ["x", 8, 5, 5, 6, 6], [0, 4, 1, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}, {"fret": 6, "from": 1, "to": 5}])
      ],
      'Fsus4': [
      P('1ª casa (pestana)', [1, 3, 3, 3, 1, 1], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 3, 5, 6, 6], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 8, 10, 10, 11, 8], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 5}])
      ],
      'G': [
      P('Abertura', [3, 2, 0, 0, 0, 3], [2, 1, 0, 0, 0, 3], 'chords-db', []),
      P('Abertura', [3, 2, 0, 0, 0, 3], [3, 2, 0, 0, 0, 4], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 5, 4, 3, 3], [1, 3, 4, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'G/A': [
      P('Abertura', ["x", 0, 0, 0, 0, 3], [0, 0, 0, 0, 0, 1], 'chords-db', []),
      P('Abertura', ["x", 0, 0, 4, 0, 3], [0, 0, 0, 2, 0, 1], 'chords-db', []),
      P('3ª casa', ["x", 0, 0, 4, 3, 3], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 3, "to": 5}])
      ],
      'G/Ab': [
      P('Abertura', [4, 2, 0, 0, 0, 3], [3, 1, 0, 0, 0, 2], 'chords-db', []),
      P('3ª casa', [4, 2, 0, 0, 3, 3], [3, 1, 0, 0, 2, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 6, 4, 3, 3], [0, 0, 4, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'G/B': [
      P('Abertura', ["x", 2, 0, 0, 0, 3], [0, 1, 0, 0, 0, 2], 'chords-db', []),
      P('3ª casa', ["x", 2, 0, 0, 3, 3], [0, 1, 0, 0, 2, 2], 'chords-db', [{"fret": 3, "from": 4, "to": 5}]),
      P('Abertura', ["x", 2, 0, 4, 0, 3], [0, 1, 0, 3, 0, 2], 'chords-db', [])
      ],
      'G/Bb': [
      P('Abertura', ["x", 1, 0, 0, 0, 3], [0, 1, 0, 0, 0, 3], 'chords-db', []),
      P('Abertura', ["x", 1, 0, 4, 0, 3], [0, 1, 0, 4, 0, 3], 'chords-db', []),
      P('7ª casa (pestana)', ["x", "x", 8, 7, 8, 7], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 7, "from": 2, "to": 5}])
      ],
      'G/C': [
      P('Abertura', ["x", 3, 0, 0, 0, 3], [0, 1, 0, 0, 0, 2], 'chords-db', []),
      P('Abertura', ["x", 3, 0, 4, 0, 3], [0, 1, 0, 3, 0, 2], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 3, 5, 4, 3, 3], [0, 1, 3, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'G/C#': [
      P('Abertura', ["x", 4, 0, 0, 0, 3], [0, 2, 0, 0, 0, 1], 'chords-db', []),
      P('Abertura', ["x", 4, 0, 4, 0, 3], [0, 2, 0, 3, 0, 1], 'chords-db', []),
      P('3ª casa', ["x", 4, 0, 4, 3, 3], [0, 2, 0, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'G/D': [
      P('Abertura', ["x", "x", 0, 0, 0, 3], [0, 0, 0, 0, 0, 1], 'chords-db', []),
      P('Abertura', ["x", "x", 0, 4, 0, 3], [0, 0, 0, 2, 0, 1], 'chords-db', []),
      P('3ª casa', ["x", "x", 0, 4, 3, 3], [0, 0, 0, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 3, "to": 5}])
      ],
      'G/E': [
      P('Abertura', [0, 2, 0, 0, 0, 3], [0, 1, 0, 0, 0, 2], 'chords-db', []),
      P('3ª casa', [0, 2, 0, 0, 3, 3], [0, 1, 0, 0, 2, 2], 'chords-db', [{"fret": 3, "from": 4, "to": 5}]),
      P('Abertura', [0, 2, 0, 4, 0, 3], [0, 1, 0, 3, 0, 2], 'chords-db', [])
      ],
      'G/Eb': [
      P('Padrão', ["x", "x", 1, 4, 3, 3], [0, 0, 1, 4, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', ["x", 6, 5, 4, 3, 3], [0, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('Padrão', ["x", "x", 13, 12, 12, 10], [0, 0, 4, 2, 3, 1], 'chords-db', [])
      ],
      'G/F': [
      P('Abertura', [1, 2, 0, 0, 0, 3], [1, 2, 0, 0, 0, 3], 'chords-db', []),
      P('Abertura', [1, 2, 0, 4, 0, 3], [1, 2, 0, 4, 0, 3], 'chords-db', []),
      P('3ª casa (pestana)', ["x", "x", 3, 4, 3, 3], [0, 0, 1, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'G/F#': [
      P('Abertura', [2, 2, 0, 0, 0, 3], [1, 2, 0, 0, 0, 3], 'chords-db', []),
      P('3ª casa', [2, 2, 0, 0, 3, 3], [1, 2, 0, 0, 3, 3], 'chords-db', [{"fret": 3, "from": 4, "to": 5}]),
      P('Abertura', [2, 2, 0, 4, 0, 3], [1, 2, 0, 4, 0, 3], 'chords-db', [])
      ],
      'G11': [
      P('1ª casa', [3, 2, 0, 0, 1, 1], [3, 2, 0, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', [5, 5, 5, 5, 6, 7], [1, 1, 1, 1, 2, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 10, 9, 10, 8, 8], [0, 3, 2, 4, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'G13': [
      P('Abertura', [3, 0, 2, 0, 0, 1], [3, 0, 2, 0, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, "x", 3, 4, 5, 5], [1, 0, 1, 2, 3, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 5, 3, 4, 5, 3], [1, 3, 1, 2, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'G5': [
      P('Padrão', [3, 5, "x", "x", "x", "x"], [1, 3, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', ["x", 10, 12, "x", "x", "x"], [0, 1, 3, 0, 0, 0], 'chords-db', []),
      P('Padrão', [3, 5, 5, "x", "x", "x"], [1, 3, 4, 0, 0, 0], 'chords-db', [])
      ],
      'G6': [
      P('Abertura', [3, 2, 0, 0, 0, 0], [2, 1, 0, 0, 0, 0], 'chords-db', []),
      P('Padrão', [3, "x", 2, 4, 3, "x"], [2, 0, 1, 4, 3, 0], 'chords-db', []),
      P('5ª casa (pestana)', ["x", 5, 5, 7, 5, 7], [0, 1, 1, 3, 1, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'G69': [
      P('Abertura', [3, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], 'chords-db', []),
      P('2ª casa (pestana)', [3, 2, 2, 2, 3, 3], [2, 1, 1, 1, 3, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 4, 5, 5], [0, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'G7': [
      P('Abertura', [3, 2, 0, 0, 0, 1], [3, 2, 0, 0, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 4, 3, 3], [1, 3, 1, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 7, 6, 7], [0, 1, 1, 3, 2, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'G7#9': [
      P('Abertura', [3, 2, 0, 3, 0, 1], [3, 2, 0, 4, 0, 1], 'chords-db', []),
      P('[3, 6]ª casa (pestana)', [3, 5, 3, 4, 6, 6], [1, 3, 1, 2, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}, {"fret": 6, "from": 4, "to": 5}]),
      P('6ª casa', ["x", 5, 5, 4, 6, 6], [0, 2, 3, 1, 4, 4], 'chords-db', [{"fret": 6, "from": 4, "to": 5}])
      ],
      'G7b5': [
      P('Padrão', [3, "x", 3, 4, 2, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 6, 6, 7], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('Padrão', ["x", 10, 9, 10, 0, 9], [0, 3, 1, 4, 0, 2], 'chords-db', [])
      ],
      'G7b9': [
      P('1ª casa', [3, 2, 0, 1, 3, 1], [3, 2, 0, 1, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, "x", 3, 4, 3, 4], [1, 0, 1, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('4ª casa (pestana)', ["x", "x", 5, 4, 6, 4], [0, 0, 2, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 2, "to": 5}])
      ],
      'G7sus4': [
      P('1ª casa (pestana)', [3, 3, 0, 0, 1, 1], [2, 3, 0, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 5, 3, 5, 3, 3], [1, 3, 1, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('8ª casa (pestana)', ["x", 10, 10, 10, 8, 8], [0, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'G9': [
      P('Abertura', [3, 0, 0, 0, 0, 1], [3, 0, 0, 0, 0, 1], 'chords-db', []),
      P('2ª casa (pestana)', [3, 2, 3, 2, 3, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', [{"fret": 2, "from": 0, "to": 4}]),
      P('3ª casa (pestana)', [3, 5, 3, 4, 3, 5], [1, 3, 1, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'G9#11': [
      P('2ª casa (pestana)', [3, 2, 3, 2, 2, 3], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 6, 6, 7], [0, 0, 1, 2, 3, 4], 'chords-db', []),
      P('9ª casa (pestana)', ["x", 10, 9, 10, 10, 9], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'G9b5': [
      P('2ª casa (pestana)', [3, 2, 3, 2, 2, 3], [2, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('3ª casa', [3, 4, 3, 4, 0, 5], [1, 2, 1, 3, 0, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('9ª casa (pestana)', ["x", 10, 9, 10, 10, 9], [0, 2, 1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 1, "to": 5}])
      ],
      'Gadd11': [
      P('Abertura', [3, 2, 0, 0, 1, 3], [3, 2, 0, 0, 1, 4], 'chords-db', []),
      P('8ª casa', ["x", 10, 9, 7, 8, 8], [0, 4, 3, 1, 2, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 5}]),
      P('Abertura', [3, 2, 0, 0, 1, "x"], [3, 2, 0, 0, 1, 0], 'chords-db', [])
      ],
      'Gadd9': [
      P('Abertura', [3, 0, 0, 2, 0, 3], [2, 0, 0, 1, 0, 3], 'chords-db', []),
      P('Padrão', ["x", "x", 3, 2, 1, 4], [0, 0, 3, 2, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', ["x", 10, 9, 7, 10, 7], [0, 3, 2, 1, 4, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Galt': [
      P('Padrão', [3, 2, "x", 0, 2, 3], [3, 1, 0, 0, 2, 4], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 6, 0, 7], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Abertura', ["x", 10, 9, 0, 0, 9], [0, 3, 1, 0, 0, 2], 'chords-db', [])
      ],
      'Gaug': [
      P('Abertura', [3, 2, 1, 0, 0, "x"], [3, 2, 1, 0, 0, 0], 'chords-db', []),
      P('Padrão', [3, "x", 5, 4, 4, "x"], [1, 0, 4, 2, 3, 0], 'chords-db', []),
      P('4ª casa (pestana)', ["x", "x", 5, 4, 4, "x"], [0, 0, 2, 1, 1, 0], 'chords-db', [{"fret": 4, "from": 2, "to": 4}])
      ],
      'Gaug7': [
      P('Abertura', [3, 2, 1, 0, 0, 1], [4, 3, 1, 0, 0, 2], 'chords-db', []),
      P('Padrão', [3, "x", 3, 4, 4, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 8, 6, 7], [0, 0, 1, 4, 2, 3], 'chords-db', [])
      ],
      'Gaug9': [
      P('Abertura', [3, 0, 1, 0, 0, 1], [3, 0, 2, 0, 0, 1], 'chords-db', []),
      P('Padrão', [3, 2, 3, 2, 4, "x"], [2, 1, 3, 1, 4, 0], 'chords-db', []),
      P('10ª casa', ["x", 10, 9, 10, 10, 11], [0, 2, 1, 3, 3, 4], 'chords-db', [{"fret": 10, "from": 1, "to": 5}])
      ],
      'Gdim': [
      P('Padrão', [3, 1, "x", 3, 2, "x"], [3, 1, 0, 4, 2, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 6, "x", 6], [0, 0, 1, 2, 0, 3], 'chords-db', []),
      P('Padrão', ["x", 10, 8, "x", 8, 9], [0, 1, 2, 4, 3, 0], 'chords-db', [])
      ],
      'Gdim7': [
      P('Padrão', [3, 1, "x", 3, 2, 0], [3, 1, 0, 4, 2, 0], 'chords-db', []),
      P('Padrão', [3, "x", 2, 3, 2, 0], [3, 0, 1, 4, 2, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 5, 3, 5, 3], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'Gm': [
      P('Abertura', [3, 1, 0, 0, 3, 3], [2, 1, 0, 0, 3, 4], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 5, 3, 3, 3], [1, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 7, 8, 6], [0, 0, 1, 3, 4, 2], 'chords-db', [])
      ],
      'Gm/A': [
      P('3ª casa', ["x", 0, 0, 3, 3, 3], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa', ["x", 0, 5, 3, 3, 3], [0, 0, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('3ª casa', ["x", 0, 5, 3, 3, 6], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'Gm/Ab': [
      P('3ª casa (pestana)', [4, 5, 5, 3, 3, 3], [2, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 6, 3, 3, 3], [0, 0, 4, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('6ª casa (pestana)', ["x", "x", 6, 7, 8, 6], [0, 0, 1, 2, 3, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Gm/B': [
      P('3ª casa', ["x", 2, 0, 3, 3, 3], [0, 1, 0, 2, 2, 2], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('Padrão', ["x", "x", 9, 7, 8, 6], [0, 0, 4, 2, 3, 1], 'chords-db', []),
      P('Padrão', ["x", "x", 9, 12, 11, 10], [0, 0, 1, 4, 3, 2], 'chords-db', [])
      ],
      'Gm/Bb': [
      P('Abertura', ["x", 1, 0, 0, 3, "x"], [0, 1, 0, 0, 3, 0], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 5, 3, 3, 3], [4, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 8, 7, 8, 6], [0, 0, 3, 2, 4, 1], 'chords-db', [])
      ],
      'Gm/C': [
      P('3ª casa (pestana)', ["x", 3, 5, 3, 3, 3], [0, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 3, 5, 3, 3, 6], [0, 1, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', ["x", "x", 10, 12, 11, 10], [0, 0, 1, 3, 2, 1], 'chords-db', [{"fret": 10, "from": 2, "to": 5}])
      ],
      'Gm/C#': [
      P('3ª casa', ["x", 4, 0, 3, 3, 3], [0, 2, 0, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 4, 5, 3, 3, 3], [0, 2, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 4, 5, 3, 3, 6], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Gm/D': [
      P('3ª casa', ["x", "x", 0, 3, 3, 3], [0, 0, 0, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa (pestana)', ["x", 5, 5, 3, 3, 3], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa (pestana)', ["x", 5, 5, 3, 3, 6], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Gm/E': [
      P('3ª casa', ["x", "x", 2, 3, 3, 3], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa', [0, 5, 5, 3, 3, 3], [0, 3, 4, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('3ª casa', [0, 5, 5, 3, 3, 6], [0, 2, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 1, "to": 5}])
      ],
      'Gm/Eb': [
      P('3ª casa', ["x", "x", 1, 3, 3, 3], [0, 0, 1, 3, 3, 3], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa (pestana)', ["x", 6, 5, 3, 3, 3], [0, 4, 3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 5}]),
      P('6ª casa (pestana)', ["x", 6, 8, 7, 8, 6], [0, 1, 3, 2, 4, 1], 'chords-db', [{"fret": 6, "from": 1, "to": 5}])
      ],
      'Gm/F': [
      P('3ª casa', [1, 1, 0, 0, 3, 3], [1, 2, 0, 0, 4, 4], 'chords-db', [{"fret": 3, "from": 4, "to": 5}]),
      P('3ª casa', [1, 1, 0, 3, 3, 3], [1, 2, 0, 4, 4, 4], 'chords-db', [{"fret": 3, "from": 3, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 3, 3, 3, 3], [0, 0, 1, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}])
      ],
      'Gm/F#': [
      P('3ª casa (pestana)', ["x", "x", 4, 3, 3, 3], [0, 0, 2, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('Abertura', [2, 1, 0, 0, 3, "x"], [2, 1, 0, 0, 3, 0], 'chords-db', []),
      P('Padrão', ["x", 9, 8, 7, 8, "x"], [0, 4, 2, 1, 3, 0], 'chords-db', [])
      ],
      'Gm11': [
      P('Padrão', [3, "x", 3, 3, 1, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 3, 3, 3, 5], [1, 1, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", "x", 5, 5, 7, 7], [0, 0, 1, 1, 2, 3], 'chords-db', [{"fret": 5, "from": 2, "to": 5}])
      ],
      'Gm6': [
      P('3ª casa', [3, "x", 2, 3, 3, 3], [2, 0, 1, 3, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 5, 5, 3, 5, 3], [1, 2, 3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 7, 5, 6], [0, 1, 1, 3, 1, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Gm69': [
      P('Abertura', [3, 1, 0, 2, 3, 0], [3, 1, 0, 2, 4, 0], 'chords-db', []),
      P('5ª casa', ["x", 5, 5, 3, 5, 5], [0, 2, 2, 1, 3, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('5ª casa (pestana)', [6, 5, 5, 7, 5, 5], [2, 1, 1, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Gm7': [
      P('Padrão', [3, "x", 3, 3, 3, "x"], [2, 0, 3, 3, 3, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 3, 3, 3], [1, 3, 1, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 7, 6, 6], [0, 1, 1, 4, 2, 3], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Gm7b5': [
      P('Padrão', [3, "x", "x", 3, 2, 1], [3, 0, 0, 4, 2, 1], 'chords-db', []),
      P('Padrão', [3, "x", 3, 3, 2, "x"], [2, 0, 3, 4, 1, 0], 'chords-db', []),
      P('6ª casa', ["x", "x", 5, 6, 6, 6], [0, 0, 1, 2, 2, 2], 'chords-db', [{"fret": 6, "from": 3, "to": 5}])
      ],
      'Gm9': [
      P('Abertura', [3, 0, 0, 3, 3, 1], [2, 0, 0, 3, 4, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 3, 3, 5], [1, 3, 1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('6ª casa', ["x", "x", 7, 0, 6, 6], [0, 0, 2, 0, 1, 1], 'chords-db', [{"fret": 6, "from": 2, "to": 5}])
      ],
      'Gm9/Bb': [
      P('5ª casa (pestana)', [6, 5, 5, 7, 6, 5], [2, 1, 1, 4, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', [6, "x", 5, 7, 6, 5], [2, 0, 1, 4, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}])
      ],
      'Gm9/F': [
      P('5ª casa (pestana)', ["x", 8, 5, 7, 6, 5], [0, 4, 1, 3, 2, 1], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('10ª casa (pestana)', [13, 10, 12, 10, 10, 10], [4, 1, 3, 1, 1, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 5}]),
      P('10ª casa (pestana)', [13, 10, 12, 12, 10, 10], [4, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 5}])
      ],
      'Gmadd9': [
      P('3ª casa', [3, 1, 0, 2, 3, 3], [3, 1, 0, 2, 4, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', ["x", "x", 5, 3, 3, 5], [0, 0, 3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 2, "to": 5}]),
      P('Padrão', ["x", "x", 7, 0, 8, 6], [0, 0, 2, 0, 3, 1], 'chords-db', [])
      ],
      'Gmaj11': [
      P('Abertura', [3, 2, 0, 0, 1, 2], [4, 2, 0, 0, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 4, 4, 3, 3], [1, 1, 2, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 9, 0, 7, 8], [0, 0, 3, 0, 1, 2], 'chords-db', [])
      ],
      'Gmaj13': [
      P('[2, 3]ª casa (pestana)', [3, 2, 2, 2, 3, 2], [3, 1, 1, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}, {"fret": 3, "from": 0, "to": 4}]),
      P('3ª casa (pestana)', [3, 3, 4, 4, 5, 3], [1, 1, 2, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('7ª casa', ["x", 10, 9, 9, 7, 7], [0, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Gmaj7': [
      P('Abertura', [3, 2, 0, 0, 0, 2], [3, 2, 0, 0, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 4, 4, 3, 3], [1, 4, 2, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('[5, 7]ª casa (pestana)', ["x", 5, 5, 7, 7, 7], [0, 1, 1, 3, 3, 3], 'chords-db', [{"fret": 5, "from": 1, "to": 5}, {"fret": 7, "from": 3, "to": 5}])
      ],
      'Gmaj7#5': [
      P('Abertura', ["x", "x", 1, 0, 0, 2], [0, 0, 1, 0, 0, 3], 'chords-db', []),
      P('Padrão', [3, "x", 4, 4, 4, "x"], [1, 0, 2, 3, 4, 0], 'chords-db', []),
      P('7ª casa (pestana)', [7, 10, 9, 8, 7, 7], [1, 4, 3, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 5}])
      ],
      'Gmaj7b5': [
      P('2ª casa (pestana)', [3, 2, 4, 4, 2, 2], [2, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', [3, 4, 4, 4, "x", "x"], [1, 2, 3, 4, 0, 0], 'chords-db', []),
      P('Padrão', ["x", "x", 5, 6, 7, 7], [0, 0, 1, 2, 3, 4], 'chords-db', [])
      ],
      'Gmaj7sus2': [
      P('Abertura', [3, 0, 0, 0, 3, 2], [2, 0, 0, 0, 3, 1], 'chords-db', []),
      P('2ª casa', [3, 0, 0, 2, 3, 2], [2, 0, 0, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Abertura', [3, 0, 4, 0, 3, 2], [2, 0, 4, 0, 3, 1], 'chords-db', [])
      ],
      'Gmaj9': [
      P('Abertura', [3, 0, 0, 0, 0, 2], [2, 0, 0, 0, 0, 1], 'chords-db', []),
      P('2ª casa (pestana)', [3, 2, 4, 2, 3, 2], [2, 1, 4, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 4, 4, 3, 5], [0, 0, 2, 3, 1, 4], 'chords-db', [])
      ],
      'Gmmaj11': [
      P('3ª casa (pestana)', [3, 3, 4, 3, 3, 5], [1, 1, 2, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 5, 7, 6], [0, 1, 1, 1, 3, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}]),
      P('8ª casa (pestana)', ["x", 10, 8, 11, 10, 8], [0, 2, 1, 4, 3, 1], 'chords-db', [{"fret": 8, "from": 1, "to": 5}])
      ],
      'Gmmaj7': [
      P('Abertura', [3, 1, 0, 0, 3, 2], [3, 1, 0, 0, 4, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 4, 3, 3, 3], [1, 3, 2, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('5ª casa (pestana)', ["x", 5, 5, 7, 7, 6], [0, 1, 1, 3, 4, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 5}])
      ],
      'Gmmaj7b5': [
      P('3ª casa (pestana)', [3, 4, 4, 3, "x", 3], [1, 2, 3, 1, 0, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 5, 6, 7, 6], [0, 0, 1, 2, 4, 3], 'chords-db', []),
      P('11ª casa', [9, 10, 11, 11, 11, "x"], [1, 2, 3, 3, 3, 0], 'chords-db', [{"fret": 11, "from": 2, "to": 4}])
      ],
      'Gmmaj9': [
      P('Abertura', [3, 0, 0, 3, 3, 2], [2, 0, 0, 3, 4, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 4, 3, 3, 5], [1, 3, 2, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('Padrão', ["x", "x", 7, 0, 7, 6], [0, 0, 2, 0, 3, 1], 'chords-db', [])
      ],
      'Gsus': [
      P('Abertura', [3, 3, 0, 0, 1, 3], [2, 3, 0, 0, 1, 4], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 5, 5, 3, 3], [1, 1, 3, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('3ª casa (pestana)', [3, 5, 5, 5, 3, 3], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}])
      ],
      'Gsus2': [
      P('Abertura', [3, 0, 0, 0, 3, 3], [1, 0, 0, 0, 2, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 7, 8, 5], [1, 1, 1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 5}]),
      P('7ª casa (pestana)', ["x", 10, 7, 7, 8, 10], [0, 3, 1, 1, 2, 4], 'chords-db', [{"fret": 7, "from": 1, "to": 5}])
      ],
      'Gsus2sus4': [
      P('Padrão', [3, 3, 0, 2, 1, "x"], [3, 4, 0, 2, 1, 0], 'chords-db', []),
      P('Padrão', [3, 3, 0, 2, 3, "x"], [2, 3, 0, 1, 4, 0], 'chords-db', []),
      P('Abertura', [3, 0, 0, 2, 1, 3], [3, 0, 0, 2, 1, 4], 'chords-db', [])
      ],
      'Gsus4': [
      P('Abertura', [3, 3, 0, 0, 1, 3], [2, 3, 0, 0, 1, 4], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 5, 5, 3, 3], [1, 2, 3, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 5}]),
      P('[5, 8]ª casa (pestana)', ["x", 5, 5, 7, 8, 8], [0, 1, 1, 3, 4, 4], 'chords-db', [{"fret": 5, "from": 1, "to": 5}, {"fret": 8, "from": 4, "to": 5}])
      ],
    },
    ukulele: {
      'A': [
      P('Abertura', [2, 1, 0, 0], [2, 1, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 5, 4], [1, 2, 4, 3], 'chords-db', []),
      P('4ª casa (pestana)', [6, 4, 5, 4], [4, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'A11': [
      P('Padrão', [4, 2, 3, 4], [3, 1, 2, 4], 'chords-db', []),
      P('Padrão', [7, 7, 7, 4], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [6, 7, 7, 5], [2, 3, 4, 1], 'chords-db', [])
      ],
      'A13': [
      P('Padrão', [0, 1, 2, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'A13b5b9': [
      P('3ª casa (pestana)', [3, 6, 3, 6], [1, 3, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 6, 9], [3, 2, 1, 4], 'chords-db', []),
      P('Padrão', [0, 10, 11, 9], [0, 2, 3, 1], 'chords-db', [])
      ],
      'A13b9': [
      P('Padrão', [0, 1, 2, 1], [0, 1, 3, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 3, 4], [1, 4, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 9], [1, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'A6': [
      P('Padrão', [2, 4, 2, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 6, 5, 7], [2, 3, 1, 4], 'chords-db', []),
      P('9ª casa (pestana)', [9, 9, 9, 9], [1, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'A69': [
      P('Padrão', [4, 4, 2, 4], [2, 3, 1, 4], 'chords-db', []),
      P('[6, 7]ª casa (pestana)', [6, 6, 7, 7], [1, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 2, "to": 3}]),
      P('9ª casa (pestana)', [9, 11, 9, 9], [1, 3, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'A7': [
      P('Abertura', [0, 1, 0, 0], [0, 1, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 5, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'A7#9': [
      P('Abertura', [0, 1, 0, 3], [0, 1, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 3, 4], [4, 2, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [6, 4, 3, 3], [4, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'A7b5': [
      P('Padrão', [2, 3, 3, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 7, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'A7b9': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'A7b9#5': [
      P('Padrão', [0, 1, 1, 1], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 4], [1, 3, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 8], [1, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'A7sus4': [
      P('Abertura', [0, 2, 0, 0], [0, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 3, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 7, 5, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'A9': [
      P('Abertura', [0, 1, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 3, 4], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [6, 7, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'A9#11': [
      P('3ª casa (pestana)', [4, 3, 3, 4], [2, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('[6, 7]ª casa (pestana)', [6, 7, 7, 6], [1, 2, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 1, "to": 2}]),
      P('Padrão', [8, 11, 9, 10], [1, 4, 2, 3], 'chords-db', [])
      ],
      'A9b5': [
      P('3ª casa (pestana)', [4, 3, 3, 4], [2, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('[6, 7]ª casa (pestana)', [6, 7, 7, 6], [1, 2, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 1, "to": 2}]),
      P('Padrão', [8, 11, 9, 10], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Aadd9': [
      P('Padrão', [2, 1, 0, 2], [2, 1, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 5, 4], [1, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa', [6, 9, 7, 7], [1, 4, 2, 2], 'chords-db', [{"fret": 7, "from": 1, "to": 3}])
      ],
      'Aalt': [
      P('Padrão', [2, 3, 5, 4], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [6, 3, 5, 4], [4, 1, 3, 2], 'chords-db', []),
      P('6ª casa (pestana)', [6, 9, 9, 6], [1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Aaug': [
      P('Padrão', [2, 1, 1, 0], [3, 1, 2, 0], 'chords-db', []),
      P('1ª casa (pestana)', [2, 1, 1, 4], [2, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [2, 5, 5, 4], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Aaug7': [
      P('Abertura', [0, 1, 1, 0], [0, 1, 2, 0], 'chords-db', []),
      P('Padrão', [2, 5, 3, 4], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [6, 7, 5, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Aaug9': [
      P('1ª casa', [0, 1, 1, 2], [0, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('Padrão', [4, 5, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('7ª casa', [6, 7, 7, 8], [1, 2, 2, 3], 'chords-db', [{"fret": 7, "from": 1, "to": 3}])
      ],
      'Ab': [
      P('Padrão', [1, 3, 4, 3], [1, 2, 4, 3], 'chords-db', []),
      P('3ª casa (pestana)', [5, 3, 4, 3], [3, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 3, 4, 6], [3, 1, 2, 4], 'chords-db', [])
      ],
      'Ab11': [
      P('Padrão', [3, 1, 2, 3], [3, 1, 2, 4], 'chords-db', []),
      P('Padrão', [6, 6, 6, 3], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [5, 6, 6, 4], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Ab13': [
      P('Padrão', [3, 5, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 6, 8], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [10, 10, 8, 9], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Ab13#9': [
      P('Padrão', [0, 1, 1, 3], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [5, 5, 3, 4], [3, 4, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 3, 3], [4, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Ab13b5b9': [
      P('2ª casa (pestana)', [2, 5, 2, 5], [1, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 5, 8], [3, 2, 1, 4], 'chords-db', []),
      P('Padrão', [11, 9, 10, 8], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Ab13b9': [
      P('Padrão', [0, 1, 1, 1], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 4], [1, 3, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 8], [1, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('2ª casa (pestana)', [2, 5, 2, 3], [1, 4, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 8], [1, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [11, 9, 8, 8], [4, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ab6': [
      P('Padrão', [1, 3, 1, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 5, 4, 6], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 8, 8, 8], [1, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ab69': [
      P('Padrão', [3, 3, 1, 3], [2, 3, 1, 4], 'chords-db', []),
      P('[5, 6]ª casa (pestana)', [5, 5, 6, 6], [1, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 2, "to": 3}]),
      P('8ª casa (pestana)', [8, 10, 8, 8], [1, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ab7': [
      P('Padrão', [1, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 4, 6], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 8, 8, 9], [1, 1, 1, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ab7#9': [
      P('Padrão', [4, 3, 2, 3], [4, 2, 1, 3], 'chords-db', []),
      P('2ª casa (pestana)', [5, 3, 2, 2], [4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [5, 6, 7, 6], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Ab7b5': [
      P('Padrão', [1, 2, 2, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 6, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Ab7b9': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Ab7b9#5': [
      P('2ª casa (pestana)', [2, 4, 2, 3], [1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 7], [1, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [9, 9, 8, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Ab7sus4': [
      P('Padrão', [1, 3, 2, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 6, 4, 6], [2, 3, 1, 4], 'chords-db', []),
      P('[8, 9]ª casa (pestana)', [8, 8, 9, 9], [1, 1, 2, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}, {"fret": 9, "from": 2, "to": 3}])
      ],
      'Ab9': [
      P('Padrão', [3, 3, 2, 3], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [5, 6, 6, 6], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 10, 8, 9], [1, 3, 1, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ab9#11': [
      P('2ª casa (pestana)', [3, 2, 2, 3], [2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('[5, 6]ª casa (pestana)', [5, 6, 6, 5], [1, 2, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 1, "to": 2}]),
      P('Padrão', [7, 10, 8, 9], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Ab9b5': [
      P('2ª casa (pestana)', [3, 2, 2, 3], [2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('[5, 6]ª casa (pestana)', [5, 6, 6, 5], [1, 2, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 1, "to": 2}]),
      P('Padrão', [7, 10, 8, 9], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Abadd9': [
      P('3ª casa (pestana)', [3, 3, 4, 3], [1, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa', [5, 8, 6, 6], [1, 4, 2, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 3}]),
      P('8ª casa (pestana)', [8, 10, 8, 11], [1, 3, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Abalt': [
      P('Padrão', [5, 2, 4, 3], [4, 1, 3, 2], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 8, 5], [1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Abaug': [
      P('Abertura', [1, 0, 0, 3], [1, 0, 0, 3], 'chords-db', []),
      P('Padrão', [1, 4, 4, 3], [1, 3, 4, 2], 'chords-db', []),
      P('4ª casa', [5, 4, 4, 3], [3, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 2}])
      ],
      'Abaug7': [
      P('Padrão', [1, 4, 2, 3], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [5, 6, 4, 7], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 8, 9], [2, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Abaug9': [
      P('Padrão', [3, 4, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('6ª casa', [5, 6, 6, 7], [1, 2, 2, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 3}]),
      P('Padrão', [9, 10, 8, 9], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Abb13#9': [
      P('2ª casa (pestana)', [5, 4, 2, 2], [4, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 4, 2, 3], [3, 4, 1, 2], 'chords-db', []),
      P('Padrão', [5, 6, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Abb13b9': [
      P('2ª casa (pestana)', [2, 4, 2, 3], [1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 7], [1, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [9, 9, 8, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Abdim': [
      P('Padrão', [1, 2, 4, 2], [1, 2, 4, 3], 'chords-db', []),
      P('2ª casa (pestana)', [4, 2, 4, 2], [3, 1, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 8, 7, 5], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Abdim7': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Abm': [
      P('Padrão', [1, 3, 4, 2], [1, 3, 4, 2], 'chords-db', []),
      P('Padrão', [4, 3, 4, 2], [3, 2, 4, 1], 'chords-db', []),
      P('Padrão', [4, 3, 4, 6], [2, 1, 3, 4], 'chords-db', [])
      ],
      'Abm11': [
      P('2ª casa', [3, 1, 2, 2], [3, 1, 2, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('1ª casa (pestana)', [4, 1, 2, 1], [4, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 6, 6, 4], [1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Abm6': [
      P('1ª casa (pestana)', [1, 3, 1, 2], [1, 3, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 6], [1, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [8, 8, 7, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Abm69': [
      P('Padrão', [3, 3, 1, 2], [3, 4, 1, 2], 'chords-db', []),
      P('1ª casa (pestana)', [4, 3, 1, 1], [4, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [4, 5, 6, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Abm7': [
      P('2ª casa', [1, 3, 2, 2], [1, 3, 2, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 3}]),
      P('Padrão', [4, 6, 4, 6], [1, 3, 2, 4], 'chords-db', []),
      P('8ª casa', [8, 8, 7, 9], [2, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Abm7b5': [
      P('Padrão', [1, 2, 2, 2], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 4, 5], [1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 9], [1, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Abm9': [
      P('Padrão', [4, 3, 2, 1], [4, 3, 2, 1], 'chords-db', []),
      P('[2, 3]ª casa (pestana)', [3, 3, 2, 2], [2, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 0, "to": 1}]),
      P('Padrão', [4, 6, 6, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Abm9b5': [
      P('2ª casa', [4, 2, 2, 1], [4, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 2}]),
      P('2ª casa (pestana)', [3, 2, 2, 2], [2, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 6, 5], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Abmadd9': [
      P('Padrão', [4, 3, 4, 1], [3, 2, 4, 1], 'chords-db', []),
      P('3ª casa', [3, 3, 4, 2], [2, 2, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 2}]),
      P('11ª casa (pestana)', [13, 11, 11, 13], [3, 1, 1, 4], 'chords-db', [{"fret": 11, "from": 0, "to": 3}])
      ],
      'Abmaj11': [
      P('Padrão', [3, 1, 3, 3], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 6, 4], [2, 1, 3, 4], 'chords-db', [])
      ],
      'Abmaj13': [
      P('Abertura', [0, 0, 1, 1], [0, 0, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 3], [1, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 6, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Abmaj7': [
      P('Padrão', [1, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 4, 6], [2, 4, 1, 3], 'chords-db', []),
      P('8ª casa (pestana)', [8, 8, 8, 10], [1, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Abmaj7#5': [
      P('Padrão', [1, 4, 3, 3], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [5, 7, 4, 7], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 8, 10], [2, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Abmaj7b5': [
      P('Padrão', [1, 2, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Abmaj9': [
      P('3ª casa (pestana)', [3, 3, 3, 3], [1, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa', [5, 7, 6, 6], [1, 3, 2, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 3}]),
      P('Padrão', [8, 10, 8, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Abmmaj11': [
      P('Padrão', [3, 1, 3, 2], [3, 1, 4, 2], 'chords-db', []),
      P('1ª casa (pestana)', [4, 1, 3, 1], [4, 1, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 7, 6, 4], [1, 4, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Abmmaj7': [
      P('Padrão', [1, 3, 3, 2], [1, 3, 4, 2], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 4, 6], [1, 4, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('8ª casa', [8, 8, 7, 10], [2, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Abmmaj7b5': [
      P('Padrão', [1, 2, 3, 2], [1, 2, 4, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 4, 5], [1, 4, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 10], [1, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Abmmaj9': [
      P('Padrão', [4, 3, 3, 1], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [3, 3, 3, 2], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [4, 7, 6, 6], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Absus2': [
      P('1ª casa (pestana)', [1, 3, 4, 1], [1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('3ª casa (pestana)', [3, 3, 4, 6], [1, 1, 2, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [8, 8, 6, 6], [3, 4, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Absus4': [
      P('Padrão', [1, 3, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa', [6, 3, 4, 4], [4, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 3, 4, 6], [3, 1, 2, 4], 'chords-db', [])
      ],
      'Adim': [
      P('Padrão', [2, 3, 5, 3], [1, 2, 4, 3], 'chords-db', []),
      P('3ª casa (pestana)', [5, 3, 5, 3], [3, 1, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 9, 8, 6], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Adim7': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Am': [
      P('Abertura', [2, 0, 0, 0], [2, 0, 0, 0], 'chords-db', []),
      P('Abertura', [2, 0, 0, 3], [2, 0, 0, 3], 'chords-db', []),
      P('Padrão', [2, 4, 5, 3], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Am11': [
      P('3ª casa', [4, 2, 3, 3], [3, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('2ª casa (pestana)', [5, 2, 3, 2], [4, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 7, 7, 5], [1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Am6': [
      P('2ª casa (pestana)', [2, 4, 2, 3], [1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 7], [1, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [9, 9, 8, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Am69': [
      P('Padrão', [4, 4, 2, 3], [3, 4, 1, 2], 'chords-db', []),
      P('2ª casa (pestana)', [5, 4, 2, 2], [4, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [5, 6, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Am7': [
      P('Abertura', [0, 0, 0, 0], [0, 0, 0, 0], 'chords-db', []),
      P('3ª casa', [2, 4, 3, 3], [1, 3, 2, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 3}]),
      P('Padrão', [5, 7, 5, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Am7b5': [
      P('Padrão', [2, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 6], [1, 3, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 10], [1, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Am9': [
      P('Abertura', [0, 0, 0, 2], [0, 0, 0, 2], 'chords-db', []),
      P('Padrão', [5, 4, 3, 2], [4, 3, 2, 1], 'chords-db', []),
      P('[3, 4]ª casa (pestana)', [4, 4, 3, 3], [2, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}, {"fret": 4, "from": 0, "to": 1}])
      ],
      'Am9b5': [
      P('3ª casa', [5, 3, 3, 2], [4, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 2}]),
      P('3ª casa (pestana)', [4, 3, 3, 3], [2, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 7, 6], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Amadd9': [
      P('Abertura', [2, 0, 0, 2], [2, 0, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 5, 2], [3, 2, 4, 1], 'chords-db', []),
      P('4ª casa', [4, 4, 5, 3], [2, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 2}])
      ],
      'Amaj11': [
      P('Padrão', [4, 2, 4, 4], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 7, 5], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Amaj13': [
      P('[1, 2]ª casa (pestana)', [1, 1, 2, 2], [1, 1, 2, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 2, "to": 3}]),
      P('4ª casa (pestana)', [4, 6, 4, 4], [1, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 7, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Amaj7': [
      P('Abertura', [1, 1, 0, 0], [1, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 5, 7], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Amaj7#5': [
      P('Padrão', [1, 1, 1, 0], [1, 2, 3, 0], 'chords-db', []),
      P('Padrão', [2, 5, 4, 4], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [6, 8, 5, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Amaj7b5': [
      P('Padrão', [2, 3, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 11], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Amaj9': [
      P('Padrão', [1, 1, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 4], [1, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa', [6, 8, 7, 7], [1, 3, 2, 2], 'chords-db', [{"fret": 7, "from": 1, "to": 3}])
      ],
      'Ammaj11': [
      P('Padrão', [4, 2, 4, 3], [3, 1, 4, 2], 'chords-db', []),
      P('2ª casa (pestana)', [5, 2, 4, 2], [4, 1, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 8, 7, 5], [1, 4, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Ammaj7': [
      P('Abertura', [1, 0, 0, 0], [1, 0, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 4, 3], [1, 3, 4, 2], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 5, 7], [1, 4, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Ammaj7b5': [
      P('Padrão', [2, 3, 4, 3], [1, 2, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 5, 6], [1, 4, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 11], [1, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ammaj9': [
      P('Abertura', [1, 0, 0, 2], [1, 0, 0, 2], 'chords-db', []),
      P('Padrão', [5, 4, 4, 2], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [4, 4, 4, 3], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Asus2': [
      P('2ª casa (pestana)', [2, 4, 5, 2], [1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 4, 5, 7], [1, 1, 2, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [9, 9, 7, 7], [3, 4, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Asus4': [
      P('Abertura', [2, 2, 0, 0], [2, 3, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa', [7, 4, 5, 5], [4, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'B': [
      P('2ª casa (pestana)', [4, 3, 2, 2], [3, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 7, 6], [1, 2, 4, 3], 'chords-db', []),
      P('6ª casa (pestana)', [8, 6, 7, 6], [3, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'B11': [
      P('Padrão', [2, 3, 0, 4], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [6, 4, 5, 6], [3, 1, 2, 4], 'chords-db', []),
      P('Padrão', [9, 9, 9, 6], [2, 3, 4, 1], 'chords-db', [])
      ],
      'B13': [
      P('Padrão', [2, 3, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 11], [1, 2, 3, 4], 'chords-db', [])
      ],
      'B13b5b9': [
      P('Abertura', [1, 0, 1, 0], [1, 0, 2, 0], 'chords-db', []),
      P('Padrão', [2, 5, 4, 3], [1, 4, 3, 2], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 5, 8], [1, 3, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'B13b9': [
      P('Padrão', [2, 3, 4, 3], [1, 2, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 5, 6], [1, 4, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 11], [1, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'B6': [
      P('Padrão', [1, 3, 2, 2], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 4, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 8, 7, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'B69': [
      P('Padrão', [1, 3, 2, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 6, 4, 6], [2, 3, 1, 4], 'chords-db', []),
      P('[8, 9]ª casa (pestana)', [8, 8, 9, 9], [1, 1, 2, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}, {"fret": 9, "from": 2, "to": 3}])
      ],
      'B7': [
      P('2ª casa (pestana)', [2, 3, 2, 2], [1, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 7, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'B7#9': [
      P('2ª casa (pestana)', [2, 3, 2, 5], [1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 5, 6], [4, 2, 1, 3], 'chords-db', []),
      P('5ª casa (pestana)', [8, 6, 5, 5], [4, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'B7b5': [
      P('Padrão', [2, 3, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 5, 6], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [8, 9, 7, 8], [2, 4, 1, 3], 'chords-db', [])
      ],
      'B7b9': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'B7b9#5': [
      P('Padrão', [2, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 6], [1, 3, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [8, 9, 8, 10], [1, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'B7sus4': [
      P('2ª casa (pestana)', [2, 4, 2, 2], [1, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 5, 7], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [9, 9, 7, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'B9': [
      P('2ª casa (pestana)', [2, 3, 2, 4], [1, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 5, 6], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [8, 9, 9, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'B9#11': [
      P('Padrão', [2, 3, 1, 4], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa', [6, 5, 5, 6], [2, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('[8, 9]ª casa (pestana)', [8, 9, 9, 8], [1, 2, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}, {"fret": 9, "from": 1, "to": 2}])
      ],
      'B9b5': [
      P('Padrão', [2, 3, 1, 4], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 5, 6], [2, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('[8, 9]ª casa (pestana)', [8, 9, 9, 8], [1, 2, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}, {"fret": 9, "from": 1, "to": 2}])
      ],
      'Badd9': [
      P('Padrão', [4, 3, 2, 4], [3, 2, 1, 4], 'chords-db', []),
      P('6ª casa', [6, 6, 7, 6], [1, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa', [8, 11, 9, 9], [1, 4, 2, 2], 'chords-db', [{"fret": 9, "from": 1, "to": 3}])
      ],
      'Balt': [
      P('Padrão', [4, 3, 1, 2], [4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [4, 5, 7, 6], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [8, 5, 7, 6], [4, 1, 3, 2], 'chords-db', [])
      ],
      'Baug': [
      P('Padrão', [0, 3, 3, 2], [0, 2, 3, 1], 'chords-db', []),
      P('3ª casa', [4, 3, 3, 2], [3, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 2}]),
      P('3ª casa (pestana)', [4, 3, 3, 6], [2, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Baug7': [
      P('[2, 3]ª casa (pestana)', [2, 3, 3, 2], [1, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 1, "to": 2}]),
      P('Padrão', [4, 7, 5, 6], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [8, 9, 7, 10], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Baug9': [
      P('3ª casa', [2, 3, 3, 4], [1, 2, 2, 3], 'chords-db', [{"fret": 3, "from": 1, "to": 3}]),
      P('Padrão', [6, 7, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('9ª casa', [8, 9, 9, 10], [1, 2, 2, 3], 'chords-db', [{"fret": 9, "from": 1, "to": 3}])
      ],
      'Bb': [
      P('1ª casa (pestana)', [3, 2, 1, 1], [3, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 6, 5], [1, 2, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [7, 5, 6, 5], [3, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Bb11': [
      P('Padrão', [5, 3, 4, 5], [3, 1, 2, 4], 'chords-db', []),
      P('Padrão', [8, 8, 8, 5], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [7, 8, 8, 6], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Bb13': [
      P('Padrão', [1, 2, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Bb13#9': [
      P('Padrão', [2, 3, 3, 5], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [8, 7, 5, 5], [4, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 5, 6], [4, 3, 1, 2], 'chords-db', [])
      ],
      'Bb13b5b9': [
      P('Padrão', [1, 4, 3, 2], [1, 4, 3, 2], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 4, 7], [1, 3, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 7, 10], [3, 2, 1, 4], 'chords-db', [])
      ],
      'Bb13b9': [
      P('Padrão', [2, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 6], [1, 3, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 10], [1, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}]),
      P('Padrão', [1, 2, 3, 2], [1, 2, 4, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 4, 5], [1, 4, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 10], [1, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bb6': [
      P('1ª casa', [0, 2, 1, 1], [0, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('Padrão', [3, 5, 3, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 7, 6, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Bb69': [
      P('Padrão', [0, 2, 1, 3], [0, 2, 1, 3], 'chords-db', []),
      P('Padrão', [5, 5, 3, 5], [2, 3, 1, 4], 'chords-db', []),
      P('[7, 8]ª casa (pestana)', [7, 7, 8, 8], [1, 1, 2, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}, {"fret": 8, "from": 2, "to": 3}])
      ],
      'Bb7': [
      P('1ª casa (pestana)', [1, 2, 1, 1], [1, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 6, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Bb7#9': [
      P('1ª casa (pestana)', [1, 2, 1, 4], [1, 2, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 4, 5], [4, 2, 1, 3], 'chords-db', []),
      P('4ª casa (pestana)', [7, 5, 4, 4], [4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Bb7b5': [
      P('Padrão', [1, 2, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 5], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [7, 8, 6, 7], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Bb7b9': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bb7b9#5': [
      P('Padrão', [1, 2, 2, 2], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 4, 5], [1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 9], [1, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bb7sus4': [
      P('1ª casa (pestana)', [1, 3, 1, 1], [1, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 4, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 8, 6, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Bb9': [
      P('1ª casa (pestana)', [1, 2, 1, 3], [1, 2, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 4, 5], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [7, 8, 8, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Bb9#11': [
      P('Padrão', [1, 2, 0, 3], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 4, 5], [2, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('[7, 8]ª casa (pestana)', [7, 8, 8, 7], [1, 2, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}, {"fret": 8, "from": 1, "to": 2}])
      ],
      'Bb9b5': [
      P('Padrão', [1, 2, 0, 3], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa', [5, 4, 4, 5], [2, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('[7, 8]ª casa', [7, 8, 8, 7], [1, 2, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}, {"fret": 8, "from": 1, "to": 2}])
      ],
      'Bbadd9': [
      P('Padrão', [3, 2, 1, 3], [3, 2, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 6, 5], [1, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [7, 10, 8, 8], [1, 4, 2, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 3}])
      ],
      'Bbalt': [
      P('Padrão', [3, 2, 0, 1], [3, 2, 0, 1], 'chords-db', []),
      P('Padrão', [3, 4, 6, 5], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [7, 4, 6, 5], [4, 1, 3, 2], 'chords-db', [])
      ],
      'Bbaug': [
      P('2ª casa', [3, 2, 2, 1], [3, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 2}]),
      P('2ª casa (pestana)', [3, 2, 2, 5], [2, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [3, 6, 6, 5], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Bbaug7': [
      P('[1, 2]ª casa (pestana)', [1, 2, 2, 1], [1, 2, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 1, "to": 2}]),
      P('Padrão', [3, 6, 4, 5], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [7, 8, 6, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Bbaug9': [
      P('2ª casa', [1, 2, 2, 3], [1, 2, 2, 3], 'chords-db', [{"fret": 2, "from": 1, "to": 3}]),
      P('Padrão', [5, 6, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('8ª casa', [7, 8, 8, 9], [1, 2, 2, 3], 'chords-db', [{"fret": 8, "from": 1, "to": 3}])
      ],
      'Bbb13#9': [
      P('Padrão', [1, 2, 2, 4], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [7, 6, 4, 4], [4, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 4, 5], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Bbb13b9': [
      P('Padrão', [1, 2, 2, 2], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 4, 5], [1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 9], [1, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bbdim': [
      P('Padrão', [3, 1, 0, 1], [3, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 6, 4], [1, 2, 4, 3], 'chords-db', []),
      P('4ª casa (pestana)', [6, 4, 6, 4], [3, 1, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Bbdim7': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bbm': [
      P('1ª casa (pestana)', [3, 1, 1, 1], [3, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('1ª casa (pestana)', [3, 1, 1, 4], [3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 6, 4], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Bbm11': [
      P('4ª casa', [5, 3, 4, 4], [3, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('3ª casa (pestana)', [6, 3, 4, 3], [4, 1, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 8, 8, 6], [1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Bbm6': [
      P('Padrão', [0, 1, 1, 1], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 4], [1, 3, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 8], [1, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Bbm69': [
      P('Padrão', [0, 1, 1, 3], [0, 2, 1, 4], 'chords-db', []),
      P('Padrão', [5, 5, 3, 4], [3, 4, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 3, 3], [4, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Bbm7': [
      P('1ª casa (pestana)', [1, 1, 1, 1], [1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa', [3, 5, 4, 4], [1, 3, 2, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 3}]),
      P('Padrão', [6, 8, 6, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bbm7b5': [
      P('Padrão', [1, 1, 0, 1], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [3, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, 6, 7], [1, 3, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Bbm9': [
      P('1ª casa (pestana)', [1, 1, 1, 3], [1, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('[4, 5]ª casa (pestana)', [5, 5, 4, 4], [2, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 0, "to": 1}]),
      P('Padrão', [6, 5, 4, 3], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Bbm9b5': [
      P('Padrão', [1, 1, 0, 3], [1, 2, 0, 4], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 4, 4], [2, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('4ª casa', [6, 4, 4, 3], [4, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 2}])
      ],
      'Bbmadd9': [
      P('1ª casa (pestana)', [3, 1, 1, 3], [3, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 6, 3], [3, 2, 4, 1], 'chords-db', []),
      P('5ª casa', [5, 5, 6, 4], [2, 2, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 2}])
      ],
      'Bbmaj11': [
      P('Padrão', [5, 3, 5, 5], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [7, 9, 8, 6], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Bbmaj13': [
      P('[2, 3]ª casa (pestana)', [2, 2, 3, 3], [1, 1, 2, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 2, "to": 3}]),
      P('5ª casa (pestana)', [5, 7, 5, 5], [1, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 9, 8, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bbmaj7': [
      P('Padrão', [3, 2, 1, 0], [3, 2, 1, 0], 'chords-db', []),
      P('1ª casa (pestana)', [2, 2, 1, 1], [2, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 5, 5], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Bbmaj7#5': [
      P('Padrão', [3, 2, 2, 0], [3, 1, 2, 0], 'chords-db', []),
      P('Padrão', [2, 2, 2, 1], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [3, 6, 5, 5], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Bbmaj7b5': [
      P('Abertura', [3, 2, 0, 0], [3, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 2, 0, 1], [2, 3, 0, 1], 'chords-db', []),
      P('Padrão', [3, 4, 5, 5], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Bbmaj9': [
      P('2ª casa', [2, 2, 1, 3], [2, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 5, 5, 5], [1, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [7, 9, 8, 8], [1, 3, 2, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 3}])
      ],
      'Bbmmaj11': [
      P('Padrão', [5, 3, 5, 4], [3, 1, 4, 2], 'chords-db', []),
      P('3ª casa (pestana)', [6, 3, 5, 3], [4, 1, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 9, 8, 6], [1, 4, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Bbmmaj7': [
      P('Padrão', [3, 1, 1, 0], [3, 1, 2, 0], 'chords-db', []),
      P('1ª casa (pestana)', [2, 1, 1, 1], [2, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 5, 4], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Bbmmaj7b5': [
      P('Padrão', [2, 1, 0, 1], [3, 1, 0, 2], 'chords-db', []),
      P('Abertura', [3, 1, 0, 0], [3, 1, 0, 0], 'chords-db', []),
      P('Padrão', [3, 4, 5, 4], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Bbmmaj9': [
      P('1ª casa (pestana)', [2, 1, 1, 3], [2, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 5, 4], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [6, 5, 5, 3], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Bbsus2': [
      P('3ª casa', [3, 5, 6, 3], [1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('5ª casa', [5, 5, 6, 8], [1, 1, 2, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [10, 10, 8, 8], [3, 4, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Bbsus4': [
      P('1ª casa (pestana)', [3, 3, 1, 1], [3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 6, 6], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa', [8, 5, 6, 6], [4, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Bdim': [
      P('Padrão', [4, 2, 1, 2], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 7, 5], [1, 2, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [7, 5, 7, 5], [3, 1, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Bdim7': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bm': [
      P('2ª casa (pestana)', [4, 2, 2, 2], [3, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('2ª casa (pestana)', [4, 2, 2, 5], [3, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 7, 5], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Bm11': [
      P('5ª casa', [6, 4, 5, 5], [3, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [7, 4, 5, 4], [4, 1, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa', [7, 9, 9, 7], [1, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bm6': [
      P('Padrão', [1, 2, 2, 2], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 4, 5], [1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 9], [1, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bm69': [
      P('Padrão', [1, 2, 2, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 6, 4, 5], [3, 4, 1, 2], 'chords-db', []),
      P('4ª casa (pestana)', [7, 6, 4, 4], [4, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Bm7': [
      P('2ª casa (pestana)', [2, 2, 2, 2], [1, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa', [4, 6, 5, 5], [1, 3, 2, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 3}]),
      P('Padrão', [7, 9, 7, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bm7b5': [
      P('Padrão', [2, 2, 1, 2], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [4, 5, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 9, 7, 8], [1, 3, 1, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bm9': [
      P('2ª casa (pestana)', [2, 2, 2, 4], [1, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 5, 4], [4, 3, 2, 1], 'chords-db', []),
      P('[5, 6]ª casa (pestana)', [6, 6, 5, 5], [2, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 0, "to": 1}])
      ],
      'Bm9b5': [
      P('2ª casa', [2, 2, 1, 4], [2, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa', [7, 5, 5, 4], [4, 2, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 2}]),
      P('5ª casa (pestana)', [6, 5, 5, 5], [2, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Bmadd9': [
      P('Abertura', [2, 0, 0, 2], [2, 0, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 5, 2], [3, 2, 4, 1], 'chords-db', []),
      P('4ª casa', [4, 4, 5, 3], [2, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 2}])
      ],
      'Bmaj11': [
      P('Padrão', [3, 3, 0, 4], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [6, 4, 6, 6], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [8, 10, 9, 7], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Bmaj13': [
      P('[3, 4]ª casa (pestana)', [3, 3, 4, 4], [1, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}, {"fret": 4, "from": 2, "to": 3}]),
      P('6ª casa (pestana)', [6, 8, 6, 6], [1, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [8, 10, 9, 11], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Bmaj7': [
      P('Padrão', [4, 3, 2, 1], [4, 3, 2, 1], 'chords-db', []),
      P('2ª casa (pestana)', [3, 3, 2, 2], [2, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 6, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Bmaj7#5': [
      P('Padrão', [4, 3, 3, 1], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [3, 3, 3, 2], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [4, 7, 6, 6], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Bmaj7b5': [
      P('1ª casa (pestana)', [4, 3, 1, 1], [4, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 3, 1, 2], [3, 4, 1, 2], 'chords-db', []),
      P('Padrão', [4, 5, 6, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Bmaj9': [
      P('3ª casa', [3, 3, 2, 4], [2, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 6, 6, 6], [1, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa', [8, 10, 9, 9], [1, 3, 2, 2], 'chords-db', [{"fret": 9, "from": 1, "to": 3}])
      ],
      'Bmmaj11': [
      P('Padrão', [6, 4, 6, 5], [3, 1, 4, 2], 'chords-db', []),
      P('4ª casa (pestana)', [7, 4, 6, 4], [4, 1, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 10, 9, 7], [1, 4, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Bmmaj7': [
      P('2ª casa', [4, 2, 2, 1], [4, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 2}]),
      P('2ª casa (pestana)', [3, 2, 2, 2], [2, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 6, 5], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Bmmaj7b5': [
      P('Padrão', [3, 2, 1, 2], [4, 2, 1, 3], 'chords-db', []),
      P('1ª casa (pestana)', [4, 2, 1, 1], [4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [4, 5, 6, 5], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Bmmaj9': [
      P('2ª casa (pestana)', [3, 2, 2, 4], [2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 6, 4], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [6, 6, 6, 5], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Bsus2': [
      P('4ª casa (pestana)', [4, 6, 7, 4], [1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 6, 7, 9], [1, 1, 2, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [11, 11, 9, 9], [3, 4, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Bsus4': [
      P('2ª casa (pestana)', [4, 4, 2, 2], [3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 7, 7], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa', [9, 6, 7, 7], [4, 1, 2, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'C': [
      P('Abertura', [0, 0, 0, 3], [0, 0, 0, 3], 'chords-db', []),
      P('3ª casa', [0, 4, 3, 3], [0, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 1, "to": 3}]),
      P('3ª casa (pestana)', [5, 4, 3, 3], [3, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'C11': [
      P('Padrão', [7, 5, 6, 7], [3, 1, 2, 4], 'chords-db', [])
      ],
      'C13': [
      P('Padrão', [2, 2, 0, 1], [2, 3, 0, 1], 'chords-db', []),
      P('Abertura', [3, 2, 0, 0], [3, 2, 0, 0], 'chords-db', []),
      P('Padrão', [3, 4, 5, 5], [1, 2, 3, 4], 'chords-db', [])
      ],
      'C13b5b9': [
      P('Padrão', [2, 1, 2, 1], [3, 1, 4, 2], 'chords-db', []),
      P('Padrão', [3, 1, 2, 0], [3, 1, 2, 0], 'chords-db', []),
      P('Padrão', [3, 6, 5, 4], [1, 4, 3, 2], 'chords-db', [])
      ],
      'C13b9': [
      P('Padrão', [2, 1, 0, 1], [3, 1, 0, 2], 'chords-db', []),
      P('Abertura', [3, 1, 0, 0], [3, 1, 0, 0], 'chords-db', []),
      P('Padrão', [3, 4, 5, 4], [1, 2, 4, 3], 'chords-db', [])
      ],
      'C6': [
      P('Abertura', [0, 0, 0, 0], [0, 0, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 3, 3], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [5, 7, 5, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'C69': [
      P('Abertura', [0, 2, 0, 0], [0, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 3, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 7, 5, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'C7': [
      P('Abertura', [0, 0, 0, 1], [0, 0, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 3], [1, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'C7#9': [
      P('Abertura', [0, 3, 0, 1], [0, 3, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 6], [1, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 6, 7], [4, 2, 1, 3], 'chords-db', [])
      ],
      'C7b5': [
      P('Padrão', [3, 4, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('6ª casa', [5, 6, 6, 7], [1, 2, 2, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 3}]),
      P('Padrão', [9, 10, 8, 9], [2, 4, 1, 3], 'chords-db', [])
      ],
      'C7b9': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'C7b9#5': [
      P('Padrão', [1, 1, 0, 1], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [3, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, 6, 7], [1, 3, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'C7sus4': [
      P('Abertura', [0, 0, 1, 1], [0, 0, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 3], [1, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 6, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'C9': [
      P('Abertura', [0, 2, 0, 1], [0, 2, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 5], [1, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 6, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'C9#11': [
      P('Padrão', [3, 4, 2, 5], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [7, 6, 6, 7], [2, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('[9, 10]ª casa (pestana)', [9, 10, 10, 9], [1, 2, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}, {"fret": 10, "from": 1, "to": 2}])
      ],
      'C9b5': [
      P('Padrão', [3, 4, 2, 5], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [7, 6, 6, 7], [2, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('[9, 10]ª casa (pestana)', [9, 10, 10, 9], [1, 2, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}, {"fret": 10, "from": 1, "to": 2}])
      ],
      'Cadd9': [
      P('Abertura', [0, 2, 0, 3], [0, 2, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 3, 5], [3, 2, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 8, 7], [1, 1, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Calt': [
      P('Padrão', [5, 4, 2, 3], [4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [5, 6, 8, 7], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [9, 6, 8, 7], [4, 1, 3, 2], 'chords-db', [])
      ],
      'Caug': [
      P('Abertura', [1, 0, 0, 3], [1, 0, 0, 4], 'chords-db', []),
      P('Padrão', [1, 4, 4, 3], [1, 3, 4, 2], 'chords-db', []),
      P('Padrão', [5, 4, 4, 3], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Caug7': [
      P('Abertura', [1, 0, 0, 1], [1, 0, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 3], [1, 4, 3, 2], 'chords-db', []),
      P('Padrão', [5, 8, 6, 7], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Caug9': [
      P('Padrão', [1, 2, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 5], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [7, 8, 6, 7], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Cb13#9': [
      P('Padrão', [1, 3, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 6], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [9, 8, 6, 6], [4, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Cb13b9': [
      P('Padrão', [1, 1, 0, 1], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [3, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, 6, 7], [1, 3, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Cdim': [
      P('Padrão', [5, 3, 2, 3], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 8, 6], [1, 2, 4, 3], 'chords-db', []),
      P('6ª casa (pestana)', [8, 6, 8, 6], [3, 1, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Cdim7': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Cm': [
      P('Padrão', [0, 3, 3, 3], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [5, 3, 3, 3], [3, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('3ª casa (pestana)', [5, 3, 3, 6], [3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Cm11': [
      P('6ª casa', [7, 5, 6, 6], [3, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [8, 5, 6, 5], [4, 1, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 10, 10, 8], [1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Cm6': [
      P('Padrão', [2, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 6], [1, 3, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 10], [1, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Cm69': [
      P('Padrão', [2, 3, 3, 5], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [7, 7, 5, 6], [3, 4, 1, 2], 'chords-db', []),
      P('5ª casa (pestana)', [8, 7, 5, 5], [4, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Cm7': [
      P('3ª casa (pestana)', [3, 3, 3, 3], [1, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa', [5, 7, 6, 6], [1, 3, 2, 2], 'chords-db', [{"fret": 6, "from": 1, "to": 3}]),
      P('Padrão', [8, 10, 8, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Cm7b5': [
      P('Padrão', [3, 3, 2, 3], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [5, 6, 6, 6], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 10, 8, 9], [1, 3, 1, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Cm9': [
      P('3ª casa', [3, 3, 3, 5], [1, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 6, 5], [4, 3, 2, 1], 'chords-db', []),
      P('[6, 7]ª casa (pestana)', [7, 7, 6, 6], [2, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 0, "to": 1}])
      ],
      'Cm9b5': [
      P('3ª casa', [3, 3, 2, 5], [2, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa', [8, 6, 6, 5], [4, 2, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 2}]),
      P('6ª casa (pestana)', [7, 6, 6, 6], [2, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Cmadd9': [
      P('3ª casa (pestana)', [5, 3, 3, 5], [3, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 8, 5], [3, 2, 4, 1], 'chords-db', []),
      P('7ª casa', [7, 7, 8, 6], [2, 2, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 2}])
      ],
      'Cmaj11': [
      P('Padrão', [7, 5, 7, 7], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [9, 11, 10, 8], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Cmaj13': [
      P('Padrão', [2, 2, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('[4, 5]ª casa (pestana)', [4, 4, 5, 5], [1, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 2, "to": 3}]),
      P('7ª casa (pestana)', [7, 9, 7, 7], [1, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Cmaj7': [
      P('Abertura', [0, 0, 0, 2], [0, 0, 0, 2], 'chords-db', []),
      P('Padrão', [5, 4, 3, 2], [4, 3, 2, 1], 'chords-db', []),
      P('3ª casa (pestana)', [4, 4, 3, 3], [2, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Cmaj7#5': [
      P('Abertura', [1, 0, 0, 2], [1, 0, 0, 2], 'chords-db', []),
      P('Padrão', [5, 4, 4, 2], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [4, 4, 4, 3], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Cmaj7b5': [
      P('2ª casa (pestana)', [5, 4, 2, 2], [4, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 4, 2, 3], [3, 4, 1, 2], 'chords-db', []),
      P('Padrão', [5, 6, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Cmaj9': [
      P('Abertura', [0, 2, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('4ª casa', [4, 4, 3, 5], [2, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 7, 7, 7], [1, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Cmmaj11': [
      P('Padrão', [7, 5, 7, 6], [3, 1, 4, 2], 'chords-db', []),
      P('5ª casa (pestana)', [8, 5, 7, 5], [4, 1, 3, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 11, 10, 8], [1, 4, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Cmmaj7': [
      P('3ª casa', [5, 3, 3, 2], [4, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 2}]),
      P('3ª casa (pestana)', [4, 3, 3, 3], [2, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 7, 6], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Cmmaj7b5': [
      P('Padrão', [4, 3, 2, 3], [4, 2, 1, 3], 'chords-db', []),
      P('2ª casa (pestana)', [5, 3, 2, 2], [4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [5, 6, 7, 6], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Cmmaj9': [
      P('3ª casa (pestana)', [4, 3, 3, 5], [2, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 7, 5], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [7, 7, 7, 6], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Csus2': [
      P('3ª casa', [0, 2, 3, 3], [0, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 2, "to": 3}]),
      P('5ª casa (pestana)', [5, 7, 8, 5], [1, 3, 4, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 7, 8, 10], [1, 1, 2, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Csus4': [
      P('Abertura', [0, 0, 1, 3], [0, 0, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [5, 5, 3, 3], [2, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 8, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'D': [
      P('Padrão', [2, 2, 2, 0], [1, 2, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 2, 5], [1, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [7, 6, 5, 5], [3, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'D11': [
      P('Padrão', [0, 4, 2, 3], [0, 3, 1, 2], 'chords-db', []),
      P('Padrão', [9, 7, 8, 9], [3, 1, 2, 4], 'chords-db', [])
      ],
      'D13': [
      P('Padrão', [4, 4, 2, 3], [3, 4, 1, 2], 'chords-db', []),
      P('2ª casa (pestana)', [5, 4, 2, 2], [4, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [5, 6, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'D13b5b9': [
      P('Padrão', [5, 3, 4, 2], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [4, 3, 4, 3], [3, 1, 4, 2], 'chords-db', []),
      P('Padrão', [5, 8, 7, 6], [1, 4, 3, 2], 'chords-db', [])
      ],
      'D13b9': [
      P('2ª casa (pestana)', [5, 3, 2, 2], [4, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 3, 2, 3], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 7, 6], [1, 2, 4, 3], 'chords-db', [])
      ],
      'D6': [
      P('2ª casa (pestana)', [2, 2, 2, 2], [1, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 5, 5], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [7, 9, 7, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'D69': [
      P('2ª casa (pestana)', [2, 4, 2, 2], [1, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 5, 7], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [9, 9, 7, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'D7': [
      P('2ª casa (pestana)', [2, 2, 2, 3], [1, 1, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 5], [1, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'D7#9': [
      P('2ª casa (pestana)', [2, 5, 2, 3], [1, 4, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 8], [1, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 8, 9], [4, 2, 1, 3], 'chords-db', [])
      ],
      'D7b5': [
      P('Padrão', [1, 2, 2, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 6, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'D7b9': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'D7b9#5': [
      P('Padrão', [3, 3, 2, 3], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [5, 6, 6, 6], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 10, 8, 9], [1, 3, 1, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'D7sus4': [
      P('[2, 3]ª casa (pestana)', [2, 2, 3, 3], [1, 1, 2, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 2, "to": 3}]),
      P('5ª casa (pestana)', [5, 7, 5, 5], [1, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 9, 8, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'D9': [
      P('2ª casa (pestana)', [2, 4, 2, 3], [1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 7], [1, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [9, 9, 8, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'D9#11': [
      P('Padrão', [1, 4, 2, 3], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [5, 6, 4, 7], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 8, 9], [2, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'D9b5': [
      P('Padrão', [1, 4, 2, 3], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [5, 6, 4, 7], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 8, 9], [2, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Dadd9': [
      P('2ª casa (pestana)', [2, 4, 2, 5], [1, 3, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 5, 7], [3, 2, 1, 4], 'chords-db', []),
      P('9ª casa (pestana)', [9, 9, 10, 9], [1, 1, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Dalt': [
      P('Padrão', [7, 6, 4, 5], [4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [7, 8, 10, 9], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [11, 8, 10, 9], [4, 1, 3, 2], 'chords-db', [])
      ],
      'Daug': [
      P('2ª casa', [3, 2, 2, 1], [3, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 2}]),
      P('2ª casa (pestana)', [3, 2, 2, 5], [2, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [3, 6, 6, 5], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Daug7': [
      P('2ª casa (pestana)', [3, 2, 2, 3], [2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('[5, 6]ª casa (pestana)', [5, 6, 6, 5], [1, 2, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 1, "to": 2}]),
      P('Padrão', [7, 10, 8, 9], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Daug9': [
      P('Padrão', [3, 4, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 6, 7], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [9, 10, 8, 9], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Db': [
      P('1ª casa (pestana)', [1, 1, 1, 4], [1, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [6, 5, 4, 4], [3, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 9, 8], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Db11': [
      P('Padrão', [8, 6, 7, 8], [3, 1, 2, 4], 'chords-db', [])
      ],
      'Db13': [
      P('Padrão', [3, 3, 1, 2], [3, 4, 1, 2], 'chords-db', []),
      P('1ª casa (pestana)', [4, 3, 1, 1], [4, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [4, 5, 6, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Db13#9': [
      P('Padrão', [3, 5, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 6, 8], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [11, 10, 8, 8], [4, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Db13b5b9': [
      P('Padrão', [4, 2, 3, 1], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [3, 2, 3, 2], [3, 1, 4, 2], 'chords-db', []),
      P('Padrão', [4, 7, 6, 5], [1, 4, 3, 2], 'chords-db', [])
      ],
      'Db13b9': [
      P('Padrão', [3, 3, 2, 3], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [5, 6, 6, 6], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 10, 8, 9], [1, 3, 1, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}]),
      P('1ª casa (pestana)', [4, 2, 1, 1], [4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 2, 1, 2], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 6, 5], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Db6': [
      P('1ª casa (pestana)', [1, 1, 1, 1], [1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 4, 4], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [6, 8, 6, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Db69': [
      P('1ª casa (pestana)', [1, 3, 1, 1], [1, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 4, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 8, 6, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Db7': [
      P('1ª casa (pestana)', [1, 1, 1, 2], [1, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 4], [1, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Db7#9': [
      P('1ª casa (pestana)', [1, 4, 1, 2], [1, 4, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 7], [1, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 7, 8], [4, 2, 1, 3], 'chords-db', [])
      ],
      'Db7b5': [
      P('Padrão', [0, 1, 1, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 5, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Db7b9': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Db7b9#5': [
      P('Padrão', [2, 2, 1, 2], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [4, 5, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 9, 7, 8], [1, 3, 1, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Db7sus4': [
      P('[1, 2]ª casa (pestana)', [1, 1, 2, 2], [1, 1, 2, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 2, "to": 3}]),
      P('4ª casa (pestana)', [4, 6, 4, 4], [1, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 7, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Db9': [
      P('1ª casa (pestana)', [1, 3, 1, 2], [1, 3, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 6], [1, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [8, 8, 7, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Db9#11': [
      P('Padrão', [0, 3, 1, 2], [0, 3, 1, 2], 'chords-db', []),
      P('Padrão', [4, 5, 3, 6], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 7, 8], [2, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Db9b5': [
      P('Padrão', [0, 3, 1, 2], [0, 3, 1, 2], 'chords-db', []),
      P('Padrão', [4, 5, 3, 6], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 7, 8], [2, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Dbadd9': [
      P('1ª casa', [1, 3, 1, 4], [1, 3, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 4, 6], [3, 2, 1, 4], 'chords-db', []),
      P('8ª casa', [8, 8, 9, 8], [1, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Dbalt': [
      P('1ª casa', [0, 1, 1, 4], [0, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('Padrão', [6, 5, 3, 4], [4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [6, 7, 9, 8], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Dbaug': [
      P('Padrão', [2, 1, 1, 0], [3, 1, 2, 0], 'chords-db', []),
      P('1ª casa (pestana)', [2, 1, 1, 4], [2, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [2, 5, 5, 4], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Dbaug7': [
      P('1ª casa (pestana)', [2, 1, 1, 2], [2, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('[4, 5]ª casa (pestana)', [4, 5, 5, 4], [1, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 1, "to": 2}]),
      P('Padrão', [6, 9, 7, 8], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Dbaug9': [
      P('Padrão', [2, 3, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 3, 1, 0], [3, 2, 1, 0], 'chords-db', []),
      P('Padrão', [4, 5, 5, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Dbb13#9': [
      P('Padrão', [2, 4, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 5, 7], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [10, 9, 7, 7], [4, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Dbb13b9': [
      P('Padrão', [2, 2, 1, 2], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [4, 5, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 9, 7, 8], [1, 3, 1, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Dbdim': [
      P('Padrão', [6, 4, 3, 4], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 9, 7], [1, 2, 4, 3], 'chords-db', []),
      P('7ª casa (pestana)', [9, 7, 9, 7], [3, 1, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Dbdim7': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Dbm': [
      P('Padrão', [1, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [6, 4, 4, 4], [2, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [6, 4, 4, 7], [3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Dbm11': [
      P('7ª casa', [8, 6, 7, 7], [3, 1, 2, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [9, 6, 7, 6], [4, 1, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [9, 11, 11, 9], [1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Dbm6': [
      P('Padrão', [1, 1, 0, 1], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [3, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, 6, 7], [1, 3, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Dbm69': [
      P('Padrão', [1, 3, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 6], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [8, 8, 6, 7], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Dbm7': [
      P('Padrão', [1, 1, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 4], [1, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa', [6, 8, 7, 7], [1, 3, 2, 2], 'chords-db', [{"fret": 7, "from": 1, "to": 3}])
      ],
      'Dbm7b5': [
      P('Abertura', [0, 1, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 3, 4], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [6, 7, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Dbm9': [
      P('Padrão', [1, 3, 0, 2], [1, 3, 0, 2], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 6], [1, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 7, 6], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Dbm9b5': [
      P('Abertura', [0, 3, 0, 2], [0, 2, 0, 1], 'chords-db', []),
      P('4ª casa', [4, 4, 3, 6], [2, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa', [9, 7, 7, 6], [4, 2, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 2}])
      ],
      'Dbmadd9': [
      P('4ª casa (pestana)', [6, 4, 4, 6], [3, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 9, 6], [3, 2, 4, 1], 'chords-db', []),
      P('8ª casa', [8, 8, 9, 7], [2, 2, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 2}])
      ],
      'Dbmaj11': [
      P('Padrão', [8, 6, 8, 8], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [10, 12, 11, 9], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Dbmaj13': [
      P('Padrão', [3, 3, 1, 3], [2, 3, 1, 4], 'chords-db', []),
      P('[5, 6]ª casa (pestana)', [5, 5, 6, 6], [1, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 2, "to": 3}]),
      P('8ª casa (pestana)', [8, 10, 8, 8], [1, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Dbmaj7': [
      P('1ª casa (pestana)', [1, 1, 1, 3], [1, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [5, 5, 4, 4], [2, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 4, 3], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Dbmaj7#5': [
      P('1ª casa (pestana)', [2, 1, 1, 3], [2, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 5, 4], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [6, 5, 5, 3], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Dbmaj7b5': [
      P('Padrão', [0, 1, 1, 3], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [5, 5, 3, 4], [3, 4, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 3, 3], [4, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Dbmaj9': [
      P('Padrão', [1, 3, 1, 3], [1, 3, 2, 4], 'chords-db', []),
      P('5ª casa', [5, 5, 4, 6], [2, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 8, 8, 8], [1, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Dbmmaj11': [
      P('Padrão', [8, 6, 8, 7], [3, 1, 4, 2], 'chords-db', []),
      P('6ª casa (pestana)', [9, 6, 8, 6], [4, 1, 3, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [9, 12, 11, 9], [1, 4, 3, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Dbmmaj7': [
      P('Padrão', [1, 1, 0, 3], [1, 2, 0, 4], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 4, 4], [2, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('4ª casa', [6, 4, 4, 3], [4, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 2}])
      ],
      'Dbmmaj7b5': [
      P('Abertura', [0, 1, 0, 3], [0, 1, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 3, 4], [4, 2, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [6, 4, 3, 3], [4, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Dbmmaj9': [
      P('Padrão', [1, 3, 0, 3], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 4, 6], [2, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 8, 6], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Dbsus2': [
      P('4ª casa', [1, 3, 4, 4], [1, 2, 3, 3], 'chords-db', [{"fret": 4, "from": 2, "to": 3}]),
      P('6ª casa (pestana)', [6, 8, 9, 6], [1, 3, 4, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 8, 9, 11], [1, 1, 2, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Dbsus4': [
      P('1ª casa (pestana)', [1, 1, 2, 4], [1, 1, 2, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [6, 6, 4, 4], [3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 9, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Ddim': [
      P('Padrão', [7, 5, 4, 5], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 10, 8], [1, 2, 4, 3], 'chords-db', []),
      P('8ª casa (pestana)', [10, 8, 10, 8], [3, 1, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ddim7': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Dm': [
      P('Padrão', [2, 2, 1, 0], [2, 3, 1, 0], 'chords-db', []),
      P('Padrão', [2, 5, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [7, 5, 5, 5], [3, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Dm11': [
      P('8ª casa', [9, 7, 8, 8], [3, 1, 2, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [10, 7, 8, 7], [4, 1, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}]),
      P('10ª casa (pestana)', [10, 12, 12, 10], [1, 3, 4, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 3}])
      ],
      'Dm6': [
      P('Padrão', [2, 2, 1, 2], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [4, 5, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 9, 7, 8], [1, 3, 1, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Dm69': [
      P('Padrão', [2, 4, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 5, 7], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [9, 9, 7, 8], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Dm7': [
      P('2ª casa', [2, 2, 1, 3], [2, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 5, 5, 5], [1, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [7, 9, 8, 8], [1, 3, 2, 2], 'chords-db', [{"fret": 8, "from": 1, "to": 3}])
      ],
      'Dm7b5': [
      P('1ª casa (pestana)', [1, 2, 1, 3], [1, 2, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 4, 5], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [7, 8, 8, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Dm9': [
      P('Padrão', [2, 4, 1, 3], [2, 4, 1, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 7], [1, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 8, 7], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Dm9b5': [
      P('1ª casa (pestana)', [1, 4, 1, 3], [1, 4, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('5ª casa', [5, 5, 4, 7], [2, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [10, 8, 8, 7], [4, 2, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 2}])
      ],
      'Dmadd9': [
      P('5ª casa (pestana)', [7, 5, 5, 7], [3, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 10, 7], [3, 2, 4, 1], 'chords-db', []),
      P('9ª casa', [9, 9, 10, 8], [2, 2, 3, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 2}])
      ],
      'Dmaj11': [
      P('Padrão', [0, 4, 2, 4], [0, 2, 1, 3], 'chords-db', []),
      P('Padrão', [9, 7, 9, 9], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [11, 13, 12, 10], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Dmaj13': [
      P('Padrão', [4, 4, 2, 4], [2, 3, 1, 4], 'chords-db', []),
      P('[6, 7]ª casa (pestana)', [6, 6, 7, 7], [1, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 2, "to": 3}]),
      P('9ª casa (pestana)', [9, 11, 9, 9], [1, 3, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Dmaj7': [
      P('2ª casa (pestana)', [2, 2, 2, 4], [1, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 5, 4], [4, 3, 2, 1], 'chords-db', []),
      P('5ª casa (pestana)', [6, 6, 5, 5], [2, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Dmaj7#5': [
      P('2ª casa (pestana)', [3, 2, 2, 4], [2, 1, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 6, 4], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [6, 6, 6, 5], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Dmaj7b5': [
      P('Padrão', [1, 2, 2, 4], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [7, 6, 4, 4], [4, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 4, 5], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Dmaj9': [
      P('Padrão', [2, 4, 2, 4], [1, 3, 2, 4], 'chords-db', []),
      P('6ª casa', [6, 6, 5, 7], [2, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [9, 9, 9, 9], [1, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Dmmaj11': [
      P('Padrão', [9, 7, 9, 8], [3, 1, 4, 2], 'chords-db', []),
      P('7ª casa (pestana)', [10, 7, 9, 7], [4, 1, 3, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}]),
      P('10ª casa (pestana)', [10, 13, 12, 10], [1, 4, 3, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 3}])
      ],
      'Dmmaj7': [
      P('2ª casa', [2, 2, 1, 4], [2, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa', [7, 5, 5, 4], [4, 2, 2, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 2}]),
      P('5ª casa (pestana)', [6, 5, 5, 5], [2, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Dmmaj7b5': [
      P('1ª casa (pestana)', [1, 2, 1, 4], [1, 2, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 4, 5], [4, 2, 1, 3], 'chords-db', []),
      P('4ª casa (pestana)', [7, 5, 4, 4], [4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'Dmmaj9': [
      P('Padrão', [2, 4, 1, 4], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 5, 7], [2, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 9, 7], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Dsus2': [
      P('5ª casa', [2, 4, 5, 5], [1, 2, 3, 3], 'chords-db', [{"fret": 5, "from": 2, "to": 3}]),
      P('7ª casa (pestana)', [7, 9, 10, 7], [1, 3, 4, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [9, 9, 10, 12], [1, 1, 2, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Dsus4': [
      P('Abertura', [0, 2, 3, 0], [0, 2, 3, 0], 'chords-db', []),
      P('Padrão', [2, 2, 3, 0], [1, 2, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 3, 5], [1, 1, 2, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}])
      ],
      'E': [
      P('Padrão', [1, 4, 0, 2], [1, 4, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 4, 2], [2, 3, 4, 1], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 7], [1, 1, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'E11': [
      P('Padrão', [1, 2, 2, 0], [1, 2, 3, 0], 'chords-db', [])
      ],
      'E13': [
      P('Padrão', [1, 2, 2, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 6, 4, 5], [3, 4, 1, 2], 'chords-db', []),
      P('4ª casa (pestana)', [7, 6, 4, 4], [4, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'E13b5b9': [
      P('Padrão', [3, 2, 1, 4], [3, 2, 1, 4], 'chords-db', []),
      P('Padrão', [7, 5, 6, 4], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [6, 5, 6, 5], [3, 1, 4, 2], 'chords-db', [])
      ],
      'E13b9': [
      P('1ª casa (pestana)', [1, 2, 1, 4], [1, 2, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [7, 5, 4, 4], [4, 2, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 4, 5], [4, 2, 1, 3], 'chords-db', [])
      ],
      'E6': [
      P('Padrão', [1, 1, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 4], [1, 1, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 7, 7], [1, 4, 2, 3], 'chords-db', [])
      ],
      'E69': [
      P('[1, 2]ª casa (pestana)', [1, 1, 2, 2], [1, 1, 2, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 2, "to": 3}]),
      P('4ª casa (pestana)', [4, 6, 4, 4], [1, 3, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 8, 7, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'E7': [
      P('Padrão', [1, 2, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 5], [1, 1, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 7], [1, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'E7#9': [
      P('Padrão', [1, 2, 3, 2], [1, 2, 4, 3], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 4, 5], [1, 4, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 10], [1, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'E7b5': [
      P('Padrão', [1, 2, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 5], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [7, 8, 6, 7], [2, 4, 1, 3], 'chords-db', [])
      ],
      'E7b9': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'E7b9#5': [
      P('1ª casa (pestana)', [1, 2, 1, 3], [1, 2, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 4, 5], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [7, 8, 8, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'E7sus4': [
      P('Padrão', [2, 2, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('[4, 5]ª casa (pestana)', [4, 4, 5, 5], [1, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 2, "to": 3}]),
      P('7ª casa (pestana)', [7, 9, 7, 7], [1, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'E9': [
      P('Padrão', [1, 2, 2, 2], [1, 2, 3, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 4, 5], [1, 3, 1, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 8, 7, 9], [1, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'E9#11': [
      P('[1, 2]ª casa (pestana)', [1, 2, 2, 1], [1, 2, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 1, "to": 2}]),
      P('Padrão', [3, 6, 4, 5], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [7, 8, 6, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'E9b5': [
      P('[1, 2]ª casa (pestana)', [1, 2, 2, 1], [1, 2, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 1, "to": 2}]),
      P('Padrão', [3, 6, 4, 5], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [7, 8, 6, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Eadd9': [
      P('2ª casa', [1, 4, 2, 2], [1, 4, 2, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 3}]),
      P('4ª casa (pestana)', [4, 6, 4, 7], [1, 3, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 7, 9], [3, 2, 1, 4], 'chords-db', [])
      ],
      'Ealt': [
      P('Padrão', [9, 8, 6, 7], [4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [9, 10, 12, 11], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [13, 10, 12, 11], [4, 1, 3, 2], 'chords-db', [])
      ],
      'Eaug': [
      P('Abertura', [1, 0, 0, 3], [1, 0, 0, 3], 'chords-db', []),
      P('Padrão', [1, 4, 4, 3], [1, 3, 4, 2], 'chords-db', []),
      P('4ª casa', [5, 4, 4, 3], [3, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 2}])
      ],
      'Eaug7': [
      P('Padrão', [1, 2, 0, 3], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa', [5, 4, 4, 5], [2, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('[7, 8]ª casa', [7, 8, 8, 7], [1, 2, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}, {"fret": 8, "from": 1, "to": 2}])
      ],
      'Eaug9': [
      P('2ª casa', [1, 2, 2, 3], [1, 2, 2, 3], 'chords-db', [{"fret": 2, "from": 1, "to": 3}]),
      P('Padrão', [5, 6, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Eb': [
      P('Padrão', [0, 3, 3, 1], [0, 3, 4, 1], 'chords-db', []),
      P('Padrão', [3, 3, 3, 1], [2, 3, 4, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 3, 6], [1, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Eb11': [
      P('Padrão', [10, 8, 9, 10], [3, 1, 2, 4], 'chords-db', [])
      ],
      'Eb13': [
      P('Padrão', [0, 1, 1, 3], [0, 1, 2, 4], 'chords-db', []),
      P('Padrão', [5, 5, 3, 4], [3, 4, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [6, 5, 3, 3], [4, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Eb13#9': [
      P('Padrão', [1, 2, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Eb13b5b9': [
      P('Padrão', [2, 1, 0, 3], [2, 1, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 5, 4], [3, 1, 4, 2], 'chords-db', []),
      P('Padrão', [6, 4, 5, 3], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Eb13b9': [
      P('1ª casa (pestana)', [1, 2, 1, 3], [1, 2, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 4, 5], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [7, 8, 8, 8], [1, 2, 3, 4], 'chords-db', []),
      P('Abertura', [0, 1, 0, 3], [0, 1, 0, 3], 'chords-db', []),
      P('Padrão', [5, 4, 3, 4], [4, 2, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [6, 4, 3, 3], [4, 2, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Eb6': [
      P('3ª casa (pestana)', [3, 3, 3, 3], [1, 1, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 6, 6], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [8, 10, 8, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Eb69': [
      P('Abertura', [0, 0, 1, 1], [0, 0, 1, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 3], [1, 3, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 7, 6, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Eb7': [
      P('3ª casa (pestana)', [3, 3, 3, 4], [1, 1, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 6], [1, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [8, 10, 9, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Eb7#9': [
      P('Padrão', [0, 1, 2, 1], [0, 1, 3, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 3, 4], [1, 4, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 9], [1, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Eb7b5': [
      P('Padrão', [2, 3, 3, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 7, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Eb7b9': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Eb7b9#5': [
      P('Abertura', [0, 1, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 3, 4], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [6, 7, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Eb7sus4': [
      P('[3, 3]ª casa (pestana)', [3, 3, 4, 4], [1, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}, {"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 8, 6, 6], [1, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [8, 10, 9, 11], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Eb9': [
      P('Padrão', [0, 1, 1, 1], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 4], [1, 3, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 8], [1, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Eb9#11': [
      P('Abertura', [0, 1, 1, 0], [0, 1, 2, 0], 'chords-db', []),
      P('Padrão', [2, 5, 3, 4], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [6, 7, 5, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Eb9b5': [
      P('Abertura', [0, 1, 1, 0], [0, 1, 2, 0], 'chords-db', []),
      P('Padrão', [2, 5, 3, 4], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [6, 7, 5, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Ebadd9': [
      P('1ª casa', [0, 3, 1, 1], [0, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('3ª casa (pestana)', [3, 5, 3, 6], [1, 3, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 6, 8], [3, 2, 1, 4], 'chords-db', [])
      ],
      'Ebalt': [
      P('Padrão', [8, 7, 5, 6], [3, 4, 1, 2], 'chords-db', []),
      P('Padrão', [8, 9, 11, 10], [1, 2, 4, 3], 'chords-db', []),
      P('Padrão', [12, 9, 11, 10], [4, 1, 3, 2], 'chords-db', [])
      ],
      'Ebaug': [
      P('Padrão', [0, 3, 3, 2], [0, 3, 2, 1], 'chords-db', []),
      P('3ª casa', [4, 3, 3, 2], [3, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 2}]),
      P('3ª casa (pestana)', [4, 3, 3, 6], [2, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Ebaug7': [
      P('3ª casa (pestana)', [4, 3, 3, 4], [2, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('[6, 7]ª casa (pestana)', [6, 7, 7, 6], [1, 2, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 1, "to": 2}]),
      P('Padrão', [8, 11, 9, 10], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Ebaug9': [
      P('1ª casa', [0, 1, 1, 2], [0, 1, 1, 2], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('Padrão', [4, 5, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Ebb13#9': [
      P('Padrão', [0, 1, 2, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Ebb13b9': [
      P('Abertura', [0, 1, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 3, 4], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [6, 7, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Ebdim': [
      P('Padrão', [2, 3, 2, 0], [1, 3, 2, 0], 'chords-db', []),
      P('Padrão', [8, 6, 5, 6], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 11, 9], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Ebdim7': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Ebm': [
      P('Padrão', [3, 3, 2, 1], [3, 4, 2, 1], 'chords-db', []),
      P('6ª casa', [3, 6, 6, 6], [1, 3, 3, 3], 'chords-db', [{"fret": 6, "from": 1, "to": 3}]),
      P('6ª casa (pestana)', [8, 6, 6, 6], [3, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Ebm11': [
      P('9ª casa', [10, 8, 9, 9], [3, 1, 2, 2], 'chords-db', [{"fret": 9, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [11, 8, 9, 8], [4, 1, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}]),
      P('11ª casa (pestana)', [11, 13, 13, 11], [1, 3, 4, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 3}])
      ],
      'Ebm6': [
      P('Padrão', [3, 3, 2, 3], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [5, 6, 6, 6], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [8, 10, 8, 9], [1, 3, 1, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ebm69': [
      P('Padrão', [3, 5, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 6, 8], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [10, 10, 8, 9], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Ebm7': [
      P('3ª casa', [3, 3, 2, 4], [2, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 6, 6, 6], [1, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa', [8, 10, 9, 9], [1, 3, 2, 2], 'chords-db', [{"fret": 9, "from": 1, "to": 3}])
      ],
      'Ebm7b5': [
      P('2ª casa (pestana)', [2, 3, 2, 4], [1, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 5, 6], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [8, 9, 9, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Ebm9': [
      P('Padrão', [3, 5, 2, 4], [2, 4, 1, 3], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 6, 8], [1, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [11, 10, 9, 8], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Ebm9b5': [
      P('2ª casa (pestana)', [2, 5, 2, 4], [1, 4, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('6ª casa', [6, 6, 5, 8], [2, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa', [11, 9, 9, 8], [4, 2, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 2}])
      ],
      'Ebmadd9': [
      P('6ª casa (pestana)', [8, 6, 6, 8], [3, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [11, 10, 11, 8], [3, 2, 4, 1], 'chords-db', []),
      P('10ª casa', [10, 10, 11, 9], [2, 2, 3, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 2}])
      ],
      'Ebmaj11': [
      P('Padrão', [10, 8, 10, 10], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [12, 14, 13, 11], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Ebmaj13': [
      P('Padrão', [0, 2, 1, 3], [0, 2, 1, 3], 'chords-db', []),
      P('Padrão', [5, 5, 3, 5], [2, 3, 1, 4], 'chords-db', []),
      P('[7, 8]ª casa (pestana)', [7, 7, 8, 8], [1, 1, 2, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}, {"fret": 8, "from": 2, "to": 3}])
      ],
      'Ebmaj7': [
      P('3ª casa (pestana)', [3, 3, 3, 5], [1, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 6, 5], [4, 3, 2, 1], 'chords-db', []),
      P('6ª casa (pestana)', [7, 7, 6, 6], [2, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Ebmaj7#5': [
      P('3ª casa (pestana)', [4, 3, 3, 5], [2, 1, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 7, 5], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [7, 7, 7, 6], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Ebmaj7b5': [
      P('Padrão', [2, 3, 3, 5], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [8, 7, 5, 5], [4, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 5, 6], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Ebmaj9': [
      P('1ª casa', [0, 2, 1, 1], [0, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('Padrão', [3, 5, 3, 5], [1, 3, 2, 4], 'chords-db', []),
      P('7ª casa', [7, 7, 6, 8], [2, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Ebmmaj11': [
      P('Padrão', [10, 8, 10, 9], [3, 1, 4, 2], 'chords-db', []),
      P('8ª casa (pestana)', [11, 8, 10, 8], [4, 1, 3, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}]),
      P('11ª casa (pestana)', [11, 14, 13, 11], [1, 4, 3, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 3}])
      ],
      'Ebmmaj7': [
      P('3ª casa', [3, 3, 2, 5], [2, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa', [8, 6, 6, 5], [4, 2, 2, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 2}]),
      P('6ª casa (pestana)', [7, 6, 6, 6], [2, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Ebmmaj7b5': [
      P('2ª casa (pestana)', [2, 3, 2, 5], [1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [7, 6, 5, 6], [4, 2, 1, 3], 'chords-db', []),
      P('5ª casa (pestana)', [8, 6, 5, 5], [4, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Ebmmaj9': [
      P('Padrão', [3, 5, 2, 5], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [7, 6, 6, 8], [2, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [11, 10, 10, 8], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Ebsus2': [
      P('1ª casa (pestana)', [3, 3, 1, 1], [3, 4, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('6ª casa', [3, 5, 6, 6], [1, 2, 3, 3], 'chords-db', [{"fret": 6, "from": 2, "to": 3}]),
      P('8ª casa (pestana)', [8, 10, 11, 8], [1, 3, 4, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Ebsus4': [
      P('1ª casa (pestana)', [1, 3, 4, 1], [1, 2, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 3, 4, 1], [2, 3, 4, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 3, 4, 6], [1, 1, 2, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Edim': [
      P('Padrão', [3, 4, 3, 1], [2, 4, 3, 1], 'chords-db', []),
      P('Padrão', [9, 7, 6, 7], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [9, 10, 12, 10], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Edim7': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Em': [
      P('Padrão', [0, 4, 3, 2], [0, 3, 2, 1], 'chords-db', []),
      P('Padrão', [4, 4, 3, 2], [3, 4, 2, 1], 'chords-db', []),
      P('Padrão', [4, 7, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Em11': [
      P('Abertura', [0, 2, 2, 0], [0, 2, 3, 0], 'chords-db', []),
      P('10ª casa', [11, 9, 10, 10], [3, 1, 2, 2], 'chords-db', [{"fret": 10, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [12, 9, 10, 9], [4, 1, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Em6': [
      P('Abertura', [0, 1, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 3, 4], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [6, 7, 7, 7], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Em69': [
      P('Padrão', [0, 1, 2, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Em7': [
      P('Abertura', [0, 2, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('4ª casa', [4, 4, 3, 5], [2, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [7, 7, 7, 7], [1, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Em7b5': [
      P('Abertura', [0, 2, 0, 1], [0, 2, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 5], [1, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 6, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Em9': [
      P('Padrão', [0, 2, 2, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 3, 5], [2, 4, 1, 3], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 7, 9], [1, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Em9b5': [
      P('Padrão', [0, 2, 2, 1], [0, 2, 3, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 3, 5], [1, 4, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('7ª casa', [7, 7, 6, 9], [2, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Emadd9': [
      P('7ª casa (pestana)', [9, 7, 7, 9], [3, 1, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}]),
      P('Padrão', [12, 11, 12, 9], [3, 2, 4, 1], 'chords-db', []),
      P('11ª casa', [11, 11, 12, 10], [2, 2, 3, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 2}])
      ],
      'Emaj11': [
      P('Padrão', [1, 3, 2, 0], [1, 3, 2, 0], 'chords-db', []),
      P('Padrão', [11, 9, 11, 11], [2, 1, 3, 4], 'chords-db', [])
      ],
      'Emaj13': [
      P('Padrão', [1, 3, 2, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 6, 4, 6], [2, 3, 1, 4], 'chords-db', []),
      P('[8, 9]ª casa (pestana)', [8, 8, 9, 9], [1, 1, 2, 2], 'chords-db', [{"fret": 8, "from": 0, "to": 3}, {"fret": 9, "from": 2, "to": 3}])
      ],
      'Emaj7': [
      P('Padrão', [1, 3, 0, 2], [1, 3, 0, 2], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 4, 6], [1, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 7, 6], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Emaj7#5': [
      P('Padrão', [1, 3, 0, 3], [1, 2, 0, 3], 'chords-db', []),
      P('4ª casa (pestana)', [5, 4, 4, 6], [2, 1, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 8, 6], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Emaj7b5': [
      P('Padrão', [1, 3, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 6], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [9, 8, 6, 6], [4, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Emaj9': [
      P('2ª casa', [1, 3, 2, 2], [1, 3, 2, 2], 'chords-db', [{"fret": 2, "from": 1, "to": 3}]),
      P('Padrão', [4, 6, 4, 6], [1, 3, 2, 4], 'chords-db', []),
      P('8ª casa', [8, 8, 7, 9], [2, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Emmaj11': [
      P('Abertura', [0, 3, 2, 0], [0, 3, 2, 0], 'chords-db', []),
      P('Padrão', [11, 9, 11, 10], [3, 1, 4, 2], 'chords-db', []),
      P('9ª casa (pestana)', [12, 9, 11, 9], [4, 1, 3, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Emmaj7': [
      P('Abertura', [0, 3, 0, 2], [0, 2, 0, 1], 'chords-db', []),
      P('4ª casa', [4, 4, 3, 6], [2, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa', [9, 7, 7, 6], [4, 2, 2, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 2}])
      ],
      'Emmaj7b5': [
      P('Abertura', [0, 3, 0, 1], [0, 3, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 6], [1, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [8, 7, 6, 7], [4, 2, 1, 3], 'chords-db', [])
      ],
      'Emmaj9': [
      P('Padrão', [0, 3, 2, 2], [0, 3, 1, 2], 'chords-db', []),
      P('Padrão', [4, 6, 3, 6], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 7, 9], [2, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Esus2': [
      P('2ª casa (pestana)', [4, 4, 2, 2], [3, 4, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('7ª casa', [4, 6, 7, 7], [1, 2, 3, 3], 'chords-db', [{"fret": 7, "from": 2, "to": 3}]),
      P('9ª casa (pestana)', [9, 11, 12, 9], [1, 3, 4, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Esus4': [
      P('2ª casa (pestana)', [2, 4, 5, 2], [1, 2, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 4, 5, 2], [2, 3, 4, 1], 'chords-db', []),
      P('4ª casa (pestana)', [4, 4, 5, 7], [1, 1, 2, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}])
      ],
      'F': [
      P('Abertura', [2, 0, 1, 0], [2, 0, 1, 0], 'chords-db', []),
      P('Padrão', [2, 0, 1, 3], [2, 0, 1, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 8], [1, 1, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'F11': [
      P('Padrão', [1, 2, 2, 0], [1, 2, 3, 0], 'chords-db', [])
      ],
      'F13': [
      P('Padrão', [2, 3, 3, 5], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [7, 7, 5, 6], [3, 4, 1, 2], 'chords-db', []),
      P('5ª casa (pestana)', [8, 7, 5, 5], [4, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'F13b5b9': [
      P('Padrão', [4, 3, 2, 5], [3, 2, 1, 4], 'chords-db', []),
      P('Padrão', [8, 6, 7, 5], [4, 2, 3, 1], 'chords-db', []),
      P('Padrão', [7, 6, 7, 6], [3, 1, 4, 2], 'chords-db', [])
      ],
      'F13b9': [
      P('2ª casa (pestana)', [2, 3, 2, 5], [1, 2, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [8, 6, 5, 5], [4, 2, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [8, 9, 10, 9], [1, 2, 4, 3], 'chords-db', [])
      ],
      'F6': [
      P('Padrão', [2, 2, 1, 3], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 5], [1, 1, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 9, 8, 8], [1, 4, 2, 3], 'chords-db', [])
      ],
      'F69': [
      P('[2, 3]ª casa (pestana)', [2, 2, 3, 3], [1, 1, 2, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 2, "to": 3}]),
      P('5ª casa (pestana)', [5, 7, 5, 5], [1, 3, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [7, 9, 8, 10], [1, 3, 2, 4], 'chords-db', [])
      ],
      'F7': [
      P('Padrão', [2, 3, 1, 3], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 6], [1, 1, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 8], [1, 2, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'F7#9': [
      P('Padrão', [2, 3, 4, 3], [1, 2, 4, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 5, 6], [1, 4, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 11], [1, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'F7b5': [
      P('Padrão', [2, 3, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 5, 6], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [8, 9, 7, 8], [2, 4, 1, 3], 'chords-db', [])
      ],
      'F7b9': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'F7b9#5': [
      P('2ª casa (pestana)', [2, 3, 2, 4], [1, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 5, 6], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [8, 9, 9, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'F7sus4': [
      P('Padrão', [3, 3, 1, 3], [2, 3, 1, 4], 'chords-db', []),
      P('[5, 6]ª casa (pestana)', [5, 5, 6, 6], [1, 1, 2, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}, {"fret": 6, "from": 2, "to": 3}]),
      P('8ª casa (pestana)', [8, 10, 8, 8], [1, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'F9': [
      P('Padrão', [2, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('5ª casa (pestana)', [5, 7, 5, 6], [1, 3, 1, 2], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 9, 8, 10], [1, 2, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'F9#11': [
      P('[2, 3]ª casa (pestana)', [2, 3, 3, 2], [1, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 1, "to": 2}]),
      P('Padrão', [4, 7, 5, 6], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [8, 9, 7, 10], [2, 3, 1, 4], 'chords-db', [])
      ],
      'F9b5': [
      P('[2, 3]ª casa (pestana)', [2, 3, 3, 2], [1, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}, {"fret": 3, "from": 1, "to": 2}]),
      P('Padrão', [4, 7, 5, 6], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [8, 9, 7, 10], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Fadd9': [
      P('Abertura', [0, 0, 1, 0], [0, 0, 1, 0], 'chords-db', []),
      P('3ª casa', [2, 5, 3, 3], [1, 4, 2, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 3}]),
      P('5ª casa (pestana)', [5, 7, 5, 8], [1, 3, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Falt': [
      P('2ª casa (pestana)', [2, 5, 5, 2], [1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 7, 8], [4, 3, 1, 2], 'chords-db', []),
      P('Padrão', [10, 11, 13, 12], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Faug': [
      P('Padrão', [2, 1, 1, 0], [3, 1, 2, 0], 'chords-db', []),
      P('1ª casa (pestana)', [2, 1, 1, 4], [2, 1, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [2, 5, 5, 4], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Faug7': [
      P('Padrão', [2, 3, 1, 4], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 5, 6], [2, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('[8, 9]ª casa (pestana)', [8, 9, 9, 8], [1, 2, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}, {"fret": 9, "from": 1, "to": 2}])
      ],
      'Faug9': [
      P('3ª casa', [2, 3, 3, 4], [1, 2, 2, 3], 'chords-db', [{"fret": 3, "from": 1, "to": 3}]),
      P('Padrão', [6, 7, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Fb13#9': [
      P('Padrão', [2, 3, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 11], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Fb13b9': [
      P('2ª casa (pestana)', [2, 3, 2, 4], [1, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 5, 6], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [8, 9, 9, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Fdim': [
      P('Padrão', [4, 5, 4, 2], [2, 4, 3, 1], 'chords-db', []),
      P('Padrão', [10, 8, 7, 8], [4, 2, 1, 3], 'chords-db', []),
      P('Padrão', [10, 11, 13, 11], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Fdim7': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Fm': [
      P('Padrão', [1, 0, 1, 3], [1, 0, 2, 4], 'chords-db', []),
      P('Padrão', [5, 5, 4, 3], [3, 4, 2, 1], 'chords-db', []),
      P('Padrão', [5, 8, 8, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Fm11': [
      P('1ª casa (pestana)', [1, 3, 3, 1], [1, 3, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('11ª casa', [12, 10, 11, 11], [3, 1, 2, 2], 'chords-db', [{"fret": 11, "from": 0, "to": 3}]),
      P('10ª casa (pestana)', [13, 10, 11, 10], [4, 1, 2, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 3}])
      ],
      'Fm6': [
      P('1ª casa (pestana)', [1, 2, 1, 3], [1, 2, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [5, 5, 4, 5], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [7, 8, 8, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Fm69': [
      P('Padrão', [1, 2, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 4, 5], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [7, 8, 8, 10], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Fm7': [
      P('Padrão', [1, 3, 1, 3], [1, 3, 2, 4], 'chords-db', []),
      P('5ª casa', [5, 5, 4, 6], [2, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa (pestana)', [8, 8, 8, 8], [1, 1, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Fm7b5': [
      P('1ª casa (pestana)', [1, 3, 1, 2], [1, 3, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 6], [1, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [8, 8, 7, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Fm9': [
      P('Padrão', [1, 3, 3, 3], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [5, 7, 4, 6], [2, 4, 1, 3], 'chords-db', []),
      P('8ª casa (pestana)', [8, 8, 8, 10], [1, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Fm9b5': [
      P('Padrão', [1, 3, 3, 2], [1, 3, 4, 2], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 4, 6], [1, 4, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('8ª casa', [8, 8, 7, 10], [2, 2, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Fmadd9': [
      P('Padrão', [0, 5, 4, 3], [0, 3, 2, 1], 'chords-db', []),
      P('8ª casa (pestana)', [10, 8, 8, 10], [3, 1, 1, 4], 'chords-db', [{"fret": 8, "from": 0, "to": 3}]),
      P('Padrão', [13, 12, 13, 10], [3, 2, 4, 1], 'chords-db', [])
      ],
      'Fmaj11': [
      P('Padrão', [2, 4, 3, 1], [2, 4, 3, 1], 'chords-db', []),
      P('Padrão', [12, 10, 12, 12], [2, 1, 3, 4], 'chords-db', [])
      ],
      'Fmaj13': [
      P('Abertura', [0, 2, 0, 0], [0, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 3, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 7, 5, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Fmaj7': [
      P('Padrão', [2, 4, 1, 3], [2, 4, 1, 3], 'chords-db', []),
      P('5ª casa (pestana)', [5, 5, 5, 7], [1, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 8, 7], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Fmaj7#5': [
      P('Padrão', [2, 4, 1, 4], [2, 3, 1, 4], 'chords-db', []),
      P('5ª casa (pestana)', [6, 5, 5, 7], [2, 1, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 9, 7], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Fmaj7b5': [
      P('Padrão', [2, 4, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 5, 7], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [10, 9, 7, 7], [4, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Fmaj9': [
      P('Abertura', [0, 0, 0, 0], [0, 0, 0, 0], 'chords-db', []),
      P('3ª casa', [2, 4, 3, 3], [1, 3, 2, 2], 'chords-db', [{"fret": 3, "from": 1, "to": 3}]),
      P('Padrão', [5, 7, 5, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Fmmaj11': [
      P('1ª casa (pestana)', [1, 4, 3, 1], [1, 4, 3, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [12, 10, 12, 11], [3, 1, 4, 2], 'chords-db', []),
      P('10ª casa (pestana)', [13, 10, 12, 10], [4, 1, 3, 1], 'chords-db', [{"fret": 10, "from": 0, "to": 3}])
      ],
      'Fmmaj7': [
      P('1ª casa (pestana)', [1, 4, 1, 3], [1, 4, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('5ª casa', [5, 5, 4, 7], [2, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('8ª casa', [10, 8, 8, 7], [4, 2, 2, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 2}])
      ],
      'Fmmaj7b5': [
      P('1ª casa (pestana)', [1, 4, 1, 2], [1, 4, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 7], [1, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [9, 8, 7, 8], [4, 2, 1, 3], 'chords-db', [])
      ],
      'Fmmaj9': [
      P('Padrão', [1, 4, 3, 3], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [5, 7, 4, 7], [2, 3, 1, 4], 'chords-db', []),
      P('8ª casa (pestana)', [9, 8, 8, 10], [2, 1, 1, 3], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Fsus2': [
      P('Abertura', [0, 0, 1, 3], [0, 0, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [5, 5, 3, 3], [3, 4, 1, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('8ª casa', [5, 7, 8, 8], [1, 2, 3, 3], 'chords-db', [{"fret": 8, "from": 2, "to": 3}])
      ],
      'Fsus4': [
      P('1ª casa', [3, 0, 1, 1], [3, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 0, 1, 3], [2, 0, 1, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 6, 3], [1, 2, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'G': [
      P('Padrão', [0, 2, 3, 2], [0, 1, 3, 2], 'chords-db', []),
      P('2ª casa (pestana)', [4, 2, 3, 2], [3, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 2, 3, 5], [3, 1, 2, 4], 'chords-db', [])
      ],
      'G11': [
      P('Padrão', [2, 0, 1, 2], [2, 0, 1, 3], 'chords-db', []),
      P('Padrão', [5, 5, 5, 2], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [4, 5, 5, 3], [2, 3, 4, 1], 'chords-db', [])
      ],
      'G13': [
      P('Padrão', [2, 4, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 5, 7], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [9, 9, 7, 8], [3, 4, 1, 2], 'chords-db', [])
      ],
      'G13b5b9': [
      P('1ª casa (pestana)', [1, 4, 1, 4], [1, 3, 1, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [6, 5, 4, 7], [3, 2, 1, 4], 'chords-db', []),
      P('Padrão', [10, 8, 9, 7], [4, 2, 3, 1], 'chords-db', [])
      ],
      'G13b9': [
      P('1ª casa (pestana)', [1, 4, 1, 2], [1, 4, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 7], [1, 2, 1, 4], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('7ª casa (pestana)', [10, 8, 7, 7], [4, 2, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'G6': [
      P('Abertura', [0, 2, 0, 2], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [4, 4, 3, 5], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 7, 7], [1, 1, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'G69': [
      P('Padrão', [2, 2, 0, 2], [1, 2, 0, 3], 'chords-db', []),
      P('[4, 5]ª casa (pestana)', [4, 4, 5, 5], [1, 1, 2, 2], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 2, "to": 3}]),
      P('7ª casa (pestana)', [7, 9, 7, 7], [1, 3, 1, 1], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'G7': [
      P('Padrão', [0, 2, 1, 2], [0, 2, 1, 3], 'chords-db', []),
      P('Padrão', [4, 5, 3, 5], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 7, 8], [1, 1, 1, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'G7#9': [
      P('Padrão', [3, 2, 1, 2], [4, 2, 1, 3], 'chords-db', []),
      P('1ª casa (pestana)', [4, 2, 1, 1], [4, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [4, 5, 6, 5], [1, 2, 4, 3], 'chords-db', [])
      ],
      'G7b5': [
      P('Padrão', [0, 1, 1, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 5, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 8], [1, 2, 3, 4], 'chords-db', [])
      ],
      'G7b9': [
      P('Padrão', [1, 2, 1, 2], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [4, 5, 4, 5], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [7, 8, 7, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'G7b9#5': [
      P('1ª casa (pestana)', [1, 3, 1, 2], [1, 3, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 6], [1, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [8, 8, 7, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'G7sus4': [
      P('Padrão', [0, 2, 1, 3], [0, 2, 1, 3], 'chords-db', []),
      P('Padrão', [5, 5, 3, 5], [2, 3, 1, 4], 'chords-db', []),
      P('[7, 7]ª casa (pestana)', [7, 7, 8, 8], [1, 1, 2, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}, {"fret": 7, "from": 0, "to": 3}])
      ],
      'G9': [
      P('Padrão', [2, 2, 1, 2], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [4, 5, 5, 5], [1, 2, 3, 4], 'chords-db', []),
      P('7ª casa (pestana)', [7, 9, 7, 8], [1, 3, 1, 2], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'G9#11': [
      P('1ª casa (pestana)', [2, 1, 1, 2], [2, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('[4, 5]ª casa (pestana)', [4, 5, 5, 4], [1, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 1, "to": 2}]),
      P('Padrão', [6, 9, 7, 8], [1, 4, 2, 3], 'chords-db', [])
      ],
      'G9b5': [
      P('1ª casa', [2, 1, 1, 2], [2, 1, 1, 3], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('[4, 5]ª casa (pestana)', [4, 5, 5, 4], [1, 2, 2, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}, {"fret": 5, "from": 1, "to": 2}]),
      P('Padrão', [6, 9, 7, 8], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Gadd9': [
      P('2ª casa (pestana)', [2, 2, 3, 2], [1, 1, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa', [4, 7, 5, 5], [1, 4, 2, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 3}]),
      P('7ª casa (pestana)', [7, 9, 7, 10], [1, 3, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Galt': [
      P('Padrão', [4, 1, 3, 2], [4, 1, 3, 2], 'chords-db', []),
      P('4ª casa (pestana)', [4, 7, 7, 4], [1, 3, 4, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [12, 11, 9, 10], [4, 3, 1, 2], 'chords-db', [])
      ],
      'Gaug': [
      P('Padrão', [0, 3, 3, 2], [0, 2, 3, 1], 'chords-db', []),
      P('3ª casa', [4, 3, 3, 2], [3, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 2}]),
      P('3ª casa (pestana)', [4, 3, 3, 6], [2, 1, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Gaug7': [
      P('Padrão', [0, 3, 1, 2], [0, 3, 1, 2], 'chords-db', []),
      P('Padrão', [4, 5, 3, 6], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 7, 8], [2, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Gaug9': [
      P('Padrão', [2, 3, 1, 2], [2, 4, 1, 3], 'chords-db', []),
      P('5ª casa', [4, 5, 5, 6], [1, 2, 2, 3], 'chords-db', [{"fret": 5, "from": 1, "to": 3}]),
      P('Padrão', [8, 9, 7, 8], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Gb': [
      P('1ª casa (pestana)', [3, 1, 2, 1], [3, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 1, 2, 4], [3, 1, 2, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 6, 9], [1, 1, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Gb11': [
      P('Padrão', [3, 4, 4, 2], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [4, 4, 4, 1], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Gb13': [
      P('Padrão', [1, 3, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 4, 6], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [8, 8, 6, 7], [3, 4, 1, 2], 'chords-db', [])
      ],
      'Gb13#9': [
      P('1ª casa (pestana)', [4, 3, 1, 1], [4, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 3, 1, 2], [3, 4, 1, 2], 'chords-db', []),
      P('Padrão', [4, 5, 6, 6], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gb13b5b9': [
      P('Abertura', [0, 3, 0, 3], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [5, 4, 3, 6], [3, 2, 1, 4], 'chords-db', []),
      P('Padrão', [9, 7, 8, 6], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Gb13b9': [
      P('1ª casa (pestana)', [1, 3, 1, 2], [1, 3, 1, 2], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [4, 5, 4, 6], [1, 2, 1, 3], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [8, 8, 7, 8], [2, 3, 1, 4], 'chords-db', []),
      P('Abertura', [0, 3, 0, 1], [0, 3, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 6], [1, 2, 1, 4], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [9, 7, 6, 6], [4, 2, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Gb6': [
      P('Padrão', [3, 3, 2, 4], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 6, 6], [1, 1, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [8, 10, 9, 9], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Gb69': [
      P('[3, 4]ª casa (pestana)', [3, 3, 4, 4], [1, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}, {"fret": 4, "from": 2, "to": 3}]),
      P('6ª casa (pestana)', [6, 8, 6, 6], [1, 3, 1, 1], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [8, 10, 9, 11], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Gb7': [
      P('Padrão', [3, 4, 2, 4], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 6, 7], [1, 1, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [9, 10, 9, 9], [1, 2, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Gb7#9': [
      P('Padrão', [2, 1, 0, 1], [3, 1, 0, 2], 'chords-db', []),
      P('Abertura', [3, 1, 0, 0], [3, 1, 0, 0], 'chords-db', []),
      P('Padrão', [3, 4, 5, 4], [1, 2, 4, 3], 'chords-db', [])
      ],
      'Gb7b5': [
      P('Padrão', [3, 4, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 6, 7], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [9, 10, 8, 9], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Gb7b9': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Gb7b9#5': [
      P('Abertura', [0, 2, 0, 1], [0, 2, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 5], [1, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 6, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gb7sus4': [
      P('Padrão', [4, 4, 2, 4], [2, 3, 1, 4], 'chords-db', []),
      P('[6, 7]ª casa (pestana)', [6, 6, 7, 7], [1, 1, 2, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}, {"fret": 7, "from": 2, "to": 3}]),
      P('9ª casa (pestana)', [9, 11, 9, 9], [1, 3, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Gb9': [
      P('Padrão', [1, 1, 0, 1], [1, 2, 0, 3], 'chords-db', []),
      P('Padrão', [3, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('6ª casa (pestana)', [6, 8, 6, 7], [1, 3, 1, 2], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Gb9#11': [
      P('Abertura', [1, 0, 0, 1], [1, 0, 0, 2], 'chords-db', []),
      P('[3, 4]ª casa (pestana)', [3, 4, 4, 3], [1, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}, {"fret": 4, "from": 1, "to": 2}]),
      P('Padrão', [5, 8, 6, 7], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Gb9b5': [
      P('Abertura', [1, 0, 0, 1], [1, 0, 0, 2], 'chords-db', []),
      P('[3, 4]ª casa (pestana)', [3, 4, 4, 3], [1, 2, 2, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}, {"fret": 4, "from": 1, "to": 2}]),
      P('Padrão', [5, 8, 6, 7], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Gbadd9': [
      P('1ª casa (pestana)', [1, 1, 2, 1], [1, 1, 2, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa', [3, 6, 4, 4], [1, 4, 2, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 3}]),
      P('6ª casa (pestana)', [6, 8, 6, 9], [1, 3, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Gbalt': [
      P('Padrão', [3, 0, 2, 1], [3, 0, 2, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 6, 3], [1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [11, 10, 8, 9], [4, 3, 1, 2], 'chords-db', [])
      ],
      'Gbaug': [
      P('2ª casa', [3, 2, 2, 1], [3, 2, 2, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 2}]),
      P('2ª casa (pestana)', [3, 2, 2, 5], [2, 1, 1, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [3, 6, 6, 5], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Gbaug7': [
      P('Padrão', [3, 4, 2, 5], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [7, 6, 6, 7], [2, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('[9, 10]ª casa (pestana)', [9, 10, 10, 9], [1, 2, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}, {"fret": 10, "from": 1, "to": 2}])
      ],
      'Gbaug9': [
      P('Padrão', [1, 2, 0, 1], [1, 3, 0, 2], 'chords-db', []),
      P('4ª casa', [3, 4, 4, 5], [1, 2, 2, 3], 'chords-db', [{"fret": 4, "from": 1, "to": 3}]),
      P('Padrão', [7, 8, 6, 7], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Gbb13#9': [
      P('Abertura', [3, 2, 0, 0], [3, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 2, 0, 1], [2, 3, 0, 1], 'chords-db', []),
      P('Padrão', [3, 4, 5, 5], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gbb13b9': [
      P('Abertura', [0, 2, 0, 1], [0, 2, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 5], [1, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 6, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gbdim': [
      P('Abertura', [2, 0, 2, 0], [2, 0, 3, 0], 'chords-db', []),
      P('Padrão', [5, 6, 5, 3], [2, 4, 3, 1], 'chords-db', []),
      P('Padrão', [11, 9, 8, 9], [4, 2, 1, 3], 'chords-db', [])
      ],
      'Gbdim7': [
      P('Padrão', [2, 3, 2, 3], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [5, 6, 5, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 9, 8, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Gbm': [
      P('Padrão', [2, 1, 2, 0], [2, 1, 3, 0], 'chords-db', []),
      P('Padrão', [2, 1, 2, 4], [2, 1, 3, 4], 'chords-db', []),
      P('Padrão', [6, 6, 5, 4], [3, 4, 2, 1], 'chords-db', [])
      ],
      'Gbm11': [
      P('2ª casa (pestana)', [2, 4, 4, 2], [1, 3, 4, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('12ª casa', [13, 11, 12, 12], [3, 1, 2, 2], 'chords-db', [{"fret": 12, "from": 0, "to": 3}]),
      P('11ª casa', [14, 11, 12, 11], [4, 1, 2, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 3}])
      ],
      'Gbm6': [
      P('2ª casa (pestana)', [2, 3, 2, 4], [1, 2, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 5, 6], [2, 3, 1, 4], 'chords-db', []),
      P('Padrão', [8, 9, 9, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gbm69': [
      P('Padrão', [2, 3, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 5, 6], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [8, 9, 9, 11], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gbm7': [
      P('Padrão', [2, 4, 2, 4], [1, 3, 2, 4], 'chords-db', []),
      P('6ª casa', [6, 6, 5, 7], [2, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa (pestana)', [9, 9, 9, 9], [1, 1, 1, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 3}])
      ],
      'Gbm7b5': [
      P('2ª casa (pestana)', [2, 4, 2, 3], [1, 3, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 7], [1, 2, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [9, 9, 8, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gbm9': [
      P('Abertura', [1, 1, 0, 0], [1, 2, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 4, 4], [1, 2, 3, 4], 'chords-db', []),
      P('Padrão', [6, 8, 5, 7], [2, 4, 1, 3], 'chords-db', [])
      ],
      'Gbm9b5': [
      P('Abertura', [1, 0, 0, 0], [1, 0, 0, 0], 'chords-db', []),
      P('Padrão', [2, 4, 4, 3], [1, 3, 4, 2], 'chords-db', []),
      P('5ª casa (pestana)', [5, 8, 5, 7], [1, 4, 1, 3], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Gbmadd9': [
      P('Padrão', [1, 1, 2, 0], [1, 2, 3, 0], 'chords-db', []),
      P('9ª casa', [11, 9, 9, 11], [3, 1, 1, 4], 'chords-db', [{"fret": 9, "from": 0, "to": 3}]),
      P('Padrão', [14, 13, 14, 11], [3, 2, 4, 1], 'chords-db', [])
      ],
      'Gbmaj11': [
      P('Padrão', [3, 5, 4, 2], [2, 4, 3, 1], 'chords-db', []),
      P('Padrão', [13, 11, 13, 13], [2, 1, 3, 4], 'chords-db', [])
      ],
      'Gbmaj13': [
      P('1ª casa (pestana)', [1, 3, 1, 1], [1, 3, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 4, 6], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [8, 8, 6, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gbmaj7': [
      P('Padrão', [3, 5, 2, 4], [2, 4, 1, 3], 'chords-db', []),
      P('6ª casa (pestana)', [6, 6, 6, 8], [1, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [11, 10, 9, 8], [4, 3, 2, 1], 'chords-db', [])
      ],
      'Gbmaj7#5': [
      P('Padrão', [3, 5, 2, 5], [2, 3, 1, 4], 'chords-db', []),
      P('6ª casa (pestana)', [7, 6, 6, 8], [2, 1, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('Padrão', [11, 10, 10, 8], [4, 2, 3, 1], 'chords-db', [])
      ],
      'Gbmaj7b5': [
      P('Padrão', [3, 5, 2, 3], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [5, 6, 6, 8], [1, 2, 3, 4], 'chords-db', []),
      P('8ª casa (pestana)', [11, 10, 8, 8], [4, 3, 1, 1], 'chords-db', [{"fret": 8, "from": 0, "to": 3}])
      ],
      'Gbmaj9': [
      P('1ª casa (pestana)', [1, 1, 1, 1], [1, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa', [3, 5, 4, 4], [1, 3, 2, 2], 'chords-db', [{"fret": 4, "from": 1, "to": 3}]),
      P('Padrão', [6, 8, 6, 8], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Gbmmaj11': [
      P('2ª casa (pestana)', [2, 5, 4, 2], [1, 4, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [13, 11, 13, 12], [3, 1, 4, 2], 'chords-db', []),
      P('11ª casa', [14, 11, 13, 11], [4, 1, 3, 1], 'chords-db', [{"fret": 11, "from": 0, "to": 3}])
      ],
      'Gbmmaj7': [
      P('2ª casa (pestana)', [2, 5, 2, 4], [1, 4, 1, 3], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('6ª casa', [6, 6, 5, 8], [2, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}]),
      P('9ª casa', [11, 9, 9, 8], [4, 2, 2, 1], 'chords-db', [{"fret": 9, "from": 0, "to": 2}])
      ],
      'Gbmmaj7b5': [
      P('2ª casa (pestana)', [2, 5, 2, 3], [1, 4, 1, 2], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [5, 6, 5, 8], [1, 2, 1, 4], 'chords-db', [{"fret": 5, "from": 0, "to": 3}]),
      P('Padrão', [10, 9, 8, 9], [4, 2, 1, 3], 'chords-db', [])
      ],
      'Gbmmaj9': [
      P('Padrão', [1, 1, 1, 0], [1, 2, 3, 0], 'chords-db', []),
      P('Padrão', [2, 5, 4, 4], [1, 4, 2, 3], 'chords-db', []),
      P('Padrão', [6, 8, 5, 8], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gbsus2': [
      P('1ª casa (pestana)', [1, 1, 2, 4], [1, 1, 2, 4], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('4ª casa (pestana)', [6, 6, 4, 4], [3, 4, 1, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('9ª casa', [6, 8, 9, 9], [1, 2, 3, 3], 'chords-db', [{"fret": 9, "from": 2, "to": 3}])
      ],
      'Gbsus4': [
      P('Padrão', [4, 1, 2, 4], [3, 1, 2, 4], 'chords-db', []),
      P('4ª casa (pestana)', [4, 6, 7, 4], [1, 2, 3, 1], 'chords-db', [{"fret": 4, "from": 0, "to": 3}]),
      P('Padrão', [6, 6, 7, 4], [2, 3, 4, 1], 'chords-db', [])
      ],
      'Gdim': [
      P('Padrão', [0, 1, 3, 1], [0, 1, 3, 2], 'chords-db', []),
      P('1ª casa (pestana)', [3, 1, 3, 1], [3, 1, 4, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [6, 7, 6, 4], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Gdim7': [
      P('Abertura', [0, 1, 0, 1], [0, 1, 0, 2], 'chords-db', []),
      P('Padrão', [3, 4, 3, 4], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [6, 7, 6, 7], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Gm': [
      P('Padrão', [0, 2, 3, 1], [0, 2, 3, 1], 'chords-db', []),
      P('Padrão', [3, 2, 3, 1], [3, 2, 4, 1], 'chords-db', []),
      P('Padrão', [3, 2, 3, 5], [2, 1, 3, 4], 'chords-db', [])
      ],
      'Gm11': [
      P('1ª casa', [2, 0, 1, 1], [3, 0, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Abertura', [3, 0, 1, 0], [3, 0, 1, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 5, 3], [1, 3, 4, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Gm6': [
      P('Abertura', [0, 2, 0, 1], [0, 2, 0, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 4, 3, 5], [1, 2, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [7, 7, 6, 7], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gm69': [
      P('Padrão', [2, 2, 0, 1], [2, 3, 0, 1], 'chords-db', []),
      P('Abertura', [3, 2, 0, 0], [3, 2, 0, 0], 'chords-db', []),
      P('Padrão', [3, 4, 5, 5], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gm7': [
      P('1ª casa', [0, 2, 1, 1], [0, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 1, "to": 3}]),
      P('Padrão', [3, 5, 3, 5], [1, 3, 2, 4], 'chords-db', []),
      P('7ª casa', [7, 7, 6, 8], [2, 2, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Gm7b5': [
      P('Padrão', [0, 1, 1, 1], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa (pestana)', [3, 5, 3, 4], [1, 3, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 8], [1, 2, 1, 3], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Gm9': [
      P('Padrão', [3, 2, 1, 0], [3, 2, 1, 0], 'chords-db', []),
      P('[1, 2]ª casa (pestana)', [2, 2, 1, 1], [2, 2, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}, {"fret": 2, "from": 0, "to": 1}]),
      P('Padrão', [3, 5, 5, 5], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gm9b5': [
      P('Padrão', [3, 1, 1, 0], [3, 1, 2, 0], 'chords-db', []),
      P('1ª casa (pestana)', [2, 1, 1, 1], [2, 1, 1, 1], 'chords-db', [{"fret": 1, "from": 0, "to": 3}]),
      P('Padrão', [3, 5, 5, 4], [1, 3, 4, 2], 'chords-db', [])
      ],
      'Gmadd9': [
      P('Padrão', [3, 2, 3, 0], [2, 1, 3, 0], 'chords-db', []),
      P('2ª casa', [2, 2, 3, 1], [2, 2, 3, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 2}]),
      P('10ª casa (pestana)', [12, 10, 10, 12], [3, 1, 1, 4], 'chords-db', [{"fret": 10, "from": 0, "to": 3}])
      ],
      'Gmaj11': [
      P('Padrão', [2, 0, 2, 2], [1, 0, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 5, 3], [2, 4, 3, 1], 'chords-db', [])
      ],
      'Gmaj13': [
      P('2ª casa (pestana)', [2, 4, 2, 2], [1, 3, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('Padrão', [4, 6, 5, 7], [1, 3, 2, 4], 'chords-db', []),
      P('Padrão', [9, 9, 7, 9], [2, 3, 1, 4], 'chords-db', [])
      ],
      'Gmaj7': [
      P('Padrão', [0, 2, 2, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 3, 5], [2, 4, 1, 3], 'chords-db', []),
      P('7ª casa (pestana)', [7, 7, 7, 9], [1, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Gmaj7#5': [
      P('2ª casa', [0, 3, 2, 2], [0, 2, 1, 1], 'chords-db', [{"fret": 2, "from": 1, "to": 3}]),
      P('Padrão', [4, 6, 3, 6], [2, 3, 1, 4], 'chords-db', []),
      P('7ª casa (pestana)', [8, 7, 7, 9], [2, 1, 1, 3], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Gmaj7b5': [
      P('Padrão', [0, 1, 2, 2], [0, 1, 2, 3], 'chords-db', []),
      P('Padrão', [4, 6, 3, 4], [2, 4, 1, 3], 'chords-db', []),
      P('Padrão', [6, 7, 7, 9], [1, 2, 3, 4], 'chords-db', [])
      ],
      'Gmaj9': [
      P('2ª casa (pestana)', [2, 2, 2, 2], [1, 1, 1, 1], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa', [4, 6, 5, 5], [1, 3, 2, 2], 'chords-db', [{"fret": 5, "from": 1, "to": 3}]),
      P('Padrão', [7, 9, 7, 9], [1, 3, 2, 4], 'chords-db', [])
      ],
      'Gmmaj11': [
      P('Padrão', [2, 0, 2, 1], [2, 0, 3, 1], 'chords-db', []),
      P('Abertura', [3, 0, 2, 0], [3, 0, 2, 0], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 5, 3], [1, 4, 3, 1], 'chords-db', [{"fret": 3, "from": 0, "to": 3}])
      ],
      'Gmmaj7': [
      P('Padrão', [0, 2, 2, 1], [0, 2, 3, 1], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 3, 5], [1, 4, 1, 3], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('7ª casa', [7, 7, 6, 9], [2, 2, 1, 4], 'chords-db', [{"fret": 7, "from": 0, "to": 3}])
      ],
      'Gmmaj7b5': [
      P('Padrão', [0, 1, 2, 1], [0, 1, 3, 2], 'chords-db', []),
      P('3ª casa (pestana)', [3, 6, 3, 4], [1, 4, 1, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('6ª casa (pestana)', [6, 7, 6, 9], [1, 2, 1, 4], 'chords-db', [{"fret": 6, "from": 0, "to": 3}])
      ],
      'Gmmaj9': [
      P('Padrão', [3, 2, 2, 0], [3, 1, 2, 0], 'chords-db', []),
      P('Padrão', [2, 2, 2, 1], [2, 3, 4, 1], 'chords-db', []),
      P('Padrão', [3, 6, 5, 5], [1, 4, 2, 3], 'chords-db', [])
      ],
      'Gsus2': [
      P('Abertura', [0, 2, 3, 0], [0, 2, 3, 0], 'chords-db', []),
      P('2ª casa (pestana)', [2, 2, 3, 5], [1, 1, 2, 4], 'chords-db', [{"fret": 2, "from": 0, "to": 3}]),
      P('5ª casa (pestana)', [7, 7, 5, 5], [3, 4, 1, 1], 'chords-db', [{"fret": 5, "from": 0, "to": 3}])
      ],
      'Gsus4': [
      P('Padrão', [0, 2, 3, 3], [0, 1, 2, 3], 'chords-db', []),
      P('3ª casa', [5, 2, 3, 3], [4, 1, 2, 2], 'chords-db', [{"fret": 3, "from": 0, "to": 3}]),
      P('Padrão', [5, 2, 3, 5], [3, 1, 2, 4], 'chords-db', [])
      ],
    },
  };
})(typeof window !== "undefined" ? window : globalThis);
