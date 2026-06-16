"""Notificações e cascata de escalação."""
from __future__ import annotations

import logging

from db import create_notification, get_user, user_display_name
from event_scale_tokens import make_scale_response_token
from models_agenda import (
    get_event_assignment_user_ids,
    get_user_event_assignment,
    respond_event_assignment,
    set_event_assignments,
)
from models_band_team import list_role_substitutes, users_blocked_on_date
from security import external_url_for

logger = logging.getLogger('setsync.scale')


def scale_token_url(event_id: str, user_id: str) -> str:
    token = make_scale_response_token(event_id, user_id)
    return external_url_for('agenda.respond_scale_token', token=token)


def scale_one_tap_url(event_id: str, user_id: str, *, accept: bool) -> str:
    token = make_scale_response_token(event_id, user_id)
    action = 'accept' if accept else 'decline'
    return external_url_for('agenda.respond_scale_token', token=token, action=action)


def build_scale_whatsapp_body(
    *,
    band_name: str,
    actor_name: str,
    event_title: str,
    when: str,
    event_id: str,
    user_id: str,
    role_label: str | None = None,
) -> str:
    role_part = f' ({role_label})' if role_label else ''
    accept_url = scale_one_tap_url(event_id, user_id, accept=True)
    decline_url = scale_one_tap_url(event_id, user_id, accept=False)
    page_url = scale_token_url(event_id, user_id)
    lines = [
        f'{actor_name} te escalou para «{event_title}»{role_part} em {band_name}.',
        f'Quando: {when}',
        '',
        f'✅ Aceitar: {accept_url}',
        f'❌ Recusar: {decline_url}',
        '',
        f'Ou abra: {page_url}',
    ]
    return '\n'.join(lines)


def send_scale_assignment_channels(
    *,
    band_id: str,
    actor_user_id: str,
    event: dict,
    user_ids: list[str] | set[str],
    band_name: str,
    actor_name: str,
    when: str,
) -> int:
    """In-app + e-mail (via create_notification) + WhatsApp com links one-tap."""
    from agenda_util import format_event_datetime
    from whatsapp_service import dispatch_notification_whatsapp, is_configured, send_whatsapp_text

    when_fmt = when or format_event_datetime(event.get('starts_at'))
    count = 0
    title = f'{band_name} — você está na escala'
    for uid in user_ids or []:
        if not uid or uid == actor_user_id:
            continue
        assignment = get_user_event_assignment(event['id'], uid)
        role = (assignment or {}).get('role_label')
        body = f'{actor_name} te escalou para «{event["title"]}».'
        if role:
            body += f' Função: {role}.'
        body += f' {when_fmt}.'
        create_notification(
            uid,
            band_id=band_id,
            actor_user_id=actor_user_id,
            type='event_scale_assigned',
            title=title,
            body=body,
            url_path=f'/agenda/{event["id"]}',
            skip_whatsapp=True,
        )
        user = get_user(uid)
        if user and is_configured():
            wa_body = build_scale_whatsapp_body(
                band_name=band_name,
                actor_name=actor_name,
                event_title=event['title'],
                when=when_fmt,
                event_id=event['id'],
                user_id=uid,
                role_label=role,
            )
            phone = user.get('phone') or ''
            from db import user_wants_whatsapp_notifications

            if phone and user_wants_whatsapp_notifications(user):
                try:
                    send_whatsapp_text(phone, f'*SetSync*\n\n*{title}*\n\n{wa_body}', link_preview=False)
                except Exception:
                    logger.exception('WhatsApp escalação para %s', uid)
            else:
                dispatch_notification_whatsapp(
                    uid, title=title, body=body, url_path=scale_token_url(event['id'], uid),
                )
        count += 1
    return count


def process_scale_response(
    event_id: str,
    user_id: str,
    *,
    accepted: bool,
    note: str | None = None,
) -> dict | None:
    """Registra resposta e dispara notificações + cascata se recusou."""
    import band_notifications as bn
    from models_agenda import get_band_event

    assignment = get_user_event_assignment(event_id, user_id)
    if not assignment:
        return None
    updated = respond_event_assignment(
        event_id, user_id, accepted=accepted, note=note,
    )
    if not updated:
        return None
    event = get_band_event(event_id)
    if not event:
        return updated
    bn.event_scale_response(
        event['band_id'],
        user_id,
        event_id,
        event['title'],
        accepted=accepted,
        note=note,
        assigned_by=assignment.get('assigned_by'),
    )
    if not accepted:
        cascade_substitute_on_decline(event, assignment, user_id)
    return updated


def cascade_substitute_on_decline(event: dict, assignment: dict, declined_user_id: str) -> int:
    """Notifica o primeiro reserva disponível para a função recusada."""
    role = (assignment.get('role_label') or '').strip()
    if not role:
        return 0
    band_id = event['band_id']
    assigned_ids = set(get_event_assignment_user_ids(event['id']))
    event_date = str(event.get('starts_at') or '')[:10]
    subs = list_role_substitutes(band_id, role)
    if not subs:
        return 0
    candidate_ids = [s['user_id'] for s in subs if s['user_id'] not in assigned_ids]
    blocked = users_blocked_on_date(candidate_ids, event_date) if event_date else set()

    from db import get_band

    band = get_band(band_id) or {}
    band_name = band.get('name') or 'Banda'
    declined_name = user_display_name(get_user(declined_user_id))
    notified = 0
    for sub in subs:
        uid = sub['user_id']
        if uid in assigned_ids or uid in blocked:
            continue
        create_notification(
            uid,
            band_id=band_id,
            actor_user_id=assignment.get('assigned_by'),
            type='event_scale_substitute_offer',
            title=f'{band_name} — vaga na escala ({role})',
            body=(
                f'{declined_name} recusou a função {role} em «{event["title"]}». '
                'Você está na lista de reserva — confirme se pode substituir.'
            ),
            url_path=f'/agenda/{event["id"]}',
        )
        notified += 1
        break
    return notified


def apply_substitute_to_event(
    event_id: str,
    user_id: str,
    role_label: str,
    *,
    assigned_by: str | None,
) -> bool:
    """Adiciona substituto à escala (mantém demais)."""
    from models_agenda import get_event_assignments

    current = get_event_assignments(event_id)
    for a in current:
        if a['user_id'] == user_id:
            return False
    assignments = [
        {'user_id': a['user_id'], 'role_label': a.get('role_label')}
        for a in current
    ]
    assignments.append({'user_id': user_id, 'role_label': role_label})
    set_event_assignments(event_id, assignments, assigned_by=assigned_by)
    return True
