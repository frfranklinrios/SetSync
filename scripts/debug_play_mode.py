#!/usr/bin/env python3
"""Executa o HTML do modo tocar no Chromium e reporta erros."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright

from app import app
from db import get_band, get_band_cifras, get_user_by_username
from blueprints.cifras import enrich_cifra_for_tocar, render_play_mode


def main() -> None:
    with app.app_context():
        u = get_user_by_username('amanda')
        bid = '2ddf62cb-77d4-4ba2-b774-9270d4f95e3d'
        band = get_band(bid)
        cifras = [enrich_cifra_for_tocar(c, user_id=u['id']) for c in get_band_cifras(bid)]
        with app.test_request_context(f'/cifras/band/{bid}/tocar'):
            from flask import session
            session['user_id'] = u['id']
            session['username'] = u['username']
            html = render_play_mode(
                {'id': None, 'band_id': bid, 'name': 'Teste'},
                band,
                cifras,
                is_virtual=True,
            )

    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))
        page.on('console', lambda m: errors.append(f'console:{m.type}:{m.text}') if m.type == 'error' else None)
        page.set_content(html, wait_until='load')
        page.wait_for_timeout(2000)
        state = page.evaluate(
            """() => ({
                playMode: document.body.classList.contains('play-mode'),
                title: (document.getElementById('bar-title') || {}).textContent || '',
                contentLen: ((document.getElementById('cifra-content') || {}).innerHTML || '').length,
                cifrasLen: (() => {
                    try {
                        const el = document.getElementById('cifras-data');
                        const raw = (el.textContent || '').trim();
                        function decodeBase64Utf8(b64) {
                            const bin = atob(b64);
                            const bytes = new Uint8Array(bin.length);
                            for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                            return new TextDecoder('utf-8').decode(bytes);
                        }
                        return JSON.parse(decodeBase64Utf8(raw)).length;
                    } catch (e) { return String(e); }
                })(),
                lyricsSample: (() => {
                    try {
                        const el = document.getElementById('cifras-data');
                        const raw = (el.textContent || '').trim();
                        const bin = atob(raw);
                        const bytes = new Uint8Array(bin.length);
                        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                        const parsed = JSON.parse(new TextDecoder('utf-8').decode(bytes));
                        const song = parsed.find(s => (s.lyrics_plain || '').includes('Refr'));
                        return song ? song.lyrics_plain.slice(0, 120) : '';
                    } catch (e) { return String(e); }
                })(),
                hasToggleDrawer: typeof window.toggleDrawer === 'function',
                hasRender: typeof window.goTo === 'function',
            })"""
        )
        print('state:', state)
        if errors:
            print('errors:')
            for e in errors[:15]:
                print(' ', e)
        browser.close()


if __name__ == '__main__':
    main()
