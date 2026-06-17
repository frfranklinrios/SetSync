"""Temperamento igual (MIDI) e grafia ciente de tonalidade."""

from __future__ import annotations

CHROMATIC_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CHROMATIC_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

NOTE_TO_PC: dict[str, int] = {}
for i, n in enumerate(CHROMATIC_SHARP):
    NOTE_TO_PC[n] = i
NOTE_TO_PC.update({'Db': 1, 'Eb': 3, 'Gb': 6, 'Ab': 8, 'Bb': 10, 'Fb': 4, 'Cb': 11, 'E#': 5, 'B#': 0})

LETTERS = ('C', 'D', 'E', 'F', 'G', 'A', 'B')
LETTER_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

MAJOR_STEPS = (0, 2, 4, 5, 7, 9, 11)
MINOR_STEPS = (0, 2, 3, 5, 7, 8, 10)

FLAT_KEYS = frozenset({'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb', 'Dm', 'Gm', 'Cm', 'Fm', 'Bbm', 'Ebm'})

MIDI_C4 = 60


def note_to_pc(note: str) -> int | None:
    n = (note or '').strip().replace('♯', '#').replace('♭', 'b')
    if not n:
        return None
  # Oitava opcional no final (ex.: C4, F#3)
    import re
    m = re.match(r'^([A-G](?:#|b)?)', n)
    if not m:
        return None
    return NOTE_TO_PC.get(m.group(1))


def prefer_flats(key: str | None) -> bool:
    if not key:
        return False
    k = key.strip()
    if k.endswith('m'):
        return k in FLAT_KEYS or k.capitalize() in FLAT_KEYS
    return k[0].upper() + k[1:] in FLAT_KEYS or k in FLAT_KEYS


def build_key_spelling_table(key: str | None = None, *, prefer_flat: bool | None = None) -> list[str]:
    """12 grafias (índice = pitch class) para a tonalidade."""
    use_flats = prefer_flats(key) if prefer_flat is None else prefer_flat
    table = list(CHROMATIC_FLAT if use_flats else CHROMATIC_SHARP)
    if not key:
        return table
    root_pc = note_to_pc(key)
    if root_pc is None:
        return table
    steps = MINOR_STEPS if key.strip().endswith('m') else MAJOR_STEPS
    li = LETTERS.index(key[0].upper())
    for i, step in enumerate(steps):
        pc = (root_pc + step) % 12
        letter = LETTERS[(li + i) % 7]
        diff = (pc - LETTER_PC[letter]) % 12
        if diff > 6:
            diff -= 12
        acc = {0: '', 1: '#', -1: 'b'}.get(diff)
        if acc is not None:
            table[pc] = letter + acc
    return table


def pc_to_spelling(pc: int, key: str | None = None) -> str:
    table = build_key_spelling_table(key)
    return table[pc % 12]


def note_to_midi(note: str, octave: int = 4) -> int | None:
    import re
    n = (note or '').strip().replace('♯', '#').replace('♭', 'b')
    m = re.match(r'^([A-G](?:#|b)?)(?:-?\d+)?$', n)
    if not m:
        pc = note_to_pc(n)
        if pc is None:
            return None
        return 12 * (octave + 1) + pc
    pc = note_to_pc(m.group(1))
    if pc is None:
        return None
    om = re.search(r'(\d+)$', n)
    octv = int(om.group(1)) if om else octave
    return 12 * (octv + 1) + pc


def midi_to_spelling(midi: int, key: str | None = None) -> tuple[str, int]:
    pc = midi % 12
    octave = midi // 12 - 1
    return pc_to_spelling(pc, key), octave
