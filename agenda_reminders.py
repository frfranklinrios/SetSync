"""Lembretes de ensaios e shows (24h antes — e-mail, WhatsApp e notificação in-app)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from agenda_util import event_type_label, format_event_datetime
from db import create_notification
from models_agenda import (
    event_reminder_was_sent,
    get_event_reminder_recipient_ids,
    list_events_in_time_window,
    mark_event_reminder_sent,
)
from config import app_now_naive, app_now_str

logger = logging.getLogger('setsync.agenda_reminders')

REMINDER_HOURS_BEFORE = 24
REMINDER_WINDOW_HOURS = 1


def _reminder_body(event: dict) -> str:
    tipo = event_type_label(event.get('event_type')).lower()
    when = format_event_datetime(event.get('starts_at'))
    parts = [f'{tipo.capitalize()} «{event.get("title", "")}» em {when}.']
    if event.get('location'):
        parts.append(f'Local: {event["location"]}.')
    if event.get('setlist_name'):
        parts.append(f'Setlist: {event["setlist_name"]}.')
    if event.get('setlist_id'):
        parts.append(f'Revise a setlist no app antes do ensaio.')
    return ' '.join(parts)


def verificar_e_enviar_lembretes_agenda() -> int:
    """Notifica membros ~24h antes de cada evento. Retorna quantidade enviada."""
    now = app_now_naive()
    window_start = (now + timedelta(hours=REMINDER_HOURS_BEFORE)).strftime('%Y-%m-%d %H:%M:%S')
    window_end = (
        now + timedelta(hours=REMINDER_HOURS_BEFORE + REMINDER_WINDOW_HOURS)
    ).strftime('%Y-%m-%d %H:%M:%S')

    events = list_events_in_time_window(window_start, window_end)
    sent = 0

    for event in events:
        event_id = event['id']
        band_id = event['band_id']
        band_name = event.get('band_name') or 'Banda'
        tipo = event_type_label(event.get('event_type'))
        title = f'{band_name} — {tipo} amanhã'
        body = _reminder_body(event)
        url_path = f'/agenda/{event_id}'

        for user_id in get_event_reminder_recipient_ids(event_id, band_id):
            if event_reminder_was_sent(event_id, user_id):
                continue
            try:
                create_notification(
                    user_id,
                    band_id=band_id,
                    actor_user_id=None,
                    type='event_reminder',
                    title=title,
                    body=body,
                    url_path=url_path,
                )
                mark_event_reminder_sent(event_id, user_id)
                sent += 1
            except Exception:
                logger.exception(
                    'Falha ao enviar lembrete do evento %s para %s', event_id, user_id,
                )

    if sent:
        logger.info('Lembretes de agenda enviados: %d', sent)
    return sent