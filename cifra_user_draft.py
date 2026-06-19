"""Rascunhos pessoais de cifra — versão do usuário vs versão oficial da banda."""

from __future__ import annotations

import json
from typing import Any

from cifra_referencia import _json_norm, _norm_text

_DRAFT_FIELDS = (
    'titulo',
    'artista',
    'tom_original',
    'conteudo',
    'cifra_json',
    'grade_json',
    'leadsheet_json',
)


def draft_payload_from_form(data: dict[str, Any]) -> dict[str, Any]:
    """Normaliza campos vindos do formulário ou JSON da API."""
    out: dict[str, Any] = {}
    for key in _DRAFT_FIELDS:
        if key not in data:
            continue
        val = data.get(key)
        if key in ('cifra_json', 'grade_json', 'leadsheet_json') and val is not None:
            if not isinstance(val, str):
                val = json.dumps(val, ensure_ascii=False)
        out[key] = val
    return out


def draft_differs_from_band(draft: dict | None, cifra: dict | None) -> bool:
    if not draft or not cifra:
        return False
    if _norm_text(draft.get('conteudo')) != _norm_text(cifra.get('conteudo')):
        return True
    if _json_norm(draft.get('cifra_json')) != _json_norm(cifra.get('cifra_json')):
        return True
    if _json_norm(draft.get('grade_json')) != _json_norm(cifra.get('grade_json')):
        return True
    if _json_norm(draft.get('leadsheet_json')) != _json_norm(cifra.get('leadsheet_json')):
        return True
    if _norm_text(draft.get('tom_original')) != _norm_text(cifra.get('tom_original')):
        return True
    if _norm_text(draft.get('titulo')) != _norm_text(cifra.get('titulo')):
        return True
    if _norm_text(draft.get('artista')) != _norm_text(cifra.get('artista')):
        return True
    return False


def merge_cifra_with_draft(cifra: dict, draft: dict | None) -> dict:
    """Sobrepõe campos do rascunho sobre a cifra oficial."""
    if not draft:
        return dict(cifra)
    merged = dict(cifra)
    for key in _DRAFT_FIELDS:
        val = draft.get(key)
        if val is not None and val != '':
            merged[key] = val
    return merged


def cifra_dict_from_import(data: dict[str, Any]) -> dict[str, Any]:
    """Monta dict compatível com prepare_cifra_sheet a partir de pacote importado."""
    cifra_json = data.get('cifra_json')
    grade_json = data.get('grade_json')
    if cifra_json is not None and not isinstance(cifra_json, str):
        cifra_json = json.dumps(cifra_json, ensure_ascii=False)
    if grade_json is not None and not isinstance(grade_json, str):
        grade_json = json.dumps(grade_json, ensure_ascii=False)
    return {
        'titulo': (data.get('titulo') or '').strip() or 'Sem título',
        'artista': (data.get('artista') or '').strip(),
        'tom_original': (data.get('tom_original') or data.get('tom') or 'C').strip(),
        'conteudo': data.get('conteudo') or '',
        'cifra_json': cifra_json,
        'grade_json': grade_json,
        'leadsheet_json': None,
        'bpm': data.get('bpm'),
        'duracao_seg': data.get('duracao_seg'),
    }
