#!/usr/bin/env python3
"""Renderiza os criativos de palco (HTML + design do site) em PNG para Meta/Google."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'marketing' / 'criativos' / 'boards.html'
OUT = ROOT / 'marketing' / 'criativos' / 'png'

BOARDS = (
    ('feed-1x1', 1080, 1080),
    ('feed-4x5', 1080, 1350),
    ('stories-9x16', 1080, 1920),
    ('igreja-4x5', 1080, 1350),
)


def main() -> int:
    from playwright.sync_api import sync_playwright

    if not HTML.exists():
        raise SystemExit(f'Não achei {HTML}')
    OUT.mkdir(parents=True, exist_ok=True)
    url = HTML.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1200, 'height': 2200}, device_scale_factor=1)
        page.goto(url, wait_until='networkidle', timeout=60_000)
        page.evaluate('() => document.fonts.ready')
        page.wait_for_timeout(400)
        for board_id, w, h in BOARDS:
            loc = page.locator(f'#{board_id}')
            loc.wait_for()
            dest = OUT / f'{board_id}.png'
            loc.screenshot(path=str(dest), type='png')
            print(f'{dest.name}  {w}×{h}')
        browser.close()
    print(f'OK → {OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
