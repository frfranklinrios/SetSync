"""Transposição de acordes."""

from __future__ import annotations

import re

from chordsheet.parser import Chart, ChartMeta

NOTES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ENHARMONIC = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B", "Fb": "E", "E#": "F", "B#": "C"}

CHORD_RE = re.compile(
    r"^([A-G])([#b]?)(.*)$",
    re.I,
)


def _parse_root(chord: str) -> tuple[str, str, str] | None:
    c = chord.strip()
    if not c or c in ("%", "NC", "N.C.") or c.startswith("*/"):
        return None
    slash = c.find("/")
    head = c[:slash] if slash >= 0 else c
    tail = c[slash:] if slash >= 0 else ""
    m = CHORD_RE.match(head)
    if not m:
        return None
    root = m.group(1).upper() + (m.group(2) or "")
    if root in ENHARMONIC:
        root = ENHARMONIC[root]
    return root, m.group(3), tail


def transpose_chord(chord: str, semitones: int) -> str:
    parsed = _parse_root(chord)
    if not parsed:
        return chord
    root, qual, tail = parsed
    if root not in NOTES_SHARP and root.replace("#", "") in NOTES_SHARP:
        pass
    try:
        idx = NOTES_SHARP.index(root)
    except ValueError:
        return chord
    new_root = NOTES_SHARP[(idx + semitones) % 12]
    if tail.startswith("/"):
        bass = tail[1:]
        bp = _parse_root(bass if bass[-1] in "#b" else bass + "maj")
        if bp:
            b_idx = NOTES_SHARP.index(bp[0])
            new_bass = NOTES_SHARP[(b_idx + semitones) % 12]
            tail = "/" + new_bass
    return new_root + qual + tail


def transpose_chart(chart: Chart, semitones: int) -> Chart:
    if not semitones:
        return chart
    out = Chart(
        meta=ChartMeta(**chart.meta.__dict__),
        prefs=chart.prefs,
        sections=list(chart.sections),
        page_breaks=list(chart.page_breaks),
        bars=[],
    )
    if out.meta.key:
        out.meta.key = transpose_chord(out.meta.key + "maj", semitones).replace("maj", "")

    for bar in chart.bars:
        if bar.nav or bar.annotation:
            out.bars.append(bar.clone())
            continue
        nb = bar.clone()
        grid = bar.get_pulse_grid()
        nb.set_pulse_grid(
            [[transpose_chord(c, semitones) for c in beat] for beat in grid]
        )
        out.bars.append(nb)
    return out
