"""Catálogo de instrumentos, afinações e limites de tocabilidade."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentSpec:
    id: str
    label: str
    family: str  # fretted | keys
    strings: int
    tuning_name: str
    tuning_pitches: tuple[str, ...]
    max_fret: int
    max_span: int
    tuning_note: str = ''


INSTRUMENTS: dict[str, InstrumentSpec] = {
    'violao': InstrumentSpec(
        id='violao', label='Violão', family='fretted', strings=6,
        tuning_name='Standard EADGBE',
        tuning_pitches=('E2', 'A2', 'D3', 'G3', 'B3', 'E4'),
        max_fret=22, max_span=4,
    ),
    'guitarra': InstrumentSpec(
        id='guitarra', label='Guitarra elétrica', family='fretted', strings=6,
        tuning_name='Standard EADGBE',
        tuning_pitches=('E2', 'A2', 'D3', 'G3', 'B3', 'E4'),
        max_fret=24, max_span=5,
    ),
    'baixo': InstrumentSpec(
        id='baixo', label='Contrabaixo 4 cordas', family='fretted', strings=4,
        tuning_name='Standard EADG',
        tuning_pitches=('E1', 'A1', 'D2', 'G2'),
        max_fret=20, max_span=3,
    ),
    'ukulele': InstrumentSpec(
        id='ukulele', label='Ukulele (soprano)', family='fretted', strings=4,
        tuning_name='Standard GCEA (reentrante)',
        tuning_pitches=('G4', 'C4', 'E4', 'A4'),
        max_fret=15, max_span=4,
        tuning_note='reentrant',
    ),
    'cavaquinho': InstrumentSpec(
        id='cavaquinho', label='Cavaquinho', family='fretted', strings=4,
        tuning_name='Standard Brazilian DGBD',
        tuning_pitches=('D4', 'G4', 'B4', 'D5'),
        max_fret=15, max_span=3,
    ),
    'piano': InstrumentSpec(
        id='piano', label='Piano', family='keys', strings=0,
        tuning_name='88 keys A0–C8',
        tuning_pitches=(),
        max_fret=0, max_span=0,
    ),
}

OPEN_STRING_PC = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
    'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
}


def open_string_pcs(spec: InstrumentSpec) -> list[int]:
    out = []
    for pitch in spec.tuning_pitches:
        name = pitch.rstrip('0123456789')
        pc = OPEN_STRING_PC.get(name)
        if pc is not None:
            out.append(pc)
    return out


def get_instrument(instrument_id: str) -> InstrumentSpec | None:
    iid = (instrument_id or '').strip().lower()
    if iid == 'cavaco':
        iid = 'cavaquinho'
    return INSTRUMENTS.get(iid)


def list_instrument_meta() -> list[dict]:
    return [
        {
            'id': s.id,
            'label': s.label,
            'family': s.family,
            'strings': s.strings,
            'tuningName': s.tuning_name,
            'tuningPitches': list(s.tuning_pitches),
        }
        for s in INSTRUMENTS.values()
    ]
