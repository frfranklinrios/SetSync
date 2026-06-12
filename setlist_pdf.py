"""Gera PDF da setlist (folha de palco + cifras) via Playwright/Chromium."""
from __future__ import annotations

import os
import re
from urllib.parse import urlparse


def _safe_filename(name: str, max_len: int = 80) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', (name or 'setlist').strip())
    s = re.sub(r'\s+', ' ', s).strip()
    return (s[:max_len] if len(s) > max_len else s) or 'setlist'


def render_url_to_pdf(
    url: str,
    cookies=None,
    *,
    timeout_ms: int = 120_000,
) -> bytes:
    """Abre a URL e devolve bytes do PDF A4 retrato (sem cookies de sessão por padrão)."""
    from playwright.sync_api import sync_playwright

    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError('URL de PDF inválida')
    if not parsed.netloc:
        raise ValueError('URL de PDF sem host')

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

        host = parsed.netloc.split(':')[0] or 'SetSync'
        pdf = page.pdf(
            format='A4',
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template=(
                '<div style="width:100%;font-size:8px;color:#64748b;padding:0 12mm;'
                'font-family:Inter,Helvetica,Arial,sans-serif;text-align:center;">'
                f'SetSync · {host}</div>'
            ),
            footer_template=(
                '<div style="width:100%;font-size:8px;color:#94a3b8;padding:0 12mm;'
                'font-family:Inter,Helvetica,Arial,sans-serif;text-align:center;">'
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


def build_setlist_pdf_url(
    setlist_id: str,
    user_id: str,
    *,
    cols: str = '2',
    sections: dict[str, bool] | None = None,
    base_url: str | None = None,
) -> str:
    """URL interna da página de impressão para captura em PDF."""
    from security import make_pdf_access_token

    token = make_pdf_access_token(setlist_id, user_id)
    internal = (base_url or os.getenv('SETSYNC_INTERNAL_URL') or 'http://127.0.0.1:5000').rstrip('/')
    cols = '1' if str(cols) == '1' else '2'
    parts = [f'cols={cols}', 'pdfgen=1', f'pdf_token={token}']
    if sections:
        for key, on in sections.items():
            if on:
                parts.append(f'{key}=1')
    return f'{internal}/setlists/{setlist_id}/imprimir?' + '&'.join(parts)


def generate_setlist_pdf_bytes(
    setlist_id: str,
    user_id: str,
    *,
    cols: str = '2',
    sections: dict[str, bool] | None = None,
) -> bytes:
    """PDF A4 com seções selecionadas (índice, cifras, letras, chord sheet)."""
    return render_url_to_pdf(
        build_setlist_pdf_url(setlist_id, user_id, cols=cols, sections=sections)
    )
