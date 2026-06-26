"""Gera PDF do relatório financeiro do estúdio via Playwright/Chromium."""

from __future__ import annotations

import os
import re

from studio_finance import month_bounds


def _safe_filename(name: str, max_len: int = 72) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', (name or 'estudio').strip())
    s = re.sub(r'\s+', ' ', s).strip()
    return (s[:max_len] if len(s) > max_len else s) or 'estudio'


MONTH_NAMES = (
    '',
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
)


def period_label(year: int, month: int) -> str:
    name = MONTH_NAMES[month] if 1 <= month <= 12 else str(month)
    return f'{name} {year}'


def build_finance_pdf_download_name(studio_name: str, year: int, month: int) -> str:
    return f'{_safe_filename(studio_name)} — Financeiro {period_label(year, month)}.pdf'


def build_studio_finance_pdf_url(
    studio_id: str,
    user_id: str,
    *,
    year: int,
    month: int,
    base_url: str | None = None,
) -> str:
    from security import make_studio_finance_pdf_token

    token = make_studio_finance_pdf_token(studio_id, user_id)
    internal = (base_url or os.getenv('SETSYNC_INTERNAL_URL') or 'http://127.0.0.1:5000').rstrip('/')
    return (
        f'{internal}/estudios/{studio_id}/financeiro/imprimir'
        f'?ano={year}&mes={month}&pdfgen=1&pdf_token={token}'
    )


def generate_studio_finance_pdf_bytes(
    studio_id: str,
    user_id: str,
    *,
    year: int,
    month: int,
) -> bytes:
    from setlist_pdf import render_url_to_pdf

    return render_url_to_pdf(
        build_studio_finance_pdf_url(studio_id, user_id, year=year, month=month),
        landscape=True,
    )
