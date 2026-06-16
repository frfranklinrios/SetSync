"""Cifra de referência (biblioteca) vs versão editada pela banda."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def _norm_text(value: str | None) -> str:
    return (value or '').replace('\r\n', '\n').strip()


def _json_norm(raw: str | list | dict | None) -> str:
    if raw is None or raw == '':
        return ''
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return _norm_text(str(raw))
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def parse_referencia(cifra: dict | None) -> dict[str, Any] | None:
    if not cifra:
        return None
    raw = cifra.get('referencia_json')
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def referencia_label(cifra: dict | None) -> str | None:
    """Rótulo discreto da referência (sem URL externa)."""
    ref = parse_referencia(cifra)
    if not ref:
        return None
    source = (ref.get('source') or '').strip().lower()
    if source in ('api-cifras', 'biblioteca'):
        return 'Biblioteca de cifras'
    if source:
        return 'Versão importada'
    return None


def referencia_diverged(cifra: dict | None) -> bool:
    ref = parse_referencia(cifra)
    if not ref or not cifra:
        return False

    if _norm_text(cifra.get('conteudo')) != _norm_text(ref.get('conteudo')):
        return True
    if _json_norm(cifra.get('cifra_json')) != _json_norm(ref.get('cifra_json')):
        return True
    if _json_norm(cifra.get('grade_json')) != _json_norm(ref.get('grade_json')):
        return True
    if _norm_text(cifra.get('tom_original')) != _norm_text(ref.get('tom_original')):
        return True
    return False


def build_referencia_snapshot(
    *,
    source: str,
    titulo: str,
    artista: str,
    tom_original: str,
    conteudo: str,
    cifra_json: str | None,
    grade_json: str | None,
    meta: dict[str, Any] | None = None,
) -> str:
    payload = {
        'source': source,
        'titulo': titulo,
        'artista': artista,
        'tom_original': tom_original,
        'conteudo': conteudo or '',
        'cifra_json': cifra_json,
        'grade_json': grade_json,
        'meta': {
            **(meta or {}),
            'saved_at': datetime.now(timezone.utc).isoformat(),
        },
    }
    return json.dumps(payload, ensure_ascii=False)


def meta_from_import_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'artist_slug': payload.get('artist_slug') or '',
        'song_slug': payload.get('song_slug') or '',
        'url_cifra': payload.get('url_cifra') or '',
        'cached': bool(payload.get('cached')),
    }


def restore_fields_from_referencia(ref: dict[str, Any]) -> dict[str, Any]:
    return {
        'titulo': (ref.get('titulo') or '').strip(),
        'artista': (ref.get('artista') or '').strip(),
        'tom_original': (ref.get('tom_original') or 'C').strip(),
        'conteudo': ref.get('conteudo') or '',
        'cifra_json': ref.get('cifra_json'),
        'grade_json': ref.get('grade_json'),
        'leadsheet_json': None,
    }
