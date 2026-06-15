"""Presets de estilo de notação de acordes no chord sheet."""

from __future__ import annotations

from chordsheet.prefs import Prefs

NOTATION_STYLES = frozenset({"br", "intl", "us"})

_PRESETS: dict[str, dict[str, object]] = {
    "br": {
        "label": "Brasil",
        "maj7_style": "maj7",
        "dim_style": "circle",
        "half_dim_style": "m7b5",
        "use_smufl": False,
        "use_brazilian": True,
    },
    "intl": {
        "label": "Internacional (jazz)",
        "maj7_style": "delta",
        "dim_style": "circle",
        "half_dim_style": "oslash",
        "use_smufl": True,
        "use_brazilian": False,
    },
    "us": {
        "label": "Americana",
        "maj7_style": "maj7",
        "dim_style": "dim",
        "half_dim_style": "m7b5",
        "use_smufl": False,
        "use_brazilian": False,
    },
}


def normalize_notation_style(value: str | None) -> str:
    style = (value or "br").strip().lower()
    return style if style in NOTATION_STYLES else "br"


def preset_for(style: str | None) -> dict[str, object]:
    return _PRESETS[normalize_notation_style(style)]


def uses_smufl(prefs: Prefs) -> bool:
    return bool(preset_for(prefs.notation_style)["use_smufl"])


def uses_brazilian(prefs: Prefs) -> bool:
    return bool(preset_for(prefs.notation_style)["use_brazilian"])


def effective_quality_prefs(prefs: Prefs) -> tuple[str, str, str]:
    """Retorna (maj7_style, dim_style, half_dim_style) conforme o preset."""
    style = normalize_notation_style(prefs.notation_style)
    if style == "intl":
        maj7 = prefs.maj7_style if prefs.maj7_style in ("delta", "MA7", "maj7") else "delta"
        dim = prefs.dim_style if prefs.dim_style in ("circle", "dim") else "circle"
        half = (
            prefs.half_dim_style
            if prefs.half_dim_style in ("oslash", "m7b5")
            else "oslash"
        )
        return maj7, dim, half
    preset = _PRESETS[style]
    return (
        str(preset["maj7_style"]),
        str(preset["dim_style"]),
        str(preset["half_dim_style"]),
    )
