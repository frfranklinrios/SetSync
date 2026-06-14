"""Renderização HTML da cifra."""

from __future__ import annotations

import html
import re
from chordsheet.format_chord import chord_to_html
from chordsheet.parser import Bar, Chart

NAV_HTML = {
    "$": '<span class="cs-nav-glyph" aria-label="Segno">𝄋</span>',
    "o": '<span class="cs-nav-glyph" aria-label="Coda">𝄌</span>',
    "O": '<span class="cs-nav-glyph" aria-label="Coda">𝄍</span>',
    "fine": '<span class="cs-nav-glyph" aria-label="Fine">𝄑</span> fine',
}

VOLTA_NUM = re.compile(r"^(\d+)")


def _volta_number(volta: str) -> int | None:
    m = VOLTA_NUM.match(volta or "")
    return int(m.group(1)) if m else None


def _volta_slot_html(volta: str) -> str:
    inner = f'<span class="cs-volta">{html.escape(volta)}</span>' if volta else ""
    return f'<span class="cs-volta-slot">{inner}</span>'


def _phantom_bar_html() -> str:
    return (
        f'<div class="cs-bar-cell cs-bar-phantom" aria-hidden="true">'
        f'<div class="cs-bar">{_volta_slot_html("")}</div></div>'
    )


def _is_indent_spacer_bar(bar: Bar) -> bool:
    """Compasso gerado por X no início da linha (indentação de 2ª volta)."""
    return bar.indent > 0 and not bar.volta and bar.chords in (["%"], [""])


def _strip_leading_indent_simile(chunk: list[Bar]) -> list[Bar]:
    """X no início da linha: não ocupa coluna (alinha 2. com 1.)."""
    out = list(chunk)
    while out and _is_indent_spacer_bar(out[0]):
        out.pop(0)
    return out


def _row_volta_layout(
    chunk: list[Bar], last_volta_col: int | None
) -> tuple[list[Bar], int, int | None]:
    """Retorna chunk ajustado, phantoms à esquerda e coluna da 1ª volta."""
    chunk = _strip_leading_indent_simile(chunk)
    leading_phantoms = 0
    new_last_col = last_volta_col

    first_volta_i = next((j for j, b in enumerate(chunk) if b.volta), None)
    if first_volta_i is not None:
        bar = chunk[first_volta_i]
        n = _volta_number(bar.volta)
        if n == 1:
            new_last_col = leading_phantoms + first_volta_i
        elif n is not None and n >= 2 and last_volta_col is not None:
            target = last_volta_col
            leading_phantoms = max(0, target - first_volta_i)

    return chunk, leading_phantoms, new_last_col


def _running_header(chart: Chart) -> str:
    m = chart.meta
    key_label = html.escape(f"tom de {m.key}") if m.key else ""
    bpm = html.escape(f"♩={m.bpm}") if m.bpm else ""
    title = html.escape(m.title or "")
    time_sig = _time_sig_html(m.time_signature or "4/4", "cs-running-ts")
    return (
        '<div class="cs-running-header">'
        f'<div class="cs-running-top">'
        f'<span class="cs-running-key">{key_label}</span>'
        f'<span class="cs-running-bpm">{bpm}</span>'
        f"</div>"
        f'<div class="cs-running-title-row">'
        f"{time_sig}"
        f'<span class="cs-running-title">{title}</span>'
        f'<span class="cs-running-artist-spacer" aria-hidden="true"></span>'
        f"</div>"
        "</div>"
    )


def _time_sig_html(time_signature: str, css_class: str = "cs-header-ts") -> str:
    if not time_signature:
        return ""
    num, _, den = time_signature.partition("/")
    return (
        f'<span class="cs-ts-stack {css_class}" '
        f'aria-label="Compasso {html.escape(time_signature)}">'
        f'<span class="cs-ts-num">{html.escape(num or "4")}</span>'
        f'<span class="cs-ts-beam" aria-hidden="true"></span>'
        f'<span class="cs-ts-den">{html.escape(den or "4")}</span>'
        f"</span>"
    )


