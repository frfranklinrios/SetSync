"""Notificações in-app sobre alterações na banda (usa display_name, não username)."""
from __future__ import annotations

from db import (
    create_notification,
    create_notifications_for_users,
    get_band,
    get_band_members,
    get_user,
    queue_whatsapp_cifra_digest,
    user_display_name,
)


def _actor_name(actor_user_id: str | None) -> str:
    if not actor_user_id:
        return 'Alguém'
    return user_display_name(get_user(actor_user_id))


def _band_label(band_id: str | None) -> str:
    if not band_id:
        return 'Banda'
    band = get_band(band_id)
    return band['name'] if band else 'Banda'


def _member_ids(band_id: str, *, exclude: str | None = None, include_extra=None) -> list[str]:
    ids = [m['id'] for m in get_band_members(band_id)]
    for uid in include_extra or []:
        if uid and uid not in ids:
            ids.append(uid)
    if exclude:
        ids = [uid for uid in ids if uid != exclude]
    return ids


def _notify_members(
    band_id: str,
    actor_user_id: str | None,
    event_type: str,
    title: str,
    body: str,
    *,
    url_path: str | None = None,
    include_extra=None,
    also_notify: list[str] | None = None,
):
    recipients = _member_ids(band_id, exclude=actor_user_id, include_extra=also_notify or [])
    if not recipients:
        return 0
    return create_notifications_for_users(
        recipients,
        band_id=band_id,
        actor_user_id=actor_user_id,
        type=event_type,
        title=title,
        body=body,
        url_path=url_path,
    )


def band_updated(band_id: str, actor_user_id: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'band_updated',
        f'{band} — configurações',
        f'{actor} atualizou as informações da banda {band}.',
        url_path=f'/bands/{band_id}',
    )


def vocalist_added(band_id: str, actor_user_id: str, vocalist_names: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'vocalist_added',
        f'{band} — cantores',
        f'{actor} adicionou cantor(a/es): {vocalist_names}.',
        url_path=f'/bands/{band_id}/settings',
    )


def vocalist_removed(band_id: str, actor_user_id: str, vocalist_name: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'vocalist_removed',
        f'{band} — cantores',
        f'{actor} removeu {vocalist_name} da lista de cantores.',
        url_path=f'/bands/{band_id}/settings',
    )


def member_added_by_admin(band_id: str, actor_user_id: str, new_user_id: str):
    actor = _actor_name(actor_user_id)
    newcomer = user_display_name(get_user(new_user_id))
    band = _band_label(band_id)
    _notify_members(
        band_id,
        actor_user_id,
        'member_joined',
        f'{band} — novo membro',
        f'{actor} adicionou {newcomer} à banda.',
        url_path=f'/bands/{band_id}/members',
    )
    if new_user_id != actor_user_id:
        create_notification(
            new_user_id,
            band_id=band_id,
            actor_user_id=actor_user_id,
            type='member_joined',
            title=f'Você entrou em {band}',
            body=f'{actor} adicionou você à banda {band}.',
            url_path=f'/bands/{band_id}',
        )


def member_joined_via_invite(band_id: str, new_user_id: str):
    newcomer = user_display_name(get_user(new_user_id))
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        new_user_id,
        'member_joined',
        f'{band} — novo membro',
        f'{newcomer} entrou na banda pelo link de convite.',
        url_path=f'/bands/{band_id}/members',
    )


def member_removed(band_id: str, actor_user_id: str, removed_user_id: str):
    actor = _actor_name(actor_user_id)
    removed = user_display_name(get_user(removed_user_id))
    band = _band_label(band_id)
    _notify_members(
        band_id,
        actor_user_id,
        'member_removed',
        f'{band} — membro removido',
        f'{actor} removeu {removed} da banda.',
        url_path=f'/bands/{band_id}/members',
        also_notify=[removed_user_id],
    )
    if removed_user_id != actor_user_id:
        create_notification(
            removed_user_id,
            band_id=band_id,
            actor_user_id=actor_user_id,
            type='member_removed',
            title=f'Removido de {band}',
            body=f'{actor} removeu você da banda {band}.',
            url_path='/bands/',
        )


def cifra_created(band_id: str, actor_user_id: str, cifra_id: str, titulo: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'cifra_created',
        f'{band} — nova cifra',
        f'{actor} adicionou a cifra «{titulo}».',
        url_path=f'/cifras/{cifra_id}',
    )


