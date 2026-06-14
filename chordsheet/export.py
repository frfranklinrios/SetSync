"""Payload de exportação compatível com integração SetSync."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from chordsheet.parser import Chart

MODULE_ID = "setsync.chordsheet"
MODULE_VERSION = "1.0.0"


def chart_to_payload(chart: Chart) -> dict[str, Any]:
    return {
        "module": MODULE_ID,
        "version": MODULE_VERSION,
        "meta": asdict(chart.meta),
        "prefs": asdict(chart.prefs),
        "source": chart.to_source(),
        "sections": [
            {"bar_index": i, "title": t} for i, t in chart.sections
        ],
        "page_breaks": list(chart.page_breaks),
        "line_breaks": list(chart.line_breaks),
        "bars": [
            {
                "chords": list(b.chords) if b.chords else ["%"],
                "pulse_grid": [list(beat) for beat in b.get_pulse_grid()],
                "indent": b.indent,
                "simile": b.simile,
                "simile_span": b.simile_span,
                "repeat_times": b.repeat_times,
                "nav": b.nav,
                "annotation": b.annotation,
                "volta": b.volta,
                "line_left": b.line_left,
                "line_right": b.line_right,
                "is_empty": b.is_empty,
            }
            for b in chart.bars
        ],
    }


def payload_to_chart(data: dict[str, Any]) -> Chart:
    from chordsheet.parser import Bar, ChartMeta, parse_chart
    from chordsheet.prefs import Prefs

    if data.get("source"):
        chart = parse_chart(
            data["source"],
            meta=data.get("meta"),
            prefs=data.get("prefs"),
        )
        stored_breaks = [int(x) for x in (data.get("line_breaks") or [])]
        if stored_breaks and not chart.line_breaks:
            chart.line_breaks = stored_breaks
        return chart

    chart = Chart(
        meta=ChartMeta.from_dict(data.get("meta")),
        prefs=Prefs.from_dict(data.get("prefs")),
    )
    for s in data.get("sections") or []:
        chart.sections.append((int(s["bar_index"]), str(s["title"])))
    chart.page_breaks = [int(x) for x in (data.get("page_breaks") or [])]
    chart.line_breaks = [int(x) for x in (data.get("line_breaks") or [])]
    from chordsheet.parser import _grid_to_chords, _parse_beat_segment

    for raw in data.get("bars") or []:
        chords = list(raw.get("chords") or ["%"])
        pg = raw.get("pulse_grid")
        if pg:
            pulse_grid = [list(beat) for beat in pg]
        else:
            pulse_grid = [_parse_beat_segment(c) for c in chords]
        bar = Bar(
            _grid_to_chords(pulse_grid),
            pulse_grid,
            indent=int(raw.get("indent") or 0),
            simile=bool(raw.get("simile")),
            simile_span=int(raw.get("simile_span") or 1),
            repeat_times=int(raw.get("repeat_times") or 0),
            nav=str(raw.get("nav") or ""),
            annotation=str(raw.get("annotation") or ""),
            volta=str(raw.get("volta") or ""),
            line_left=str(raw.get("line_left") or "single"),
            line_right=str(raw.get("line_right") or "single"),
            is_empty=bool(raw.get("is_empty")),
        )
        chart.bars.append(bar)
    return chart
