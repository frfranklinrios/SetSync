"""Formatação visual de símbolos de acordes."""

from __future__ import annotations

import html
import re

from chordsheet.chord_token import parse_chord_token
from chordsheet.notation_style import effective_quality_prefs, uses_smufl
from chordsheet.prefs import Prefs
from chordsheet.smufl_chord import display_to_smufl
from util import to_brazilian_chord_notation

ROOT = re.compile(
    r"^([A-G])([#b]?)(.*)$",
    re.IGNORECASE,
)

# Cifra BR com hífen: A- → Am, G-7 → Gm7 (comum em cifras importadas)
_MINUS_MINOR = re.compile(r"^([A-G][#b]?)-(\d*)(.*)$", re.IGNORECASE)


def _br_minus_minor_to_m(chord: str) -> str:
    m = _MINUS_MINOR.match((chord or "").strip())
    if not m:
        return chord
    root, digits, tail = m.group(1), m.group(2), m.group(3)
    if tail and not tail.startswith("/"):
        return chord
    return f"{root}m{digits}{tail}"


def format_chord_display(chord: str, prefs: Prefs) -> str:
    parsed = parse_chord_token(chord)
    raw = parsed.text
    if not raw or raw in ("%", "NC", "N.C."):
        return raw.replace("N.C.", "N.C.") if raw else raw
    if raw.upper() in ("NC", "N.C."):
        return "N.C."

    if parsed.blank_head:
        return raw if raw.startswith("/") else f"/{raw.lstrip('/')}"

    if prefs.notation_style == "br":
        out = to_brazilian_chord_notation(raw)
        out = re.sub(r"ø7", "m7b5", out, flags=re.I)
        out = re.sub(r"Δ(\d*)", lambda m: f"{m.group(1) or '7'}+", out)
        slash = out.find("/")
        if slash >= 0:
            head, tail = out[:slash], out[slash:]
            return _br_minus_minor_to_m(head) + tail
        return _br_minus_minor_to_m(out)

    slash = raw.find("/")
    head = raw[:slash] if slash >= 0 else raw
    tail = raw[slash:] if slash >= 0 else ""

    head = _apply_quality_styles(head, prefs)
    return head + tail


def _apply_quality_styles(head: str, prefs: Prefs) -> str:
    maj7_style, dim_style, half_dim_style = effective_quality_prefs(prefs)
    h = head
    if maj7_style == "delta":
        h = re.sub(r"maj13", "Δ13", h, flags=re.I)
        h = re.sub(r"maj9", "Δ9", h, flags=re.I)
        h = re.sub(r"maj7", "Δ7", h, flags=re.I)
        h = re.sub(r"MA7", "Δ7", h, flags=re.I)
    elif maj7_style == "MA7":
        h = re.sub(r"maj7", "MA7", h, flags=re.I)

    if dim_style == "circle":
        h = re.sub(r"dim7", "°7", h, flags=re.I)
        h = re.sub(r"dim", "°", h, flags=re.I)
    elif dim_style == "dim":
        h = re.sub(r"dim7", "dim7", h, flags=re.I)

    if half_dim_style == "oslash":
        h = re.sub(r"m7b5", "ø7", h, flags=re.I)
    elif half_dim_style == "m7b5":
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
        css = "cs-chord cs-smufl" if uses_smufl(prefs) else "cs-chord"
        inner = f'<span class="{css}">{html.escape(display)}</span>'
        return _wrap_chord(inner, parsed)

    if uses_smufl(prefs):
        inner = f'<span class="cs-chord cs-smufl">{display_to_smufl(display)}</span>'
    else:
        inner = f'<span class="cs-chord">{html.escape(display)}</span>'
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
