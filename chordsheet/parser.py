"""Parser do formato texto estilo chordsheet.com."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from chordsheet.prefs import Prefs

REPRINT = re.compile(r"^%(?:(\d+))?$")
REPRINT2 = re.compile(r"^%%$")
SECTION = re.compile(r"^=\s*(.+)$")
COLON_SECTION = re.compile(r"^:\s*(.+)$")
PAGE_BREAK = re.compile(r"^\+\s*(.*)$")
TEXT_LINE = re.compile(r"^-\s+(.+)$")
BLANK_LINE = re.compile(r"^-\s*$")
LITERAL_LINE = re.compile(r"^;(.*)$")
FLOAT_LABEL = re.compile(r"^<=\s*(.+)$")
FLOAT_NUM = re.compile(r"^<-\s*(.+)$")
VOLTA_TOKEN = re.compile(r"^(\d+)\.$")
VOLTA_LABEL = re.compile(r"^\d+\.")
BAR_TIMESIG = re.compile(r"^(\d+):(\d+)$")
REPEAT_GROUP = re.compile(r"^\((.+)\)(?:x(\d+)|(\d+)x)?$", re.I)
REPEAT_SUFFIX = re.compile(r"^(?:x(\d+)|(\d+)x)", re.I)

NAV_MARKERS_ORDERED = [
    "D.C. al coda senza rep.",
    "D.C. al coda con rep.",
    "D.S. al coda con rep.",
    "D.C. al coda",
    "D.S. al coda",
    "D.C. al fine",
    "D.S. al fine",
    "D.C.",
    "D.S.",
    "fine",
]
NAV_MARKERS = set(NAV_MARKERS_ORDERED) | {"$", "o", "O"}


def _grid_to_chords(grid: list[list[str]]) -> list[str]:
    """Serializa grade de pulsos para lista plana (um item por pulso)."""
    out: list[str] = []
    for beat in grid:
        if len(beat) == 1:
            out.append(beat[0])
        else:
            out.append("&".join(beat))
    return out


def _parse_beat_segment(part: str) -> list[str]:
    """Um segmento _ pode conter & para semi-pulsos (ex.: C&D)."""
    if "&" in part:
        subs = [p.strip() if p.strip() else "*" for p in part.split("&")]
        return subs if subs else ["*"]
    if not part or part == "*":
        return ["*"]
    return [part]


@dataclass
class Bar:
    chords: list[str]
    pulse_grid: list[list[str]] | None = None
    indent: int = 0
    simile: bool = False
    simile_span: int = 1
    nav: str = ""
    annotation: str = ""
    annotation_literal: bool = False
    blank_spacer: bool = False
    floating_label: str = ""
    bar_time_signature: str = ""
    volta: str = ""
    line_left: str = "single"
    line_right: str = "single"
    is_empty: bool = False
    repeat_times: int = 0

    def get_pulse_grid(self) -> list[list[str]]:
        if self.pulse_grid is not None:
            return self.pulse_grid
        return [[c] for c in self.chords]

    def set_pulse_grid(self, grid: list[list[str]]) -> None:
        self.pulse_grid = [list(beat) for beat in grid]
        self.chords = _grid_to_chords(self.pulse_grid)

    def clone(self) -> "Bar":
        pg = [list(beat) for beat in self.pulse_grid] if self.pulse_grid else None
        return Bar(
            list(self.chords),
            pg,
            self.indent,
            self.simile,
            self.simile_span,
            self.nav,
            self.annotation,
            self.annotation_literal,
            self.blank_spacer,
            self.floating_label,
            self.bar_time_signature,
            self.volta,
            self.line_left,
            self.line_right,
            self.is_empty,
            self.repeat_times,
        )

    def column_slots(self) -> int:
        if self.simile and self.simile_span > 1:
            return self.simile_span
        return 1

    @property
    def is_full_width(self) -> bool:
        return bool(self.nav or self.annotation or self.blank_spacer)

    def display_slots(self) -> int:
        if self.is_empty:
            return 1
        n = 0
        for beat in self.get_pulse_grid():
            n += len([c for c in beat if c and c not in ("%", "NC", "N.C.", "*")])
        return max(1, n)


@dataclass
class ChartMeta:
    title: str = "Sem título"
    artist: str = ""
    key: str = ""
    bpm: str = ""
    time_signature: str = "4/4"
    capo: str = ""
    style: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "ChartMeta":
        m = cls()
        if not raw:
            return m
        for k in m.__dataclass_fields__:
            if k in raw and raw[k] is not None:
                setattr(m, k, str(raw[k]).strip())
        return m


@dataclass
class Chart:
    meta: ChartMeta = field(default_factory=ChartMeta)
    prefs: Prefs = field(default_factory=Prefs)
    sections: list[tuple[int, str]] = field(default_factory=list)
    page_breaks: list[int] = field(default_factory=list)
    bars: list[Bar] = field(default_factory=list)

    def to_source(self) -> str:
        lines: list[str] = []
        sec_at = {i: t for i, t in self.sections}
        pb_at = set(self.page_breaks)
        for i, bar in enumerate(self.bars):
            if i in pb_at:
                lines.append("+")
            if i in sec_at:
                lines.append(f"= {sec_at[i]}")
            if bar.annotation:
                lines.append(f"- {bar.annotation}")
                continue
            if bar.nav:
                lines.append(bar.nav)
                continue
            token = _bar_to_token(bar)
            if lines and not lines[-1].startswith(("=", "+", "-")) and lines[-1] not in NAV_MARKERS:
                if lines[-1] and not lines[-1].startswith("="):
                    lines[-1] += f" {token}"
                    continue
            lines.append(token)
        return "\n".join(lines)


@dataclass
class _ParseState:
    pending_repeat_start: bool = False
    pending_volta: str = ""
    pending_double_left: bool = False
    pending_float: str = ""
    pending_bar_ts: str = ""


def _bar_to_token(bar: Bar) -> str:
    if bar.simile:
        body = "%"
    elif bar.is_empty:
        body = "*"
    else:
        grid = bar.get_pulse_grid()
        if len(grid) > 1 or any(len(b) > 1 for b in grid):
            parts: list[str] = []
            for beat in grid:
                if len(beat) == 1:
                    c = beat[0]
                    parts.append("*" if c in ("", "%") else c)
                else:
                    parts.append("&".join("*" if c in ("", "%") else c for c in beat))
            body = "_".join(parts)
        elif bar.chords:
            body = bar.chords[0] if bar.chords[0] not in ("", "%") else "%"
        else:
            body = "%"
    prefix = "X" * bar.indent
    if bar.volta:
        prefix = f"{bar.volta} {prefix}"
    if bar.line_left == "repeat-start":
        prefix = "|:" + prefix
    if bar.line_right == "repeat-end":
        body = f"{body}:|"
    return prefix + body


def _simile_bar(span: int = 1) -> Bar:
    return Bar(["%"], simile=True, simile_span=max(1, span))


def _expand_reprint(token: str, history: list[Bar]) -> list[Bar]:
    if REPRINT2.match(token):
        return [_simile_bar(2)]
    m = REPRINT.match(token)
    if m:
        if m.group(1):
            n = int(m.group(1))
            if len(history) >= n:
                return [b.clone() for b in history[-n:]]
            if n == 2:
                return [_simile_bar(2)]
            if n >= 4:
                return [_simile_bar(n)]
            return [_simile_bar(1) for _ in range(n)]
        return [_simile_bar(1)]
    return []


def _mark_repeat_brackets(chart: Chart, start: int, end: int, times: int = 1) -> None:
    """Marca |: … :| no grupo (sem duplicar compassos)."""
    indices: list[int] = []
    for i in range(start, min(end, len(chart.bars))):
        b = chart.bars[i]
        if b.nav or b.annotation or b.blank_spacer:
            continue
        if b.chords or b.is_empty or b.simile:
            indices.append(i)
    if not indices:
        return
    first, last = indices[0], indices[-1]
    if chart.bars[first].line_left in ("single", "double"):
        chart.bars[first].line_left = "repeat-start"
    chart.bars[last].line_right = "repeat-end"
    if times > 1:
        chart.bars[last].repeat_times = times


def _extract_barline_edges(token: str) -> tuple[str, str | None, str | None]:
    left = None
    right = None
    t = token
    if t.startswith("|:"):
        left = "repeat-start"
        t = t[2:]
    if t.endswith(":|"):
        right = "repeat-end"
        t = t[:-2]
    return t, left, right


def _try_nav_phrase(tokens: list[str], start: int) -> tuple[str | None, int]:
    for n in range(min(6, len(tokens) - start), 0, -1):
        phrase = " ".join(tokens[start : start + n])
        if phrase in NAV_MARKERS_ORDERED:
            return phrase, start + n
    if start < len(tokens) and tokens[start] in {"$", "o", "O"}:
        return tokens[start], start + 1
    return None, start


def _parse_bar_token(token: str, volta: str = "") -> Bar | None:
    if token in NAV_MARKERS:
        return Bar([], nav=token)

    raw, left_edge, right_edge = _extract_barline_edges(token)
    if not raw and (left_edge or right_edge):
        return Bar(["%"], line_left=left_edge or "single", line_right=right_edge or "single")

    indent = 0
    while raw.startswith("X"):
        indent += 1
        raw = raw[1:]

    if not raw:
        return Bar(["%"], indent=indent, volta=volta, line_left=left_edge or "single", line_right=right_edge or "single")

    if raw == "*":
        return Bar(
            [""],
            indent=indent,
            volta=volta,
            is_empty=True,
            line_left=left_edge or "single",
            line_right=right_edge or "single",
        )

    if "/" in raw and raw.startswith("*/"):
        return Bar(
            [raw],
            indent=indent,
            volta=volta,
            line_left=left_edge or "single",
            line_right=right_edge or "single",
        )

    parts = [p.strip() for p in raw.split("_")]
    pulse_grid = [_parse_beat_segment(p) for p in parts] if parts else [["%"]]
    chords = _grid_to_chords(pulse_grid)
    if not chords or chords == ["*"]:
        chords = ["%"]
        pulse_grid = [["%"]]
        is_empty = True
    else:
        is_empty = all(c == "*" for beat in pulse_grid for c in beat)
    return Bar(
        chords,
        pulse_grid,
        indent=indent,
        volta=volta,
        is_empty=is_empty,
        line_left=left_edge or "single",
        line_right=right_edge or "single",
    )


def _apply_section_delimiter(chart: Chart, state: _ParseState) -> None:
    """= seção: fecha || no compasso anterior e abre || no próximo (manual basics)."""
    closed = False
    for i in range(len(chart.bars) - 1, -1, -1):
        b = chart.bars[i]
        if b.nav or b.annotation or b.blank_spacer:
            continue
        if b.chords or b.is_empty or b.simile:
            b.line_right = "double"
            closed = True
            break
    state.pending_double_left = closed


def _ensure_final_barline(chart: Chart) -> None:
    """Último compasso fecha com |] (fino + grosso), como no chordsheet.com."""
    for i in range(len(chart.bars) - 1, -1, -1):
        bar = chart.bars[i]
        if bar.nav or bar.annotation or bar.blank_spacer or not bar.chords:
            continue
        if bar.line_right == "single":
            bar.line_right = "final"
        break


def _append_bar(chart: Chart, state: _ParseState, bar: Bar, history: list[Bar], bar_index: int) -> int:
    if state.pending_float and bar.chords:
        bar.floating_label = state.pending_float
        state.pending_float = ""
    if state.pending_bar_ts and bar.chords:
        bar.bar_time_signature = state.pending_bar_ts
        state.pending_bar_ts = ""
    # |: tem prioridade sobre barra dupla de seção (= refrão)
    if state.pending_repeat_start:
        bar.line_left = "repeat-start"
        state.pending_repeat_start = False
        state.pending_double_left = False
    elif state.pending_double_left:
        bar.line_left = "double"
        state.pending_double_left = False

    chart.bars.append(bar)
    if not bar.nav and not bar.annotation and not bar.blank_spacer and bar.chords:
        history.append(bar)
    return bar_index + 1


def _merge_quoted_chords(tokens: list[str]) -> list[str]:
    merged: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if i + 1 < len(tokens) and tokens[i + 1].startswith('"'):
            tok = f'{tok} {tokens[i + 1]}'
            i += 2
            merged.append(tok)
            continue
        merged.append(tok)
        i += 1
    return merged


def _normalize_barline_tokens(tokens: list[str]) -> list[str]:
    """Une | : e : | separados por espaço; ignora | solto."""
    out: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if tok == "|" and nxt == ":":
                out.append("|:")
                i += 2
                continue
            if tok == ":" and nxt == "|":
                out.append(":|")
                i += 2
                continue
            if tok == "||" and nxt == ":":
                out.append("||")
                out.append(":")
                i += 2
                continue
            if tok == "||" and nxt == "|:":
                out.append("||")
                out.append("|:")
                i += 2
                continue
        if tok == "|":
            i += 1
            continue
        out.append(tok)
        i += 1
    return out


def _apply_double_bar_close(chart: Chart) -> None:
    for j in range(len(chart.bars) - 1, -1, -1):
        b = chart.bars[j]
        if b.nav or b.annotation or b.blank_spacer:
            continue
        b.line_right = "double"
        break


def _parse_tokens_into_chart(
    tokens: list[str],
    chart: Chart,
    state: _ParseState,
    history: list[Bar],
    bar_index: int,
) -> int:
    tokens = _normalize_barline_tokens(_merge_quoted_chords(tokens))
    i = 0
    while i < len(tokens):
        token = tokens[i]

        nav, next_i = _try_nav_phrase(tokens, i)
        if nav:
            bar = Bar([], nav=nav)
            bar_index = _append_bar(chart, state, bar, history, bar_index)
            i = next_i
            continue

        if token == "||":
            _apply_double_bar_close(chart)
            state.pending_double_left = True
            i += 1
            continue

        if token == ":":
            state.pending_repeat_start = True
            i += 1
            continue

        if token == "|:":
            state.pending_repeat_start = True
            i += 1
            continue

        if token == ":|":
            if chart.bars and not chart.bars[-1].nav:
                chart.bars[-1].line_right = "repeat-end"
            i += 1
            continue

        if VOLTA_LABEL.match(token):
            state.pending_volta = token if token.endswith(".") else f"{token}."
            i += 1
            continue

        tsm = BAR_TIMESIG.match(token)
        if tsm:
            state.pending_bar_ts = f"{tsm.group(1)}/{tsm.group(2)}"
            i += 1
            continue

        gm = REPEAT_GROUP.match(token)
        if gm:
            inner_tokens = _tokenize_chord_line(gm.group(1))
            count = int(gm.group(2) or gm.group(3) or 1)
            group_start = len(chart.bars)
            bar_index = _parse_tokens_into_chart(
                inner_tokens, chart, state, history, bar_index,
            )
            _mark_repeat_brackets(chart, group_start, len(chart.bars), count)
            i += 1
            continue

        expanded = _expand_reprint(token, history)
        if expanded:
            for bar in expanded:
                bar_index = _append_bar(chart, state, bar, history, bar_index)
            i += 1
            continue

        volta = state.pending_volta
        state.pending_volta = ""
        bar = _parse_bar_token(token, volta=volta)
        if bar is None:
            i += 1
            continue
        if bar.nav:
            bar_index = _append_bar(chart, state, bar, history, bar_index)
            i += 1
            continue
        bar_index = _append_bar(chart, state, bar, history, bar_index)
        i += 1

    return bar_index


def _repeat_open_before(chart: Chart, index: int) -> bool:
    """Há |: aberto numa linha anterior sem :| correspondente."""
    for j in range(index - 1, -1, -1):
        b = chart.bars[j]
        if b.nav or b.annotation or b.blank_spacer:
            continue
        if b.line_right == "repeat-end":
            return False
        if b.line_left == "repeat-start":
            return True
    return False


def _finalize_line_repeat(chart: Chart, line_start: int) -> None:
    """Se a linha fecha com :| mas não abriu com |:, marca o 1º compasso."""
    if line_start >= len(chart.bars):
        return
    chunk: list[tuple[int, Bar]] = []
    for i in range(line_start, len(chart.bars)):
        b = chart.bars[i]
        if b.nav or b.annotation:
            break
        chunk.append((i, b))
    if not chunk:
        return
    has_end = any(b.line_right == "repeat-end" for _, b in chunk)
    has_start = any(b.line_left == "repeat-start" for _, b in chunk)
    if has_end and not has_start:
        if _repeat_open_before(chart, line_start):
            return
        idx, first = chunk[0]
        if first.line_left in ("single", "double"):
            chart.bars[idx].line_left = "repeat-start"


def _paren_balance(text: str) -> int:
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
    return depth


def _tokenize_chord_line(line: str) -> list[str]:
    """Tokeniza linha preservando grupos ( … )xN como um único token."""
    tokens: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        while i < n and line[i].isspace():
            i += 1
        if i >= n:
            break
        if line[i] == "(":
            depth = 0
            j = i
            while j < n:
                if line[j] == "(":
                    depth += 1
                elif line[j] == ")":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            if depth != 0:
                tokens.append(line[i:].strip())
                break
            suffix_m = REPEAT_SUFFIX.match(line[j:])
            end = j + (suffix_m.end() if suffix_m else 0)
            tokens.append(line[i:end].strip())
            i = end
            continue
        j = i
        while j < n and not line[j].isspace() and line[j] != "(":
            j += 1
        tokens.append(line[i:j])
        i = j
    return [t for t in tokens if t]


def _try_nav_line(line: str) -> str | None:
    s = line.strip()
    for pat in NAV_MARKERS_ORDERED:
        if s == pat:
            return pat
    if s in {"$", "o", "O"}:
        return s
    return None


def parse_chart(
    source: str,
    meta: dict[str, Any] | None = None,
    prefs: dict[str, Any] | None = None,
) -> Chart:
    chart = Chart(meta=ChartMeta.from_dict(meta), prefs=Prefs.from_dict(prefs))
    history: list[Bar] = []
    state = _ParseState()
    bar_index = 0

    pending_chord_line = ""

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        nav_line = _try_nav_line(line)
        if nav_line:
            bar = Bar([], nav=nav_line)
            bar_index = _append_bar(chart, state, bar, history, bar_index)
            continue

        if BLANK_LINE.match(line):
            bar_index = _append_bar(chart, state, Bar([], blank_spacer=True), history, bar_index)
            continue

        lm = LITERAL_LINE.match(raw_line.rstrip())
        if lm:
            bar = Bar([], annotation=lm.group(1), annotation_literal=True)
            bar_index = _append_bar(chart, state, bar, history, bar_index)
            continue

        fl = FLOAT_LABEL.match(line)
        if fl:
            state.pending_float = fl.group(1).strip()
            continue
        fn = FLOAT_NUM.match(line)
        if fn:
            state.pending_float = fn.group(1).strip()
            continue

        tm = TEXT_LINE.match(line)
        if tm:
            bar = Bar([], annotation=tm.group(1).strip())
            bar_index = _append_bar(chart, state, bar, history, bar_index)
            continue

        sm = SECTION.match(line)
        if sm:
            _apply_section_delimiter(chart, state)
            chart.sections.append((bar_index, sm.group(1).strip()))
            continue

        cm = COLON_SECTION.match(line)
        if cm:
            chart.sections.append((bar_index, cm.group(1).strip()))
            continue

        pm = PAGE_BREAK.match(line)
        if pm:
            chart.page_breaks.append(bar_index)
            label = pm.group(1).strip()
            if label:
                _apply_section_delimiter(chart, state)
                chart.sections.append((bar_index, label))
            continue

        if pending_chord_line:
            line = f"{pending_chord_line} {line}".strip()
            pending_chord_line = ""

        if _paren_balance(line) > 0:
            pending_chord_line = line
            continue

        line_start = len(chart.bars)
        tokens = _tokenize_chord_line(line)
        bar_index = _parse_tokens_into_chart(tokens, chart, state, history, bar_index)
        _finalize_line_repeat(chart, line_start)

    if pending_chord_line:
        line_start = len(chart.bars)
        tokens = _tokenize_chord_line(pending_chord_line)
        bar_index = _parse_tokens_into_chart(tokens, chart, state, history, bar_index)
        _finalize_line_repeat(chart, line_start)

    _ensure_final_barline(chart)
    return chart
