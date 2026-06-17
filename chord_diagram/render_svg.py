"""Renderização SVG server-side do braço e do piano."""

from __future__ import annotations

import html
from typing import Sequence

from chord_diagram.instruments import InstrumentSpec, get_instrument
from chord_diagram.voicing import adapt_guitar_voicing_to_four_strings, detect_barres, string_on_barre

LAYOUT = {
    'col_gap': 32,
    'row_gap': 30,
    'margin_x': 46,
    'margin_y': 26,
    'dot_r': 12,
    'root_dot_r': 12,
    'barre_h': 26,
    'open_r': 7,
    'mute_s': 6.5,
    'rows': 5,
}

SVG_STYLE = """
.board{fill:rgba(0,0,0,.04);stroke:#e5e7eb;stroke-width:1}
.string{stroke:#6b7280;stroke-width:1.1;stroke-linecap:square;opacity:.9}
.fret{stroke:#e5e7eb;stroke-width:1.1;stroke-linecap:square;opacity:.95}
.nut{stroke:#1a1a1a;stroke-width:5;stroke-linecap:square}
.dot{fill:#2ab5a0;stroke:none}
.dot-root{fill:#1a9b8a;stroke:none}
.barre{fill:#2ab5a0;opacity:1;stroke:none}
.mark{fill:#1a1a1a;font:700 17px system-ui,sans-serif;text-anchor:middle;dominant-baseline:middle}
.finger{fill:#fff;font:700 13px system-ui,sans-serif;text-anchor:middle;dominant-baseline:middle}
.tuning{fill:#6b7280;font:600 14px system-ui,sans-serif;text-anchor:middle;opacity:.85}
.fret-side{fill:#6b7280;font:600 15px system-ui,sans-serif;text-anchor:end;dominant-baseline:middle}
.title{font:600 16px system-ui,sans-serif}
"""


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _tuning_labels(spec: InstrumentSpec) -> list[str]:
    return [p.rstrip('0123456789') for p in spec.tuning_pitches]


def _compute_window(frets: Sequence, rows: int = 5) -> tuple[int, int]:
    nums = [f for f in frets if isinstance(f, int) and f > 0]
    has_open = any(f == 0 for f in frets)
    if not nums:
        return 0, rows
    lo, hi = min(nums), max(nums)
    # Uma casa mais grave que a primeira nota (estilo Cifra Club)
    start = 0 if has_open else max(0, lo - 1)
    if not has_open and hi - start + 1 > rows:
        start = max(0, hi - rows + 1)
    return start, rows


def _string_x(margin_x: int, col_gap: int, si: int) -> float:
    return margin_x + si * col_gap


def _fret_y(margin_y: int, row_gap: int, fret: int, start_fret: int) -> float:
    if fret == 0 and start_fret == 0:
        return margin_y - 12
    if start_fret == 0:
        return margin_y + (fret - 0.5) * row_gap
    return margin_y + (fret - start_fret + 0.5) * row_gap


def _barre_pill(x1: float, x2: float, y: float, h: float) -> str:
    left = min(x1, x2) - h / 2
    w = abs(x2 - x1) + h
    return f'<rect class="barre" x="{left}" y="{y - h/2}" width="{w}" height="{h}" rx="{h/2}"/>'


def _barre_draw_range(bar: dict, frets: list, string_count: int) -> tuple[int, int] | None:
    from_s = max(0, bar['startString'] - 1)
    to_s = min(bar['endString'] - 1, string_count - 1)
    while from_s <= to_s and frets[from_s] in ('x', 'X'):
        from_s += 1
    while to_s >= from_s and frets[to_s] in ('x', 'X'):
        to_s -= 1
    if from_s >= to_s:
        return None
    return from_s, to_s


def _barre_finger_label(bar: dict, frets: list, fingers: list[int] | None) -> int:
    s0 = bar['startString'] - 1
    s1 = bar['endString'] - 1
    for si in range(s0, min(s1, len(frets) - 1) + 1):
        if frets[si] != bar['fret']:
            continue
        if fingers and si < len(fingers) and fingers[si] == 1:
            return 1
        if fingers and si < len(fingers) and fingers[si] > 0:
            return fingers[si]
    return 1


