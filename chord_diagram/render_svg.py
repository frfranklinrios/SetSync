"""Renderização SVG server-side do braço e do piano."""

from __future__ import annotations

import html
from typing import Sequence

from chord_diagram.instruments import InstrumentSpec, get_instrument
from chord_diagram.voicing import detect_barres

LAYOUT = {
    'col_gap': 34,
    'row_gap': 36,
    'margin_x': 28,
    'margin_y': 30,
    'dot_r': 8.5,
    'root_dot_r': 9.5,
    'barre_h': 10,
    'open_r': 5.5,
    'mute_s': 5,
    'rows': 5,
}

SVG_STYLE = """
.board{fill:#f7f3ed;stroke:#e8e0d4;stroke-width:1}
.string{stroke:#8a7f72;stroke-linecap:round;opacity:.88}
.fret{stroke:#c4b8a8;stroke-width:1.2;stroke-linecap:round}
.nut{stroke:#3d3832;stroke-width:4.5;stroke-linecap:round}
.dot{fill:#2ab5a0;stroke:rgba(255,255,255,.35);stroke-width:1}
.dot-root{fill:#1f9a88;stroke:#fff;stroke-width:2.2}
.barre{fill:#3d3832;opacity:.82}
.open{fill:none;stroke:#3d3832;stroke-width:2}
.mute{stroke:#3d3832;stroke-width:2.2;stroke-linecap:round}
.lbl{fill:#fff;font:700 9.5px system-ui,sans-serif;text-anchor:middle;dominant-baseline:middle}
.title{font:600 14px system-ui,sans-serif}
"""


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _compute_window(frets: Sequence, rows: int = 5) -> tuple[int, int]:
    nums = [f for f in frets if isinstance(f, int) and f > 0]
    has_open = any(f == 0 for f in frets)
    if not nums:
        return 0, rows
    lo, hi = min(nums), max(nums)
    start = 0 if has_open else lo
    if not has_open and hi - start + 1 > rows:
        start = max(1, hi - rows + 1)
    if not has_open and lo < start:
        start = lo
    return start, rows


def _string_x(margin_x: int, col_gap: int, si: int) -> float:
    return margin_x + si * col_gap


def _fret_y(margin_y: int, row_gap: int, fret: int, start_fret: int) -> float:
    if fret == 0 and start_fret == 0:
        return margin_y - 12
    return margin_y + (fret - start_fret - 0.5) * row_gap


def _barre_pill(x1: float, x2: float, y: float, h: float) -> str:
    left = min(x1, x2) - h / 2
    w = abs(x2 - x1) + h
    return f'<rect class="barre" x="{left}" y="{y - h/2}" width="{w}" height="{h}" rx="{h/2}"/>'


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
    pad_x = 10
    board_w = (n - 1) * cg
    board_h = rows * rg
    svg_w = mx * 2 + board_w
    svg_h = my + board_h + 40
    top_y = my - 12

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" role="img">',
        '<defs><filter id="dot-shadow" x="-40%" y="-40%" width="180%" height="180%">',
        '<feDropShadow dx="0" dy="1.2" stdDeviation="1.1" flood-opacity="0.22"/></filter></defs>',
        f'<style>{SVG_STYLE}</style>',
    ]
    if title:
        parts.append(f'<text class="title" x="{mx}" y="16">{_esc(title)}</text>')

    parts.append(
        f'<rect class="board" x="{mx - pad_x}" y="{my - 6}" '
        f'width="{board_w + pad_x * 2}" height="{board_h + 12}" rx="6"/>'
    )

    y0 = my
    for row in range(rows + 1):
        y = y0 + row * rg
        cls = 'nut' if start == 0 and row == 0 else 'fret'
        parts.append(
            f'<line class="{cls}" x1="{mx - pad_x + 2}" y1="{y}" '
            f'x2="{mx + board_w + pad_x - 2}" y2="{y}"/>'
        )

    for si in range(n):
        x = _string_x(mx, cg, si)
        thick = 1 + (n - 1 - si) * 0.22
        parts.append(
            f'<line class="string" x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + board_h}" '
            f'style="stroke-width:{thick:.2f}"/>'
        )

    if start > 0:
        parts.append(f'<text class="title" x="{mx - 14}" y="{y0 + rg/2}" style="font-size:12px">{start}</text>')

    barres = detect_barres(list(frets))
    for b in barres:
        yb = _fret_y(y0, rg, b['fret'], start)
        x1 = _string_x(mx, cg, b['startString'] - 1)
        x2 = _string_x(mx, cg, b['endString'] - 1)
        parts.append(_barre_pill(x1, x2, yb, LAYOUT['barre_h']))

    for si, f in enumerate(frets):
        x = _string_x(mx, cg, si)
        s = LAYOUT['mute_s']
        if f == 'x' or f == 'X':
            parts.append(
                f'<g class="mute"><line x1="{x-s}" y1="{top_y-s}" x2="{x+s}" y2="{top_y+s}"/>'
                f'<line x1="{x+s}" y1="{top_y-s}" x2="{x-s}" y2="{top_y+s}"/></g>'
            )
        elif f == 0 and start == 0:
            parts.append(f'<circle class="open" cx="{x}" cy="{top_y}" r="{LAYOUT["open_r"]}"/>')

    root_si = n - 1
    for si, f in enumerate(frets):
        if f in ('x', 'X') or (f == 0 and start == 0):
            continue
        if not isinstance(f, int) or f <= 0:
            continue
        cy = _fret_y(y0, rg, f, start)
        if cy < y0 or cy > y0 + board_h:
            continue
        x = _string_x(mx, cg, si)
        cls = 'dot-root' if si == root_si else 'dot'
        r = LAYOUT['root_dot_r'] if cls == 'dot-root' else LAYOUT['dot_r']
        parts.append(f'<circle class="{cls}" cx="{x}" cy="{cy}" r="{r}" filter="url(#dot-shadow)"/>')
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
