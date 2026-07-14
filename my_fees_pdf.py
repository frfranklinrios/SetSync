"""Gera PDF do relatório pessoal de cachês via Playwright/Chromium."""

from __future__ import annotations

import os
from urllib.parse import urlencode

from studio_finance_pdf import period_label


def build_my_fees_pdf_download_name(year: int, month: int, band_name: str | None = None) -> str:
    base = f'Meu financeiro {period_label(year, month)}'
    if band_name:
        from band_finance_pdf import safe_filename
        return f'{base} — {safe_filename(band_name)}.pdf'
    return f'{base}.pdf'


def build_my_fees_pdf_url(
    user_id: str,
    *,
    year: int,
    month: int,
    band_id: str | None = None,
    base_url: str | None = None,
) -> str:
    from security import make_my_fees_pdf_token

    token = make_my_fees_pdf_token(user_id)
    internal = (base_url or os.getenv('SETSYNC_INTERNAL_URL') or 'http://127.0.0.1:5000').rstrip('/')
    params = {
        'ano': year,
        'mes': month,
        'pdfgen': '1',
        'pdf_token': token,
    }
    if band_id:
        params['banda_id'] = band_id
    return f'{internal}/bands/meus-caches/imprimir?{urlencode(params)}'


def generate_my_fees_pdf_bytes(
    user_id: str,
    *,
    year: int,
    month: int,
    band_id: str | None = None,
) -> bytes:
    from setlist_pdf import render_url_to_pdf

    return render_url_to_pdf(
        build_my_fees_pdf_url(user_id, year=year, month=month, band_id=band_id),
        landscape=False,
    )
