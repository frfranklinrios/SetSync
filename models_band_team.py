"""Funções, formações, reservas, indisponibilidade e convidados de eventos."""
from __future__ import annotations

import uuid
from datetime import datetime

from database import IS_POSTGRES, IntegrityError
from db import get_db

DEFAULT_BAND_ROLES = (
    'Vocal',
    'Guitarra',
    'Baixo',
    'Bateria',
    'Teclado',
    'Violão',
    'Som',
)


def ensure_default_band_roles(band_id: str) -> None:
    if list_band_roles(band_id):
        return
    db = get_db()
    c = db.cursor()
    for i, label in enumerate(DEFAULT_BAND_ROLES):
        c.execute(
            'INSERT INTO band_roles (band_id, label, sort_order) VALUES (?, ?, ?)',
            (band_id, label, i),
        )
    db.commit()
    db.close()


def list_band_roles(band_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM band_roles WHERE band_id = ? ORDER BY sort_order, label',
        (band_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def add_band_role(band_id: str, label: str) -> bool:
    label = (label or '').strip()[:40]
    if not label:
        return False
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT COALESCE(MAX(sort_order), -1) + 1 AS n FROM band_roles WHERE band_id = ?',
        (band_id,),
    )
    row = c.fetchone()
    order = int(row['n'] if row else 0)
    try:
        c.execute(
            'INSERT INTO band_roles (band_id, label, sort_order) VALUES (?, ?, ?)',
            (band_id, label, order),
        )
        db.commit()
        ok = True
    except IntegrityError:
        ok = False
    db.close()
    return ok


def delete_band_role(band_id: str, label: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'DELETE FROM band_roles WHERE band_id = ? AND label = ?',
        (band_id, label),
    )
    db.commit()
    db.close()


def list_band_lineups(band_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT l.*, COUNT(m.user_id) AS member_count
           FROM band_lineups l
           LEFT JOIN band_lineup_members m ON m.lineup_id = l.id
           WHERE l.band_id = ?
           GROUP BY l.id
           ORDER BY l.name''',
        (band_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def get_lineup(lineup_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM band_lineups WHERE id = ?', (lineup_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_lineup_members(lineup_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT m.*, u.display_name, u.username, u.email
           FROM band_lineup_members m
           JOIN users u ON u.id = m.user_id
           WHERE m.lineup_id = ?
           ORDER BY m.sort_order, u.display_name, u.username''',
        (lineup_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def create_lineup(band_id: str, name: str, members: list[dict]) -> str:
    lineup_id = str(uuid.uuid4())
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        'INSERT INTO band_lineups (id, band_id, name, created_at) VALUES (?, ?, ?, ?)',
        (lineup_id, band_id, name.strip()[:80], now),
    )
    for i, item in enumerate(members):
        uid = item.get('user_id')
        if not uid:
            continue
        role = (item.get('role_label') or '').strip()[:40] or None
        c.execute(
            '''INSERT INTO band_lineup_members (lineup_id, user_id, role_label, sort_order)
               VALUES (?, ?, ?, ?)''',
            (lineup_id, uid, role, i),
        )
    db.commit()
    db.close()
    return lineup_id


def update_lineup(lineup_id: str, name: str, members: list[dict]) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE band_lineups SET name = ? WHERE id = ?', (name.strip()[:80], lineup_id))
    c.execute('DELETE FROM band_lineup_members WHERE lineup_id = ?', (lineup_id,))
    for i, item in enumerate(members):
        uid = item.get('user_id')
        if not uid:
            continue
        role = (item.get('role_label') or '').strip()[:40] or None
        c.execute(
            '''INSERT INTO band_lineup_members (lineup_id, user_id, role_label, sort_order)
               VALUES (?, ?, ?, ?)''',
            (lineup_id, uid, role, i),
        )
    db.commit()
    db.close()


def delete_lineup(lineup_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM band_lineup_members WHERE lineup_id = ?', (lineup_id,))
    c.execute('DELETE FROM band_lineups WHERE id = ?', (lineup_id,))
    db.commit()
    db.close()


def lineup_assignments(lineup_id: str) -> list[dict]:
    return [
        {'user_id': m['user_id'], 'role_label': m.get('role_label')}
        for m in get_lineup_members(lineup_id)
    ]


def list_role_substitutes(band_id: str, role_label: str | None = None) -> list[dict]:
    db = get_db()
    c = db.cursor()
    if role_label:
        c.execute(
            '''SELECT s.*, u.display_name, u.username
               FROM band_role_substitutes s
               JOIN users u ON u.id = s.user_id
               WHERE s.band_id = ? AND s.role_label = ?
               ORDER BY s.sort_order, u.display_name''',
            (band_id, role_label),
        )
    else:
        c.execute(
            '''SELECT s.*, u.display_name, u.username
               FROM band_role_substitutes s
               JOIN users u ON u.id = s.user_id
               WHERE s.band_id = ?
               ORDER BY s.role_label, s.sort_order, u.display_name''',
            (band_id,),
        )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def set_role_substitutes(band_id: str, role_label: str, user_ids: list[str]) -> None:
    role_label = (role_label or '').strip()[:40]
    if not role_label:
        return
    db = get_db()
    c = db.cursor()
    c.execute(
        'DELETE FROM band_role_substitutes WHERE band_id = ? AND role_label = ?',
        (band_id, role_label),
    )
    for i, uid in enumerate(user_ids or []):
        if not uid:
            continue
        c.execute(
            '''INSERT INTO band_role_substitutes (band_id, role_label, user_id, sort_order)
               VALUES (?, ?, ?, ?)''',
            (band_id, role_label, uid, i),
        )
    db.commit()
    db.close()


def list_user_blockouts(user_id: str) -> list[dict]:
    today = datetime.utcnow().strftime('%Y-%m-%d')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM user_availability_blockouts
           WHERE user_id = ? AND block_date >= ?
           ORDER BY block_date''',
        (user_id, today),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def add_user_blockout(user_id: str, block_date: str, note: str | None = None) -> bool:
    block_date = (block_date or '').strip()[:10]
    if len(block_date) != 10:
        return False
    note = (note or '').strip()[:200] or None
    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            '''INSERT INTO user_availability_blockouts (user_id, block_date, note)
               VALUES (?, ?, ?)''',
            (user_id, block_date, note),
        )
        db.commit()
        ok = True
    except IntegrityError:
        ok = False
    db.close()
    return ok


def remove_user_blockout(user_id: str, block_date: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'DELETE FROM user_availability_blockouts WHERE user_id = ? AND block_date = ?',
        (user_id, block_date),
    )
    db.commit()
    db.close()


def users_blocked_on_date(user_ids: list[str], event_date: str) -> set[str]:
    if not user_ids or not event_date:
        return set()
    day = str(event_date)[:10]
    db = get_db()
    c = db.cursor()
    ph = ','.join('?' * len(user_ids))
    c.execute(
        f'''SELECT user_id FROM user_availability_blockouts
            WHERE block_date = ? AND user_id IN ({ph})''',
        [day, *user_ids],
    )
    blocked = {str(r['user_id']) for r in c.fetchall()}
    db.close()
    return blocked


def list_event_guests(event_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM band_event_guests WHERE event_id = ? ORDER BY name',
        (event_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def add_event_guest(
    event_id: str,
    *,
    name: str,
    phone: str | None = None,
    role_label: str | None = None,
    invited_by: str | None = None,
) -> str:
    guest_id = str(uuid.uuid4())
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO band_event_guests
           (id, event_id, name, phone, role_label, invited_by, response_status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)''',
        (
            guest_id,
            event_id,
            name.strip()[:80],
            (phone or '').strip()[:20] or None,
            (role_label or '').strip()[:40] or None,
            invited_by,
            now,
        ),
    )
    db.commit()
    db.close()
    return guest_id


def remove_event_guest(guest_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM band_event_guests WHERE id = ?', (guest_id,))
    db.commit()
    db.close()


def get_assignment_response_stats(event_id: str) -> dict:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT response_status, COUNT(*) AS n
           FROM band_event_assignments WHERE event_id = ?
           GROUP BY response_status''',
        (event_id,),
    )
    stats = {'pending': 0, 'accepted': 0, 'declined': 0, 'total': 0}
    for row in c.fetchall():
        st = (row['response_status'] or 'pending').lower()
        n = int(row['n'])
        if st in stats:
            stats[st] = n
        stats['total'] += n
    db.close()
    return stats


def list_pending_assignments_for_user(user_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''SELECT a.*, e.title, e.starts_at, e.event_type, e.location,
                  b.id AS band_id, b.name AS band_name
           FROM band_event_assignments a
           JOIN band_events e ON e.id = a.event_id
           JOIN bands b ON b.id = e.band_id
           WHERE a.user_id = ?
             AND COALESCE(a.response_status, 'pending') = 'pending'
             AND e.starts_at >= ?
           ORDER BY e.starts_at ASC''',
        (user_id, now),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_events_pending_responses_for_editor(user_id: str) -> list[dict]:
    """Eventos futuros com respostas pendentes em bandas que o usuário pode editar."""
    from db import is_band_editor

    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''SELECT e.id, e.title, e.starts_at, e.band_id, b.name AS band_name,
                  SUM(CASE WHEN COALESCE(a.response_status, 'pending') = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                  SUM(CASE WHEN a.response_status = 'accepted' THEN 1 ELSE 0 END) AS accepted_count,
                  SUM(CASE WHEN a.response_status = 'declined' THEN 1 ELSE 0 END) AS declined_count,
                  COUNT(a.user_id) AS total_count
           FROM band_events e
           JOIN bands b ON b.id = e.band_id
           JOIN band_event_assignments a ON a.event_id = e.id
           WHERE e.starts_at >= ?
           GROUP BY e.id, e.title, e.starts_at, e.band_id, b.name
           HAVING SUM(CASE WHEN COALESCE(a.response_status, 'pending') = 'pending' THEN 1 ELSE 0 END) > 0
           ORDER BY e.starts_at ASC''',
        (now,),
    )
    rows = []
    for row in c.fetchall():
        r = dict(row)
        if is_band_editor(r['band_id'], user_id):
            rows.append(r)
    db.close()
    return rows


def suggest_scale_assignments(band_id: str, event_id: str | None = None) -> list[dict]:
    """Sugere escala com base no último evento similar ou na primeira formação."""
    from models_agenda import get_band_event, get_event_assignments

    event = get_band_event(event_id) if event_id else None
    event_type = (event or {}).get('event_type') or 'ensaio'
    event_date = str((event or {}).get('starts_at') or '')[:10]

    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT e.id FROM band_events e
           WHERE e.band_id = ? AND e.event_type = ?
             AND EXISTS (SELECT 1 FROM band_event_assignments a WHERE a.event_id = e.id)
           ORDER BY e.starts_at DESC LIMIT 1''',
        (band_id, event_type),
    )
    row = c.fetchone()
    source_assignments: list[dict] = []
    reason = 'Último evento do mesmo tipo'
    if row:
        source_assignments = get_event_assignments(row['id'])
    else:
        lineups = list_band_lineups(band_id)
        if lineups:
            members = get_lineup_members(lineups[0]['id'])
            source_assignments = [
                {'user_id': m['user_id'], 'role_label': m.get('role_label')}
                for m in members
            ]
            reason = f'Formação «{lineups[0]["name"]}»'

    db.close()
    if not source_assignments:
        return []

    user_ids = [a['user_id'] for a in source_assignments if a.get('user_id')]
    blocked = users_blocked_on_date(user_ids, event_date) if event_date else set()

    out = []
    for a in source_assignments:
        uid = a.get('user_id')
        if not uid:
            continue
        item = {
            'user_id': uid,
            'role_label': a.get('role_label'),
            'reason': reason,
            'blocked': uid in blocked,
        }
        out.append(item)
    return out
