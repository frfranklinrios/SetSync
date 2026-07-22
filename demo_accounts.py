"""Contas e bandas de demonstração (showcase / marketing / QA).

Usadas no painel Master: destaque visual e exclusão dos totais financeiros.
A marcação efetiva combina flag no banco (`users.is_demo`) com heurística
de username/e-mail e listas do .env.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable


# Contas conhecidas de seed (marketing / merch / estúdio).
_DEFAULT_DEMO_USERNAMES = frozenset({
    'showcase',
    'igreja_showcase',
    'carlos_groove',
    'lucas_showcase',
    'bia_showcase',
    'raf_showcase',
    'estudio_teste',
})

_DEFAULT_DEMO_EMAILS = frozenset({
    'showcase@unissono.app',
    'igreja.showcase@unissono.app',
    'carlos.groove@unissono.app',
    'showcase@setsync.com.br',
    'lucas@setsync.com.br',
    'bia@setsync.com.br',
    'raf@setsync.com.br',
})


def _csv_env(name: str) -> frozenset[str]:
    raw = (os.getenv(name) or '').strip()
    if not raw:
        return frozenset()
    return frozenset(p.strip().lower() for p in raw.split(',') if p.strip())


@lru_cache(maxsize=1)
def demo_usernames() -> frozenset[str]:
    return _DEFAULT_DEMO_USERNAMES | _csv_env('SETSYNC_DEMO_USERNAMES')


@lru_cache(maxsize=1)
def demo_emails() -> frozenset[str]:
    return _DEFAULT_DEMO_EMAILS | _csv_env('SETSYNC_DEMO_EMAILS')


def is_demo_username(username: str | None) -> bool:
    u = (username or '').strip().lower()
    if not u:
        return False
    if u in demo_usernames():
        return True
    # Membros gerados como *_showcase
    return u.endswith('_showcase') or 'showcase' in u


def is_demo_email(email: str | None) -> bool:
    e = (email or '').strip().lower()
    if not e:
        return False
    if e in demo_emails():
        return True
    local, _, domain = e.partition('@')
    return 'showcase' in local or local.endswith('.showcase')


def is_demo_manual(user: dict | None) -> bool:
    """Flag persistente marcada no admin (`users.is_demo`)."""
    if not user:
        return False
    return bool(user.get('is_demo'))


def is_demo_heuristic(user: dict | None) -> bool:
    """Showcase / .env — independente da flag manual."""
    if not user:
        return False
    return is_demo_username(user.get('username')) or is_demo_email(user.get('email'))


def is_demo_user(user: dict | None) -> bool:
    if not user:
        return False
    return is_demo_manual(user) or is_demo_heuristic(user)


def is_demo_user_id(user_id: str | None) -> bool:
    if not user_id:
        return False
    from db import get_user

    return is_demo_user(get_user(user_id))


def demo_user_ids() -> set[str]:
    """IDs de usuários demo no banco (consulta leve)."""
    from database import get_db

    names = list(demo_usernames())
    emails = list(demo_emails())
    db = get_db()
    c = db.cursor()
    ids: set[str] = set()
    # Flag manual no banco
    try:
        c.execute('SELECT id FROM users WHERE COALESCE(is_demo, 0) = 1')
        for r in c.fetchall():
            ids.add(str(r['id']))
    except Exception:
        pass
    # Usernames fixos
    if names:
        ph = ','.join('?' for _ in names)
        c.execute(
            f'SELECT id, username, email FROM users WHERE lower(username) IN ({ph})',
            [n.lower() for n in names],
        )
        for r in c.fetchall():
            ids.add(str(r['id']))
    # Emails fixos
    if emails:
        ph = ','.join('?' for _ in emails)
        c.execute(
            f'SELECT id FROM users WHERE lower(email) IN ({ph})',
            [e.lower() for e in emails],
        )
        for r in c.fetchall():
            ids.add(str(r['id']))
    # Sufixo / padrão showcase
    c.execute('SELECT id, username, email FROM users')
    for r in c.fetchall():
        if is_demo_username(r.get('username')) or is_demo_email(r.get('email')):
            ids.add(str(r['id']))
    db.close()
    return ids


def demo_band_ids(user_ids: Iterable[str] | None = None) -> set[str]:
    """Bandas cujo titular é conta demo."""
    uids = set(user_ids) if user_ids is not None else demo_user_ids()
    if not uids:
        return set()
    from database import get_db

    db = get_db()
    c = db.cursor()
    ph = ','.join('?' for _ in uids)
    c.execute(
        f'SELECT id FROM bands WHERE owner_id IN ({ph})',
        list(uids),
    )
    ids = {str(r['id']) for r in c.fetchall()}
    db.close()
    return ids


def is_demo_band(band: dict | None, *, owner: dict | None = None) -> bool:
    if not band:
        return False
    if owner is not None:
        return is_demo_user(owner)
    return is_demo_user_id(band.get('owner_id'))
