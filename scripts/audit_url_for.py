#!/usr/bin/env python3
"""Audita url_for() em templates e Python contra endpoints Flask registrados."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PATTERN = re.compile(r"""url_for\(\s*['"]([a-zA-Z0-9_\.]+)['"]""")
SKIP_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', 'data'}
EXTRA_ENDPOINTS = {
    'index', 'dashboard', 'manifest', 'sitemap', 'robots_txt',
    'google_site_verification', 'health', 'offline', 'comece',
    'login_redirect', 'exportar_setlist_pdf',
}


def collect_refs() -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for path in ROOT.rglob('*'):
        if path.suffix not in ('.html', '.py'):
            continue
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.name == 'audit_url_for.py':
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        if 'url_for(' not in text:
            continue
        rel = str(path.relative_to(ROOT))
        for m in PATTERN.finditer(text):
            ep = m.group(1)
            if ep == 'static':
                continue
            refs.setdefault(ep, []).append(rel)
    return refs


def main() -> int:
    from app import app

    registered = {r.endpoint for r in app.url_map.iter_rules()} | EXTRA_ENDPOINTS
    refs = collect_refs()
    broken = {ep: files for ep, files in sorted(refs.items()) if ep not in registered}

    print(f'Endpoints referenciados: {len(refs)}')
    print(f'Endpoints registrados:   {len(registered)}')
    if not broken:
        print('Nenhum url_for quebrado encontrado.')
        return 0
    print(f'\nQUEBRADOS ({len(broken)}):')
    for ep, files in broken.items():
        print(f'  {ep}')
        for f in sorted(set(files)):
            print(f'    - {f}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
