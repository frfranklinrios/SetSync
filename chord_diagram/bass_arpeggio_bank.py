"""Banco de arpejos de baixo — padrões do Bass Guitar Resource Book (Dan Hawkins)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent / 'data' / 'bass_arpeggio_shapes.json'

# Padrões moveáveis (uma oitava) — seção «Harmonising The Major Scale» / «The 7 Arpeggios From C Major»
# Afinação E A D G (4 cordas). Cordas: E grave → G agudo.
_HARMONIZED_C_MAJOR = [
    {
        'id': 'C_maj7_harm',
        'label': 'C Major 7 (I)',
        'symbols': ['C', 'Cmaj7', 'CΔ7'],
        'root': 'C',
        'quality': 'maj7',
        'pattern': 'root',
        'roman': 'I',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
            {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
            {'string': 'D', 'fret': 5, 'finger': 4, 'interval': '5', 'note': 'G'},
            {'string': 'G', 'fret': 4, 'finger': 3, 'interval': '7', 'note': 'B'},
            {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
        ],
    },
    {
        'id': 'D_m7_harm',
        'label': 'D Minor 7 (ii)',
        'symbols': ['Dm', 'Dm7', 'D-7'],
        'root': 'D',
        'quality': 'm7',
        'pattern': 'root',
        'roman': 'ii',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 5, 'finger': 1, 'interval': '1', 'note': 'D', 'isRoot': True},
            {'string': 'D', 'fret': 3, 'finger': 1, 'interval': 'b3', 'note': 'F'},
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': '5', 'note': 'A'},
            {'string': 'G', 'fret': 4, 'finger': 3, 'interval': 'b7', 'note': 'C'},
            {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'D', 'isRoot': True},
        ],
    },
    {
        'id': 'E_m7_harm',
        'label': 'E Minor 7 (iii)',
        'symbols': ['Em', 'Em7', 'E-7'],
        'root': 'E',
        'quality': 'm7',
        'pattern': 'root',
        'roman': 'iii',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 7, 'finger': 1, 'interval': '1', 'note': 'E', 'isRoot': True},
            {'string': 'D', 'fret': 2, 'finger': 1, 'interval': 'b3', 'note': 'G'},
            {'string': 'D', 'fret': 4, 'finger': 3, 'interval': '5', 'note': 'B'},
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': 'b7', 'note': 'D'},
            {'string': 'G', 'fret': 4, 'finger': 3, 'interval': '8', 'note': 'E', 'isRoot': True},
        ],
    },
    {
        'id': 'F_maj7_harm',
        'label': 'F Major 7 (IV)',
        'symbols': ['F', 'Fmaj7', 'FΔ7'],
        'root': 'F',
        'quality': 'maj7',
        'pattern': 'root',
        'roman': 'IV',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'D', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'F', 'isRoot': True},
            {'string': 'D', 'fret': 5, 'finger': 3, 'interval': '3', 'note': 'A'},
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': '5', 'note': 'C'},
            {'string': 'G', 'fret': 4, 'finger': 3, 'interval': '7', 'note': 'E'},
            {'string': 'D', 'fret': 7, 'finger': 4, 'interval': '8', 'note': 'F', 'isRoot': True},
        ],
    },
    {
        'id': 'G_7_harm',
        'label': 'G Dominant 7 (V)',
        'symbols': ['G', 'G7'],
        'root': 'G',
        'quality': '7',
        'pattern': 'root',
        'roman': 'V',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'G', 'fret': 0, 'finger': 0, 'interval': '1', 'note': 'G', 'isRoot': True},
            {'string': 'A', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'B'},
            {'string': 'D', 'fret': 0, 'finger': 0, 'interval': '5', 'note': 'D'},
            {'string': 'D', 'fret': 3, 'finger': 2, 'interval': 'b7', 'note': 'F'},
            {'string': 'G', 'fret': 0, 'finger': 0, 'interval': '8', 'note': 'G', 'isRoot': True},
        ],
    },
    {
        'id': 'A_m7_harm',
        'label': 'A Minor 7 (vi)',
        'symbols': ['Am', 'Am7', 'A-7'],
        'root': 'A',
        'quality': 'm7',
        'pattern': 'root',
        'roman': 'vi',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': '1', 'note': 'A', 'isRoot': True},
            {'string': 'A', 'fret': 3, 'finger': 2, 'interval': 'b3', 'note': 'C'},
            {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '5', 'note': 'E'},
            {'string': 'G', 'fret': 0, 'finger': 0, 'interval': 'b7', 'note': 'G'},
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': '8', 'note': 'A', 'isRoot': True},
        ],
    },
    {
        'id': 'B_m7b5_harm',
        'label': 'B Minor 7 b5 (vii)',
        'symbols': ['Bm7b5', 'Bø', 'Bm7(b5)'],
        'root': 'B',
        'quality': 'm7b5',
        'pattern': 'root',
        'roman': 'vii',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 2, 'finger': 1, 'interval': '1', 'note': 'B', 'isRoot': True},
            {'string': 'D', 'fret': 0, 'finger': 0, 'interval': 'b3', 'note': 'D'},
            {'string': 'D', 'fret': 3, 'finger': 3, 'interval': 'b5', 'note': 'F'},
            {'string': 'G', 'fret': 2, 'finger': 2, 'interval': 'b7', 'note': 'A'},
            {'string': 'A', 'fret': 2, 'finger': 1, 'interval': '8', 'note': 'B', 'isRoot': True},
        ],
    },
]

# Tríades e sétimas básicas (Theory In A Nutshell) — forma em C moveável
_QUALITY_TEMPLATES = [
    {
        'id': 'C_maj_triad',
        'label': 'Major Triad',
        'symbols': ['C', 'Cmaj'],
        'root': 'C',
        'quality': 'maj',
        'pattern': 'root',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
            {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
            {'string': 'D', 'fret': 5, 'finger': 4, 'interval': '5', 'note': 'G'},
            {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
        ],
    },
    {
        'id': 'C_min_triad',
        'label': 'Minor Triad',
        'symbols': ['Cm', 'Cmin', 'C-'],
        'root': 'C',
        'quality': 'm',
        'pattern': 'root',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
            {'string': 'D', 'fret': 3, 'finger': 2, 'interval': 'b3', 'note': 'Eb'},
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': '5', 'note': 'A'},
            {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
        ],
    },
    {
        'id': 'C_7_dom',
        'label': 'Dominant 7',
        'symbols': ['C7'],
        'root': 'C',
        'quality': '7',
        'pattern': 'root',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
            {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
            {'string': 'D', 'fret': 5, 'finger': 4, 'interval': '5', 'note': 'G'},
            {'string': 'G', 'fret': 3, 'finger': 2, 'interval': 'b7', 'note': 'Bb'},
            {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
        ],
    },
    {
        'id': 'C_m7_qual',
        'label': 'Minor 7',
        'symbols': ['Cm7', 'C-7'],
        'root': 'C',
        'quality': 'm7',
        'pattern': 'root',
        'source': 'The Bass Guitar Resource Book',
        'steps': [
            {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
            {'string': 'D', 'fret': 3, 'finger': 2, 'interval': 'b3', 'note': 'Eb'},
            {'string': 'G', 'fret': 2, 'finger': 1, 'interval': '5', 'note': 'A'},
            {'string': 'G', 'fret': 4, 'finger': 3, 'interval': 'b7', 'note': 'D'},
            {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
        ],
    },
]


def default_seed_bank() -> dict:
    patterns = _HARMONIZED_C_MAJOR + _QUALITY_TEMPLATES
    bank: dict = {
        'meta': {
            'source': 'The Bass Guitar Resource Book (Dan Hawkins / Online Bass Courses)',
            'instrument': 'baixo4',
            'tuning': ['E', 'A', 'D', 'G'],
            'strings': 4,
        },
        'patterns': {},
    }
    for p in patterns:
        for sym in p['symbols']:
            bank['patterns'].setdefault(sym, []).append({
                k: v for k, v in p.items() if k != 'symbols'
            } | {'symbols': p['symbols']})
    return bank


@lru_cache(maxsize=1)
def load_bank() -> dict:
    if _DATA.is_file():
        return json.loads(_DATA.read_text(encoding='utf-8'))
    return default_seed_bank()


def _normalize_symbol(symbol: str) -> list[str]:
    import re
    text = re.sub(r'\s+', '', (symbol or ''))
    text = text.replace('(', '').replace(')', '')
    keys = [text]
    m = re.match(r'^([A-G])([#b]?)(.*)$', text)
    if m:
        letter, acc, rest = m.group(1), m.group(2), m.group(3)
        root = letter.upper() + acc
        keys.append(root + rest)
    return keys


def get_arpeggio_pattern(symbol: str, pattern_id: str = 'root') -> dict | None:
    bank = load_bank()
    patterns_map = bank.get('patterns') or {}
    for key in _normalize_symbol(symbol):
        entries = patterns_map.get(key) or []
        for entry in entries:
            if entry.get('pattern', 'root') == pattern_id:
                return entry
        if entries:
            return entries[0]
    return None


def pattern_steps_for_api(entry: dict) -> list[dict]:
    return [
        {
            'string': s['string'],
            'fret': s['fret'],
            'finger': s.get('finger'),
            'interval': s.get('interval', ''),
            'note': s.get('note', ''),
            'isRoot': bool(s.get('isRoot')),
        }
        for s in (entry.get('steps') or [])
    ]
