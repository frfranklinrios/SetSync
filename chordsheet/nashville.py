"""Numeração Nashville (graus) para exibição na grade harmônica."""
from __future__ import annotations

import re

_PC: dict[str, int] = {
    "C": 0,
    "B#": 0,
    "D#": 1,
    "Eb": 1,
    "D": 2,
    "Fb": 2,
    "E": 4,
    "F": 5,
    "E#": 5,
    "G#": 6,
    "Ab": 6,
    "G": 7,
    "A#": 8,
    "Bb": 8,
    "A": 9,
    "B": 11,
    "Cb": 11,
    "C#": 1,
    "F#": 6,
}

_DEGREE = ("1", "b2", "2", "b3", "3", "4", "#4", "5", "b6", "6", "b7", "7")


def _parse_root(chord: str) -> tuple[int, str, str] | None:
    token = (chord or "").strip()
    if not token or token in ("%", "*", ".", "NC", "N.C."):
        return None
    m = re.match(r"^([A-G](?:#|b)?)(.*)$", token, re.I)
    if not m:
        return None
    root = m.group(1)[0].upper() + m.group(1)[1:]
    rest = m.group(2) or ""
    pc = _PC.get(root)
    if pc is None:
        return None
    bass = ""
    if "/" in rest:
        body, bass_raw = rest.split("/", 1)
        bm = re.match(r"^([A-G](?:#|b)?)", bass_raw.strip(), re.I)
        if bm:
            b = bm.group(1)[0].upper() + bm.group(1)[1:]
            bass = b
        rest = body
    return pc, rest, bass


def key_tonic_pc(key: str) -> int | None:
    raw = (key or "").strip()
    if not raw:
        return None
    root = raw.split()[0]
    root = root[0].upper() + root[1:] if len(root) > 1 else root.upper()
    return _PC.get(root)


def chord_to_nashville(chord: str, key: str) -> str:
    parsed = _parse_root(chord)
    if not parsed:
        return chord
    pc, quality, bass = parsed
    tonic = key_tonic_pc(key)
    if tonic is None:
        return chord
    interval = (pc - tonic) % 12
    num = _DEGREE[interval]
    q = quality or ""
    ql = q.lower()
    if (ql.startswith("m") and not ql.startswith("maj")) or ql.startswith("min"):
        if not num.endswith("m"):
            num += "m"
    elif "dim" in ql or "°" in q or "º" in q:
        num += "°"
    elif "aug" in ql or "+" in q:
        num += "+"
    ext = re.sub(r"^(m(in)?|maj)", "", q, flags=re.I)
    if ext and ext.lower() not in ("", "m"):
        num += ext
    if bass:
        bpc = _PC.get(bass)
        if bpc is not None:
            bdeg = _DEGREE[(bpc - tonic) % 12]
            num += "/" + bdeg
    return num
