"""Gorjeta Pix — QR estático; 100% do valor vai para a chave do músico."""

from __future__ import annotations

import json
import re
from typing import Any

from pix_emv import build_pix_payload, normalize_pix_key, qrcode_data_uri

_SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,40}$')
_DEFAULT_VALORES = [10, 20, 50]


def slugify_band_name(name: str) -> str:
    raw = (name or '').strip().lower()
    raw = re.sub(r'[^a-z0-9]+', '-', raw)
    raw = re.sub(r'-{2,}', '-', raw).strip('-')
    return (raw or 'banda')[:40]


def parse_valores_sugeridos(raw: str | None) -> list[int]:
    if not raw:
        return list(_DEFAULT_VALORES)
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            out = []
            for v in data:
                try:
                    n = int(float(v))
                except (TypeError, ValueError):
                    continue
                if 1 <= n <= 5000:
                    out.append(n)
            return out[:6] or list(_DEFAULT_VALORES)
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    out = []
    for part in re.split(r'[,;\s]+', str(raw)):
        if not part:
            continue
        try:
            n = int(float(part.replace(',', '.')))
        except ValueError:
            continue
        if 1 <= n <= 5000:
            out.append(n)
    return out[:6] or list(_DEFAULT_VALORES)


def valores_to_storage(valores: list[int] | None) -> str:
    vals = valores or _DEFAULT_VALORES
    return json.dumps([int(v) for v in vals[:6]])


def banda_gorjeta_pronta(band: dict | None) -> bool:
    if not band:
        return False
    if not int(band.get('gorjeta_enabled') or 0):
        return False
    return bool(normalize_pix_key(band.get('pix_chave') or ''))


def montar_gorjeta_qr(
    band: dict,
    *,
    valor: float | None = None,
) -> dict[str, Any]:
    chave = normalize_pix_key(band.get('pix_chave') or '')
    if not chave:
        raise ValueError('Configure a chave Pix da banda')
    nome = (band.get('name') or 'Banda')[:25]
    msg = (band.get('gorjeta_mensagem') or f'Gorjeta {nome}')[:50]
    payload = build_pix_payload(
        chave=chave,
        nome=nome,
        mensagem=msg,
        valor=valor,
    )
    return {
        'payload': payload,
        'qr_data_uri': qrcode_data_uri(payload),
        'chave': chave,
        'mensagem': msg,
        'valor': valor,
        'valores': parse_valores_sugeridos(band.get('gorjeta_valores')),
        'slug': (band.get('gorjeta_slug') or '').strip(),
        'band_name': band.get('name') or 'Banda',
    }


def validate_gorjeta_slug(slug: str) -> str | None:
    s = (slug or '').strip().lower()
    if not s:
        return 'Informe um link curto (ex.: minha-banda).'
    if not _SLUG_RE.match(s):
        return 'Use só letras minúsculas, números e hífen (2–41 caracteres).'
    return None
