"""Teoria musical computacional — temperamento igual, intervalos e parsing."""

from chord_diagram.theory.chord_parser import parse_chord_symbol, chord_theory_block
from chord_diagram.theory.intervals import interval_name, INTERVAL_SEMITONES
from chord_diagram.theory.pitch import (
    note_to_pc,
    pc_to_spelling,
    note_to_midi,
    midi_to_spelling,
    build_key_spelling_table,
)

__all__ = [
    'parse_chord_symbol',
    'chord_theory_block',
    'interval_name',
    'INTERVAL_SEMITONES',
    'note_to_pc',
    'pc_to_spelling',
    'note_to_midi',
    'midi_to_spelling',
    'build_key_spelling_table',
]
