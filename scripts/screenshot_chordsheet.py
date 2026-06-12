#!/usr/bin/env python3
"""Gera PNG da prévia do chord sheet (manual meta) para revisão visual."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chordsheet.examples import EXAMPLES
from chordsheet.parser import parse_chart
from chordsheet.render import render_chart_html
from chordsheet_bridge import apply_chart_cifra_spelling


def main() -> None:
    ex = EXAMPLES["manual_meta"]
    meta = dict(ex["meta"])
    meta.update({
        "title": "Amor, Amor?",
        "artist": "MASTRUZ COM LEITE",
        "key": "F#",
        "bpm": "120",
    })
    chart = parse_chart(ex["source"], meta=meta)
    apply_chart_cifra_spelling(chart, "F#")
    body = render_chart_html(chart)

    out_dir = ROOT / "static" / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "_cs_preview_test.html"
    png_path = out_dir / "chordsheet-preview.png"

    css1 = (ROOT / "static/css/chordsheet.css").read_text()
    css2 = (ROOT / "static/css/cifra-sheet-print.css").read_text()
    html_path.write_text(
        f"""<!DOCTYPE html>
<html lang="pt-br" data-theme="dark">
<head>
<meta charset="utf-8">
<style>
{css1}
{css2}
body {{
  margin: 0;
  padding: 1.5rem;
  background: #0b1220;
}}
.preview-shell {{
  max-width: 920px;
  margin: 0 auto;
  background: #fff;
  color: #1c1917;
  padding: 1.25rem 1rem 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,.35);
}}
.setsync-cs-sheet .cs-chart {{
  --ss-chord: #0d9488;
  --chord-highlight: #0d9488;
  --rb-ink: #1c1917;
}}
</style>
</head>
<body>
<div class="preview-shell setsync-cs-sheet">{body}</div>
</body>
</html>""",
        encoding="utf-8",
    )

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 980, "height": 2400})
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()

    print(png_path)


if __name__ == "__main__":
    main()
