"""Progresso de onboarding e ativação pós-cadastro."""

from __future__ import annotations

from urllib.parse import quote

from db import (
    count_band_cifras,
    count_band_members,
    count_user_personal_cifras,
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


def user_has_bandmate(user_id: str) -> bool:
    """True se alguma banda do usuário já tem 2+ pessoas (incluindo o dono)."""
    for band in list(get_owned_bands(user_id) or []) + list(get_user_bands(user_id) or []):
        if count_band_members(band['id']) >= 2:
            return True
    return False


def get_invite_loop_cta(user_id: str) -> dict | None:
    """Depois do palco real: um toque para chamar a banda. Some quando já tem 2 pessoas."""
    if not user_id:
        return None
    from product_funnel import get_user_funnel_steps
    from security import external_url_for

    done = (get_user_funnel_steps(user_id).get('done') or set())
    if 'play_mode_real' not in done:
        return None
    if user_has_bandmate(user_id):
        return None

    owned = list(get_owned_bands(user_id) or [])
    site = external_url_for('index')
    if owned:
        from band_invites import make_band_invite_token

        band = owned[0]
        invite = external_url_for(
            'auth.convite', token=make_band_invite_token(band['id']),
        )
        name = band.get('name') or 'minha banda'
        msg = (
            f'Toquei no Uníssono no ensaio da banda "{name}". '
            f'Entra no palco (cifra no tom certo): {invite}'
        )
        return {
            'has_band': True,
            'band_name': name,
            'members_url': url_for('bands.members', band_id=band['id']),
            'wa_href': f'https://wa.me/?text={quote(msg)}',
        }
    msg = f'Toquei a cifra do ensaio no Uníssono. Entra no palco comigo: {site}'
    return {
        'has_band': False,
        'band_name': '',
        'members_url': url_for('bands.create', bem_vindo=1),
        'wa_href': f'https://wa.me/?text={quote(msg)}',
    }


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
    total_band_cifras = sum(count_band_cifras(b['id']) for b in bands) if bands else 0
    total_personal = count_user_personal_cifras(user_id)
    played = user_play_mode_used(user_id)
    from demo_onboarding import count_real_personal_cifras

    real_songs = count_real_personal_cifras(user_id) + total_band_cifras
    played_real = False
    try:
        from product_funnel import get_user_funnel_steps
        played_real = 'play_mode_real' in (get_user_funnel_steps(user_id).get('done') or set())
    except Exception:
        played_real = bool(played and real_songs > 0)

    first_band_id = bands[0]['id'] if bands else None
    add_url = (
        url_for('cifras.add', band_id=first_band_id)
        if first_band_id
        else url_for('cifras.comecar')
    )
    if first_band_id and total_band_cifras:
        tocar_url = url_for('cifras.tocar_band', band_id=first_band_id)
    elif total_personal:
        tocar_url = url_for('cifras.tocar_colecao')
    else:
        tocar_url = add_url
    invite_url = (
        url_for('bands.members', band_id=first_band_id)
        if first_band_id
        else url_for('bands.create', bem_vindo=1)
    )
    has_bandmate = user_has_bandmate(user_id)

    steps = [
        {
            'id': 'cifra',
            'label': '1. Adicionar a música do seu ensaio',
            'hint': 'Busque na biblioteca ou cole a cifra — não use o exemplo como se fosse sua.',
            'done': real_songs > 0,
            'url': url_for('cifras.comecar'),
        },
        {
            'id': 'tocar',
            'label': '2. Tocar essa música no palco',
            'hint': 'Transposição e diagramas na tela cheia — com a cifra que você vai usar de verdade.',
            'done': played_real,
            'url': tocar_url if real_songs else url_for('cifras.comecar'),
        },
        {
            'id': 'band',
            'label': '3. Chamar alguém do ensaio no WhatsApp',
            'hint': 'Um link. A banda entra no mesmo tom, no mesmo palco.',
            'done': has_bandmate,
            'url': invite_url,
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
        'activated': played_real,
        'next_step': next_step,
        'can_dismiss': has_band or played,
    }
