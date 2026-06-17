"""API REST v1 — acordes, escalas, arpejos e renderização SVG."""

from __future__ import annotations

import os
import time
from functools import wraps

from flask import Blueprint, jsonify, request, Response

music_api_bp = Blueprint('music_api', __name__, url_prefix='/api/v1')

_TELEMETRY: list[dict] = []
_MAX_TELEMETRY = 5000


def _api_key_ok() -> bool:
    expected = (os.getenv('MUSIC_API_KEY') or '').strip()
    if not expected:
        return True
    return request.headers.get('x-api-key', '') == expected


def _telemetry(endpoint: str, status: int, ms: float) -> None:
    _TELEMETRY.append({
        'ts': time.time(),
        'endpoint': endpoint,
        'status': status,
        'ms': round(ms, 2),
        'instrument': request.args.get('instrument'),
    })
    if len(_TELEMETRY) > _MAX_TELEMETRY:
        del _TELEMETRY[: len(_TELEMETRY) - _MAX_TELEMETRY]


def music_api_guard(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not _api_key_ok():
            return jsonify({'error': 'x-api-key inválida ou ausente'}), 401
        t0 = time.time()
        resp = fn(*args, **kwargs)
        status = resp[1] if isinstance(resp, tuple) else 200
        _telemetry(request.path, status, (time.time() - t0) * 1000)
        return resp
    return wrapper


@music_api_bp.route('/catalog', methods=['GET'])
@music_api_guard
def catalog():
    from chord_diagram.api_service import catalog_payload
    return jsonify(catalog_payload())


@music_api_bp.route('/chords', methods=['GET'])
@music_api_guard
def chords_index():
    from chord_diagram.api_service import build_chord_document
    from util import split_chord_progression

    symbol = (request.args.get('symbol') or request.args.get('root') or '').strip()
    if not symbol:
        return jsonify({'error': 'Parâmetro symbol obrigatório'}), 400
    instrument = request.args.get('instrument', 'violao')
    key_ctx = request.args.get('key') or request.args.get('keyContext')
    chunks = split_chord_progression(symbol) or [symbol]
    if len(chunks) == 1:
        if request.args.get('format') == 'modal':
            from chord_diagram.api_service import fetch_progression_for_modal
            doc = fetch_progression_for_modal(
                symbol, instrument=instrument, key_context=key_ctx,
            )
            if doc.get('error'):
                return jsonify(doc), 400
            return jsonify(doc)

        doc = build_chord_document(symbol, instrument=instrument, key_context=key_ctx)
        if doc.get('error'):
            return jsonify(doc), 400
        fmt = request.args.get('format', 'json')
        if fmt == 'svg' and doc.get('positions'):
            from chord_diagram.api_service import render_chord_svg_for_position
            svg = render_chord_svg_for_position(symbol, instrument, 0)
            if svg:
                return Response(svg, mimetype='image/svg+xml')
        return jsonify(doc)

    results = []
    for ch in chunks:
        doc = build_chord_document(ch, instrument=instrument, key_context=key_ctx)
        if not doc.get('error'):
            results.append(doc)
    if not results:
        return jsonify({'error': 'Acorde não reconhecido'}), 400
    return jsonify({'progression': results, 'symbol': symbol})


@music_api_bp.route('/chords/<path:symbol>', methods=['GET'])
@music_api_guard
def chords_detail(symbol):
    from chord_diagram.api_service import build_chord_document, render_chord_svg_for_position

    instrument = request.args.get('instrument', 'violao')
    key_ctx = request.args.get('key')
    doc = build_chord_document(symbol, instrument=instrument, key_context=key_ctx)
    if doc.get('error'):
        return jsonify(doc), 400
    if request.args.get('format') == 'svg':
        pos = int(request.args.get('pos', 0))
        svg = render_chord_svg_for_position(symbol, instrument, pos)
        if not svg:
            return jsonify({'error': 'Posição não encontrada'}), 404
        return Response(svg, mimetype='image/svg+xml')
    return jsonify(doc)


@music_api_bp.route('/scales', methods=['GET'])
@music_api_guard
def scales_index():
    from chord_diagram.api_service import build_scale_document
    from chord_diagram.scales_db import list_scale_types

    root = request.args.get('root', 'C')
    scale_type = request.args.get('type') or request.args.get('scale', 'major')
    instrument = request.args.get('instrument', 'violao')
    max_frets = min(int(request.args.get('maxFrets', 15)), 24)
    if request.args.get('list'):
        return jsonify({'scaleTypes': list_scale_types()})
    doc = build_scale_document(
        root, scale_type, instrument=instrument, max_frets=max_frets,
        key_context=request.args.get('key'),
    )
    if doc.get('error'):
        return jsonify(doc), 400
    return jsonify(doc)


@music_api_bp.route('/arpeggios', methods=['GET'])
@music_api_guard
def arpeggios_index():
    from chord_diagram.api_service import build_arpeggio_document

    symbol = request.args.get('symbol', 'Am7')
    instrument = request.args.get('instrument', 'baixo')
    pattern = request.args.get('pattern', 'root')
    octaves = min(int(request.args.get('octaves', 2)), 4)
    doc = build_arpeggio_document(symbol, instrument=instrument, pattern=pattern, octaves=octaves)
    if doc.get('error'):
        return jsonify(doc), 400
    return jsonify(doc)


@music_api_bp.route('/render/fretboard', methods=['GET'])
@music_api_guard
def render_fretboard():
    from chord_diagram.api_service import render_chord_svg_for_position

    symbol = request.args.get('symbol', '')
    instrument = request.args.get('instrument', 'violao')
    pos = int(request.args.get('pos', 0))
    if not symbol:
        return jsonify({'error': 'symbol obrigatório'}), 400
    svg = render_chord_svg_for_position(symbol, instrument, pos)
    if not svg:
        return jsonify({'error': 'Não foi possível renderizar'}), 404
    return Response(svg, mimetype='image/svg+xml')


@music_api_bp.route('/render/piano', methods=['GET'])
@music_api_guard
def render_piano():
    from chord_diagram.piano import piano_key_mappings
    from chord_diagram.render_svg import render_piano_svg
    from chord_diagram.theory.chord_parser import chord_theory_block

    symbol = request.args.get('symbol') or request.args.get('target', 'Cmaj7')
    notes_param = request.args.get('notes')
    if notes_param:
        notes = [n.strip() for n in notes_param.split(',') if n.strip()]
        keys = piano_key_mappings(notes)
    else:
        theory = chord_theory_block(symbol)
        if not theory:
            return jsonify({'error': 'Notas inválidas'}), 400
        keys = piano_key_mappings(theory['notes'])
    svg = render_piano_svg(keys)
    if request.args.get('format') == 'json':
        return jsonify({'instrument': 'piano', 'target': symbol, 'keyMappings': keys})
    return Response(svg, mimetype='image/svg+xml')


@music_api_bp.route('/notation/vexflow', methods=['GET'])
@music_api_guard
def notation_vexflow():
    from chord_diagram.api_service import build_chord_document
    from chord_diagram.vexflow_export import chord_to_vextab

    symbol = request.args.get('symbol', 'C')
    instrument = request.args.get('instrument', 'violao')
    pos = int(request.args.get('pos', 0))
    doc = build_chord_document(symbol, instrument=instrument, max_positions=pos + 1)
    positions = doc.get('positions') or []
    if pos >= len(positions):
        return jsonify({'error': 'Posição não encontrada'}), 404
    frets = []
    for f in positions[pos]['frets']:
        frets.append('x' if f == 'X' else f)
    vextab = chord_to_vextab(frets, instrument)
    return jsonify({
        'format': 'vextab',
        'symbol': symbol,
        'instrument': instrument,
        'position': pos,
        'vextab': vextab,
    })


@music_api_bp.route('/telemetry', methods=['GET'])
@music_api_guard
def telemetry_ndjson():
    """Últimos eventos em ndJSON (uso interno / monitoramento)."""
    lines = '\n'.join(
        __import__('json').dumps(row, ensure_ascii=False) for row in _TELEMETRY[-500:]
    )
    return Response(lines + '\n', mimetype='application/x-ndjson')
