"""Analisador léxico de acordes — raiz, qualidade, tensões, baixo."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from pychord import Chord

from chord_diagram.theory.intervals import intervals_for_pcs
from chord_diagram.theory.pitch import note_to_midi, note_to_pc, pc_to_spelling
from util import _normalize_chord_for_pychord, clean_chord_symbol

ROOT_RE = re.compile(
    r'^([A-G](?:#|b)?)'
    r'(.*?)'
    r'(?:/([A-G](?:#|b)?))?$',
    re.I,
)

QUALITY_PATTERNS = (
    (re.compile(r'^(maj7|ma7|M7|7\+|Δ7)', re.I), 'maj7', [0, 4, 7, 11]),
    (re.compile(r'^(maj|ma|M)(?!7|9|11|13)', re.I), 'maj', [0, 4, 7]),
    (re.compile(r'^(m7b5|ø|min7b5)', re.I), 'm7b5', [0, 3, 6, 10]),
    (re.compile(r'^(dim7|°7|º7)', re.I), 'dim7', [0, 3, 6, 9]),
    (re.compile(r'^(dim|°|º)', re.I), 'dim', [0, 3, 6]),
    (re.compile(r'^(aug|\+)(?!\d)', re.I), 'aug', [0, 4, 8]),
    (re.compile(r'^(m7|min7|mi7)(?!\w)', re.I), 'm7', [0, 3, 7, 10]),
    (re.compile(r'^(m|min|mi)(?!\w)', re.I), 'min', [0, 3, 7]),
    (re.compile(r'^(sus4)', re.I), 'sus4', [0, 5, 7]),
    (re.compile(r'^(sus2)', re.I), 'sus2', [0, 2, 7]),
    (re.compile(r'^(7)(?!\w)', re.I), '7', [0, 4, 7, 10]),
    (re.compile(r'^$', re.I), 'maj', [0, 4, 7]),
)

TENSION_RE = re.compile(
    r'(add\d+|#?\d{1,2}|b\d{1,2}|omit\s*\d+|no\s*\d+)',
    re.I,
)


@dataclass
class ParsedChord:
    raw: str
    root: str
    quality: str
    tensions: list[str] = field(default_factory=list)
    bass: str | None = None
    omit: list[str] = field(default_factory=list)
    triad_intervals: list[int] = field(default_factory=list)


def parse_chord_symbol(symbol: str) -> ParsedChord | None:
    s = clean_chord_symbol(symbol or '').replace(' ', '')
    if not s:
        return None
    m = ROOT_RE.match(s)
    if not m:
        return None
    root = m.group(1)[0].upper() + m.group(1)[1:]
    rest = (m.group(2) or '').replace('(', ' ').replace(')', ' ')
    bass = m.group(3)
    if bass:
        bass = bass[0].upper() + bass[1:]

    quality = 'maj'
    triad = [0, 4, 7]
    consumed = 0
    for pat, qname, intervals in QUALITY_PATTERNS:
        qm = pat.match(rest)
        if qm:
            quality = qname
            triad = intervals[:3] if len(intervals) >= 3 else intervals
            consumed = qm.end()
            break

    tail = rest[consumed:]
    tensions: list[str] = []
    omit: list[str] = []
    for tm in TENSION_RE.finditer(tail):
        tok = tm.group(1)
        if re.match(r'omit|no', tok, re.I):
            omit.append(re.sub(r'\D', '', tok) or tok)
        else:
            tensions.append(tok)

    return ParsedChord(
        raw=symbol,
        root=root,
        quality=quality,
        tensions=tensions,
        bass=bass,
        omit=omit,
        triad_intervals=triad,
    )


def chord_theory_block(symbol: str, *, key_context: str | None = None) -> dict | None:
    """Bloco theory do payload v1 (notas + intervalos + MIDI)."""
    parsed = parse_chord_symbol(symbol)
    if not parsed:
        return None
    normalized = _normalize_chord_for_pychord(clean_chord_symbol(symbol))
    try:
        notes = Chord(normalized).components()
    except Exception:
        return None
    if not isinstance(notes, list) or not notes:
        return None

    root_pc = note_to_pc(parsed.root)
    if root_pc is None:
        return None
    pcs = []
    for n in notes:
        pc = note_to_pc(n)
        if pc is not None:
            pcs.append(pc)
    spelled = [pc_to_spelling(pc, key_context or parsed.root) for pc in pcs]
    midi = [note_to_midi(n) for n in notes]
    midi = [m for m in midi if m is not None]

    return {
        'root': parsed.root,
        'quality': parsed.quality,
        'tensions': parsed.tensions,
        'bass': parsed.bass,
        'omit': parsed.omit,
        'intervals': intervals_for_pcs(root_pc, pcs),
        'notes': spelled,
        'midi': midi,
    }
