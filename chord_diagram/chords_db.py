"""Posições do banco tombatossals/chords-db (chords_db_shapes.json)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent / 'data' / 'chords_db_shapes.json'

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


def get_chords_db_positions(instrument_id: str, chord_display: str) -> list[dict]:
    inst = _INSTRUMENT_ALIAS.get((instrument_id or '').lower(), (instrument_id or '').lower())
    bank = _load_bank().get(inst) or {}
    for key in _chord_keys(chord_display):
        if key in bank:
            return [dict(p) for p in bank[key]]
    return []


def barre_span(frets: list, barre_fret: int) -> dict | None:
    """Uma pestana no traste indicado."""
    if not barre_fret:
        return None
    from_i: int | None = None
    to_i: int | None = None
    for i, f in enumerate(frets):
        if f in ('x', 'X'):
            continue
        if isinstance(f, int) and f >= barre_fret:
            if from_i is None:
                from_i = i
            to_i = i
    if from_i is None or to_i is None or to_i <= from_i:
        return None
    return {'fret': barre_fret, 'from': from_i, 'to': to_i}


def barres_from_position(frets: list, barre) -> list[dict]:
    """Campo barres do chords-db: número ou lista de trastes."""
    if not barre:
        return []
    frets_list = list(frets)
    if isinstance(barre, list):
        out: list[dict] = []
        for bf in barre:
            span = barre_span(frets_list, int(bf))
            if span:
                out.append(span)
        return out
    span = barre_span(frets_list, int(barre))
    return [span] if span else []


def barres_to_api(barres: list[dict]) -> list[dict]:
    return [
        {
            'fret': b['fret'],
            'startString': b['from'] + 1,
            'endString': b['to'] + 1,
        }
        for b in barres
    ]


def chords_db_to_voicing(pos: dict) -> dict:
    frets = pos.get('frets') or []
    barres = pos.get('barres') or []
    return {
        'frets': list(frets),
        'fingers': pos.get('fingers'),
        'label': pos.get('label') or 'Padrão',
        'source': pos.get('source') or 'chords-db',
        'barres': list(barres),
        'fromChordsDb': True,
    }
