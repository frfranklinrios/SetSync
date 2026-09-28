"""Payload EMV (BR Code) para Pix estático — sem intermediação."""

from __future__ import annotations

import re
from io import BytesIO


def _tlv(tag: str, value: str) -> str:
    value = value or ''
    return f'{tag}{len(value):02d}{value}'


def _crc16_ccitt(payload: str) -> str:
    crc = 0xFFFF
    for ch in payload.encode('utf-8'):
        crc ^= ch << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f'{crc:04X}'


def normalize_pix_key(chave: str) -> str:
    raw = (chave or '').strip()
    digits = re.sub(r'\D+', '', raw)
    if '@' in raw:
        return raw.lower()
    if re.fullmatch(r'[0-9a-fA-F-]{36}', raw):
        return raw.lower()
    if len(digits) in (11, 14):
        return digits
    if digits.startswith('55') and len(digits) in (12, 13):
        return digits
    return raw


def build_pix_payload(
    *,
    chave: str,
    nome: str,
    cidade: str = 'SAO PAULO',
    valor: float | None = None,
    mensagem: str = '',
    txid: str = '***',
) -> str:
    """Monta BR Code estático. O Pix cai direto na chave informada."""
    key = normalize_pix_key(chave)
    if not key:
        raise ValueError('Chave Pix obrigatória')

    merchant_name = re.sub(r'[^A-Za-z0-9 ]+', '', (nome or 'BANDA')[:25]).strip().upper() or 'BANDA'
    merchant_city = re.sub(r'[^A-Za-z0-9 ]+', '', (cidade or 'SAO PAULO')[:15]).strip().upper() or 'SAO PAULO'
    guima = _tlv('00', 'br.gov.bcb.pix') + _tlv('01', key)
    desc = (mensagem or '').strip()[:50]
    if desc:
        guima += _tlv('02', desc)

    parts = [
        _tlv('00', '01'),
        _tlv('01', '11'),
        _tlv('26', guima),
        _tlv('52', '0000'),
        _tlv('53', '986'),
    ]
    if valor is not None and float(valor) > 0:
        parts.append(_tlv('54', f'{float(valor):.2f}'))
    parts.extend([
        _tlv('58', 'BR'),
        _tlv('59', merchant_name),
        _tlv('60', merchant_city),
        _tlv('62', _tlv('05', (txid or '***')[:25])),
    ])
    body = ''.join(parts) + '6304'
    return body + _crc16_ccitt(body)


def qrcode_data_uri(payload: str, *, box_size: int = 6) -> str:
    import base64
    import qrcode

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/png;base64,{b64}'
