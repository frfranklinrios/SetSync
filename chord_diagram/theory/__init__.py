"""Teoria musical computacional — temperamento igual, intervalos e parsing."""

from chord_diagram.theory.chord_parser import chord_theory_block, parse_chord_symbol
from chord_diagram.theory.intervals import INTERVAL_SEMITONES, interval_name
from chord_diagram.theory.pitch import (
    build_key_spelling_table,
    midi_to_spelling,
    note_to_midi,
    note_to_pc,
    pc_to_spelling,
)

__all__ = [
    "INTERVAL_SEMITONES",
    "build_key_spelling_table",
    "chord_theory_block",
    "interval_name",
    "midi_to_spelling",
    "note_to_midi",
    "note_to_pc",
    "parse_chord_symbol",
    "pc_to_spelling",
]
