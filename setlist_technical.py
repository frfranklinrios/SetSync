"""Dados técnicos para PDF de estudo (escalas por tom)."""

from __future__ import annotations

import re

from chord_diagram.scales_db import scale_note_names


def _scale_root(display_key: str | None, tom_original: str | None) -> str:
    raw = (display_key or tom_original or 'C').strip()
    if not raw:
        return 'C'
    m = re.match(r'^([A-G](?:#|b)?)', raw, re.I)
    return m.group(1) if m else raw[:2]


def enrich_sheet_technical(sheet: dict) -> dict:
    root = _scale_root(sheet.get('display_key'), sheet.get('tom_original'))
    try:
        major = scale_note_names(root, 'major')
    except Exception:
        major = []
    try:
        minor_pent = scale_note_names(root, 'minor_pentatonic')
    except Exception:
        minor_pent = []
    sheet = dict(sheet)
    sheet['tech_root'] = root
    sheet['tech_major_notes'] = major
    sheet['tech_minor_pent_notes'] = minor_pent
    return sheet