def _beat_count(chart: Chart, bar: Bar) -> int:
    ts = bar.bar_time_signature or chart.meta.time_signature or "4/4"
    num, _, _ = ts.partition("/")
    try:
        return max(1, int(num.strip() or 4))
    except ValueError:
        return 4


def _semi_pulse_slot_html(chord: str, prefs) -> str:
    if chord in ("*", "", "%"):
        return '<span class="cs-semi"><span class="cs-empty">·</span></span>'
    ch = chord_to_html(chord, prefs)
    if not ch:
        return '<span class="cs-semi"><span class="cs-empty">·</span></span>'
    return f'<span class="cs-semi"><span class="cs-slot">{ch}</span></span>'


def _render_full_semi_pulse_bar(semi_chords: list[str], prefs) -> tuple[str, str]:
    """Compasso só com semi-pulsos (ex.: C&D) — metade do compasso por acorde."""
    inner = "".join(_semi_pulse_slot_html(c, prefs) for c in semi_chords)
    return inner, "cs-chords-semi-bar"


def _last_active_beat(grid: list[list[str]]) -> int:
    for i in range(len(grid) - 1, -1, -1):
        if any(c not in ("*", "", "%") for c in grid[i]):
            return i + 1
    return 0


def _render_beat_cell(col: int, beat_chords: list[str], prefs) -> str:
    """Renderiza uma coluna de pulso (inteiro ou subdividido em semi-pulsos)."""
    if len(beat_chords) == 1:
        c = beat_chords[0]
        if c in ("*", "", "%"):
            inner = '<span class="cs-empty">·</span>'
        else:
            ch = chord_to_html(c, prefs)
            inner = f'<span class="cs-slot">{ch}</span>' if ch else '<span class="cs-empty">·</span>'
        return f'<span class="cs-beat" style="grid-column:{col}">{inner}</span>'

    subs: list[str] = []
    for c in beat_chords:
        if c in ("*", "", "%"):
            subs.append('<span class="cs-sub"><span class="cs-empty">·</span></span>')
        else:
            ch = chord_to_html(c, prefs)
            if ch:
                subs.append(f'<span class="cs-sub"><span class="cs-slot">{ch}</span></span>')
            else:
                subs.append('<span class="cs-sub"><span class="cs-empty">·</span></span>')
    return (
        f'<span class="cs-beat cs-beat--split" style="grid-column:{col}">'
        f'{"".join(subs)}</span>'
    )


def _render_beat_grid(beats: int, grid: list[list[str]], prefs) -> str:
    """Distribui pulsos (e semi-pulsos) nas colunas do compasso."""
    has_semi = any(len(b) > 1 for b in grid)
    if has_semi:
        display_beats = max(_last_active_beat(grid), 1)
    else:
        display_beats = beats
    parts = []
    for j in range(1, display_beats + 1):
        beat_idx = j - 1
        if beat_idx < len(grid):
            parts.append(_render_beat_cell(j, grid[beat_idx], prefs))
        else:
            parts.append(
                f'<span class="cs-beat" style="grid-column:{j}">'
                f'<span class="cs-empty">·</span></span>'
            )
    return "".join(parts), "cs-chords-beats"


