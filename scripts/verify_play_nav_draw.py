#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = os.environ.get('SCREENSHOT_BASE_URL', 'https://unissono.app').rstrip('/')
USER = os.environ.get('VERIFY_USER', 'showcase')


def session_cookie(user_id: str, username: str) -> dict:
    from app import app

    name = app.config.get('SESSION_COOKIE_NAME', 'session')
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = username
            sess['display_name'] = username
        c = client.get_cookie(name)
        if c is None:
            raise RuntimeError('no cookie')
        host = urlparse(BASE).hostname or 'unissono.app'
        return {
            'name': name,
            'value': c.value,
            'domain': host,
            'path': '/',
            'httpOnly': True,
            'secure': BASE.startswith('https'),
            'sameSite': 'Lax',
        }


def main() -> int:
    from playwright.sync_api import sync_playwright
    from db import get_user_by_username, get_owned_bands, init_db
    from models_setlist import get_band_setlists

    init_db()
    user = get_user_by_username(USER)
    band = get_owned_bands(user['id'])[0]
    sl = get_band_setlists(band['id'])[0]

    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(ignore_https_errors=True, locale='pt-BR')
        ctx.add_cookies([session_cookie(user['id'], USER)])
        page = ctx.new_page()
        pageerrs = []
        page.on('pageerror', lambda e: pageerrs.append(str(e)))
        page.goto(f"{BASE}/setlists/{sl['id']}/tocar", wait_until='domcontentloaded', timeout=90_000)
        page.wait_for_timeout(2500)
        page.evaluate(
            """() => {
            const o = document.getElementById('play-onboard-overlay');
            if (o) { o.classList.add('d-none'); o.style.display = 'none'; }
            document.body.focus();
            }"""
        )

        def snap():
            return page.evaluate(
                """() => {
                const prog = document.getElementById('prog-text-l');
                const meta = document.getElementById('song-meta') || document.querySelector('.play-meta');
                const wrap = document.getElementById('cifra-scroll');
                const draw = document.getElementById('draw-btn');
                return {
                  prog: prog ? prog.textContent.trim() : '',
                  meta: meta ? meta.textContent.trim().slice(0, 80) : '',
                  scrollTop: wrap ? wrap.scrollTop : -1,
                  scrollH: wrap ? wrap.scrollHeight : -1,
                  clientH: wrap : wrap ? wrap.clientHeight : -1,
                  drawOn: draw ? draw.classList.contains('pb-on') : false,
                  canvasOn: !!document.querySelector('canvas.play-draw-active'),
                  nextDisabled: (document.getElementById('btn-next') || {}).disabled,
                };
                }""".replace('wrap : wrap', 'wrap')
            )

        # fix the botched replace - rewrite snap properly via second evaluate
        def snap2():
            return page.evaluate(
                """() => {
                const prog = document.getElementById('prog-text-l');
                const wrap = document.getElementById('cifra-scroll');
                const draw = document.getElementById('draw-btn');
                const title = document.getElementById('play-title') || document.querySelector('.pb-title');
                return {
                  prog: prog ? prog.textContent.trim() : '',
                  title: title ? title.textContent.trim().slice(0, 60) : '',
                  scrollTop: wrap ? wrap.scrollTop : -1,
                  needsScroll: wrap ? wrap.scrollHeight > wrap.clientHeight + 8 : false,
                  drawOn: draw ? draw.classList.contains('pb-on') : false,
                  canvasOn: !!document.querySelector('canvas.play-draw-active'),
                  nextDisabled: !!(document.getElementById('btn-next') || {}).disabled,
                  prevDisabled: !!(document.getElementById('btn-prev') || {}).disabled,
                };
                }"""
            )

        b = snap2()
        print('BASE', b, 'pageerrs', pageerrs)

        page.keyboard.press('ArrowDown')
        page.wait_for_timeout(500)
        after_down = snap2()
        print('ARROW_DOWN', after_down)

        page.keyboard.press('ArrowUp')
        page.wait_for_timeout(500)
        after_up = snap2()
        print('ARROW_UP', after_up)

        # use page.evaluate to call key handlers via CustomEvent
        page.evaluate(
            """() => {
            document.dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowRight', bubbles:true}));
            }"""
        )
        page.wait_for_timeout(300)
        after_right = snap2()
        print('ARROW_RIGHT_dispatch', after_right)

        page.evaluate(
            """() => {
            if (typeof window.nextSong === 'function') window.nextSong();
            }"""
        )
        page.wait_for_timeout(400)
        after_next = snap2()
        print('NEXT_SONG_FN', after_next)

        page.click('#draw-btn', force=True)
        page.wait_for_timeout(300)
        after_draw_click = snap2()
        print('DRAW_CLICK', after_draw_click)

        page.keyboard.press('d')
        page.wait_for_timeout(300)
        after_d = snap2()
        print('KEY_D', after_d)

        # tap next
        page.locator('#tap-next').click(force=True)
        page.wait_for_timeout(400)
        after_tap = snap2()
        print('TAP_NEXT', after_tap)

        # btn next
        page.click('#btn-next', force=True)
        page.wait_for_timeout(400)
        after_btn = snap2()
        print('BTN_NEXT', after_btn)

        print('VERDICT', {
            'song_nav_arrow_down': b.get('prog') != after_down.get('prog'),
            'song_nav_btn': after_tap.get('prog') != after_btn.get('prog') or b.get('prog') != after_btn.get('prog'),
            'draw_works': after_draw_click.get('drawOn') or after_d.get('drawOn') or after_draw_click.get('canvasOn'),
            'pageerrs': pageerrs,
        })
        br.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