def cifra_updated(band_id: str, actor_user_id: str, cifra_id: str, titulo: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    url_path = f'/cifras/{cifra_id}'
    recipients = _member_ids(band_id, exclude=actor_user_id)
    if not recipients:
        return 0
    count = create_notifications_for_users(
        recipients,
        band_id=band_id,
        actor_user_id=actor_user_id,
        type='cifra_updated',
        title=f'{band} — cifra editada',
        body=f'{actor} editou a cifra «{titulo}».',
        url_path=url_path,
        skip_whatsapp=True,
    )
    for uid in recipients:
        queue_whatsapp_cifra_digest(
            uid,
            band_id=band_id,
            cifra_id=cifra_id,
            titulo=titulo,
            actor_user_id=actor_user_id,
            url_path=url_path,
        )
    return count


def cifra_deleted(band_id: str, actor_user_id: str, titulo: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'cifra_deleted',
        f'{band} — cifra removida',
        f'{actor} removeu a cifra «{titulo}».',
        url_path=f'/bands/{band_id}',
    )


def setlist_created(band_id: str, actor_user_id: str, setlist_id: int, name: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'setlist_created',
        f'{band} — nova setlist',
        f'{actor} criou a setlist «{name}».',
        url_path=f'/setlists/{setlist_id}',
    )


def setlist_deleted(band_id: str, actor_user_id: str, name: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'setlist_deleted',
        f'{band} — setlist removida',
        f'{actor} excluiu a setlist «{name}».',
        url_path=f'/setlists/band/{band_id}',
    )


def setlist_song_added(band_id: str, actor_user_id: str, setlist_id: int, setlist_name: str, song_title: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'setlist_updated',
        f'{band} — setlist atualizada',
        f'{actor} adicionou «{song_title}» à setlist «{setlist_name}».',
        url_path=f'/setlists/{setlist_id}',
    )


def _event_type_label(event_type: str | None) -> str:
    return {'ensaio': 'ensaio', 'show': 'show'}.get((event_type or '').strip(), 'evento')


def event_created(band_id: str, actor_user_id: str, event_id: str, title: str, event_type: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    tipo = _event_type_label(event_type)
    return _notify_members(
        band_id,
        actor_user_id,
        'event_created',
        f'{band} — {tipo} agendado',
        f'{actor} marcou «{title}» na agenda.',
        url_path=f'/agenda/{event_id}',
    )


def event_updated(band_id: str, actor_user_id: str, event_id: str, title: str, event_type: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    tipo = _event_type_label(event_type)
    return _notify_members(
        band_id,
        actor_user_id,
        'event_updated',
        f'{band} — {tipo} atualizado',
        f'{actor} alterou «{title}» na agenda.',
        url_path=f'/agenda/{event_id}',
    )


def event_scale_response(
    band_id: str,
    responder_user_id: str,
    event_id: str,
    title: str,
    *,
    accepted: bool,
    note: str | None,
    assigned_by: str | None,
):
    """Notifica quem escalou sobre aceite ou recusa."""
    if not assigned_by or assigned_by == responder_user_id:
        return 0
    responder = _actor_name(responder_user_id)
    band = _band_label(band_id)
    if accepted:
        ntype = 'event_scale_accepted'
        verb = 'aceitou'
    else:
        ntype = 'event_scale_declined'
        verb = 'recusou'
    body = f'{responder} {verb} a escalação para «{title}».'
    if note:
        body += f' Observação: {note}'
    create_notification(
        assigned_by,
        band_id=band_id,
        actor_user_id=responder_user_id,
        type=ntype,
        title=f'{band} — resposta da escalação',
        body=body,
        url_path=f'/agenda/{event_id}',
    )
    return 1


def event_scale_assigned(
    band_id: str,
    actor_user_id: str,
    event_id: str,
    title: str,
    user_ids: list[str] | set[str],
):
    """Notifica integrantes recém-escalados para um evento."""
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    count = 0
    for uid in user_ids or []:
        if not uid or uid == actor_user_id:
            continue
        create_notification(
            uid,
            band_id=band_id,
            actor_user_id=actor_user_id,
            type='event_scale_assigned',
            title=f'{band} — você está na escala',
            body=f'{actor} te escalou para «{title}».',
            url_path=f'/agenda/{event_id}',
        )
        count += 1
    return count


def event_deleted(band_id: str, actor_user_id: str, title: str, event_type: str | None):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    tipo = _event_type_label(event_type)
    return _notify_members(
        band_id,
        actor_user_id,
        'event_deleted',
        f'{band} — {tipo} cancelado',
        f'{actor} removeu «{title}» da agenda.',
        url_path=f'/bands/{band_id}#tab-agenda',
    )


def setlist_song_removed(band_id: str, actor_user_id: str, setlist_id: int, setlist_name: str, song_title: str):
    actor = _actor_name(actor_user_id)
    band = _band_label(band_id)
    return _notify_members(
        band_id,
        actor_user_id,
        'setlist_updated',
        f'{band} — setlist atualizada',
        f'{actor} removeu «{song_title}» da setlist «{setlist_name}».',
        url_path=f'/setlists/{setlist_id}',
    )
