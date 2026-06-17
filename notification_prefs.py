"""Categorias e preferências de notificação por canal (push, e-mail, WhatsApp)."""

from __future__ import annotations

import json
from typing import Any

NOTIFICATION_CHANNELS = ('push', 'email', 'whatsapp')

NOTIFICATION_CATEGORIES: dict[str, dict[str, Any]] = {
    'escalacao': {
        'label': 'Escalação',
        'description': 'Convites para tocar, respostas e substitutos',
        'types': frozenset({
            'event_scale_assigned',
            'event_scale_accepted',
            'event_scale_declined',
            'event_scale_substitute_offer',
        }),
    },
    'agenda': {
        'label': 'Agenda',
        'description': 'Eventos criados, alterados, cancelados e lembretes',
        'types': frozenset({
            'event_created',
            'event_updated',
            'event_deleted',
            'event_reminder',
        }),
    },
    'convites': {
        'label': 'Convites de banda',
        'description': 'Convites para entrar na banda e novos integrantes',
        'types': frozenset({
            'band_invite',
            'band_invite_declined',
            'member_joined',
            'member_removed',
        }),
    },
    'cifras': {
        'label': 'Cifras',
        'description': 'Músicas adicionadas, editadas ou removidas',
        'types': frozenset({'cifra_created', 'cifra_updated', 'cifra_deleted'}),
    },
    'setlists': {
        'label': 'Setlists',
        'description': 'Setlists criados, alterados ou excluídos',
        'types': frozenset({'setlist_created', 'setlist_deleted', 'setlist_updated'}),
    },
    'banda': {
        'label': 'Banda',
        'description': 'Alterações no perfil da banda e cantores',
        'types': frozenset({'band_updated', 'vocalist_added', 'vocalist_removed'}),
    },
    'produto': {
        'label': 'Novidades',
        'description': 'Comunicados e atualizações do SetSync',
        'types': frozenset({'product_update'}),
    },
}

_TYPE_TO_CATEGORY: dict[str, str] = {}
for _cat_id, _meta in NOTIFICATION_CATEGORIES.items():
    for _t in _meta['types']:
        _TYPE_TO_CATEGORY[_t] = _cat_id


def notification_category(notification_type: str) -> str | None:
    if not notification_type or notification_type.startswith('admin_'):
        return None
    return _TYPE_TO_CATEGORY.get(notification_type)


def default_category_prefs() -> dict[str, dict[str, bool]]:
    """Padrão: tudo ligado; push de cifras desligado (muito frequente)."""
    out: dict[str, dict[str, bool]] = {}
    for cat_id in NOTIFICATION_CATEGORIES:
        out[cat_id] = {
            'push': cat_id != 'cifras',
            'email': True,
            'whatsapp': True,
        }
    return out


def default_notification_prefs() -> dict[str, Any]:
    return {'categories': default_category_prefs()}


def parse_notification_prefs(raw: str | dict | None) -> dict[str, Any]:
    if isinstance(raw, dict):
        data = raw
    elif raw:
        try:
            data = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            data = {}
    else:
        data = {}
    base = default_notification_prefs()
    cats_in = data.get('categories') if isinstance(data.get('categories'), dict) else {}
    for cat_id in NOTIFICATION_CATEGORIES:
        merged = dict(base['categories'][cat_id])
        user_cat = cats_in.get(cat_id)
        if isinstance(user_cat, dict):
            for ch in NOTIFICATION_CHANNELS:
                if ch in user_cat:
                    merged[ch] = bool(user_cat[ch])
        base['categories'][cat_id] = merged
    return base


def category_channel_enabled(
    prefs: dict[str, Any],
    category: str,
    channel: str,
) -> bool:
    cats = prefs.get('categories') or {}
    cat_prefs = cats.get(category) or default_category_prefs().get(category, {})
    return bool(cat_prefs.get(channel, True))


def serialize_notification_prefs(prefs: dict[str, Any]) -> str:
    normalized = parse_notification_prefs(prefs)
    return json.dumps(normalized, ensure_ascii=False, separators=(',', ':'))
