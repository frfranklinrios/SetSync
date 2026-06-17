"""Montagem de payloads JSON v1 para a API musical."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import quote

from util import chord_components_info, split_chord_progression, to_brazilian_chord_notation

from chord_diagram.cache import get_cached, set_cached
from chord_diagram.fretboard import build_arpeggio_sequence, build_scale_fretboard_map
from chord_diagram.instruments import get_instrument, list_instrument_meta
from chord_diagram.piano import piano_key_mappings
from chord_diagram.real_shapes import get_real_positions, real_to_voicing
from chord_diagram.render_svg import render_fretboard_svg, render_piano_svg
from chord_diagram.scales_db import list_scale_types, resolve_scale_type, scale_note_names
from chord_diagram.theory.chord_parser import chord_theory_block
from chord_diagram.voicing import (
    assign_fingers,
    compute_base_fret,
    detect_barres,
    discover_voicings,
    frets_to_api,
)

API_VERSION = '1.0.0'

_INSTRUMENT_API_ALIAS = {
    'guitar': 'violao',
    'guitarra': 'guitarra',
}


def _normalize_instrument(instrument: str) -> str:
    i = (instrument or 'violao').strip().lower()
    return _INSTRUMENT_API_ALIAS.get(i, i)


def _position_id(instrument: str, symbol: str, idx: int, frets: list) -> str:
    h = hashlib.md5(f'{instrument}:{symbol}:{frets}'.encode()).hexdigest()[:8]
    safe = re.sub(r'[^A-Za-z0-9]', '', symbol)[:12] or 'chord'
    return f'{instrument}_{safe}_pos{idx}_{h}'


def _frets_key(frets: list) -> str:
    return ''.join('x' if f in ('x', 'X') else str(f) for f in frets)


def _collect_voicings(spec, display: str, notes: list[str], *, max_positions: int) -> list[dict]:
    """Combina posições clássicas + motor automático, sem duplicatas."""
    merged: list[dict] = []
    seen: set[str] = set()

    for pos in get_real_positions(spec.id, display):
        v = real_to_voicing(pos)
        key = _frets_key(v['frets'])
        if key in seen:
            continue
        seen.add(key)
        merged.append(v)

    if spec.id == 'guitarra':
        for pos in get_real_positions('violao', display):
            v = real_to_voicing(pos)
            key = _frets_key(v['frets'])
            if key in seen:
                continue
            seen.add(key)
            merged.append(v)

    auto = discover_voicings(spec, notes, limit=max(max_positions, 8))
    for v in auto:
        key = _frets_key(v['frets'])
        if key in seen:
            continue
        seen.add(key)
        merged.append({
            'frets': v['frets'],
            'fingers': None,
            'label': 'Sugerido' if len(merged) == 0 else f'Variação {len(merged) + 1}',
            'source': 'Algoritmo de voicings',
            'fromRealShapes': False,
        })
        if len(merged) >= max_positions:
            break

    return merged[:max_positions]


def _voicings_to_positions(
    voicings: list[dict],
    spec,
    symbol: str,
    display: str,
) -> list[dict]:
    from chord_diagram.instruments import open_string_pcs

    ocs = open_string_pcs(spec)
    positions = []
    for i, v in enumerate(voicings):
        frets = v['frets']
        barres = detect_barres(frets)
        fingers = v.get('fingers') or assign_fingers(frets, barres)
        pid = _position_id(spec.id, display, i + 1, frets)
        midi_pat = []
        for si, f in enumerate(frets):
            if f == 'x':
                continue
            if f == 0:
                midi_pat.append(40 + ocs[si])
            elif isinstance(f, int):
                midi_pat.append(40 + ocs[si] + f)

        positions.append({
            'positionId': pid,
            'baseFret': compute_base_fret(frets),
            'frets': frets_to_api(frets),
            'fingers': fingers,
            'barres': [
                {'fret': b['fret'], 'startString': b['startString'], 'endString': b['endString']}
                for b in barres
            ],
            'capo': False,
            'label': v.get('label') or f'Posição {i + 1}',
            'source': v.get('source') or '',
            'midiPattern': midi_pat,
            'renderEndpoints': {
                'svg': f'/api/v1/render/fretboard?instrument={spec.id}&symbol={quote(symbol)}&pos={i}',
                'vexflow': f'/api/v1/notation/vexflow?symbol={quote(symbol)}&instrument={spec.id}&pos={i}',
            },
        })
    return positions


def _build_chord_document_uncached(
    symbol: str,
    *,
    instrument: str = 'violao',
    key_context: str | None = None,
    max_positions: int = 6,
) -> dict:
    symbol = (symbol or '').strip()
    instrument = _normalize_instrument(instrument)
    spec = get_instrument(instrument) or get_instrument('violao')
    assert spec is not None

    theory = chord_theory_block(symbol, key_context=key_context)
    if not theory:
        return {'error': 'Acorde não reconhecido', 'symbol': symbol}

    info = chord_components_info(symbol)
    notes = (info or {}).get('notes') or theory['notes']
    display = to_brazilian_chord_notation((info or {}).get('display') or symbol)

    if spec.family == 'keys':
        keys = piano_key_mappings(notes, key_context=key_context or theory['root'])
        return {
            'meta': {'instrument': spec.id, 'version': API_VERSION},
            'theory': {**theory, 'display': display, 'input': symbol},
            'instrument': spec.id,
            'target': display,
            'keyMappings': keys,
        }

    voicings = _collect_voicings(spec, display, notes, max_positions=max_positions)
    positions = _voicings_to_positions(voicings, spec, symbol, display)

    return {
        'meta': {
            'instrument': spec.id,
            'tuningName': spec.tuning_name,
            'tuningPitches': list(spec.tuning_pitches),
            'version': API_VERSION,
        },
        'theory': {**theory, 'display': display, 'input': symbol},
        'positions': positions,
    }


def build_chord_document(
    symbol: str,
    *,
    instrument: str = 'violao',
    key_context: str | None = None,
    max_positions: int = 6,
    use_cache: bool = True,
) -> dict:
    instrument = _normalize_instrument(instrument)
    cache_key = f'chord:{instrument}:{symbol}:{max_positions}:{key_context or ""}'
    if use_cache:
        cached = get_cached(cache_key)
        if cached:
            return cached
    doc = _build_chord_document_uncached(
        symbol,
        instrument=instrument,
        key_context=key_context,
        max_positions=max_positions,
    )
    if use_cache and not doc.get('error'):
        set_cached(cache_key, doc)
    return doc


def build_scale_document(
    root: str,
    scale_type: str,
    *,
    instrument: str = 'violao',
    max_frets: int = 15,
    key_context: str | None = None,
    use_cache: bool = True,
) -> dict:
    instrument = _normalize_instrument(instrument)
    sid = resolve_scale_type(scale_type)
    if not sid:
        return {'error': 'Tipo de escala inválido', 'scale_type': scale_type}
    cache_key = f'scale:{instrument}:{root}:{sid}:{max_frets}'
    if use_cache:
        cached = get_cached(cache_key)
        if cached:
            return cached
    mapping = build_scale_fretboard_map(
        root, sid, instrument, max_frets=max_frets, key_context=key_context,
    )
    if not mapping:
        return {'error': 'Instrumento ou escala inválidos'}
    mapping['notes'] = scale_note_names(root, sid, key_context=key_context)
    mapping['scaleId'] = sid
    if use_cache:
        set_cached(cache_key, mapping)
    return mapping


def build_arpeggio_document(
    symbol: str,
    *,
    instrument: str = 'baixo',
    pattern: str = 'root',
    octaves: int = 2,
) -> dict:
    cache_key = f'arp:{instrument}:{symbol}:{pattern}:{octaves}'
    cached = get_cached(cache_key)
    if cached:
        return cached
    theory = chord_theory_block(symbol)
    if not theory:
        return {'error': 'Acorde não reconhecido'}
    notes = theory['notes']
    sequence = build_arpeggio_sequence(notes, octaves=octaves, pattern=pattern)
    spec = get_instrument(_normalize_instrument(instrument))
    voicings = []
    if spec and spec.family == 'fretted':
        voicings = discover_voicings(spec, notes, limit=4)
    doc = {
        'type': 'arpeggio',
        'symbol': symbol,
        'pattern': pattern,
        'theory': theory,
        'sequence': sequence,
        'fretboardPositions': [
            {'frets': frets_to_api(v['frets']), 'baseFret': compute_base_fret(v['frets'])}
            for v in voicings
        ],
    }
    set_cached(cache_key, doc)
    return doc


def chord_document_for_modal(
    symbol: str,
    *,
    instrument: str = 'violao',
    key_context: str | None = None,
) -> dict:
    """Payload unificado para o modal (teoria + posições + escalas sugeridas)."""
    from chord_diagram.scales import suggest_scales_for_chord

    doc = build_chord_document(symbol, instrument=instrument, key_context=key_context)
    if doc.get('error'):
        return doc
    theory = doc.get('theory') or {}
    chord_entry = {
        'input': theory.get('input') or symbol,
        'display': theory.get('display') or symbol,
        'normalized': symbol,
        'notes': theory.get('notes') or [],
        'intervals': theory.get('intervals') or [],
        'quality': theory.get('quality'),
        'root': theory.get('root'),
        'positions': doc.get('positions') or [],
        'keyMappings': doc.get('keyMappings'),
        'scales': suggest_scales_for_chord({
            'display': theory.get('display'),
            'notes': theory.get('notes'),
        }),
        'meta': doc.get('meta'),
    }
    return {
        'chord': chord_entry,
        'document': doc,
        'instruments': list_instrument_meta(),
        'scale_types': list_scale_types(),
    }


def fetch_progression_for_modal(
    symbol: str,
    *,
    instrument: str = 'violao',
    key_context: str | None = None,
) -> dict:
    chunks = split_chord_progression(symbol) or [symbol]
    chords = []
    for ch in chunks:
        item = chord_document_for_modal(ch, instrument=instrument, key_context=key_context)
        if item.get('chord'):
            chords.append(item['chord'])
    if not chords:
        return {'error': 'Acorde não reconhecido', 'chords': []}
    return {
        'chords': chords,
        'instruments': list_instrument_meta(),
        'scale_types': list_scale_types(),
        'apiVersion': API_VERSION,
    }


def render_chord_svg_for_position(symbol: str, instrument: str, pos: int = 0) -> str | None:
    doc = build_chord_document(symbol, instrument=instrument, max_positions=pos + 1)
    positions = doc.get('positions') or []
    if pos >= len(positions):
        return None
    spec = get_instrument(_normalize_instrument(instrument))
    if not spec:
        return None
    p = positions[pos]
    frets_raw = []
    for f in p['frets']:
        frets_raw.append('x' if f == 'X' else f)
    return render_fretboard_svg(
        spec,
        frets_raw,
        fingers=p.get('fingers'),
        title=doc.get('theory', {}).get('display', symbol),
    )


def catalog_payload() -> dict:
    from chord_diagram.cache import cache_stats
    return {
        'version': API_VERSION,
        'instruments': list_instrument_meta(),
        'scaleTypes': list_scale_types(),
        'cache': cache_stats(),
    }
