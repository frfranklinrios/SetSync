"""Gera PDF da setlist (folha de palco + cifras) via Playwright/Chromium."""
from __future__ import annotations

import re
from urllib.parse import urlparse


def _safe_filename(name: str, max_len: int = 80) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', (name or 'setlist').strip())
    s = re.sub(r'\s+', ' ', s).strip()
    return (s[:max_len] if len(s) > max_len else s) or 'setlist'


def playwright_cookies_from_flask_request(req):
    """Repasse cookies da sessão Flask para o Chromium."""
    host = (req.host or 'localhost').split(':')[0]
    secure = req.is_secure or req.headers.get('X-Forwarded-Proto', '').lower() == 'https'
    cookies = []
    for name, value in req.cookies.items():
        cookies.append({
            'name': name,
            'value': value,
            'domain': host,
            'path': '/',
            'secure': bool(secure),
        })
    return cookies


def render_url_to_pdf(
    url: str,
    cookies=None,
    *,
    timeout_ms: int = 120_000,
) -> bytes:
    """Abre a URL (com sessão) e devolve bytes do PDF A4 retrato."""
    from playwright.sync_api import sync_playwright

    cookies = cookies or []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 794, 'height': 1123},
            device_scale_factor=1,
        )
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()
        page.goto(url, wait_until='networkidle', timeout=timeout_ms)
        try:
            page.wait_for_selector('[data-pdf-ready="1"]', timeout=20_000)
        except Exception:
            try:
                page.wait_for_function(
                    'document.fonts && document.fonts.ready',
                    timeout=15_000,
                )
            except Exception:
                pass
            page.evaluate(
                """() => {
                    document.querySelectorAll('.setlist-print-song').forEach(sec => {
                        const sheet = sec.querySelector('.setlist-print-sheet');
                        if (sheet && sheet.offsetHeight > 680) sec.classList.add('is-long');
                    });
                }"""
            )
        page.wait_for_timeout(250)

        host = urlparse(url).netloc.split(':')[0] or 'SetSync'
        pdf = page.pdf(
            format='A4',
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template=(
                '<div style="width:100%;font-size:8px;color:#64748b;padding:0 12mm;'
                'font-family:system-ui,sans-serif;text-align:center;">'
                f'SetSync · {host}</div>'
            ),
            footer_template=(
                '<div style="width:100%;font-size:8px;color:#94a3b8;padding:0 12mm;'
                'font-family:system-ui,sans-serif;text-align:center;">'
                'Página <span class="pageNumber"></span> de <span class="totalPages"></span>'
                '</div>'
            ),
            margin={
                'top': '16mm',
                'bottom': '16mm',
                'left': '11mm',
                'right': '11mm',
            },
        )
        context.close()
        browser.close()
        return pdf


def build_pdf_download_name(setlist_name: str, band_name: str | None = None) -> str:
    parts = [_safe_filename(setlist_name)]
    if band_name:
        parts.insert(0, _safe_filename(band_name))
    return ' — '.join(parts) + '.pdf'
