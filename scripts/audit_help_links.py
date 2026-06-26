#!/usr/bin/env python3
"""Audita links internos em ajuda, guia, FAQ e posts do blog."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_AJUDA_ANCHOR_RE = re.compile(r'href="/ajuda#([a-z0-9-]+)"')
_INTERNAL_PATH_RE = re.compile(r'href="(/[^"#?]+)"')


def _ajuda_section_ids() -> set[str]:
    from bs4 import BeautifulSoup

    html = (ROOT / 'templates/ajuda/index.html').read_text(encoding='utf-8')
    html = re.sub(r'\{%.*?%\}', '', html, flags=re.DOTALL)
    html = re.sub(r'\{\{.*?\}\}', '', html, flags=re.DOTALL)
    soup = BeautifulSoup(html, 'html.parser')
    ids = {el.get('id') for el in soup.find_all(id=True) if el.get('id')}
    return {i for i in ids if i}


def _collect_internal_paths() -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    files = [
        ROOT / 'content_seed.py',
        ROOT / 'seo_pages.py',
        ROOT / 'help_chatbot.py',
        ROOT / 'templates/guia/index.html',
        ROOT / 'templates/blog/index.html',
    ]
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        rel = str(path.relative_to(ROOT))
        for m in _INTERNAL_PATH_RE.finditer(text):
            p = m.group(1)
            if p.startswith('/static'):
                continue
            refs.setdefault(p, []).append(rel)
        for m in _AJUDA_ANCHOR_RE.finditer(text):
            refs.setdefault(f'/ajuda#{m.group(1)}', []).append(rel)
    return refs


def main() -> int:
    from app import app

    ajuda_ids = _ajuda_section_ids()
    errors: list[str] = []

    for anchor in _AJUDA_ANCHOR_RE.findall(
        (ROOT / 'content_seed.py').read_text(encoding='utf-8', errors='ignore')
    ):
        if anchor not in ajuda_ids:
            errors.append(f'Âncora /ajuda#{anchor} inexistente (content_seed.py)')

    with app.test_client() as client:
        key_paths = [
            '/', '/bandas', '/ajuda', '/guia', '/blog', '/roadmap', '/igrejas',
            '/planos', '/assinatura/planos', '/estudios/buscar', '/estudios',
        ]
        for path in key_paths:
            resp = client.get(path, follow_redirects=False)
            if resp.status_code in (301, 302, 303, 307, 308):
                loc = resp.headers.get('Location', '')
                if loc.startswith('http'):
                    continue
                resp = client.get(loc, follow_redirects=False)
            if resp.status_code >= 400:
                errors.append(f'{path} → HTTP {resp.status_code}')

        from seo_pages import list_seo_pages, _PREMIUM_SLUGS

        for page in list_seo_pages():
            if page['slug'] not in _PREMIUM_SLUGS:
                continue
            resp = client.get(f'/guia/{page["slug"]}', follow_redirects=False)
            if resp.status_code >= 400:
                errors.append(f'/guia/{page["slug"]} → HTTP {resp.status_code}')

        from db import list_blog_posts

        for post in list_blog_posts(published_only=True):
            resp = client.get(f'/blog/{post["slug"]}', follow_redirects=False)
            if resp.status_code >= 400:
                errors.append(f'/blog/{post["slug"]} → HTTP {resp.status_code}')

        resp = client.get('/planos', follow_redirects=False)
        if resp.status_code not in (301, 302):
            errors.append(f'/planos → esperado 301, obteve {resp.status_code}')

    from scripts.audit_url_for import collect_refs

    registered = {r.endpoint for r in app.url_map.iter_rules()}
    for ep, files in collect_refs().items():
        if ep not in registered and ep != 'static':
            if 'help_chatbot.py' in files or 'templates/guia' in ' '.join(files):
                errors.append(f'url_for quebrado: {ep} em {", ".join(sorted(set(files))[:3])}')

    if errors:
        print(f'Falhas ({len(errors)}):')
        for e in errors:
            print(' -', e)
        return 1
    print('OK: ajuda, guia, blog, FAQ e links internos verificados.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
