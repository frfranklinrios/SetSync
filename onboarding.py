"""Progresso de onboarding e ativação pós-cadastro."""

from __future__ import annotations

from db import (
    count_band_cifras,
    count_band_setlists,
    get_owned_bands,
    get_user_bands,
    user_onboarding_checklist_dismissed,
    user_play_mode_used,
)
from flask import url_for


def user_has_any_band(user_id: str) -> bool:
    """True se o usuário administra ou participa de alguma banda."""
    if get_owned_bands(user_id):
        return True
    return bool(get_user_bands(user_id))


def user_needs_band_activation(user_id: str) -> bool:
    """Usuário sem banda e sem convite pendente — precisa criar ou aceitar convite."""
    from db import is_superadmin

    if is_superadmin(user_id):
        return False
    if user_has_any_band(user_id):
        return False
    from band_member_invites import list_pending_invites_for_user

    return not list_pending_invites_for_user(user_id)


def get_onboarding_progress(user_id: str) -> dict | None:
    """Checklist de ativação para o dashboard. None se oculto ou concluído."""
    from db import is_superadmin

    if is_superadmin(user_id):
        return None
    if user_onboarding_checklist_dismissed(user_id):
        return None

    owned = get_owned_bands(user_id)
    member_bands = get_user_bands(user_id)
    # Preferir banda própria; senão a primeira em que participa
    bands = owned or member_bands

    has_band = bool(bands)
    total_cifras = sum(count_band_cifras(b['id']) for b in bands) if bands else 0
    total_setlists = sum(count_band_setlists(b['id']) for b in bands) if bands else 0

    first_band_id = bands[0]['id'] if bands else None
    first_cifra_id = None
    if first_band_id and total_cifras:
        from db import get_band_cifras

        rows = get_band_cifras(first_band_id)
        if rows:
            first_cifra_id = rows[0]['id']

    band_url = (
        url_for('bands.view', band_id=first_band_id)
        if has_band
        else url_for('bands.create', bem_vindo=1)
    )
    cifra_url = (
        url_for('cifras.add', band_id=first_band_id)
        if first_band_id
        else url_for('bands.create', bem_vindo=1)
    )
    setlist_url = (
        url_for('setlists.create', band_id=first_band_id)
        if first_band_id
        else url_for('bands.create', bem_vindo=1)
    )
    if first_band_id and first_cifra_id:
        tocar_url = url_for('cifras.tocar_band', band_id=first_band_id, start=first_cifra_id)
    elif first_band_id and total_cifras:
        tocar_url = url_for('cifras.tocar_band', band_id=first_band_id)
    elif first_band_id:
        tocar_url = cifra_url
    else:
        tocar_url = url_for('bands.create', bem_vindo=1)

    # Funil curto até o valor principal (tocar no ensaio/culto). Agenda fica opcional.
    steps = [
        {
            'id': 'band',
            'label': '1. Criar sua banda',
            'hint': 'É o espaço da sua equipe — cifras e setlists ficam juntos.',
            'done': has_band,
            'url': band_url,
        },
        {
            'id': 'cifra',
            'label': '2. Adicionar a primeira música',
            'hint': 'Cole uma cifra ou importe — leva menos de um minuto.',
            'done': total_cifras > 0,
            'url': cifra_url,
        },
        {
            'id': 'setlist',
            'label': '3. Montar um setlist',
            'hint': 'A ordem das músicas do ensaio ou do culto.',
            'done': total_setlists > 0,
            'url': setlist_url,
        },
        {
            'id': 'tocar',
            'label': '4. Abrir o Modo Tocar',
            'hint': 'Tela limpa para o palco — sem distrações.',
            'done': user_play_mode_used(user_id),
            'url': tocar_url,
        },
    ]

    done_count = sum(1 for s in steps if s['done'])
    if done_count == len(steps):
        return None

    next_step = next((s for s in steps if not s['done']), None)

    return {
        'steps': steps,
        'done_count': done_count,
        'total': len(steps),
        'percent': round(100 * done_count / len(steps)) if steps else 0,
        'complete': False,
        'activated': has_band and total_cifras > 0,
        'next_step': next_step,
        'can_dismiss': has_band,
    }
