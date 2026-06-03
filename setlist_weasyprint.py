"""Geração de PDF de setlist com WeasyPrint."""

from __future__ import annotations

from datetime import datetime

from flask import render_template


def render_setlist_pdf_html(app, data: dict) -> str:
    """Renderiza HTML para conversão em PDF."""
    with app.app_context():
        return render_template(
            'pdf/setlist.html',
            setlist=data['setlist'],
            band=data['band'],
            sheets=data.get('sheets', []),
            printed_at=data.get('printed_at') or datetime.now(),
            band_logo_data_uri=data.get('band_logo_data_uri'),
        )


def html_to_pdf_bytes(html: str) -> bytes:
    from weasyprint import HTML
    return HTML(string=html, base_url='.').write_pdf()
