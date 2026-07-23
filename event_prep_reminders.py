"""Alertas de preparação: próximo evento sem setlist ou com escala incompleta."""

from __future__ import annotations

import logging
from datetime import timedelta

from agenda_util import event_type_label, format_event_datetime
from config import app_now_naive
from db import (
    create_notification,
    get_band_members,
    get_user,
    mark_retention_sent,
    retention_was_sent,
    user_wants_email_notifications,
)
from models_agenda import event_has_assignments, list_events_in_time_window
from models_band_team import get_assignment_response_stats, get_assignment_stats_by_events
from models_setlist import count_setlist_cifras_by_ids

logger = logging.getLogger('setsync.event_prep_reminders')

# Olha eventos entre 36h e 7 dias à frente (fora da janela do lembrete 24h).
PREP_WINDOW_START_HOURS = 36
PREP_WINDOW_END_HOURS = 24 * 7
EDITOR_ROLES = frozenset({'owner', 'admin', 'editor'})


def event_prep_gaps(
    event: dict,
    *,
    cifra_counts: dict[int, int] | None = None,
    assignment_stats: dict | None = None,
) -> dict:
    """Retorna gaps de preparação do evento (setlist / escala).

    Se ``assignment_stats`` (mapa {event_id: stats} pré-calculado em lote) for
    passado, evita uma query de escala por evento.
    """
    setlist_id = event.get('setlist_id')
    missing_setlist = not setlist_id
    empty_setlist = False
    if setlist_id:
        counts = cifra_counts
        if counts is None:
            counts = count_setlist_cifras_by_ids([int(setlist_id)])
        empty_setlist = int(counts.get(int(setlist_id), 0)) == 0

    if assignment_stats is not None:
        stats = assignment_stats.get(event['id'])
    else:
        stats = get_assignment_response_stats(event['id']) if event_has_assignments(event['id']) else None
    no_scale = not stats or int(stats.get('total') or 0) == 0
    pending = 0
    accepted = 0
    if not no_scale:
        pending = int(stats.get('pending') or 0)
        accepted = int(stats.get('accepted') or 0)

    return {
        'missing_setlist': missing_setlist,
        'empty_setlist': empty_setlist,
        'no_scale': no_scale,
        'pending_responses': pending,
        'accepted': accepted,
        'has_gaps': bool(
            missing_setlist
            or empty_setlist
            or no_scale
            or pending > 0
        ),
    }


def _editor_recipient_ids(band_id: str) -> list[str]:
    members = get_band_members(band_id)
    ids = [
        str(m['id'])
        for m in members
        if (m.get('role') or '').lower() in EDITOR_ROLES
    ]
    if ids:
        return ids
    # Fallback: dono da banda via lista de membros (role owner) ou qualquer membro.
    return [str(m['id']) for m in members][:1]


def _campaign_key(event_id: str) -> str:
    return f'prep_event:{event_id}'


def _email_campaign_key(event_id: str) -> str:
    return f'prep_event_email:{event_id}'


def _prep_body(event: dict, gaps: dict) -> str:
    tipo = event_type_label(event.get('event_type')).lower()
    when = format_event_datetime(event.get('starts_at'))
    parts = [f'{tipo.capitalize()} «{event.get("title", "")}» em {when}.']
    fixes: list[str] = []
    if gaps.get('missing_setlist'):
        fixes.append('vincule uma setlist')
    elif gaps.get('empty_setlist'):
        fixes.append('adicione músicas na setlist')
    if gaps.get('no_scale'):
        fixes.append('monte a escala')
    elif gaps.get('pending_responses'):
        n = gaps['pending_responses']
        fixes.append(f'{n} resposta{"s" if n != 1 else ""} de escala pendente{"s" if n != 1 else ""}')
    if fixes:
        parts.append('Ainda falta: ' + '; '.join(fixes) + '.')
    parts.append('Prepare antes do ensaio para a banda tocar sem surpresa.')
    return ' '.join(parts)


