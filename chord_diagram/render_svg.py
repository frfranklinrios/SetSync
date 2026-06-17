"""Renderização SVG server-side do braço e do piano."""

from __future__ import annotations

import html
from typing import Sequence

from chord_diagram.instruments import InstrumentSpec, get_instrument
from chord_diagram.voicing import detect_barres

LAYOUT = {
    'col_gap': 36,
    'row_gap': 40,
    'margin_x': 24,
    'margin_y': 26,
    'dot_r': 9,
    'rows': 5,
}


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _compute_window(frets: Sequence, rows: int = 5) -> tuple[int, int]:
    nums = [f for f in frets if isinstance(f, int) and f > 0]
    if not nums:
        return 0, rows
    lo, hi = min(nums), max(nums)
    if hi <= rows:
        return 0, rows
    start = max(0, lo - 1)
    return start, rows


def _string_x(margin_x: int, col_gap: int, si: int, n_strings: int) -> float:
    return margin_x + si * col_gap


def _fret_y(margin_y: int, row_gap: int, fret: int, start_fret: int) -> float:
    if fret == 0:
        return margin_y - 8
    return margin_y + (fret - start_fret - 0.5) * row_gap


def render_fretboard_svg(
    spec: InstrumentSpec,
    frets: list,
    *,
    fingers: list[int] | None = None,
    title: str = '',
    label_mode: str = 'fingers',
) -> str:
    n = spec.strings
    start, rows = _compute_window(frets, LAYOUT['rows'])
    mx, my = LAYOUT['margin_x'], LAYOUT['margin_y']
    cg, rg = LAYOUT['col_gap'], LAYOUT['row_gap']
    board_h = rows * rg
    svg_w = mx * 2 + (n - 1) * cg
    svg_h = my + board_h + 40

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" role="img">',
        '<style>',
        '.nut{stroke:#333;stroke-width:4}',
        '.fret{stroke:#999;stroke-width:1}',
        '.string{stroke:#666;stroke-width:1}',
        '.dot{fill:#87deb8}',
        '.dot-root{fill:#5bc49a}',
        '.barre{stroke:#444;stroke-width:9;stroke-linecap:round}',
        '.lbl{font:11px sans-serif;text-anchor:middle;dominant-baseline:middle}',
        '.title{font:14px sans-serif;font-weight:600}',
        '</style>',
    ]
    if title:
        parts.append(f'<text class="title" x="{mx}" y="16">{_esc(title)}</text>')

    y0 = my
    for si in range(n):
        x = _string_x(mx, cg, si, n)
        parts.append(f'<line class="string" x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + board_h}"/>')

    for row in range(rows + 1):
        y = y0 + row * rg
        cls = 'nut' if start == 0 and row == 0 else 'fret'
        sw = 4 if cls == 'nut' else 1
        parts.append(f'<line class="{cls}" x1="{mx - 8}" y1="{y}" x2="{mx + (n-1)*cg + 8}" y2="{y}" stroke-width="{sw}"/>')

    if start > 0:
        parts.append(f'<text class="lbl" x="{mx - 14}" y="{y0 + rg/2}">{start}</text>')

    barres = detect_barres(list(frets))
    for b in barres:
        yb = _fret_y(y0, rg, b['fret'], start)
        x1 = _string_x(mx, cg, b['startString'] - 1, n)
        x2 = _string_x(mx, cg, b['endString'] - 1, n)
        parts.append(f'<line class="barre" x1="{x1}" y1="{yb}" x2="{x2}" y2="{yb}"/>')

    top_y = y0 - 14
    for si, f in enumerate(frets):
        x = _string_x(mx, cg, si, n)
        if f == 'x' or f == 'X':
            parts.append(f'<text class="lbl" x="{x}" y="{top_y}">×</text>')
        elif f == 0 and start == 0:
            parts.append(f'<text class="lbl" x="{x}" y="{top_y}">○</text>')

    for si, f in enumerate(frets):
        if f in ('x', 'X'):
            continue
        if f == 0 and start == 0:
            cy = top_y + 4
            r = 6
        elif isinstance(f, int) and f > 0:
            cy = _fret_y(y0, rg, f, start)
            r = LAYOUT['dot_r']
            if cy < y0 or cy > y0 + board_h:
                continue
        else:
            continue
        x = _string_x(mx, cg, si, n)
        cls = 'dot-root' if si == len(frets) - 1 else 'dot'
        parts.append(f'<circle class="{cls}" cx="{x}" cy="{cy}" r="{r}"/>')
        if fingers and label_mode == 'fingers' and fingers[si]:
            parts.append(f'<text class="lbl" x="{x}" y="{cy}">{fingers[si]}</text>')

    parts.append('</svg>')
    return ''.join(parts)


def render_piano_svg(
    key_mappings: list[dict],
    *,
    start_midi: int = 48,
    key_count: int = 24,
) -> str:
    nw, nh = 28, 120
    bw, bh = 18, 72
    w = key_count * nw + 40
    h = nh + 40
    active = {k['midiId'] for k in key_mappings}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<style>.nat{fill:#fffff0;stroke:#333}.sh{fill:#36454f}.on{fill:#f33}</style>',
    ]
    ox = 20
    for i in range(key_count):
        midi = start_midi + i
        x = ox + i * nw
        cls = 'nat on' if midi in active else 'nat'
        parts.append(f'<rect class="{cls}" x="{x}" y="20" width="{nw-2}" height="{nh}"/>')
    # Teclas pretas simplificadas
    black_pos = {1, 3, 6, 8, 10}
    for i in range(key_count):
        pc = (start_midi + i) % 12
        if pc not in black_pos:
            continue
        midi = start_midi + i
        x = ox + i * nw + nw // 2 - bw // 2
        cls = 'sh on' if midi in active else 'sh'
        parts.append(f'<rect class="{cls}" x="{x}" y="20" width="{bw}" height="{bh}"/>')
    parts.append('</svg>')
    return ''.join(parts)
