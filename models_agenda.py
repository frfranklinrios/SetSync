"""Agenda da banda — ensaios e shows com setlist opcional."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from database import IS_POSTGRES, IntegrityError
from db import get_db

EVENT_ENSAIO = 'ensaio'
EVENT_SHOW = 'show'
EVENT_TYPES = (EVENT_ENSAIO, EVENT_SHOW)


def create_band_event(
    band_id: str,
    *,
    title: str,
    event_type: str,
    starts_at: str,
    ends_at: str | None = None,
    location: str | None = None,
    location_lat: float | None = None,
    location_lng: float | None = None,
    location_place_id: str | None = None,
    notes: str | None = None,
    setlist_id: int | None = None,
    created_by: str | None = None,
) -> str:
    event_id = str(uuid.uuid4())
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO band_events
           (id, band_id, setlist_id, event_type, title, starts_at, ends_at,
            location, location_lat, location_lng, location_place_id,
            notes, created_by, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            event_id,
            band_id,
            setlist_id,
            event_type,
            title,
            starts_at,
            ends_at,
            location,
            location_lat,
            location_lng,
            location_place_id,
            notes,
            created_by,
            now,
        ),
    )
    db.commit()
    db.close()
    return event_id


def get_band_event(event_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT e.*, s.name AS setlist_name
           FROM band_events e
           LEFT JOIN setlists s ON s.id = e.setlist_id
           WHERE e.id = ?''',
        (event_id,),
    )
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_band_events(
    band_id: str,
    *,
    include_past: bool = True,
    limit: int | None = None,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    sql = '''
        SELECT e.*, s.name AS setlist_name
        FROM band_events e
        LEFT JOIN setlists s ON s.id = e.setlist_id
        WHERE e.band_id = ?
    '''
    params: list = [band_id]
    if not include_past:
        sql += ' AND e.starts_at >= ?'
        params.append(now)
    sql += ' ORDER BY e.starts_at ASC'
    if limit:
        sql += ' LIMIT ?'
        params.append(int(limit))
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def update_band_event(
    event_id: str,
    *,
    title: str,
    event_type: str,
    starts_at: str,
    ends_at: str | None,
    location: str | None,
    location_lat: float | None,
    location_lng: float | None,
    location_place_id: str | None,
    notes: str | None,
    setlist_id: int | None,
) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE band_events
           SET title = ?, event_type = ?, starts_at = ?, ends_at = ?,
               location = ?, location_lat = ?, location_lng = ?, location_place_id = ?,
               notes = ?, setlist_id = ?
           WHERE id = ?''',
        (
            title, event_type, starts_at, ends_at,
            location, location_lat, location_lng, location_place_id,
            notes, setlist_id, event_id,
        ),
    )
    db.commit()
    db.close()


def delete_band_event(event_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM band_events WHERE id = ?', (event_id,))
    db.commit()
    db.close()


def get_upcoming_events_for_user(
    user_id: str,
    *,
    all_bands: bool = False,
    limit: int = 10,
    days_ahead: int = 30,
) -> list[dict]:
    """Próximos eventos das bandas do usuário (ou todas, para superadmin)."""
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    until = (datetime.utcnow() + timedelta(days=days_ahead)).strftime('%Y-%m-%d %H:%M:%S')
    sql = '''
        SELECT e.*, b.name AS band_name, s.name AS setlist_name
        FROM band_events e
        JOIN bands b ON b.id = e.band_id
        LEFT JOIN setlists s ON s.id = e.setlist_id
    '''
    params: list = []
    if all_bands:
        sql += ' WHERE e.starts_at >= ? AND e.starts_at <= ?'
        params.extend([now, until])
    else:
        sql += '''
            JOIN band_members bm ON bm.band_id = e.band_id AND bm.user_id = ?
            WHERE e.starts_at >= ? AND e.starts_at <= ?
        '''
        params.extend([user_id, now, until])
    sql += ' ORDER BY e.starts_at ASC LIMIT ?'
    params.append(int(limit))
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def get_user_agenda_events(user_id: str, *, all_bands: bool = False) -> list[dict]:
    """Eventos de todas as bandas do usuário (para calendário pessoal)."""
    db = get_db()
    c = db.cursor()
    if all_bands:
        c.execute(
            '''SELECT e.*, b.name AS band_name, s.name AS setlist_name
               FROM band_events e
               JOIN bands b ON b.id = e.band_id
               LEFT JOIN setlists s ON s.id = e.setlist_id
               ORDER BY e.starts_at ASC''',
        )
    else:
        c.execute(
            '''SELECT e.*, b.name AS band_name, s.name AS setlist_name
               FROM band_events e
               JOIN bands b ON b.id = e.band_id
               JOIN band_members bm ON bm.band_id = e.band_id AND bm.user_id = ?
               LEFT JOIN setlists s ON s.id = e.setlist_id
               ORDER BY e.starts_at ASC''',
            (user_id,),
        )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_events_in_time_window(window_start: str, window_end: str) -> list[dict]:
    """Eventos com starts_at dentro do intervalo [window_start, window_end)."""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT e.*, b.name AS band_name, s.name AS setlist_name
           FROM band_events e
           JOIN bands b ON b.id = e.band_id
           LEFT JOIN setlists s ON s.id = e.setlist_id
           WHERE e.starts_at >= ? AND e.starts_at < ?
           ORDER BY e.starts_at ASC''',
        (window_start, window_end),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def event_reminder_was_sent(event_id: str, user_id: str) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT 1 FROM event_reminders WHERE event_id = ? AND user_id = ? LIMIT 1',
        (event_id, user_id),
    )
    found = c.fetchone() is not None
    db.close()
    return found


def mark_event_reminder_sent(event_id: str, user_id: str) -> None:
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    try:
        c.execute(
            'INSERT INTO event_reminders (event_id, user_id, sent_at) VALUES (?, ?, ?)',
            (event_id, user_id, now),
        )
    except IntegrityError:
        pass
    db.commit()
    db.close()


def get_event_assignments(event_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT a.*, u.display_name, u.username, u.email, bm.role AS band_role
           FROM band_event_assignments a
           JOIN users u ON u.id = a.user_id
           LEFT JOIN band_events e ON e.id = a.event_id
           LEFT JOIN band_members bm ON bm.band_id = e.band_id AND bm.user_id = a.user_id
           WHERE a.event_id = ?
           ORDER BY u.display_name, u.username''',
        (event_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def get_event_assignment_user_ids(event_id: str) -> list[str]:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT user_id FROM band_event_assignments WHERE event_id = ? ORDER BY user_id',
        (event_id,),
    )
    ids = [str(r['user_id']) for r in c.fetchall()]
    db.close()
    return ids


def event_has_assignments(event_id: str) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT 1 FROM band_event_assignments WHERE event_id = ? LIMIT 1',
        (event_id,),
    )
    found = c.fetchone() is not None
    db.close()
    return found


def get_event_reminder_recipient_ids(event_id: str, band_id: str) -> list[str]:
    """Membros escalados; se não houver escala, todos os membros da banda."""
    from db import get_band_members

    assigned = get_event_assignment_user_ids(event_id)
    if assigned:
        return assigned
    return [m['id'] for m in get_band_members(band_id)]


def set_event_assignments(
    event_id: str,
    assignments: list[dict],
    *,
    assigned_by: str | None = None,
) -> list[str]:
    """Atualiza escala preservando respostas de quem permanece. Retorna IDs recém-adicionados."""
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    existing = {a['user_id']: a for a in get_event_assignments(event_id)}
    new_map: dict[str, dict] = {}
    for item in assignments:
        uid = item.get('user_id')
        if not uid:
            continue
        new_map[str(uid)] = item

    db = get_db()
    c = db.cursor()
    added: list[str] = []

    for uid in existing:
        if uid not in new_map:
            c.execute(
                'DELETE FROM band_event_assignments WHERE event_id = ? AND user_id = ?',
                (event_id, uid),
            )

    for uid, item in new_map.items():
        role = (item.get('role_label') or '').strip() or None
        if uid in existing:
            prev = existing[uid]
            c.execute(
                '''UPDATE band_event_assignments
                   SET role_label = ?, assigned_by = COALESCE(?, assigned_by)
                   WHERE event_id = ? AND user_id = ?''',
                (role, assigned_by, event_id, uid),
            )
        else:
            c.execute(
                '''INSERT INTO band_event_assignments
                   (event_id, user_id, role_label, assigned_by, assigned_at,
                    response_status, response_note, responded_at)
                   VALUES (?, ?, ?, ?, ?, 'pending', NULL, NULL)''',
                (event_id, uid, role, assigned_by, now),
            )
            added.append(uid)

    db.commit()
    db.close()
    return added


def get_user_event_assignment(event_id: str, user_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT a.*, u.display_name, u.username
           FROM band_event_assignments a
           JOIN users u ON u.id = a.user_id
           WHERE a.event_id = ? AND a.user_id = ?''',
        (event_id, user_id),
    )
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def respond_event_assignment(
    event_id: str,
    user_id: str,
    *,
    accepted: bool,
    note: str | None = None,
) -> dict | None:
    """Registra aceite ou recusa do escalado. Retorna a linha atualizada."""
    status = 'accepted' if accepted else 'declined'
    note = (note or '').strip()[:500] or None
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE band_event_assignments
           SET response_status = ?, response_note = ?, responded_at = ?
           WHERE event_id = ? AND user_id = ?''',
        (status, note, now, event_id, user_id),
    )
    if c.rowcount < 1:
        db.close()
        return None
    db.commit()
    db.close()
    return get_user_event_assignment(event_id, user_id)


def get_events_where_user_assigned(user_id: str, event_ids: list[str]) -> set[str]:
    if not user_id or not event_ids:
        return set()
    db = get_db()
    c = db.cursor()
    ph = ','.join('?' * len(event_ids))
    c.execute(
        f'''SELECT event_id FROM band_event_assignments
            WHERE user_id = ? AND event_id IN ({ph})''',
        [user_id, *event_ids],
    )
    found = {str(r['event_id']) for r in c.fetchall()}
    db.close()
    return found


def get_events_scale_summaries(event_ids: list[str]) -> dict[str, dict]:
    if not event_ids:
        return {}
    db = get_db()
    c = db.cursor()
    ph = ','.join('?' * len(event_ids))
    c.execute(
        f'''SELECT a.event_id, a.user_id, a.role_label, u.display_name, u.username
            FROM band_event_assignments a
            JOIN users u ON u.id = a.user_id
            WHERE a.event_id IN ({ph})
            ORDER BY a.event_id, u.display_name, u.username''',
        event_ids,
    )
    out: dict[str, dict] = {}
    for row in c.fetchall():
        r = dict(row)
        eid = r['event_id']
        name = (r.get('display_name') or r.get('username') or '').strip()
        if r.get('role_label'):
            name = f'{name} ({r["role_label"]})' if name else r['role_label']
        if eid not in out:
            out[eid] = {'count': 0, 'names': [], 'preview': ''}
        out[eid]['count'] += 1
        if name:
            out[eid]['names'].append(name)
    db.close()
    for eid, data in out.items():
        names = data['names']
        if len(names) <= 2:
            data['preview'] = ', '.join(names)
        else:
            data['preview'] = f'{names[0]}, {names[1]} +{len(names) - 2}'
    return out


def count_band_events(band_id: str, *, upcoming_only: bool = False) -> int:
    db = get_db()
    c = db.cursor()
    if upcoming_only:
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute(
            'SELECT COUNT(*) AS n FROM band_events WHERE band_id = ? AND starts_at >= ?',
            (band_id, now),
        )
    else:
        c.execute('SELECT COUNT(*) AS n FROM band_events WHERE band_id = ?', (band_id,))
    row = c.fetchone()
    db.close()
    return int(row['n'] if row else 0)
