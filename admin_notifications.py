"""Notificações in-app para administradores globais (perfil master / superadmin)."""
from __future__ import annotations

from db import (
    create_notifications_for_users,
    get_all_users,
    get_band,
    get_user,
    is_superadmin,
    user_display_name,
)


def superadmin_user_ids(*, exclude: str | None = None) -> list[str]:
    """IDs de contas com privilégio SETSYNC_SUPERADMIN_* no .env."""
    ids = [u['id'] for u in get_all_users() if is_superadmin(u['id'])]
    if exclude:
        ids = [uid for uid in ids if uid != exclude]
    return ids


def notify_superadmins(
    event_type: str,
    title: str,
    body: str,
    *,
    actor_user_id: str | None = None,
    band_id: str | None = None,
    url_path: str | None = None,
    exclude_actor: bool = True,
) -> int:
    """Envia notificação a todos os superadmins. Retorna quantidade criada."""
    exclude = actor_user_id if exclude_actor else None
    recipients = superadmin_user_ids(exclude=exclude)
    if not recipients:
        return 0
    return create_notifications_for_users(
        recipients,
        band_id=band_id,
        actor_user_id=actor_user_id,
        type=event_type,
        title=title,
        body=body,
        url_path=url_path or '/admin/',
    )


def _actor_name(actor_user_id: str | None) -> str:
    if not actor_user_id:
        return 'Alguém'
    return user_display_name(get_user(actor_user_id))


def user_registered(user_id: str):
    user = get_user(user_id)
    if not user:
        return 0
    name = user_display_name(user)
    login = user.get('username') or ''
    via = 'Google' if user.get('google_id') and not user.get('password_hash') else 'cadastro'
    return notify_superadmins(
        'admin_user_registered',
        'Novo usuário no app',
        f'{name} (@{login}) criou conta via {via}.',
        actor_user_id=user_id,
        url_path='/admin/',
        exclude_actor=True,
    )


def band_created(band_id: str, actor_user_id: str):
    band = get_band(band_id)
    if not band:
        return 0
    actor = _actor_name(actor_user_id)
    owner = user_display_name(get_user(band['owner_id']))
    return notify_superadmins(
        'admin_band_created',
        'Nova banda',
        f'{actor} criou a banda «{band["name"]}» (titular: {owner}).',
        actor_user_id=actor_user_id,
        band_id=band_id,
        url_path=f'/bands/{band_id}',
    )


def band_deleted(band_id: str, actor_user_id: str, band_name: str):
    actor = _actor_name(actor_user_id)
    return notify_superadmins(
        'admin_band_deleted',
        'Banda excluída',
        f'{actor} excluiu a banda «{band_name}».',
        actor_user_id=actor_user_id,
        band_id=None,
        url_path='/admin/',
    )


def subscription_activated(banda_id: str, plano: str, *, source: str = 'Mercado Pago'):
    from monetizacao import PLANOS

    band = get_band(banda_id)
    if not band:
        return 0
    plano_nome = PLANOS.get(plano).nome if plano in PLANOS else plano
    owner = user_display_name(get_user(band['owner_id']))
    return notify_superadmins(
        'admin_subscription_active',
        f'Assinatura {plano_nome} ativa',
        f'Banda «{band["name"]}» ({owner}) — plano {plano_nome} ativado ({source}).',
        band_id=banda_id,
        url_path=f'/assinatura/planos?banda_id={banda_id}',
        exclude_actor=False,
    )


def subscription_cancelled(banda_id: str):
    from monetizacao import PLANOS
    from db import get_assinatura

    band = get_band(banda_id)
    if not band:
        return 0
    row = get_assinatura(banda_id) or {}
    plano = row.get('plano', 'pro')
    plano_nome = PLANOS.get(plano).nome if plano in PLANOS else plano
    return notify_superadmins(
        'admin_subscription_cancelled',
        f'Assinatura {plano_nome} cancelada',
        f'Banda «{band["name"]}» — assinatura cancelada no Mercado Pago.',
        band_id=banda_id,
        url_path=f'/assinatura/planos?banda_id={banda_id}',
        exclude_actor=False,
    )


def subscription_inadimplente(banda_id: str):
    band = get_band(banda_id)
    if not band:
        return 0
    return notify_superadmins(
        'admin_subscription_paused',
        'Pagamento pendente',
        f'Banda «{band["name"]}» — assinatura pausada ou inadimplente.',
        band_id=banda_id,
        url_path=f'/assinatura/planos?banda_id={banda_id}',
        exclude_actor=False,
    )


def voucher_redeemed(banda_id: str, actor_user_id: str, codigo: str, plano_nome: str, dias: int):
    band = get_band(banda_id)
    if not band:
        return 0
    actor = _actor_name(actor_user_id)
    return notify_superadmins(
        'admin_voucher_redeemed',
        'Voucher resgatado',
        f'{actor} resgatou {codigo} ({dias} dias {plano_nome}) na banda «{band["name"]}».',
        actor_user_id=actor_user_id,
        band_id=banda_id,
        url_path='/admin/vouchers',
    )