def _render_chords_content(bar: Bar, chart: Chart) -> tuple[str, str]:
    """Distribui acordes nas colunas de tempo do compasso."""
    beats = _beat_count(chart, bar)

    if bar.is_empty:
        inner = "".join(
            f'<span class="cs-beat" style="grid-column:{j}"><span class="cs-empty">·</span></span>'
            for j in range(1, beats + 1)
        )
        return inner, "cs-chords-beats"

    if bar.simile or (len(bar.chords) == 1 and bar.chords[0] in ("%",)):
        span = max(1, int(bar.simile_span or 1))
        if span <= 1:
            return (
                '<span class="cs-simile cs-simile--1">%</span>',
                "cs-align-center",
            )
        return (
            f'<span class="cs-simile cs-simile--x{span}">'
            f'<span class="cs-simile-num">{span}</span>'
            f'<span class="cs-simile-slash">/</span>'
            f'<span class="cs-simile-dots" aria-hidden="true"><span></span><span></span></span>'
            f"</span>",
            "cs-align-center",
        )

    grid = bar.get_pulse_grid()
    if len(grid) == 1 and len(grid[0]) > 1:
        return _render_full_semi_pulse_bar(grid[0], chart.prefs)
    multi_beat = len(grid) > 1 or any(len(b) > 1 for b in grid)
    if multi_beat:
        return _render_beat_grid(beats, grid, chart.prefs)

    ch = chord_to_html(bar.chords[0] if bar.chords else "", chart.prefs)
    if not ch:
        inner = "".join(
            f'<span class="cs-beat" style="grid-column:{j}"><span class="cs-empty">·</span></span>'
            for j in range(1, beats + 1)
        )
        return inner, "cs-chords-beats"

    # Um acorde por compasso: centralizado, sem pontos de pulso vazios
    return ch, "cs-align-center"


def _align_class(bar: Bar, prefs) -> str:
    slots = bar.display_slots()
    if prefs.align_chords == "center":
        return "cs-align-center"
    if prefs.align_chords == "left":
        return "cs-align-left"
    return "cs-align-center" if slots <= 1 else "cs-align-left"


def _repeat_dots() -> str:
    return '<span class="cs-bl-dots" aria-hidden="true"><span></span><span></span></span>'


def _barline_html(side: str, kind: str) -> str:
    if kind == "repeat-start":
        return (
            f'<div class="cs-barline cs-barline-{side} cs-bl-repeat-start" aria-hidden="true">'
            '<span class="cs-bl-bar cs-bl-thick"></span>'
            '<span class="cs-bl-bar cs-bl-thin"></span>'
            f"{_repeat_dots()}</div>"
        )
    if kind == "repeat-end":
        return (
            f'<div class="cs-barline cs-barline-{side} cs-bl-repeat-end" aria-hidden="true">'
            f"{_repeat_dots()}"
            '<span class="cs-bl-bar cs-bl-thin"></span>'
            '<span class="cs-bl-bar cs-bl-thick"></span></div>'
        )
    if kind == "final":
        return (
            f'<div class="cs-barline cs-barline-{side} cs-bl-final" aria-hidden="true">'
            '<span class="cs-bl-bar cs-bl-thin"></span>'
            '<span class="cs-bl-bar cs-bl-thick"></span></div>'
        )
    return f'<div class="cs-barline cs-barline-{side} cs-bl-{kind}" aria-hidden="true"></div>'


def _prepare_chunk_barlines(chunk: list[Bar]) -> list[Bar]:
    """Evita || duplicado entre compassos (fecha + abre na mesma fronteira)."""
    bars = [b.clone() for b in chunk]
    for j in range(1, len(bars)):
        if bars[j - 1].line_right == "double" and bars[j].line_left == "double":
            bars[j - 1].line_right = "single"
    return bars


def _render_nav(bar: Bar) -> str:
    label = NAV_HTML.get(bar.nav, html.escape(bar.nav))
    return f'<div class="cs-nav-row"><div class="cs-nav-marker">{label}</div></div>'


def _annotation_is_section_label(text: str) -> bool:
    t = text.strip()
    if not t or len(t) > 40 or "  " in t:
        return False
    lowered = t.lower()
    if lowered.startswith(
        ("simile", "empty", "optional", "strokes", "blank", "annotation", "4 bars", "linha", "- ")
    ):
        return False
    return True


