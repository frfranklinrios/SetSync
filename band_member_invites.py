"""Convites de membro para banda (aceitar antes de entrar)."""
from __future__ import annotations

import uuid
from datetime import datetime

from db import get_db, get_user


def _migrate_schema(c) -> None:
    c.execute(
        '''CREATE TABLE IF NOT EXISTS band_member_invites (
            id TEXT PRIMARY KEY,
            band_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            invited_by TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responded_at TIMESTAMP,
            UNIQUE (band_id, user_id),
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL
        )'''
    )
    c.execute(
        '''CREATE INDEX IF NOT EXISTS idx_band_member_invites_user_pending
           ON band_member_invites(user_id, status)'''
    )


def ensure_band_member_invites_schema() -> None:
    db = get_db()
    c = db.cursor()
    _migrate_schema(c)
    db.commit()
    db.close()


def _row_to_invite(row) -> dict | None:
    if not row:
        return None
    return dict(row)


def get_band_member_invite(invite_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT i.*, b.name AS band_name,
                  inviter.display_name AS inviter_display_name,
                  inviter.username AS inviter_username
           FROM band_member_invites i
           JOIN bands b ON b.id = i.band_id
           LEFT JOIN users inviter ON inviter.id = i.invited_by
           WHERE i.id = ?''',
        (invite_id,),
    )
    row = c.fetchone()
    db.close()
    return _row_to_invite(row)


def list_pending_invites_for_user(user_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT i.*, b.name AS band_name,
                  inviter.display_name AS inviter_display_name,
                  inviter.username AS inviter_username
           FROM band_member_invites i
           JOIN bands b ON b.id = i.band_id
           LEFT JOIN users inviter ON inviter.id = i.invited_by
           WHERE i.user_id = ? AND i.status = 'pending'
           ORDER BY i.created_at DESC''',
        (user_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_pending_invites_for_band(band_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT i.*, u.email AS user_email,
                  u.display_name AS user_display_name,
                  u.username AS user_username
           FROM band_member_invites i
           JOIN users u ON u.id = i.user_id
           WHERE i.band_id = ? AND i.status = 'pending'
           ORDER BY i.created_at DESC''',
        (band_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def create_band_member_invite(
    band_id: str,
    user_id: str,
    invited_by: str,
    *,
    role: str = 'member',
) -> str:
    """
    Cria ou reabre convite pendente.
    Retorna: 'created', 'already_pending', 'already_member'.
    """
    from db import is_band_member

    if is_band_member(band_id, user_id):
        return 'already_member'

    role = role if role in ('member', 'editor', 'admin') else 'member'
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT id, status FROM band_member_invites WHERE band_id = ? AND user_id = ?',
        (band_id, user_id),
    )
    row = c.fetchone()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if row:
        if row['status'] == 'pending':
            db.close()
            return 'already_pending'
        invite_id = row['id']
        c.execute(
            '''UPDATE band_member_invites
               SET status = 'pending', invited_by = ?, role = ?, created_at = ?, responded_at = NULL
               WHERE id = ?''',
            (invited_by, role, now, invite_id),
        )
        db.commit()
        db.close()
        return 'created'

    invite_id = str(uuid.uuid4())
    c.execute(
        '''INSERT INTO band_member_invites
           (id, band_id, user_id, invited_by, role, status, created_at)
           VALUES (?, ?, ?, ?, ?, 'pending', ?)''',
        (invite_id, band_id, user_id, invited_by, role, now),
    )
    db.commit()
    db.close()
    return 'created'


def accept_band_member_invite(invite_id: str, user_id: str) -> tuple[bool, str]:
    """Retorna (ok, código): ok | invalid | limit."""
    from db import add_band_member, get_band, is_band_member
    from monetizacao import check_limite

    inv = get_band_member_invite(invite_id)
    if not inv or inv['user_id'] != user_id or inv['status'] != 'pending':
        return False, 'invalid'

    band = get_band(inv['band_id'])
    if not band:
        return False, 'invalid'

    if is_band_member(inv['band_id'], user_id):
        _set_invite_status(invite_id, 'accepted')
        return True, 'ok'

    if not check_limite(band, 'integrante'):
        return False, 'limit'

    add_band_member(inv['band_id'], user_id, inv.get('role') or 'member')
    _set_invite_status(invite_id, 'accepted')
    return True, 'ok'


def decline_band_member_invite(invite_id: str, user_id: str) -> bool:
    inv = get_band_member_invite(invite_id)
    if not inv or inv['user_id'] != user_id or inv['status'] != 'pending':
        return False
    _set_invite_status(invite_id, 'declined')
    return True


def cancel_band_member_invite(invite_id: str, band_id: str) -> bool:
    inv = get_band_member_invite(invite_id)
    if not inv or inv['band_id'] != band_id or inv['status'] != 'pending':
        return False
    _set_invite_status(invite_id, 'cancelled')
    return True


def _set_invite_status(invite_id: str, status: str) -> None:
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE band_member_invites SET status = ?, responded_at = ? WHERE id = ?',
        (status, now, invite_id),
    )
    db.commit()
    db.close()


def inviter_display_name(invite: dict) -> str:
    from db import user_display_name

    u = {
        'display_name': invite.get('inviter_display_name'),
        'username': invite.get('inviter_username'),
    }
    if invite.get('inviter_display_name') or invite.get('inviter_username'):
        return user_display_name(u)
    if invite.get('invited_by'):
        return user_display_name(get_user(invite['invited_by']))
    return 'Alguém'
