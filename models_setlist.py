# Modelos e funções para Setlists
from database import IS_POSTGRES
from db import get_db

def create_setlist(band_id, name, description=None):
    db = get_db()
    c = db.cursor()
    if IS_POSTGRES:
        c.execute(
            'INSERT INTO setlists (band_id, name, description) VALUES (?, ?, ?) RETURNING id',
            (band_id, name, description),
        )
        row = c.fetchone()
        setlist_id = int(row['id']) if row else None
    else:
        c.execute(
            'INSERT INTO setlists (band_id, name, description) VALUES (?, ?, ?)',
            (band_id, name, description),
        )
        setlist_id = c.lastrowid
    db.commit()
    db.close()
    return setlist_id

def get_band_setlists(band_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM setlists WHERE band_id = ?', (band_id,))
    setlists = c.fetchall()
    db.close()
    return setlists

def get_setlist(setlist_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM setlists WHERE id = ?', (setlist_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def set_setlist_vocalist(setlist_id, vocalist_id: str | None) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE setlists SET vocalist_id = ? WHERE id = ?',
        (vocalist_id or None, setlist_id),
    )
    db.commit()
    db.close()

def delete_setlist(setlist_id):
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM setlists WHERE id = ?', (setlist_id,))
    c.execute('DELETE FROM setlist_cifras WHERE setlist_id = ?', (setlist_id,))
    db.commit()
    db.close()

def _default_vocalist_for_setlist(setlist_id) -> str | None:
    sl = get_setlist(setlist_id)
    if not sl:
        return None
    if sl.get('vocalist_id'):
        return sl['vocalist_id']
    from db import get_band_vocalists
    vocalists = get_band_vocalists(sl['band_id'])
    return vocalists[0]['id'] if vocalists else None


def add_cifra_to_setlist(setlist_id, cifra_id, position=None, vocalist_id=None):
    db = get_db()
    c = db.cursor()
    if position is None:
        c.execute(
            'SELECT COALESCE(MAX(position), 0) + 1 AS next_pos FROM setlist_cifras WHERE setlist_id = ?',
            (setlist_id,),
        )
        row = c.fetchone()
        position = int((row['next_pos'] if row else 1) or 1)
    vid = vocalist_id or _default_vocalist_for_setlist(setlist_id)
    c.execute(
        'INSERT INTO setlist_cifras (setlist_id, cifra_id, position, vocalist_id) VALUES (?, ?, ?, ?)',
        (setlist_id, cifra_id, position, vid),
    )
    db.commit()
    db.close()


def set_setlist_cifra_vocalist(setlist_id, cifra_id, vocalist_id: str | None) -> bool:
    """Atualiza cantor da música na setlist. Retorna False se a linha não existir."""
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE setlist_cifras SET vocalist_id = ? WHERE setlist_id = ? AND cifra_id = ?',
        (vocalist_id or None, int(setlist_id), str(cifra_id)),
    )
    updated = (c.rowcount or 0) > 0
    db.commit()
    db.close()
    return updated

def remove_cifra_from_setlist(setlist_id, cifra_id):
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM setlist_cifras WHERE setlist_id = ? AND cifra_id = ?', (setlist_id, cifra_id))
    db.commit()
    db.close()

def reorder_setlist(setlist_id, ordered_cifra_ids):
    db = get_db()
    c = db.cursor()
    for pos, cifra_id in enumerate(ordered_cifra_ids, 1):
        c.execute('UPDATE setlist_cifras SET position = ? WHERE setlist_id = ? AND cifra_id = ?', (pos, setlist_id, cifra_id))
    db.commit()
    db.close()

