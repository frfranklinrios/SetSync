"""Dicionário de escalas por vetores intervalares (módulo 12)."""

from __future__ import annotations

from chord_diagram.theory.pitch import note_to_pc, pc_to_spelling

SCALE_TYPES: dict[str, dict] = {
    'major': {'label': 'Maior (Jônio)', 'intervals': [0, 2, 4, 5, 7, 9, 11]},
    'minor': {'label': 'Menor natural (Eólio)', 'intervals': [0, 2, 3, 5, 7, 8, 10]},
    'dorian': {'label': 'Dórico', 'intervals': [0, 2, 3, 5, 7, 9, 10]},
    'phrygian': {'label': 'Frígio', 'intervals': [0, 1, 3, 5, 7, 8, 10]},
    'lydian': {'label': 'Lídio', 'intervals': [0, 2, 4, 6, 7, 9, 11]},
    'mixolydian': {'label': 'Mixolídio', 'intervals': [0, 2, 4, 5, 7, 9, 10]},
    'locrian': {'label': 'Lócrio', 'intervals': [0, 1, 3, 5, 6, 8, 10]},
    'pent_major': {'label': 'Pentatônica maior', 'intervals': [0, 2, 4, 7, 9]},
    'pent_minor': {'label': 'Pentatônica menor', 'intervals': [0, 3, 5, 7, 10]},
    'minor_pentatonic': {'label': 'Pentatônica menor', 'intervals': [0, 3, 5, 7, 10]},
    'blues': {'label': 'Blues menor', 'intervals': [0, 3, 5, 6, 7, 10]},
    'blues_major': {'label': 'Blues maior', 'intervals': [0, 2, 3, 4, 7, 9]},
    'harmonic_minor': {'label': 'Menor harmônica', 'intervals': [0, 2, 3, 5, 7, 8, 11]},
    'melodic_minor': {'label': 'Menor melódica', 'intervals': [0, 2, 3, 5, 7, 9, 11]},
    'whole_tone': {'label': 'Tom inteiro', 'intervals': [0, 2, 4, 6, 8, 10]},
    'dim_half_whole': {'label': 'Diminuta tom-semitom', 'intervals': [0, 1, 3, 4, 6, 7, 9, 10]},
    'dim_whole_half': {'label': 'Diminuta semitom-tom', 'intervals': [0, 2, 3, 5, 6, 8, 9, 11]},
    'hirajoshi': {'label': 'Hirajoshi', 'intervals': [0, 2, 3, 7, 8]},
    'kumoi': {'label': 'Kumoi', 'intervals': [0, 2, 3, 7, 9]},
    'pelog': {'label': 'Pelog', 'intervals': [0, 1, 3, 7, 8]},
}

# Alias de nomes da especificação
_ALIASES = {
    'ionian': 'major',
    'aeolian': 'minor',
    'minor_pentatonic': 'pent_minor',
    'major_pentatonic': 'pent_major',
}


def resolve_scale_type(scale_type: str) -> str | None:
    key = (scale_type or '').strip().lower().replace('-', '_').replace(' ', '_')
    if key in SCALE_TYPES:
        return key
    return _ALIASES.get(key)


def scale_note_names(root: str, scale_id: str, *, key_context: str | None = None) -> list[str]:
    sid = resolve_scale_type(scale_id) or scale_id
    spec = SCALE_TYPES.get(sid)
    ri = note_to_pc(root)
    if not spec or ri is None:
        return []
    ctx = key_context or root
    return [pc_to_spelling((ri + iv) % 12, ctx) for iv in spec['intervals']]


def scale_formula(scale_id: str) -> list[int]:
    sid = resolve_scale_type(scale_id) or scale_id
    spec = SCALE_TYPES.get(sid)
    return list(spec['intervals']) if spec else []


def list_scale_types() -> list[dict]:
    seen: set[str] = set()
    out = []
    for k, v in SCALE_TYPES.items():
        if k in _ALIASES.values() and k != 'pent_minor':
            continue
        if k in seen:
            continue
        seen.add(k)
        out.append({'id': k, 'label': v['label'], 'formula': v['intervals']})
    return out
