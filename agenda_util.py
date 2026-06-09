"""Formatação de datas da agenda."""

from __future__ import annotations

from datetime import datetime

_EVENT_LABELS = {
    'ensaio': 'Ensaio',
    'show': 'Show',
}


def event_type_label(event_type: str | None) -> str:
    return _EVENT_LABELS.get((event_type or '').strip(), 'Evento')


def parse_event_datetime(date_str: str, time_str: str) -> str | None:
    """Combina data e hora do formulário em timestamp UTC string."""
    date_str = (date_str or '').strip()
    time_str = (time_str or '').strip() or '00:00'
    if not date_str:
        return None
    try:
        dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def split_event_datetime(value: str | None) -> tuple[str, str]:
    if not value:
        return '', ''
    text = str(value)[:16]
    try:
        dt = datetime.strptime(text.replace('T', ' ')[:16], '%Y-%m-%d %H:%M')
        return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M')
    except ValueError:
        return str(value)[:10], ''


def format_event_datetime(value: str | None) -> str:
    if not value:
        return '—'
    try:
        dt = datetime.strptime(str(value)[:19], '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d/%m/%Y às %H:%M')
    except ValueError:
        return str(value)[:16]


def event_relative_label(value: str | None, *, now: datetime | None = None) -> str:
    """Rótulo curto: Hoje, Amanhã, Em N dias."""
    if not value:
        return ''
    try:
        dt = datetime.strptime(str(value)[:19], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return ''
    ref = now or datetime.utcnow()
    delta = (dt.date() - ref.date()).days
    if delta == 0:
        return 'Hoje'
    if delta == 1:
        return 'Amanhã'
    if 2 <= delta <= 7:
        return f'Em {delta} dias'
    return ''
