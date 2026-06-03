"""Geração de QR Code (PNG) para links públicos."""
from __future__ import annotations

import io


def qrcode_png_bytes(url: str, *, box_size: int = 8, border: int = 2) -> bytes:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M

    if not (url or '').strip():
        raise ValueError('URL vazia')

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url.strip())
    qr.make(fit=True)
    img = qr.make_image(fill_color='#0f172a', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
