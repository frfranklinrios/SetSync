#!/usr/bin/env python3
"""Valida correção do lápis: canvas cobre conteúdo, traços sobrevivem grade, draw fica ativo."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = os.environ.get("SCREENSHOT_BASE_URL", "https://unissono.app").rstrip("/")
USER = os.environ.get("VERIFY_USER", "showcase")


def session_cookie(user_id: str, username: str) -> dict:
    from app import app

    name = app.config.get("SESSION_COOKIE_NAME", "session")
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = username
            sess["display_name"] = username
        c = client.get_cookie(name)
        host = urlparse(BASE).hostname or "unissono.app"
        return {
            "name": name,
            "value": c.value,
            "domain": host,
            "path": "/",
            "httpOnly": True,
            "secure": BASE.startswith("https"),
            "sameSite": "Lax",
        }


def main() -> int:
    from playwright.sync_api import sync_playwright

    from db import get_owned_bands, get_user_by_username, init_db
    from models_setlist import get_band_setlists

    init_db()
    user = get_user_by_username(USER)
    band = get_owned_bands(user["id"])[0]
    sl = get_band_setlists(band["id"])[0]

    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(
            ignore_https_errors=True, viewport={"width": 1280, "height": 800}
        )
        ctx.add_cookies([session_cookie(user["id"], USER)])
        page = ctx.new_page()
        page.goto(
            f"{BASE}/setlists/{sl['id']}/tocar",
            wait_until="domcontentloaded",
            timeout=90_000,
        )
        page.wait_for_timeout(2500)
        page.evaluate(
            """() => {
            const o = document.getElementById('play-onboard-overlay');
            if (o) { o.classList.add('d-none'); o.style.display = 'none'; }
            }"""
        )

        def info():
            return page.evaluate(
                """() => {
                const c = document.querySelector('.play-draw-canvas');
                const wrap = document.getElementById('cifra-scroll');
                if (!c || !wrap) return {};
                const ctx = c.getContext('2d');
                const data = ctx.getImageData(0, 0, c.width, c.height).data;
                let nonzero = 0;
                for (let i = 3; i < data.length; i += 32) if (data[i] > 10) nonzero++;
                return {
                  cw: c.width, ch: c.height,
                  scrollH: wrap.scrollHeight, clientH: wrap.clientHeight,
                  coversContent: c.height >= wrap.scrollHeight - 2,
                  active: c.classList.contains('play-draw-active'),
                  bodyDrawing: document.body.classList.contains('play-drawing'),
                  tapPe: getComputedStyle(document.getElementById('tap-next')).pointerEvents,
                  enabled: !!(window.SetSyncDrawOverlay && SetSyncDrawOverlay.isEnabled && SetSyncDrawOverlay.isEnabled()),
                  nonzero,
                  viewLabel: (document.getElementById('view-mode-label') || {}).textContent || '',
                };
                }"""
            )

        page.click("#draw-btn", force=True)
        page.wait_for_timeout(200)
        box = page.locator(".play-draw-canvas").bounding_box()
        x0 = box["x"] + box["width"] * 0.3
        y0 = box["y"] + box["height"] * 0.3
        page.mouse.move(x0, y0)
        page.mouse.down()
        page.mouse.move(x0 + 140, y0 + 60, steps=14)
        page.mouse.up()
        page.wait_for_timeout(400)
        after_draw = info()
        print("AFTER_DRAW", after_draw)

        page.click("#view-mode-btn", force=True)
        page.click('#view-mode-menu [data-view-mode="chordsheet"]', force=True)
        page.wait_for_timeout(1800)
        after_grade = info()
        print("AFTER_GRADE", after_grade)

        # Ainda deve poder desenhar
        if not after_grade.get("active"):
            page.click("#draw-btn", force=True)
            page.wait_for_timeout(200)
        box = page.locator(".play-draw-canvas").bounding_box()
        x0 = box["x"] + box["width"] * 0.4
        y0 = box["y"] + box["height"] * 0.4
        page.mouse.move(x0, y0)
        page.mouse.down()
        page.mouse.move(x0 + 100, y0 + 50, steps=10)
        page.mouse.up()
        page.wait_for_timeout(300)
        after_grade_stroke = info()
        print("AFTER_GRADE_STROKE", after_grade_stroke)

        ok = True
        if after_draw.get("nonzero", 0) < 1:
            print("FAIL: stroke não apareceu na cifra")
            ok = False
        if after_grade.get("nonzero", 0) < 1:
            print("FAIL: strokes sumiram ao ir para Grade")
            ok = False
        if not after_grade.get("enabled"):
            print("FAIL: lápis desligou ao trocar para Grade")
            ok = False
        if after_grade.get("tapPe") != "none":
            print(
                "FAIL: tap-zone ainda captura pointer com lápis ativo",
                after_grade.get("tapPe"),
            )
            ok = False
        if not after_draw.get("coversContent"):
            print("WARN: canvas menor que scrollHeight", after_draw)
        if after_grade_stroke.get("nonzero", 0) <= after_grade.get("nonzero", 0):
            print("FAIL: não conseguiu desenhar na grade")
            ok = False

        print("RESULT", "OK" if ok else "FAIL")
        br.close()
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
