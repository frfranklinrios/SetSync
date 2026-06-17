/** Arpejos de baixo — gerado por scripts/build_bass_arpeggios_from_pdf.py */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  CD.BASS_ARPEGGIO_BANK = {
  "meta": {
    "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
    "instrument": "baixo4",
    "tuning": [
      "E",
      "A",
      "D",
      "G"
    ],
    "strings": 4,
    "templateRoot": "C",
    "qualities": [
      "maj7",
      "maj",
      "7",
      "m7",
      "m",
      "m7b5",
      "dim",
      "aug"
    ]
  },
  "qualityTemplates": {
    "maj7": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 2,
        "finger": 1,
        "interval": "3",
        "note": "E"
      },
      {
        "string": "D",
        "fret": 5,
        "finger": 4,
        "interval": "5",
        "note": "G"
      },
      {
        "string": "G",
        "fret": 4,
        "finger": 3,
        "interval": "7",
        "note": "B"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ],
    "maj": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 2,
        "finger": 1,
        "interval": "3",
        "note": "E"
      },
      {
        "string": "D",
        "fret": 5,
        "finger": 4,
        "interval": "5",
        "note": "G"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ],
    "7": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 2,
        "finger": 1,
        "interval": "3",
        "note": "E"
      },
      {
        "string": "D",
        "fret": 5,
        "finger": 4,
        "interval": "5",
        "note": "G"
      },
      {
        "string": "G",
        "fret": 3,
        "finger": 2,
        "interval": "b7",
        "note": "Bb"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ],
    "m7": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 3,
        "finger": 2,
        "interval": "b3",
        "note": "Eb"
      },
      {
        "string": "G",
        "fret": 0,
        "finger": 0,
        "interval": "5",
        "note": "G"
      },
      {
        "string": "G",
        "fret": 4,
        "finger": 3,
        "interval": "b7",
        "note": "Bb"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ],
    "m": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 3,
        "finger": 2,
        "interval": "b3",
        "note": "Eb"
      },
      {
        "string": "G",
        "fret": 0,
        "finger": 0,
        "interval": "5",
        "note": "G"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ],
    "m7b5": [
      {
        "string": "A",
        "fret": 2,
        "finger": 1,
        "interval": "1",
        "note": "B",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 0,
        "finger": 0,
        "interval": "b3",
        "note": "D"
      },
      {
        "string": "D",
        "fret": 3,
        "finger": 3,
        "interval": "b5",
        "note": "F"
      },
      {
        "string": "G",
        "fret": 2,
        "finger": 2,
        "interval": "b7",
        "note": "A"
      },
      {
        "string": "A",
        "fret": 2,
        "finger": 1,
        "interval": "8",
        "note": "B",
        "isRoot": true
      }
    ],
    "dim": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 3,
        "finger": 2,
        "interval": "b3",
        "note": "Eb"
      },
      {
        "string": "D",
        "fret": 6,
        "finger": 4,
        "interval": "b5",
        "note": "Gb"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ],
    "aug": [
      {
        "string": "A",
        "fret": 3,
        "finger": 1,
        "interval": "1",
        "note": "C",
        "isRoot": true
      },
      {
        "string": "D",
        "fret": 2,
        "finger": 1,
        "interval": "3",
        "note": "E"
      },
      {
        "string": "G",
        "fret": 1,
        "finger": 1,
        "interval": "#5",
        "note": "G#"
      },
      {
        "string": "G",
        "fret": 5,
        "finger": 4,
        "interval": "8",
        "note": "C",
        "isRoot": true
      }
    ]
  },
  "patterns": {
    "C": [
      {
        "id": "C_maj",
        "label": "C Major Triad",
        "root": "C",
        "quality": "maj",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 1,
            "interval": "3",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 5,
            "finger": 4,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "C"
        ]
      }
    ],
    "Cmaj": [
      {
        "id": "C_maj",
        "label": "C Major Triad",
        "root": "C",
        "quality": "maj",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 1,
            "interval": "3",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 5,
            "finger": 4,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Cmaj"
        ]
      }
    ],
    "Cmaj7": [
      {
        "id": "C_maj7",
        "label": "C Major 7",
        "root": "C",
        "quality": "maj7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 1,
            "interval": "3",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 5,
            "finger": 4,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 4,
            "finger": 3,
            "interval": "7",
            "note": "B",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Cmaj7"
        ]
      }
    ],
    "C7": [
      {
        "id": "C_7",
        "label": "C Dominant 7",
        "root": "C",
        "quality": "7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 1,
            "interval": "3",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 5,
            "finger": 4,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 3,
            "finger": 2,
            "interval": "b7",
            "note": "A#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "C7"
        ]
      }
    ],
    "Cm": [
      {
        "id": "C_m",
        "label": "C Minor Triad",
        "root": "C",
        "quality": "m",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 1,
            "finger": 2,
            "interval": "b3",
            "note": "D#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 0,
            "finger": 0,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Cm"
        ]
      }
    ],
    "Cm7": [
      {
        "id": "C_m7",
        "label": "C Minor 7",
        "root": "C",
        "quality": "m7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 1,
            "finger": 2,
            "interval": "b3",
            "note": "D#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 0,
            "finger": 0,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 3,
            "finger": 3,
            "interval": "b7",
            "note": "A#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Cm7"
        ]
      }
    ],
    "Cdim": [
      {
        "id": "C_dim",
        "label": "C Diminished Triad",
        "root": "C",
        "quality": "dim",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 1,
            "finger": 2,
            "interval": "b3",
            "note": "D#",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 4,
            "finger": 4,
            "interval": "b5",
            "note": "F#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Cdim"
        ]
      }
    ],
    "Caug": [
      {
        "id": "C_aug",
        "label": "C Augmented Triad",
        "root": "C",
        "quality": "aug",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 1,
            "interval": "3",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 1,
            "finger": 1,
            "interval": "#5",
            "note": "G#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Caug"
        ]
      }
    ],
    "Cm7b5": [
      {
        "id": "C_m7b5",
        "label": "C Minor 7 b5",
        "root": "C",
        "quality": "m7b5",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 1,
            "finger": 0,
            "interval": "b3",
            "note": "D#",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 4,
            "finger": 3,
            "interval": "b5",
            "note": "F#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 3,
            "finger": 2,
            "interval": "b7",
            "note": "A#",
            "isRoot": false
          },
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "Cm7b5"
        ]
      }
    ],
    "Am7": [
      {
        "id": "A_m7",
        "label": "A Minor 7",
        "root": "A",
        "quality": "m7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 0,
            "finger": 1,
            "interval": "1",
            "note": "A",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 10,
            "finger": 2,
            "interval": "b3",
            "note": "C",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 9,
            "finger": 0,
            "interval": "5",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 0,
            "finger": 3,
            "interval": "b7",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 2,
            "finger": 4,
            "interval": "8",
            "note": "A",
            "isRoot": true
          }
        ],
        "symbols": [
          "Am7"
        ]
      }
    ],
    "Dm7": [
      {
        "id": "D_m7",
        "label": "D Minor 7",
        "root": "D",
        "quality": "m7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 5,
            "finger": 1,
            "interval": "1",
            "note": "D",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 3,
            "finger": 2,
            "interval": "b3",
            "note": "F",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 2,
            "finger": 0,
            "interval": "5",
            "note": "A",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 3,
            "interval": "b7",
            "note": "C",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 7,
            "finger": 4,
            "interval": "8",
            "note": "D",
            "isRoot": true
          }
        ],
        "symbols": [
          "Dm7"
        ]
      }
    ],
    "Em7": [
      {
        "id": "E_m7",
        "label": "E Minor 7",
        "root": "E",
        "quality": "m7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 7,
            "finger": 1,
            "interval": "1",
            "note": "E",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 5,
            "finger": 2,
            "interval": "b3",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 4,
            "finger": 0,
            "interval": "5",
            "note": "B",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 7,
            "finger": 3,
            "interval": "b7",
            "note": "D",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 9,
            "finger": 4,
            "interval": "8",
            "note": "E",
            "isRoot": true
          }
        ],
        "symbols": [
          "Em7"
        ]
      }
    ],
    "Fmaj7": [
      {
        "id": "F_maj7",
        "label": "F Major 7",
        "root": "F",
        "quality": "maj7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 8,
            "finger": 1,
            "interval": "1",
            "note": "F",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 7,
            "finger": 1,
            "interval": "3",
            "note": "A",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 10,
            "finger": 4,
            "interval": "5",
            "note": "C",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 9,
            "finger": 3,
            "interval": "7",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 10,
            "finger": 4,
            "interval": "8",
            "note": "F",
            "isRoot": true
          }
        ],
        "symbols": [
          "Fmaj7"
        ]
      }
    ],
    "G7": [
      {
        "id": "G_7",
        "label": "G Dominant 7",
        "root": "G",
        "quality": "7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 10,
            "finger": 1,
            "interval": "1",
            "note": "G",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 9,
            "finger": 1,
            "interval": "3",
            "note": "B",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 0,
            "finger": 4,
            "interval": "5",
            "note": "D",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 10,
            "finger": 2,
            "interval": "b7",
            "note": "F",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 0,
            "finger": 4,
            "interval": "8",
            "note": "G",
            "isRoot": true
          }
        ],
        "symbols": [
          "G7"
        ]
      }
    ],
    "Bm7b5": [
      {
        "id": "B_m7b5",
        "label": "B Minor 7 b5",
        "root": "B",
        "quality": "m7b5",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 2,
            "finger": 1,
            "interval": "1",
            "note": "B",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 0,
            "finger": 0,
            "interval": "b3",
            "note": "D",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 3,
            "finger": 3,
            "interval": "b5",
            "note": "F",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 2,
            "finger": 2,
            "interval": "b7",
            "note": "A",
            "isRoot": false
          },
          {
            "string": "A",
            "fret": 2,
            "finger": 1,
            "interval": "8",
            "note": "B",
            "isRoot": true
          }
        ],
        "symbols": [
          "Bm7b5"
        ]
      }
    ],
    "A7+": [
      {
        "id": "A_maj7",
        "label": "A Major 7",
        "root": "A",
        "quality": "maj7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 0,
            "finger": 1,
            "interval": "1",
            "note": "A",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 11,
            "finger": 1,
            "interval": "3",
            "note": "C#",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 4,
            "interval": "5",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 1,
            "finger": 3,
            "interval": "7",
            "note": "G#",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 2,
            "finger": 4,
            "interval": "8",
            "note": "A",
            "isRoot": true
          }
        ],
        "symbols": [
          "A7+"
        ]
      }
    ],
    "C7+": [
      {
        "id": "C_maj7",
        "label": "C Major 7",
        "root": "C",
        "quality": "maj7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 3,
            "finger": 1,
            "interval": "1",
            "note": "C",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 2,
            "finger": 1,
            "interval": "3",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 5,
            "finger": 4,
            "interval": "5",
            "note": "G",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 4,
            "finger": 3,
            "interval": "7",
            "note": "B",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 5,
            "finger": 4,
            "interval": "8",
            "note": "C",
            "isRoot": true
          }
        ],
        "symbols": [
          "C7+"
        ]
      }
    ],
    "F7+": [
      {
        "id": "F_maj7",
        "label": "F Major 7",
        "root": "F",
        "quality": "maj7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 8,
            "finger": 1,
            "interval": "1",
            "note": "F",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 7,
            "finger": 1,
            "interval": "3",
            "note": "A",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 10,
            "finger": 4,
            "interval": "5",
            "note": "C",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 9,
            "finger": 3,
            "interval": "7",
            "note": "E",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 10,
            "finger": 4,
            "interval": "8",
            "note": "F",
            "isRoot": true
          }
        ],
        "symbols": [
          "F7+"
        ]
      }
    ],
    "Bb7+": [
      {
        "id": "Bb_maj7",
        "label": "Bb Major 7",
        "root": "Bb",
        "quality": "maj7",
        "pattern": "root",
        "source": "The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)",
        "steps": [
          {
            "string": "A",
            "fret": 1,
            "finger": 1,
            "interval": "1",
            "note": "Bb",
            "isRoot": true
          },
          {
            "string": "D",
            "fret": 0,
            "finger": 1,
            "interval": "3",
            "note": "D",
            "isRoot": false
          },
          {
            "string": "D",
            "fret": 3,
            "finger": 4,
            "interval": "5",
            "note": "F",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 2,
            "finger": 3,
            "interval": "7",
            "note": "A",
            "isRoot": false
          },
          {
            "string": "G",
            "fret": 3,
            "finger": 4,
            "interval": "8",
            "note": "Bb",
            "isRoot": true
          }
        ],
        "symbols": [
          "Bb7+"
        ]
      }
    ]
  }
};
})(typeof window !== "undefined" ? window : globalThis);
