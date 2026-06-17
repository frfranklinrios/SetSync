"""Posições reais (cifra clássica) carregadas de real_shapes.json."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent / 'data' / 'real_shapes.json'

_INSTRUMENT_ALIAS = {
    'guitarra': 'violao',
    'guitar': 'violao',
    'viola': 'violao',
}


@lru_cache(maxsize=1)
def _load_bank() -> dict:
    if not _DATA.is_file():
        return {}
    return json.loads(_DATA.read_text(encoding='utf-8'))


def _chord_keys(display: str) -> list[str]:
    text = re.sub(r'\s+', '', (display or ''))
    text = text.replace('(', '').replace(')', '')
    slash = text.split('/')[0]
    keys = [slash]
    m = re.match(r'^([A-G])([#b]?)(.*)$', slash)
    if not m:
        return keys
    letter, acc, rest = m.group(1), m.group(2), m.group(3)
    keys.append(letter + acc + rest)
    if acc == 'b':
        sharp_map = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
        alt = sharp_map.get(letter + acc)
        if alt:
            keys.append(alt + rest)
    return keys


def get_real_positions(instrument_id: str, chord_display: str) -> list[dict]:
    inst = _INSTRUMENT_ALIAS.get((instrument_id or '').lower(), (instrument_id or '').lower())
    bank = _load_bank().get(inst) or {}
    for key in _chord_keys(chord_display):
        if key in bank:
            return [dict(p) for p in bank[key]]
    return []


def real_to_voicing(pos: dict) -> dict:
    frets = pos.get('frets') or []
    return {
        'frets': list(frets),
        'fingers': pos.get('fingers'),
        'label': pos.get('label') or 'Padrão',
        'source': pos.get('source') or 'Cifra clássica',
        'fromRealShapes': True,
    }
