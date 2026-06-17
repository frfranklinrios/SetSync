"""Mapeamento de acordes no teclado do piano."""

from __future__ import annotations

from chord_diagram.theory.pitch import note_to_midi, note_to_pc, pc_to_spelling

SHARP_PCS = {1, 3, 6, 8, 10}


def key_class_for_pc(pc: int) -> str:
    return 'accidental' if pc in SHARP_PCS else 'natural'


def piano_key_mappings(
    note_names: list[str],
    *,
    start_octave: int = 4,
    key_context: str | None = None,
) -> list[dict]:
    root_pc = note_to_pc(note_names[0]) if note_names else None
    out = []
    for i, raw in enumerate(note_names):
        pc = note_to_pc(raw)
        if pc is None:
            continue
        octave = start_octave + (i // 4)
        spelling = pc_to_spelling(pc, key_context)
        midi = note_to_midi(spelling, octave)
        if midi is None:
            midi = 12 * (octave + 1) + pc
        out.append({
            'note': spelling.rstrip('0123456789') or spelling,
            'octave': octave,
            'isRoot': pc == root_pc,
            'keyClass': key_class_for_pc(pc),
            'midiId': midi,
        })
    return out
