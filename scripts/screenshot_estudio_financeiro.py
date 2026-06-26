#!/usr/bin/env python3
"""Captura screenshot em alta resolução do financeiro do estúdio demo."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT_PATH = ROOT / 'static' / 'screenshots' / 'estudio-financeiro-desktop.png'
HTML_PATH = ROOT / 'static' / 'screenshots' / '_finance_capture.html'
VIEWPORT = {'width': 1440, 'height': 900}
DEVICE_SCALE = 2
ASSET_BASE = os.environ.get('SCREENSHOT_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')


def load_seed_module():
    import importlib.util

    path = ROOT / 'scripts' / 'seed_demo_estudio.py'
    spec = importlib.util.spec_from_file_location('seed_demo_estudio', path)
    if not spec or not spec.loader:
        raise RuntimeError('seed_demo_estudio não encontrado')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ensure_demo_password(email: str, password: str) -> None:
    from db import update_user_password_by_email

    if not update_user_password_by_email(email, password):
        raise RuntimeError(f'Não foi possível atualizar senha de {email}')


def fetch_finance_html(studio_id: str, user_id: str) -> str:
    from flask import session

    from app import app
    from blueprints.studios import owner_finance

    with app.test_request_context(
        f'/estudios/{studio_id}/financeiro?mes=6&ano=2026',
        headers={'Host': 'setsync.com.br'},
    ):
        session['user_id'] = user_id
        resp = owner_finance(studio_id)
        if isinstance(resp, str):
            html = resp
        else:
            if resp.status_code != 200:
                raise RuntimeError(f'Financeiro retornou HTTP {resp.status_code}')
            html = resp.get_data(as_text=True)
    if '<base ' not in html:
        html = html.replace('<head>', f'<head><base href="{ASSET_BASE}/">', 1)
    html = html.replace('<html', '<html data-theme="dark"', 1)
    return html


def main() -> int:
    seed = load_seed_module()
    seed.main()

    from db import get_user_by_username, init_db, set_privacy_accepted
    from models_studio import list_studios_by_owner

    init_db()
    user = get_user_by_username(seed.DEMO_USERNAME)
    if not user:
        print('Usuário demo não encontrado', file=sys.stderr)
        return 1
    set_privacy_accepted(user['id'])
    ensure_demo_password(seed.DEMO_EMAIL, seed.DEMO_PASSWORD)
    from db import update_user_profile
    update_user_profile(user['id'], display_name=seed.DEMO_DISPLAY, phone='85999999999')
    studios = list_studios_by_owner(user['id'])
    if not studios:
        print('Estúdio demo não encontrado', file=sys.stderr)
        return 1
    studio_id = studios[0]['id']

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(fetch_finance_html(studio_id, user['id']), encoding='utf-8')

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=DEVICE_SCALE,
            color_scheme='dark',
        )
        page = context.new_page()
        page.goto(HTML_PATH.as_uri(), wait_until='networkidle', timeout=120_000)
        page.wait_for_selector('text=Financeiro', timeout=60_000)
        page.wait_for_timeout(500)
        page.locator('main').screenshot(path=str(OUT_PATH), type='png')
        browser.close()

    HTML_PATH.unlink(missing_ok=True)

    print(f'Gerado {OUT_PATH} — {OUT_PATH.stat().st_size // 1024} KB')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