def _concierge_email_copy(event: dict, gaps: dict) -> tuple[str, str, str]:
    """Assunto, texto e HTML — tom concierge (ajuda com importação)."""
    tipo = event_type_label(event.get('event_type')).lower()
    when = format_event_datetime(event.get('starts_at'))
    title = event.get('title') or tipo
    subject = f'Precisa de ajuda com o {tipo} «{title}»?'
    help_bits = []
    if gaps.get('missing_setlist') or gaps.get('empty_setlist'):
        help_bits.append('importação de cifras / setlist')
    if gaps.get('no_scale') or gaps.get('pending_responses'):
        help_bits.append('escala da banda')
    help_line = ' e '.join(help_bits) if help_bits else 'preparação do ensaio'
    body = (
        f'Vi que você tem um {tipo} («{title}») em {when}, '
        f'mas o setlist ainda não está pronto.\n\n'
        f'Precisa de ajuda com {help_line}? '
        f'Responda este e-mail ou abra o evento no Uníssono — a gente te guia.\n'
    )
    html = (
        f'<p>Vi que você tem um <strong>{tipo}</strong> («{title}») em <strong>{when}</strong>, '
        f'mas o setlist ainda não está pronto.</p>'
        f'<p>Precisa de ajuda com <strong>{help_line}</strong>? '
        f'Abra o evento no app ou responda este e-mail — estamos aqui.</p>'
    )
    return subject, body, html


def _url_path(event: dict, gaps: dict) -> str:
    event_id = event['id']
    if gaps.get('no_scale') or gaps.get('pending_responses'):
        return f'/agenda/{event_id}/escala'
    return f'/agenda/{event_id}'


def _send_concierge_email(user_id: str, event: dict, gaps: dict, event_url: str) -> bool:
    from email_service import is_configured, send_email
    from notification_email_service import _html_wrapper

    try:
        if not is_configured():
            return False
    except RuntimeError:
        # Fora do app context (ex.: testes unitários sem Flask)
        return False
    user = get_user(user_id)
    if not user or not user_wants_email_notifications(user):
        return False
    email = (user.get('email') or '').strip()
    if not email:
        return False
    subject, body, html_inner = _concierge_email_copy(event, gaps)
    text = body + f'\n{event_url}\n'
    html = _html_wrapper(
        subject,
        html_inner,
        event_url,
        'Abrir evento',
    )
    try:
        return bool(send_email([email], subject, html, text))
    except Exception:
        logger.exception('Falha no e-mail concierge evento %s → %s', event.get('id'), user_id)
        return False


def verificar_e_enviar_alertas_evento_incompleto() -> int:
    """Notifica editores sobre eventos próximos incompletos. Retorna envios."""
    now = app_now_naive()
    window_start = (now + timedelta(hours=PREP_WINDOW_START_HOURS)).strftime(
        '%Y-%m-%d %H:%M:%S'
    )
    window_end = (now + timedelta(hours=PREP_WINDOW_END_HOURS)).strftime(
        '%Y-%m-%d %H:%M:%S'
    )
    events = list_events_in_time_window(window_start, window_end)
    if not events:
        return 0

    setlist_ids = [
        int(e['setlist_id']) for e in events if e.get('setlist_id')
    ]
    cifra_counts = count_setlist_cifras_by_ids(setlist_ids) if setlist_ids else {}
    assignment_stats = get_assignment_stats_by_events([e['id'] for e in events])

    sent = 0
    for event in events:
        gaps = event_prep_gaps(
            event, cifra_counts=cifra_counts, assignment_stats=assignment_stats,
        )
        if not gaps['has_gaps']:
            continue

        event_id = event['id']
        band_id = event['band_id']
        band_name = event.get('band_name') or 'Banda'
        tipo = event_type_label(event.get('event_type'))
        title = f'{band_name} — prepare o {tipo.lower()}'
        body = _prep_body(event, gaps)
        url_path = _url_path(event, gaps)
        campaign = _campaign_key(event_id)
        email_campaign = _email_campaign_key(event_id)

        try:
            from security import external_url_for
            event_url = external_url_for('agenda.view', event_id=event_id)
        except Exception:
            event_url = url_path

        for user_id in _editor_recipient_ids(band_id):
            if not retention_was_sent(user_id, campaign):
                try:
                    create_notification(
                        user_id,
                        band_id=band_id,
                        actor_user_id=None,
                        type='event_prep_reminder',
                        title=title,
                        body=body,
                        url_path=url_path,
                    )
                    mark_retention_sent(user_id, campaign, 'enviado')
                    sent += 1
                except Exception:
                    logger.exception(
                        'Falha no alerta de prep do evento %s para %s',
                        event_id,
                        user_id,
                    )
                    try:
                        mark_retention_sent(user_id, campaign, 'erro')
                    except Exception:
                        pass

            # Concierge: e-mail direto (uma vez) — base ainda tratável
            if not retention_was_sent(user_id, email_campaign):
                if _send_concierge_email(user_id, event, gaps, event_url):
                    mark_retention_sent(user_id, email_campaign, 'enviado')
                    sent += 1

    if sent:
        logger.info('Alertas de preparação de evento enviados: %d', sent)
    return sent
