"""Links de calendário (Google) e exportação ICS para eventos."""
from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import quote


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = str(value).strip().replace('T', ' ')[:19]
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _ics_dt(dt: datetime) -> str:
    return dt.strftime('%Y%m%dT%H%M%SZ')


def google_calendar_url(event: dict, *, band_name: str = '') -> str:
    start = _parse_dt(event.get('starts_at'))
    if not start:
        return ''
    end = _parse_dt(event.get('ends_at')) or (start + timedelta(hours=2))
    title = event.get('title') or 'Evento'
    if band_name:
        title = f'{band_name}: {title}'
    details = (event.get('notes') or '').strip()
    if event.get('setlist_name'):
        details = (details + '\n\nSetlist: ' + event['setlist_name']).strip()
    loc = (event.get('location') or '').strip()
    params = [
        ('action', 'TEMPLATE'),
        ('text', title),
        ('dates', f'{_ics_dt(start)}/{_ics_dt(end)}'),
    ]
    if details:
        params.append(('details', details))
    if loc:
        params.append(('location', loc))
    qs = '&'.join(f'{k}={quote(str(v))}' for k, v in params)
    return f'https://calendar.google.com/calendar/render?{qs}'


def ics_content(event: dict, *, band_name: str = '', app_url: str = '') -> str:
    start = _parse_dt(event.get('starts_at'))
    if not start:
        return ''
    end = _parse_dt(event.get('ends_at')) or (start + timedelta(hours=2))
    uid = event.get('id') or 'event'
    title = event.get('title') or 'Evento'
    if band_name:
        title = f'{band_name}: {title}'
    desc_parts = []
    if event.get('notes'):
        desc_parts.append(str(event['notes']))
    if event.get('setlist_name'):
        desc_parts.append(f'Setlist: {event["setlist_name"]}')
    if app_url and event.get('id'):
        desc_parts.append(app_url)
    description = '\\n'.join(desc_parts).replace('\r', '')
    location = (event.get('location') or '').replace('\n', ' ')
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//SetSync//Agenda//PT',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        f'UID:{uid}@setsync',
        f'DTSTAMP:{_ics_dt(datetime.utcnow())}',
        f'DTSTART:{_ics_dt(start)}',
        f'DTEND:{_ics_dt(end)}',
        f'SUMMARY:{title}',
    ]
    if description:
        lines.append(f'DESCRIPTION:{description}')
    if location:
        lines.append(f'LOCATION:{location}')
    lines.extend(['END:VEVENT', 'END:VCALENDAR'])
    return '\r\n'.join(lines) + '\r\n'
