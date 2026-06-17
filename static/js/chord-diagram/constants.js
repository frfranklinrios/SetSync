/** Constantes compartilhadas — diagramas de acordes SetSync */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  CD.NOTE_IDX = {
    C: 0, 'B#': 0,
    'C#': 1, Db: 1,
    D: 2,
    'D#': 3, Eb: 3,
    E: 4, Fb: 4,
    F: 5, 'E#': 5,
    'F#': 6, Gb: 6,
    G: 7,
    'G#': 8, Ab: 8,
    A: 9,
    'A#': 10, Bb: 10,
    B: 11, Cb: 11,
  };

  CD.TUNINGS = {
    violao: ['E', 'A', 'D', 'G', 'B', 'E'],
    cavaco: ['D', 'G', 'B', 'D'],
    ukulele: ['G', 'C', 'E', 'A'],
    baixo4: ['E', 'A', 'D', 'G'],
    baixo5: ['B', 'E', 'A', 'D', 'G'],
    baixo6: ['B', 'E', 'A', 'D', 'G', 'C'],
  };

  CD.ROOT_ALIAS = {
    Db: 'C#',
    Eb: 'D#',
    Gb: 'F#',
    Ab: 'G#',
    Bb: 'A#',
  };

  CD.LAYOUT = {
    rows: 5,
    colGap: 36,
    rowGap: 40,
    marginX: 24,
    marginY: 26,
    dotR: 9,
    rootDotR: 10,
    barreWidth: 9,
  };

  CD.ARP_PATTERNS_BASS = [
    { id: 'root', label: 'Fundamental' },
    { id: 'inv1', label: '1ª inversão' },
    { id: 'inv2', label: '2ª inversão' },
    { id: 'inv3', label: '3ª inversão' },
  ];

  CD.escText = function escText(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  };
})(typeof window !== 'undefined' ? window : globalThis);
