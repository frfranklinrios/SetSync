"""Escalas sugeridas para diagramas (metadados; render no cliente)."""

from __future__ import annotations

SCALE_TYPES = {
    'major': {'id': 'major', 'label': 'Maior', 'intervals': [0, 2, 4, 5, 7, 9, 11]},
    'minor': {'id': 'minor', 'label': 'Menor natural', 'intervals': [0, 2, 3, 5, 7, 8, 10]},
    'pent_major': {'id': 'pent_major', 'label': 'Pentatônica maior', 'intervals': [0, 2, 4, 7, 9]},
    'pent_minor': {'id': 'pent_minor', 'label': 'Pentatônica menor', 'intervals': [0, 3, 5, 7, 10]},
    'blues': {'id': 'blues', 'label': 'Blues', 'intervals': [0, 3, 5, 6, 7, 10]},
    'mixolydian': {'id': 'mixolydian', 'label': 'Mixolídio', 'intervals': [0, 2, 4, 5, 7, 9, 10]},
    'dorian': {'id': 'dorian', 'label': 'Dórico', 'intervals': [0, 2, 3, 5, 7, 9, 10]},
}

_CHROMATIC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
_NOTE_IDX = {n: i for i, n in enumerate(_CHROMATIC)}
_NOTE_IDX.update({'Db': 1, 'Eb': 3, 'Gb': 6, 'Ab': 8, 'Bb': 10})


def _note_index(note: str) -> int | None:
    n = (note or '').strip().replace('♯', '#').replace('♭', 'b')
    return _NOTE_IDX.get(n)


def scale_note_names(root: str, scale_id: str) -> list[str]:
    spec = SCALE_TYPES.get(scale_id)
    ri = _note_index(root)
    if not spec or ri is None:
        return []
    return [_CHROMATIC[(ri + iv) % 12] for iv in spec['intervals']]


def suggest_scale_ids(chord_display: str) -> list[str]:
    """IDs de escala sugeridas conforme a qualidade do acorde."""
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