def render_fretboard_svg(
    spec: InstrumentSpec,
    frets: list,
    *,
    fingers: list[int] | None = None,
    title: str = '',
    label_mode: str = 'fingers',
) -> str:
    n = spec.strings
    if len(frets) == 6 and n == 4:
        adapted = adapt_guitar_voicing_to_four_strings({'frets': list(frets), 'fingers': fingers})
        frets = adapted['frets']
        fingers = adapted.get('fingers')
    frets = list(frets)[:n]
    if fingers:
        fingers = list(fingers)[:n]
    start, rows = _compute_window(frets, LAYOUT['rows'])
    mx, my = LAYOUT['margin_x'], LAYOUT['margin_y']
    cg, rg = LAYOUT['col_gap'], LAYOUT['row_gap']
    pad_x, pad_y = 8, 8
    board_w = (n - 1) * cg
    board_h = rows * rg
    svg_w = mx * 2 + board_w
    svg_h = my + board_h + 48
    top_y = my - 13

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}" role="img">',
        f'<style>{SVG_STYLE}</style>',
    ]
    if title:
        parts.append(f'<text class="title" x="{mx}" y="16">{_esc(title)}</text>')

    parts.append(
        f'<rect class="board" x="{mx - pad_x}" y="{my - pad_y}" '
        f'width="{board_w + pad_x * 2}" height="{board_h + pad_y * 2}" rx="10"/>'
    )

    y0 = my
    for row in range(rows + 1):
        y = y0 + row * rg
        cls = 'nut' if start == 0 and row == 0 else 'fret'
        parts.append(
            f'<line class="{cls}" x1="{mx - 2}" y1="{y}" '
            f'x2="{mx + board_w + 2}" y2="{y}"/>'
        )

    for si in range(n):
        x = _string_x(mx, cg, si)
        parts.append(
            f'<line class="string" x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + board_h}"/>'
        )

    for fr in range(rows):
        fret_num = fr + 1 if start == 0 else start + fr
        parts.append(
            f'<text class="fret-side" x="{mx - 18}" y="{y0 + fr * rg + rg / 2}">{fret_num}</text>'
        )

    barres = detect_barres(list(frets), fingers)
    for b in barres:
        span = _barre_draw_range(b, list(frets), n)
        if not span:
            continue
        yb = _fret_y(y0, rg, b['fret'], start)
        x1 = _string_x(mx, cg, span[0])
        x2 = _string_x(mx, cg, span[1])
        parts.append(_barre_pill(x1, x2, yb, LAYOUT['barre_h']))

    for si, f in enumerate(frets):
        x = _string_x(mx, cg, si)
        if f == 'x' or f == 'X':
            parts.append(f'<text class="mark" x="{x}" y="{top_y}">X</text>')
        elif f == 0 and start == 0:
            parts.append(f'<text class="mark" x="{x}" y="{top_y}">o</text>')

    for si, f in enumerate(frets):
        if string_on_barre(si, list(frets), barres):
            continue
        if f in ('x', 'X'):
            continue
        if f == 0 and start == 0:
            continue
        if not isinstance(f, int) or f <= 0:
            continue
        cy = _fret_y(y0, rg, f, start)
        if cy < y0 or cy > y0 + board_h:
            continue
        x = _string_x(mx, cg, si)
        parts.append(f'<circle class="dot" cx="{x}" cy="{cy}" r="{LAYOUT["dot_r"]}"/>')

    if fingers and label_mode == 'fingers':
        for b in barres:
            yb = _fret_y(y0, rg, b['fret'], start)
            if yb < y0 or yb > y0 + board_h:
                continue
            span = _barre_draw_range(b, list(frets), n)
            if not span:
                continue
            x1 = _string_x(mx, cg, span[0])
            x2 = _string_x(mx, cg, span[1])
            finger = _barre_finger_label(b, list(frets), fingers)
            parts.append(f'<text class="finger" x="{(x1 + x2) / 2}" y="{yb}">{finger}</text>')
        for si, f in enumerate(frets):
            if string_on_barre(si, list(frets), barres):
                continue
            if f in ('x', 'X'):
                continue
            if f == 0 and start == 0:
                continue
            if not isinstance(f, int) or f <= 0:
                continue
            finger = fingers[si] if si < len(fingers) else 0
            if not finger:
                continue
            cy = _fret_y(y0, rg, f, start)
            if cy < y0 or cy > y0 + board_h:
                continue
            x = _string_x(mx, cg, si)
            parts.append(f'<text class="finger" x="{x}" y="{cy}">{finger}</text>')

    tuning_y = y0 + board_h + 18
    for si, note in enumerate(_tuning_labels(spec)):
        x = _string_x(mx, cg, si)
        parts.append(f'<text class="tuning" x="{x}" y="{tuning_y}">{_esc(note)}</text>')

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
