"""Preferências de renderização (manual Chord Sheet Maker)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

BAR_LINE_STYLES = frozenset({"regular", "none", "grille", "trackline", "tab"})
NOTATION_STYLES = frozenset({"br", "intl", "us"})


@dataclass
class Prefs:
    bars_per_row: int = 4
    font_size: str = "M"  # M | S | XS
    line_spacing: str = "normal"  # compact | normal | relaxed
    align_chords: str = "auto"  # auto | left | center
    notation_style: str = "br"  # br | intl | us
    maj7_style: str = "delta"  # delta | MA7 | maj7
    dim_style: str = "circle"  # circle | dim
    half_dim_style: str = "oslash"  # oslash | m7b5
    show_footer: bool = True
    # https://www.chordsheet.com/manual/style
    bar_line_style: str = "tab"  # regular | none | grille | trackline | tab
    tab_lines: int = 6
    tab_show_barlines: bool = True

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "Prefs":
        base = cls()
        if not raw:
            return base
        for key in base.__dataclass_fields__:
            if key in raw and raw[key] is not None:
                setattr(base, key, raw[key])
        if raw and "notation_style" not in raw:
            if raw.get("half_dim_style") == "oslash" or raw.get("maj7_style") == "delta":
                base.notation_style = "intl"
        base.bars_per_row = max(1, min(8, int(base.bars_per_row)))
        if base.notation_style not in NOTATION_STYLES:
            base.notation_style = "br"
        if base.bar_line_style not in BAR_LINE_STYLES:
            base.bar_line_style = "tab"
        base.tab_lines = max(3, min(8, int(base.tab_lines)))
        base.tab_show_barlines = bool(base.tab_show_barlines)
        return base

    def css_classes(self) -> str:
        size = {"XS": "cs-size-xs", "S": "cs-size-s"}.get(self.font_size, "cs-size-m")
        spacing = {
            "compact": "cs-spacing-compact",
            "relaxed": "cs-spacing-relaxed",
        }.get(self.line_spacing, "cs-spacing-normal")
        bl = f"cs-bl-style-{self.bar_line_style}"
        extra = " cs-tab-no-barlines" if self.bar_line_style == "tab" and not self.tab_show_barlines else ""
        return f"cs-chart {size} {spacing} {bl}{extra}"
