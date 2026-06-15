"""Transposição de acordes."""

from __future__ import annotations

from chordsheet.parser import Chart, ChartMeta


def _skip_transpose(chord: str) -> bool:
    c = (chord or "").strip()
    return not c or c in ("%", "NC", "N.C.") or c.startswith("*/") or c.startswith("*")


def transpose_chord(
    chord: str,
    semitones: int,
    tom_origem: str | None = None,
) -> str:
    """Transpõe um acorde com grafia pela armadura do tom de destino."""
    from util import format_text_chords_br, normalize_tom_label, transpose_chord_display

    if _skip_transpose(chord):
        return chord
    tom = normalize_tom_label(tom_origem or "C")
    if not semitones:
        return format_text_chords_br(chord, tom) if tom else chord
    return transpose_chord_display(chord, semitones, tom)


def transpose_chart(
    chart: Chart,
    semitones: int,
    *,
    source_key: str | None = None,
) -> Chart:
    from util import key_at_transpose, normalize_tom_label

    origin = normalize_tom_label(source_key or chart.meta.key or "C")
    if not semitones:
        return chart

    target_key = key_at_transpose(origin, semitones)
    out = Chart(
        meta=ChartMeta(**chart.meta.__dict__),
        prefs=chart.prefs,
        sections=list(chart.sections),
        page_breaks=list(chart.page_breaks),
        line_breaks=list(chart.line_breaks),
        bars=[],
    )
    out.meta.key = target_key

    for bar in chart.bars:
        if bar.nav or bar.annotation:
            out.bars.append(bar.clone())
            continue
        nb = bar.clone()
        grid = bar.get_pulse_grid()
        nb.set_pulse_grid(
            [
                [transpose_chord(c, semitones, origin) for c in beat]
                for beat in grid
            ]
        )
        out.bars.append(nb)
    return out
