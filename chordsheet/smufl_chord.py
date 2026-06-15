"""Mapeia símbolos de acorde para glifos SMuFL (Bravura Text).

Referência: https://w3c.github.io/smufl/latest/tables/chord-symbols.html
"""

from __future__ import annotations

import re

# Standard accidentals for chord symbols (U+ED60–U+ED66)
CSYM_ACCIDENTAL_FLAT = "\uED60"
CSYM_ACCIDENTAL_SHARP = "\uED62"

# Chord symbols (U+E870–U+E87F)
CSYM_DIMINISHED = "\uE870"
CSYM_HALF_DIMINISHED = "\uE871"
CSYM_AUGMENTED = "\uE872"
CSYM_MAJOR_SEVENTH = "\uE873"
CSYM_MINOR = "\uE874"
CSYM_ALTERED_BASS_SLASH = "\uE87B"

_ROOT = re.compile(r"^([A-G])([#b]?)(.*)$", re.IGNORECASE)


def _accidental_smufl(acc: str) -> str:
    if acc == "#":
        return CSYM_ACCIDENTAL_SHARP
    if acc == "b":
        return CSYM_ACCIDENTAL_FLAT
    return acc


def _qual_to_smufl(qual: str) -> str:
    if not qual:
        return ""

    q = qual

    # Diminuído / meio-diminuído (já normalizado por prefs ou entrada direta)
    q = re.sub(r"°7", CSYM_DIMINISHED + "7", q)
    q = re.sub(r"°", CSYM_DIMINISHED, q)
    q = re.sub(r"ø7", CSYM_HALF_DIMINISHED + "7", q)
    q = re.sub(r"ø", CSYM_HALF_DIMINISHED, q)
    q = re.sub(r"(?i)dim7", CSYM_DIMINISHED + "7", q)
    q = re.sub(r"(?i)dim", CSYM_DIMINISHED, q)
    q = re.sub(r"(?i)m7b5", CSYM_HALF_DIMINISHED + "7", q)

    # Sétima maior (Δ, MA7, maj7)
    q = re.sub(r"Δ(\d*)", lambda m: CSYM_MAJOR_SEVENTH + m.group(1), q)
    q = re.sub(r"(?i)MA7(\d*)", lambda m: CSYM_MAJOR_SEVENTH + (m.group(1) or "7"), q)
    q = re.sub(
        r"(?i)maj(\d+)",
        lambda m: CSYM_MAJOR_SEVENTH + m.group(1),
        q,
    )
    q = re.sub(r"(?i)maj7", CSYM_MAJOR_SEVENTH + "7", q)

    # Menor (símbolo SMuFL no lugar do "m" inicial)
    if re.match(r"(?i)^m(\d|$)", q):
        q = CSYM_MINOR + q[1:]

    # Aumentado
    q = re.sub(r"\+", CSYM_AUGMENTED, q)
    q = re.sub(r"(?i)aug", CSYM_AUGMENTED, q)

    return q


def _note_to_smufl(note: str) -> str:
    note = (note or "").strip()
    if not note:
        return ""
    m = _ROOT.match(note)
    if not m:
        return note
    root, acc, rest = m.group(1), m.group(2), m.group(3)
    return root.upper() + _accidental_smufl(acc) + rest


def display_to_smufl(display: str) -> str:
    """Converte texto de acorde (pós-prefs) em string com glifos SMuFL."""
    if not display or display in ("%", "NC", "N.C."):
        return display

    slash = display.find("/")
    head = display[:slash] if slash >= 0 else display
    tail = display[slash:] if slash >= 0 else ""

    m = _ROOT.match(head)
    if not m:
        return display

    root, acc, qual = m.group(1), m.group(2), m.group(3)
    out = root.upper() + _accidental_smufl(acc) + _qual_to_smufl(qual)

    if tail.startswith("/"):
        bass = _note_to_smufl(tail[1:])
        if bass:
            out += CSYM_ALTERED_BASS_SLASH + bass

    return out
