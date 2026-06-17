"""Mapa de intervalos — nomenclatura teórica ↔ semitons."""

from __future__ import annotations

INTERVAL_SEMITONES: dict[str, int] = {
    'P1': 0, 'R': 0, 'm2': 1, 'b9': 1,
    'M2': 2, '9': 2,
    'm3': 3, '#9': 3,
    'M3': 4,
    'P4': 5, '11': 5,
    'A4': 6, 'd5': 6, '#11': 6,
    'P5': 7,
    'A5': 8, 'm6': 8, '#5': 8,
    'M6': 9, '13': 9,
    'm7': 10,
    'M7': 11,
}

_BY_SEMITONE = [
    ('P1', 'm2', 'M2', 'm3', 'M3', 'P4', 'A4', 'P5', 'A5', 'M6', 'm7', 'M7'),
]


def interval_name(semitones: int, *, prefer: str | None = None) -> str:
    s = semitones % 12
    names = _BY_SEMITONE[0]
    if prefer and prefer in INTERVAL_SEMITONES and INTERVAL_SEMITONES[prefer] % 12 == s:
        return prefer
    return names[s]


def intervals_for_pcs(root_pc: int, pcs: list[int]) -> list[str]:
    out = []
    for pc in pcs:
        out.append(interval_name((pc - root_pc) % 12))
    return out
