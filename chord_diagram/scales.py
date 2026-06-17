"""Escalas sugeridas para diagramas (compat — ver scales_db.py)."""

from __future__ import annotations

from chord_diagram.scales_db import (
    SCALE_TYPES,
    list_scale_types,
    resolve_scale_type,
    scale_formula,
    scale_note_names,
)

__all__ = [
    'SCALE_TYPES',
    'list_scale_types',
    'resolve_scale_type',
    'scale_formula',
    'scale_note_names',
    'suggest_scale_ids',
    'suggest_scales_for_chord',
]


def suggest_scale_ids(chord_display: str) -> list[str]:
    import re

    text = (chord_display or '').strip()
    m = re.match(r'^([A-G](?:#|b)?)(.*)$', text.replace(' ', ''))
    ql = (m.group(2) if m else '').lower().replace('maj', '').strip()

    if not ql or ql in ('', '7+'):
        return ['major', 'pent_major', 'mixolydian']
    if ql in ('m', 'min', 'm7', 'dim', 'º', '°'):
        return ['minor', 'pent_minor', 'blues', 'dorian']
    if ql in ('7', '9', '7sus4', '13', '11'):
        return ['mixolydian', 'pent_minor', 'blues', 'major']
    if 'sus' in ql:
        return ['major', 'mixolydian', 'pent_major']
    return ['major', 'minor', 'pent_major', 'pent_minor']


def suggest_scales_for_chord(chord_info: dict) -> list[dict]:
    notes = chord_info.get('notes') or []
    root = notes[0] if notes else None
    display = chord_info.get('display') or chord_info.get('input') or ''
    if not root:
        import re
        m = re.match(r'^([A-G](?:#|b)?)', display.replace(' ', ''))
        root = m.group(1) if m else None
    if not root:
        return []

    out = []
    seen = set()
    for sid in suggest_scale_ids(display):
        if sid in seen or sid not in SCALE_TYPES:
            continue
        seen.add(sid)
        out.append({
            'id': sid,
            'label': SCALE_TYPES[sid]['label'],
            'root': root,
            'notes': scale_note_names(root, sid),
        })
    return out
