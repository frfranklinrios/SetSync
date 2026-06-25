"""Instrumentos vinculados ao perfil do usuário."""

from __future__ import annotations

from chord_diagram.instruments import INSTRUMENTS
from db import get_db

_LABEL_OVERRIDES = {
    'piano': 'Piano / teclado',
}

_EXTRA_INSTRUMENTS = (
    ('vocal', 'Vocal'),
    ('bateria', 'Bateria'),
    ('percussao', 'Percussão'),
    ('som', 'Som / áudio'),
    ('violino', 'Violino'),
    ('metais', 'Metais'),
    ('sopros', 'Sopros'),
    ('gaita', 'Gaita'),
)


def _build_catalog() -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for spec in INSTRUMENTS.values():
        if spec.id in seen:
            continue
        seen.add(spec.id)
        out.append({
            'id': spec.id,
            'label': _LABEL_OVERRIDES.get(spec.id, spec.label),
        })
    for iid, label in _EXTRA_INSTRUMENTS:
        if iid in seen:
            continue
        seen.add(iid)
        out.append({'id': iid, 'label': label})
    return out


_INSTRUMENT_CATALOG = _build_catalog()
_CATALOG_IDS = {item['id'] for item in _INSTRUMENT_CATALOG}
_CATALOG_LABELS = {item['id']: item['label'] for item in _INSTRUMENT_CATALOG}


def instrument_catalog() -> list[dict]:
    return list(_INSTRUMENT_CATALOG)


def normalize_instrument_ids(raw_ids: list[str] | None) -> list[str]:
    if not raw_ids:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for raw in raw_ids:
        iid = (raw or '').strip().lower()
        if not iid or iid not in _CATALOG_IDS or iid in seen:
            continue
        seen.add(iid)
        out.append(iid)
    return out


def list_user_instruments(user_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT instrument_id FROM user_instruments
           WHERE user_id = ? ORDER BY sort_order, instrument_id''',
        (user_id,),
    )
    rows = c.fetchall()
    db.close()
    return [
        {'id': row['instrument_id'], 'label': _CATALOG_LABELS[row['instrument_id']]}
        for row in rows
        if row['instrument_id'] in _CATALOG_LABELS
    ]


def instruments_by_user_ids(user_ids: list[str]) -> dict[str, list[dict]]:
    ids = [uid for uid in user_ids if uid]
    if not ids:
        return {}
    placeholders = ','.join('?' * len(ids))
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT user_id, instrument_id, sort_order
            FROM user_instruments
            WHERE user_id IN ({placeholders})
            ORDER BY user_id, sort_order, instrument_id''',
        ids,
    )
    rows = c.fetchall()
    db.close()
    out: dict[str, list[dict]] = {uid: [] for uid in ids}
    for row in rows:
        iid = row['instrument_id']
        if iid not in _CATALOG_LABELS:
            continue
        out.setdefault(row['user_id'], []).append({
            'id': iid,
            'label': _CATALOG_LABELS[iid],
        })
    return out


def instruments_label(user_id: str) -> str:
    return ', '.join(item['label'] for item in list_user_instruments(user_id))


def set_user_instruments(user_id: str, instrument_ids: list[str] | None) -> None:
    normalized = normalize_instrument_ids(instrument_ids)
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM user_instruments WHERE user_id = ?', (user_id,))
    for order, iid in enumerate(normalized):
        c.execute(
            '''INSERT INTO user_instruments (user_id, instrument_id, sort_order)
               VALUES (?, ?, ?)''',
            (user_id, iid, order),
        )
    db.commit()
    db.close()


def enrich_members_with_instruments(members: list[dict]) -> list[dict]:
    if not members:
        return members
    by_user = instruments_by_user_ids([m['id'] for m in members if m.get('id')])
    for member in members:
        uid = member.get('id')
        instruments = by_user.get(uid, [])
        member['instruments'] = instruments
        member['instruments_label'] = ', '.join(i['label'] for i in instruments)
    return members
