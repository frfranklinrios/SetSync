"""Gera PDF do relatório financeiro da banda via Playwright/Chromium."""

from __future__ import annotations

import os
import re

from studio_finance_pdf import period_label


def _safe_filename(name: str, max_len: int = 72) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', (name or 'banda').strip())
    s = re.sub(r'\s+', ' ', s).strip()
    return (s[:max_len] if len(s) > max_len else s) or 'banda'


def build_finance_pdf_download_name(band_name: str, year: int, month: int) -> str:
    return f'{_safe_filename(band_name)} — Financeiro {period_label(year, month)}.pdf'


def build_band_finance_pdf_url(
    band_id: str,
    user_id: str,
    *,
    year: int,
    month: int,
    base_url: str | None = None,
) -> str:
    from security import make_band_finance_pdf_token

    token = make_band_finance_pdf_token(band_id, user_id)
    internal = (base_url or os.getenv('SETSYNC_INTERNAL_URL') or 'http://127.0.0.1:5000').rstrip('/')
    return (
        f'{internal}/bands/{band_id}/financeiro/imprimir'
        f'?ano={year}&mes={month}&pdfgen=1&pdf_token={token}'
    )


def generate_band_finance_pdf_bytes(
    band_id: str,
    user_id: str,
    *,
    year: int,
    month: int,
) -> bytes:
    from setlist_pdf import render_url_to_pdf

    return render_url_to_pdf(
        build_band_finance_pdf_url(band_id, user_id, year=year, month=month),
        landscape=True,
    )