def _render_annotation(bar: Bar) -> str:
    if bar.blank_spacer:
        return '<div class="cs-blank-spacer" aria-hidden="true"></div>'
    if bar.annotation_literal:
        text = html.escape(bar.annotation)
        return f'<div class="cs-literal">{text}</div>'
    if "  " in bar.annotation:
        cols = [c for c in re.split(r"  +", bar.annotation) if c]
        cols_html = "".join(f'<span class="cs-col">{html.escape(c)}</span>' for c in cols)
        return f'<div class="cs-annotation cs-cols-3">{cols_html}</div>'
    if _annotation_is_section_label(bar.annotation):
        return f'<div class="cs-section"><span>{html.escape(bar.annotation.strip())}</span></div>'
    return f'<div class="cs-annotation">{html.escape(bar.annotation)}</div>'


def _show_left_barline(bar: Bar, is_first_in_chunk: bool) -> bool:
    """Uma linha por fronteira — evita || duplo entre compassos adjacentes."""
    if bar.line_left in ("repeat-start", "double"):
        return True
    return is_first_in_chunk


def _render_bar(bar: Bar, chart: Chart, *, is_first_in_chunk: bool = True) -> str:
    if bar.nav:
        return _render_nav(bar)
    if bar.annotation or bar.blank_spacer:
        return _render_annotation(bar)

    indent = max(0, bar.indent)
    beats = _beat_count(chart, bar)
    inner, beat_align = _render_chords_content(bar, chart)
    align = (
        beat_align
        if beat_align in ("cs-chords-beats", "cs-chords-semi-bar")
        else _align_class(bar, chart.prefs)
    )

    volta_slot = _volta_slot_html(bar.volta)

    bar_ts = ""
    if bar.bar_time_signature:
        bar_ts = _time_sig_html(bar.bar_time_signature, "cs-bar-ts")

    float_lbl = ""
    if bar.floating_label:
        float_lbl = f'<span class="cs-float-label">{html.escape(bar.floating_label)}</span>'

    left = (
        _barline_html("start", bar.line_left)
        if _show_left_barline(bar, is_first_in_chunk)
        else ""
    )
    if bar.line_right in ("repeat-end", "double", "final"):
        right = _barline_html("end", bar.line_right)
    else:
        right = _barline_html("end", "single")

    repeat_lbl = ""
    if bar.repeat_times and bar.repeat_times > 1:
        repeat_lbl = (
            f'<span class="cs-repeat-count" aria-label="Repetir {bar.repeat_times} vezes">'
            f"×{bar.repeat_times}</span>"
        )

    col_span = bar.column_slots()
    span_attr = f' data-col-span="{col_span}"' if col_span > 1 else ""

    return (
        f'<div class="cs-bar-cell"{span_attr}>'
        f'<div class="cs-bar" style="--cs-indent:{indent};--cs-beats:{beats}">'
        f"{volta_slot}{float_lbl}{bar_ts}{left}"
        f'<div class="cs-chords {align}">{inner}</div>'
        f"{right}</div>{repeat_lbl}</div>"
    )


def _section_label_at(sections: list[tuple[int, str]], index: int) -> str:
    for i, title in sections:
        if i == index:
            return f'<div class="cs-section"><span>{html.escape(title)}</span></div>'
    return ""


def _section_start_indices(sections: list[tuple[int, str]]) -> set[int]:
    return {i for i, _ in sections}


def _is_new_section_row(sections: list[tuple[int, str]], index: int) -> bool:
    if not sections:
        return False
    first_index = sections[0][0]
    return any(i == index for i, _ in sections) and index != first_index


