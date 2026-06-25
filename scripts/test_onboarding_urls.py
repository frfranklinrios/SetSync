#!/usr/bin/env python3
"""Garante que links do onboarding resolvem endpoints Flask válidos."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app import app
    from db import get_db

    with app.app_context(), app.test_request_context('/dashboard'):
        c = app.test_client()
        c.get('/health')

        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT id FROM users LIMIT 1')
        row = cur.fetchone()
        if not row:
            print('SKIP: sem usuários')
            return 0
        user_id = row['id']

        from onboarding import get_onboarding_progress

        progress = get_onboarding_progress(user_id)
        if progress:
            for step in progress['steps']:
                url = step['url']
                assert url.startswith('/'), url
                path = url.split('#')[0]
                resp = c.get(path, follow_redirects=False)
                assert resp.status_code < 500, f"{step['id']} {path} -> {resp.status_code}"

        from studio_onboarding import get_studio_onboarding_progress
        from models_studio import list_studios_by_owner

        for studio in list_studios_by_owner(user_id)[:1]:
            prog = get_studio_onboarding_progress(studio)
            if prog:
                for step in prog['steps']:
                    path = step['url'].split('#')[0]
                    resp = c.get(path, follow_redirects=False)
                    assert resp.status_code < 500, f"studio {step['id']} {path} -> {resp.status_code}"

        with c.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = 'smoke'
        resp = c.get('/dashboard', follow_redirects=False)
        assert resp.status_code < 500, f'dashboard -> {resp.status_code}'
        if resp.status_code in (301, 302, 303):
            resp2 = c.get(resp.headers.get('Location', '/dashboard'), follow_redirects=True)
            assert resp2.status_code < 500, f'dashboard redirect -> {resp2.status_code}'

    print('OK onboarding_urls')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
