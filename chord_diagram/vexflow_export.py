"""Exportação VexTab / AlphaTex para integração com VexFlow no cliente."""

from __future__ import annotations

from chord_diagram.instruments import get_instrument, open_string_pcs
from chord_diagram.theory.pitch import note_to_pc


def chord_to_vextab(
    frets: list,
    instrument_id: str,
    *,
  clef: str = 'treble',
    time: str = '4/4',
) -> str:
    spec = get_instrument(instrument_id)
    if not spec or spec.family != 'fretted':
        return f'tabstave notation=true tablature=true clef={clef} time={time}\n'

    open_pcs = open_string_pcs(spec)
    tab_parts = []
    for si, f in enumerate(frets):
        string_num = spec.strings - si
        if f in ('x', 'X'):
            continue
        if f == 0:
            tab_parts.append(f'{string_num}-0/4')
        elif isinstance(f, int):
            tab_parts.append(f'{string_num}-{f}/4')

    line = ' '.join(tab_parts) if tab_parts else 'notes /4'
    return (
        f'tabstave notation=true tablature=true clef={clef} time={time}\n'
        f'notes {line}\n'
    )


def arpeggio_to_vextab(
    frets_sequence: list[list],
    instrument_id: str,
) -> str:
    lines = [f'tabstave notation=true tablature=true clef=treble time=4/4']
    for frets in frets_sequence:
        lines.append(chord_to_vextab(frets, instrument_id).strip().split('\n')[-1])
    return '\n'.join(lines) + '\n'
