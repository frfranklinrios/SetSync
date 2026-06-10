"""Serviço de diagramas: notas do acorde e metadados para renderização no cliente."""

from __future__ import annotations

from util import chord_components_info, split_chord_progression, to_brazilian_chord_notation

from chord_diagram.scales import SCALE_TYPES, suggest_scales_for_chord

INSTRUMENTS = (
    {'id': 'violao', 'label': 'Violão', 'strings': 6},
    {'id': 'cavaco', 'label': 'Cavaco', 'strings': 4},
    {'id': 'ukulele', 'label': 'Ukulele', 'strings': 4},
    {'id': 'baixo', 'label': 'Baixo (arpejo)', 'strings': 4},
)


def list_instruments() -> list[dict]:
    return [dict(i) for i in INSTRUMENTS]


def chord_diagram_payload(symbol: str) -> dict:
    """Monta payload JSON para o modal de diagramas (notas + rótulos BR)."""
    symbol = (symbol or '').strip()
    if not symbol:
        return {'error': 'Acorde não informado', 'chords': []}

    chunks = split_chord_progression(symbol) or [symbol]
    chords = []
    for chunk in chunks:
        info = chord_components_info(chunk)
        if not info:
            continue
        info = dict(info)
        info['display'] = to_brazilian_chord_notation(info.get('display', chunk))
        info['scales'] = suggest_scales_for_chord(info)
        chords.append(info)

    if not chords:
        return {'error': 'Acorde não reconhecido', 'chords': []}

    return {
        'chords': chords,
        'instruments': list_instruments(),
        'scale_types': [
            {'id': k, 'label': v['label']}
            for k, v in SCALE_TYPES.items()
        ],
    }
