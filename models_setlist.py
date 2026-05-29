# Modelos e funções para Setlists
import sqlite3
from db import get_db

def create_setlist(band_id, name, description=None):
    db = get_db()
    c = db.cursor()
    c.execute('INSERT INTO setlists (band_id, name, description) VALUES (?, ?, ?)', (band_id, name, description))
    db.commit()
    setlist_id = c.lastrowid
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
        c.execute('SELECT COALESCE(MAX(position), 0) + 1 FROM setlist_cifras WHERE setlist_id = ?', (setlist_id,))
        position = c.fetchone()[0]
    vid = vocalist_id or _default_vocalist_for_setlist(setlist_id)
    c.execute(
        'INSERT INTO setlist_cifras (setlist_id, cifra_id, position, vocalist_id) VALUES (?, ?, ?, ?)',
        (setlist_id, cifra_id, position, vid),
    )
    db.commit()
    db.close()


def set_setlist_cifra_vocalist(setlist_id, cifra_id, vocalist_id: str | None) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE setlist_cifras SET vocalist_id = ? WHERE setlist_id = ? AND cifra_id = ?',
        (vocalist_id or None, setlist_id, cifra_id),
    )
    db.commit()
    db.close()

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

def get_setlist_cifras(setlist_id):
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT cifras.*, setlist_cifras.vocalist_id AS setlist_vocalist_id
           FROM cifras
           JOIN setlist_cifras ON cifras.id = setlist_cifras.cifra_id
           WHERE setlist_cifras.setlist_id = ?
           ORDER BY setlist_cifras.position''',
        (setlist_id,),
    )
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]
