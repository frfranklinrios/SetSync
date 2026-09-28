#!/usr/bin/env python3
"""Checks extras: setas, tecla D, role persist, 404s."""
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
            raise RuntimeError('cookie de sessão não criado')
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
        fails_404: list[str] = []
        pageerrs: list[str] = []
        page.on('response', lambda r: fails_404.append(r.url) if r.status == 404 else None)
        page.on('pageerror', lambda e: pageerrs.append(str(e)))

        page.goto(f"{BASE}/setlists/{sl['id']}/tocar", wait_until='domcontentloaded', timeout=90_000)
        page.wait_for_timeout(2000)
        page.evaluate(
            """() => {
            const o = document.getElementById('play-onboard-overlay');
            if (o) { o.classList.add('d-none'); o.style.display = 'none'; }
            }"""
        )

        def st():
            return page.evaluate(
                """() => {
                const scroll = document.getElementById('cifra-scroll') || document.documentElement;
                const titleEl = document.getElementById('song-title')
                    || document.querySelector('.play-song-title')
                    || document.querySelector('h1');
                let draw = false;
                try {
                    draw = !!(window.SetSyncDrawOverlay
                        && (SetSyncDrawOverlay.isActive ? SetSyncDrawOverlay.isActive()
                            : SetSyncDrawOverlay.active));
                } catch (e) {}
                return {
                    title: (titleEl && titleEl.textContent || '').trim().slice(0, 80),
                    scroll: scroll.scrollTop || 0,
                    drawBtnOn: !!(document.getElementById('draw-btn')
                        && document.getElementById('draw-btn').classList.contains('active')),
                    pageAttr: document.body.getAttribute('data-page') || '',
                    sectionsVisible: (() => {
                        const m = document.getElementById('sections-pop')
                            || document.getElementById('section-jump')
                            || document.querySelector('[id*=\"section\"]');
                        return !!(m && !m.classList.contains('d-none'));
                    })(),
                    uni: typeof window['UníssonoMetronome'],
                    setSync: typeof window.SetSyncMetronome,
                };
                }"""
            )

        before = st()
        page.keyboard.press('ArrowRight')
        page.wait_for_timeout(300)
        after_right = st()
        page.keyboard.press('ArrowLeft')
        page.wait_for_timeout(300)
        after_left = st()
        page.keyboard.press('d')
        page.wait_for_timeout(400)
        after_d = st()
        page.keyboard.press('d')
        page.wait_for_timeout(200)

        # Role persist
        page.goto(f"{BASE}/bands/{band['id']}/members", wait_until='domcontentloaded', timeout=60_000)
        page.wait_for_timeout(800)
        selects = page.locator('form select[name="role"], select[name="role"]')
        n = selects.count()
        role_info: dict = {'selects': n}
        if n >= 2:
            sel = selects.nth(1)
            cur = sel.input_value()
            target = 'editor' if cur != 'editor' else 'member'
            with page.expect_navigation(timeout=15_000):
                sel.select_option(target)
            page.wait_for_timeout(500)
            after = page.locator('form select[name="role"], select[name="role"]').nth(1).input_value()
            role_info.update({'cur': cur, 'target': target, 'after': after, 'persist_ok': after == target})
            with page.expect_navigation(timeout=15_000):
                page.locator('form select[name="role"], select[name="role"]').nth(1).select_option(cur)

        print('404_count', len(fails_404))
        print('404_sample', fails_404[:12])
        print('pageerrs', pageerrs)
        print('before', before)
        print('after_right', after_right)
        print('after_left', after_left)
        print('after_d', after_d)
        print('arrows_changed_scroll', after_right.get('scroll') != before.get('scroll')
              or after_left.get('scroll') != after_right.get('scroll'))
        print('draw_toggled', after_d.get('drawBtnOn') or after_d.get('drawBtnOn') != before.get('drawBtnOn'))
        print('role', role_info)
        br.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
