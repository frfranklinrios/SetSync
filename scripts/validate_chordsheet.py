#!/usr/bin/env python3
"""Valida payload JSON setsync.chordsheet (stdin ou arquivo)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chordsheet.export import payload_to_chart
from chordsheet.render import render_chart_html


def validate(data: dict) -> tuple[int, str]:
    if data.get("module") != "setsync.chordsheet":
        raise ValueError(f"module inválido: {data.get('module')!r}")
    chart = payload_to_chart(data)
    html = render_chart_html(chart)
    if "cs-chart" not in html:
        raise ValueError("HTML sem cs-chart")
    return len(chart.bars), data.get("meta", {}).get("title") or "sem título"


def main() -> int:
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    data = json.loads(raw)
    n, title = validate(data)
    print(f"OK — {n} compassos — {title}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
