"""Banco de arpejos de baixo — formas do Bass Guitar Resource Book / TalkingBass Manual.

Formas canônicas em Dó (extraídas dos diagramas do manual) e transposição para qualquer acorde.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from chord_diagram.bass_arpeggio_transpose import (
    quality_from_theory,
    resolve_steps_for_symbol,
    transpose_steps,
)
from chord_diagram.theory.chord_parser import chord_theory_block

_DATA = Path(__file__).resolve().parent / 'data' / 'bass_arpeggio_shapes.json'

# Formas em Dó — TalkingBass Arpeggio Reference Manual / Resource Book (diagramas 4 cordas EADG)
# Cordas: E grave → G agudo; G no topo do diagrama.
_QUALITY_TEMPLATES_C: dict[str, list[dict]] = {
    'maj7': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
        {'string': 'D', 'fret': 5, 'finger': 4, 'interval': '5', 'note': 'G'},
        {'string': 'G', 'fret': 4, 'finger': 3, 'interval': '7', 'note': 'B'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
    'maj': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
        {'string': 'D', 'fret': 5, 'finger': 4, 'interval': '5', 'note': 'G'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
    '7': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
        {'string': 'D', 'fret': 5, 'finger': 4, 'interval': '5', 'note': 'G'},
        {'string': 'G', 'fret': 3, 'finger': 2, 'interval': 'b7', 'note': 'Bb'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
    'm7': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 3, 'finger': 2, 'interval': 'b3', 'note': 'Eb'},
        {'string': 'G', 'fret': 0, 'finger': 0, 'interval': '5', 'note': 'G'},
        {'string': 'G', 'fret': 4, 'finger': 3, 'interval': 'b7', 'note': 'Bb'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
    'm': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 3, 'finger': 2, 'interval': 'b3', 'note': 'Eb'},
        {'string': 'G', 'fret': 0, 'finger': 0, 'interval': '5', 'note': 'G'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
    'm7b5': [
        {'string': 'A', 'fret': 2, 'finger': 1, 'interval': '1', 'note': 'B', 'isRoot': True},
        {'string': 'D', 'fret': 0, 'finger': 0, 'interval': 'b3', 'note': 'D'},
        {'string': 'D', 'fret': 3, 'finger': 3, 'interval': 'b5', 'note': 'F'},
        {'string': 'G', 'fret': 2, 'finger': 2, 'interval': 'b7', 'note': 'A'},
        {'string': 'A', 'fret': 2, 'finger': 1, 'interval': '8', 'note': 'B', 'isRoot': True},
    ],
    'dim': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 3, 'finger': 2, 'interval': 'b3', 'note': 'Eb'},
        {'string': 'D', 'fret': 6, 'finger': 4, 'interval': 'b5', 'note': 'Gb'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
    'aug': [
        {'string': 'A', 'fret': 3, 'finger': 1, 'interval': '1', 'note': 'C', 'isRoot': True},
        {'string': 'D', 'fret': 2, 'finger': 1, 'interval': '3', 'note': 'E'},
        {'string': 'G', 'fret': 1, 'finger': 1, 'interval': '#5', 'note': 'G#'},
        {'string': 'G', 'fret': 5, 'finger': 4, 'interval': '8', 'note': 'C', 'isRoot': True},
    ],
}

_QUALITY_LABELS = {
    'maj7': 'Major 7',
    'maj': 'Major Triad',
    '7': 'Dominant 7',
    'm7': 'Minor 7',
    'm': 'Minor Triad',
    'm7b5': 'Minor 7 b5',
    'dim': 'Diminished Triad',
    'aug': 'Augmented Triad',
}

_SOURCE = 'The Bass Guitar Resource Book (Dan Hawkins / TalkingBass Manual)'


def quality_templates() -> dict[str, list[dict]]:
    return {k: [dict(s) for s in v] for k, v in _QUALITY_TEMPLATES_C.items()}


def default_seed_bank() -> dict:
    """Banco com formas por qualidade + entradas por símbolo (transpostas a partir de Dó)."""
    templates = quality_templates()
    bank: dict = {
        'meta': {
            'source': _SOURCE,
            'instrument': 'baixo4',
            'tuning': ['E', 'A', 'D', 'G'],
            'strings': 4,
            'templateRoot': 'C',
            'qualities': list(templates.keys()),
        },
        'qualityTemplates': templates,
        'patterns': {},
    }

    symbols = [
        'C', 'Cmaj', 'Cmaj7', 'CΔ7', 'C7', 'Cm', 'Cm7', 'Cdim', 'Caug', 'Cm7b5',
        'Am7', 'Dm7', 'Em7', 'Fmaj7', 'G7', 'Bm7b5',
        'A7+', 'C7+', 'F7+', 'Bb7+',
    ]
    for sym in symbols:
        steps = resolve_steps_for_symbol(sym, templates)
        if not steps:
            continue
        theory = chord_theory_block(sym) or {}
        quality = quality_from_theory(theory)
        root = theory.get('root') or sym[0]
        bank['patterns'].setdefault(sym, []).append({
            'id': f'{root}_{quality}',
            'label': f'{root} {_QUALITY_LABELS.get(quality, quality)}',
            'root': root,
            'quality': quality,
            'pattern': 'root',
            'source': _SOURCE,
            'steps': steps,
            'symbols': [sym],
        })
    return bank


@lru_cache(maxsize=1)
def load_bank() -> dict:
    if _DATA.is_file():
        data = json.loads(_DATA.read_text(encoding='utf-8'))
        if data.get('qualityTemplates'):
            return data
    return default_seed_bank()


def _normalize_symbol(symbol: str) -> list[str]:
    import re
    text = re.sub(r'\s+', '', (symbol or ''))
    text = text.replace('(', '').replace(')', '')
    slash = text.split('/')[0]
    keys: list[str] = []
    for candidate in (text, slash):
        if candidate and candidate not in keys:
            keys.append(candidate)
    m = re.match(r'^([A-G])([#b]?)(.*)$', slash)
    if m:
        letter, acc, rest = m.group(1), m.group(2), m.group(3)
        root = letter.upper() + acc
        alt = root + rest
        if alt not in keys:
            keys.append(alt)
        maj_m = re.fullmatch(r'(\d+)\+', rest)
        if maj_m:
            n = maj_m.group(1)
            maj_key = root + ('maj7' if n == '7' else f'maj{n}')
            if maj_key not in keys:
                keys.append(maj_key)
        if rest.lower() in ('m', 'min'):
            minor = root + 'm'
            if minor not in keys:
                keys.append(minor)
    return keys


def get_arpeggio_pattern(symbol: str, pattern_id: str = 'root') -> dict | None:
    if pattern_id != 'root':
        return None
    bank = load_bank()
    templates = bank.get('qualityTemplates') or quality_templates()

    steps = resolve_steps_for_symbol(symbol, templates)
    if steps:
        theory = chord_theory_block(symbol) or {}
        quality = quality_from_theory(theory)
        root = theory.get('root') or symbol[0]
        return {
            'id': f'{root}_{quality}',
            'label': f'{root} {_QUALITY_LABELS.get(quality, quality)}',
            'root': root,
            'quality': quality,
            'pattern': 'root',
            'source': _SOURCE,
            'steps': steps,
        }

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
