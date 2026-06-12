"""Formatação visual de símbolos de acordes."""

from __future__ import annotations

import html
import re

from chordsheet.chord_token import parse_chord_token
from chordsheet.prefs import Prefs

ROOT = re.compile(
    r"^([A-G])([#b]?)(.*)$",
    re.IGNORECASE,
)


def format_chord_display(chord: str, prefs: Prefs) -> str:
    parsed = parse_chord_token(chord)
    raw = parsed.text
    if not raw or raw in ("%", "NC", "N.C."):
        return raw.replace("N.C.", "N.C.") if raw else raw
    if raw.upper() in ("NC", "N.C."):
        return "N.C."

    if parsed.blank_head:
        return raw if raw.startswith("/") else f"/{raw.lstrip('/')}"

    slash = raw.find("/")
    head = raw[:slash] if slash >= 0 else raw
    tail = raw[slash:] if slash >= 0 else ""

    head = _apply_quality_styles(head, prefs)
    return head + tail


def _apply_quality_styles(head: str, prefs: Prefs) -> str:
    h = head
    if prefs.maj7_style == "delta":
        h = re.sub(r"maj13", "Δ13", h, flags=re.I)
        h = re.sub(r"maj9", "Δ9", h, flags=re.I)
        h = re.sub(r"maj7", "Δ7", h, flags=re.I)
        h = re.sub(r"MA7", "Δ7", h, flags=re.I)
    elif prefs.maj7_style == "MA7":
        h = re.sub(r"maj7", "MA7", h, flags=re.I)

    if prefs.dim_style == "circle":
        h = re.sub(r"dim7", "°7", h, flags=re.I)
        h = re.sub(r"dim", "°", h, flags=re.I)
    elif prefs.dim_style == "dim":
        h = re.sub(r"dim7", "dim7", h, flags=re.I)

    if prefs.half_dim_style == "oslash":
        h = re.sub(r"m7b5", "ø7", h, flags=re.I)
    elif prefs.half_dim_style == "m7b5":
        h = re.sub(r"m7b5", "m7b5", h, flags=re.I)

    h = re.sub(r"aug", "+", h, flags=re.I)
    return h


def chord_to_html(chord: str, prefs: Prefs) -> str:
    parsed = parse_chord_token(chord)
    display = format_chord_display(chord, prefs)

    if parsed.blank_head and display.startswith("/"):
        bass_html = f'<span class="cs-chord cs-blank-bass">{html.escape(display)}</span>'
        return _wrap_chord(bass_html, parsed)

    if not display or display == "%":
        return ""
    if display == "N.C.":
        return '<span class="cs-nc">N.C.</span>'

    m = ROOT.match(display)
    if not m:
        inner = f'<span class="cs-chord">{html.escape(display)}</span>'
        return _wrap_chord(inner, parsed)

    root, acc, qual = m.group(1), m.group(2), m.group(3)
    acc_html = ""
    if acc == "#":
        acc_html = '<span class="cs-acc">♯</span>'
    elif acc == "b":
        acc_html = '<span class="cs-acc">♭</span>'

    qual_html = f'<span class="cs-qual">{html.escape(qual)}</span>' if qual else ""
    inner = (
        f'<span class="cs-chord">'
        f'<span class="cs-root">{root}</span>{acc_html}{qual_html}'
        f"</span>"
    )
    return _wrap_chord(inner, parsed)


def _wrap_chord(inner: str, parsed) -> str:
    parts = []
    if parsed.optional:
        parts.append('<span class="cs-paren">(</span>')
    parts.append(inner)
    if parsed.strokes:
        parts.append(f'<span class="cs-strokes">{"," * parsed.strokes}</span>')
    if parsed.optional:
        parts.append('<span class="cs-paren">)</span>')
    if parsed.note:
        parts.append(f'<span class="cs-chord-note">{html.escape(parsed.note)}</span>')
    return "".join(parts)
