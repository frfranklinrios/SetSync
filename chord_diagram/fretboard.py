"""Mapeamento de escalas e arpejos no braço."""

from __future__ import annotations

from chord_diagram.instruments import InstrumentSpec, get_instrument, open_string_pcs
from chord_diagram.scales_db import scale_formula, scale_note_names, resolve_scale_type
from chord_diagram.theory.intervals import interval_name
from chord_diagram.theory.pitch import note_to_pc, pc_to_spelling


def build_scale_fretboard_map(
    root: str,
    scale_type: str,
    instrument_id: str,
    *,
    max_frets: int | None = None,
    key_context: str | None = None,
) -> dict | None:
    spec = get_instrument(instrument_id)
    sid = resolve_scale_type(scale_type)
    if not spec or spec.family != 'fretted' or not sid:
        return None
    formula = scale_formula(sid)
    root_pc = note_to_pc(root)
    if root_pc is None:
        return None
    scale_pcs = {(root_pc + iv) % 12 for iv in formula}
    ctx = key_context or root
    mf = min(max_frets or 15, spec.max_fret)
    open_pcs = open_string_pcs(spec)
    nodes = []
    for si, oi in enumerate(open_pcs):
        for fret in range(0, mf + 1):
            pc = (oi + fret) % 12
            if pc not in scale_pcs:
                continue
            note = pc_to_spelling(pc, ctx)
            nodes.append({
                'string': si + 1,
                'fret': fret,
                'note': note,
                'isRoot': pc == root_pc,
                'interval': interval_name((pc - root_pc) % 12),
            })
    return {
        'type': 'scale_map',
        'name': f'{root} {sid}',
        'root': root,
        'formula': formula,
        'fretboardMapping': {
            'strings': spec.strings,
            'maxFrets': mf,
            'activeNodes': nodes,
        },
    }


def build_arpeggio_sequence(
    note_names: list[str],
    *,
    octaves: int = 2,
    pattern: str = 'ascend',
) -> list[dict]:
    """Arpejo como notas em oitavas sucessivas (mesma fórmula do acorde)."""
    pcs = []
    for n in note_names:
        pc = note_to_pc(n)
        if pc is not None:
            pcs.append(pc)
    if not pcs:
        return []
    seq = []
    base_midi = 48
    for oct_i in range(octaves):
        for i, pc in enumerate(pcs if pattern != 'inv1' else pcs[1:] + pcs[:1]):
            midi = base_midi + oct_i * 12 + ((pc - pcs[0]) % 12)
            seq.append({'midiId': midi, 'pitchClass': pc, 'order': len(seq)})
    return seq