def count_setlist_cifras_by_ids(setlist_ids: list) -> dict[int, int]:
    """Contagem de faixas por setlist em uma única query."""
    if not setlist_ids:
        return {}
    placeholders = ','.join('?' * len(setlist_ids))
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT setlist_id, COUNT(*) AS n
            FROM setlist_cifras
            WHERE setlist_id IN ({placeholders})
            GROUP BY setlist_id''',
        tuple(setlist_ids),
    )
    rows = c.fetchall()
    db.close()
    counts = {int(sid): 0 for sid in setlist_ids}
    for row in rows:
        counts[int(row['setlist_id'])] = int(row['n'])
    return counts


def get_setlist_cifras(setlist_id):
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT cifras.*,
                  setlist_cifras.vocalist_id AS setlist_vocalist_id,
                  setlist_cifras.play_notes AS setlist_play_notes
           FROM cifras
           JOIN setlist_cifras ON cifras.id = setlist_cifras.cifra_id
           WHERE setlist_cifras.setlist_id = ?
           ORDER BY setlist_cifras.position''',
        (setlist_id,),
    )
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def set_setlist_cifra_play_notes(setlist_id, cifra_id, play_notes: str | None) -> bool:
    """Notas de palco desta música na setlist."""
    notes = (play_notes or '').strip() or None
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE setlist_cifras SET play_notes = ? WHERE setlist_id = ? AND cifra_id = ?',
        (notes, int(setlist_id), str(cifra_id)),
    )
    updated = (c.rowcount or 0) > 0
    db.commit()
    db.close()
    return updated


def clone_setlist(source_setlist_id: int, *, name: str | None = None) -> int | None:
    """Copia setlist (metadados + músicas/ordem/cantor/notas) para a mesma banda."""
    source = get_setlist(source_setlist_id)
    if not source:
        return None
    band_id = source['band_id']
    base_name = (name or '').strip() or f"{source.get('name') or 'Setlist'} (cópia)"
    new_id = create_setlist(band_id, base_name[:120], source.get('description'))
    if not new_id:
        return None
    if source.get('vocalist_id'):
        set_setlist_vocalist(new_id, source['vocalist_id'])

    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT cifra_id, position, vocalist_id, play_notes
           FROM setlist_cifras WHERE setlist_id = ? ORDER BY position''',
        (int(source_setlist_id),),
    )
    rows = c.fetchall()
    for r in rows:
        c.execute(
            '''INSERT INTO setlist_cifras (setlist_id, cifra_id, position, vocalist_id, play_notes)
               VALUES (?, ?, ?, ?, ?)''',
            (
                int(new_id),
                r['cifra_id'],
                r['position'],
                r.get('vocalist_id'),
                r.get('play_notes'),
            ),
        )
    db.commit()
    db.close()
    return int(new_id)


def find_suggestable_setlist(
    band_id: str,
    *,
    exclude_setlist_id: int | None = None,
) -> dict | None:
    """Último setlist com músicas usado em evento da banda (senão o mais cheio da banda)."""
    db = get_db()
    c = db.cursor()
    params: list = [band_id]
    exclude_sql = ''
    if exclude_setlist_id:
        exclude_sql = ' AND s.id <> ?'
        params.append(int(exclude_setlist_id))
    c.execute(
        f'''SELECT s.id, s.name, e.title AS event_title, e.starts_at,
                  (SELECT COUNT(*) FROM setlist_cifras sc WHERE sc.setlist_id = s.id) AS n_songs
           FROM band_events e
           JOIN setlists s ON s.id = e.setlist_id AND s.band_id = e.band_id
           WHERE e.band_id = ?
             {exclude_sql}
             AND EXISTS (SELECT 1 FROM setlist_cifras sc WHERE sc.setlist_id = s.id)
           ORDER BY e.starts_at DESC
           LIMIT 1''',
        params,
    )
    row = c.fetchone()
    if row:
        db.close()
        d = dict(row)
        d['source'] = 'event'
        return d

    params2: list = [band_id]
    exclude2 = ''
    if exclude_setlist_id:
        exclude2 = ' AND s.id <> ?'
        params2.append(int(exclude_setlist_id))
    c.execute(
        f'''SELECT s.id, s.name, NULL AS event_title, NULL AS starts_at,
                  (SELECT COUNT(*) FROM setlist_cifras sc WHERE sc.setlist_id = s.id) AS n_songs
           FROM setlists s
           WHERE s.band_id = ?
             {exclude2}
             AND EXISTS (SELECT 1 FROM setlist_cifras sc WHERE sc.setlist_id = s.id)
           ORDER BY n_songs DESC, s.id DESC
           LIMIT 1''',
        params2,
    )
    row = c.fetchone()
    db.close()
    if not row:
        return None
    d = dict(row)
    d['source'] = 'band'
    return d