def render_chart_html(chart: Chart) -> str:
    m = chart.meta
    p = chart.prefs
    if p.bar_line_style == "grille":
        per_row = max(4, min(8, int(p.bars_per_row)))
    else:
        per_row = 4

    title = html.escape(m.title or "Sem título")
    artist = html.escape(m.artist.upper()) if m.artist else ""
    key_label = html.escape(f"tom de {m.key}") if m.key else ""
    bpm = html.escape(f"♩={m.bpm}") if m.bpm else ""
    subtitle = html.escape(m.style) if m.style else ""
    subtitle = html.escape(subtitle) if subtitle else ""

    time_sig = _time_sig_html(m.time_signature or "4/4")
    header = f"""
    <header class="cs-header">
      <div class="cs-meta-top">
        <span class="cs-key">{key_label}</span>
        <span class="cs-bpm">{bpm}</span>
      </div>
      <div class="cs-title-row">
        {time_sig}
        <h1 class="cs-title">{title}</h1>
        {f'<div class="cs-artist">{artist}</div>' if artist else '<div class="cs-artist"></div>'}
      </div>
      {f'<div class="cs-sub">{subtitle}</div>' if subtitle else ''}
      <div class="cs-rule"></div>
    </header>"""

    rows_html: list[str] = []
    last_volta_col: int | None = None
    section_starts = _section_start_indices(chart.sections)
    line_break_starts = set(chart.line_breaks)
    i = 0
    while i < len(chart.bars):
        if i in chart.page_breaks:
            rows_html.append('<div class="cs-page-break"></div>')
            rows_html.append(_running_header(chart))

        bar = chart.bars[i]
        if bar.is_full_width:
            sec = _section_label_at(chart.sections, i)
            rows_html.append(
                f'<div class="cs-row cs-row-full">{sec}{_render_bar(bar, chart, is_first_in_chunk=True)}</div>'
            )
            i += 1
            continue

        sec = _section_label_at(chart.sections, i)
        section_row = " cs-row-section-start" if _is_new_section_row(chart.sections, i) else ""
        chunk: list[Bar] = []
        slots_used = 0
        while i < len(chart.bars):
            b = chart.bars[i]
            if b.is_full_width:
                break
            if chunk and i in line_break_starts:
                break
            if chunk and i in section_starts:
                break
            need = b.column_slots()
            if chunk and slots_used + need > per_row:
                break
            chunk.append(b)
            slots_used += need
            i += 1
            if slots_used >= per_row:
                break

        chunk = _prepare_chunk_barlines(chunk)
        chunk, leading_phantoms, last_volta_col = _row_volta_layout(chunk, last_volta_col)
        chunk_slots = sum(b.column_slots() for b in chunk)
        trailing_phantoms = max(0, per_row - leading_phantoms - chunk_slots)
        bars_html = (
            _phantom_bar_html() * leading_phantoms
            + "".join(_render_bar(b, chart, is_first_in_chunk=(j == 0)) for j, b in enumerate(chunk))
            + _phantom_bar_html() * trailing_phantoms
        )
        rows_html.append(
            f'<div class="cs-row{section_row}">{sec}'
            f'<div class="cs-row-bars" style="--cs-bars-per-row:{per_row}">{bars_html}</div></div>'
        )

    footer = ""
    print_margin_css = ""
    if p.show_footer:
        from config import app_now

        today = app_now().strftime("%d/%m/%Y")
        footer = f"""
        <footer class="cs-footer" aria-hidden="true">
          <span class="cs-footer-brand">SetSync</span>
          <span class="cs-page-count"></span>
          <span class="cs-footer-date">editado em {today}</span>
        </footer>"""
        print_margin_css = f"""
        <style class="cs-print-margins">@media print {{
          @page {{
            @bottom-left {{
              content: "SetSync";
              font-family: Inter, system-ui, sans-serif;
              font-size: 7pt;
              color: #a8a29e;
            }}
            @bottom-center {{
              content: "página " counter(page) " de " counter(pages);
              font-family: Inter, system-ui, sans-serif;
              font-size: 7pt;
              color: #a8a29e;
            }}
            @bottom-right {{
              content: "editado em {today}";
              font-family: Inter, system-ui, sans-serif;
              font-size: 7pt;
              color: #a8a29e;
            }}
          }}
        }}</style>"""

    chart_style = (
        f' style="--cs-bars-per-row:{per_row};--cs-tab-lines:{max(3, min(8, int(p.tab_lines)))}"'
    )
    return (
        f'<article class="{p.css_classes()}"{chart_style}>'
        f"{print_margin_css}{header}<div class=\"cs-body\">{''.join(rows_html)}</div>{footer}</article>"
    )
