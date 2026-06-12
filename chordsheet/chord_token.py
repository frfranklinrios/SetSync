"""Parse de tokens de acorde (manual chordsheet.com — chord-types, meta)."""

from __future__ import annotations

import re
from dataclasses import dataclass

CHORD_NOTE = re.compile(r'^(.+?)\s+"([^"]*)"$')
OPTIONAL = re.compile(r"^(.+)\?$")
STROKES = re.compile(r"^(.+?)(,+)$")


@dataclass
class ParsedChord:
    text: str
    optional: bool = False
    strokes: int = 0
    note: str = ""
    blank_head: bool = False


def parse_chord_token(raw: str) -> ParsedChord:
    token = (raw or "").strip()
    if not token:
        return ParsedChord("")

    note = ""
    m = CHORD_NOTE.match(token)
    if m:
        token = m.group(1).strip()
        note = m.group(2).strip()

    optional = False
    om = OPTIONAL.match(token)
    if om:
        token = om.group(1).strip()
        optional = True

    strokes = 0
    sm = STROKES.match(token)
    if sm:
        token = sm.group(1).strip()
        strokes = len(sm.group(2))

    blank_head = token.startswith("*/")
    if blank_head:
        token = token[2:].lstrip("/")
        token = f"/{token}" if token else ""

    return ParsedChord(
        text=token,
        optional=optional,
        strokes=strokes,
        note=note,
        blank_head=blank_head,
    )
