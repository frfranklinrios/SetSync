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
    setlist = c.fetchone()
    db.close()
    return setlist

def delete_setlist(setlist_id):
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM setlists WHERE id = ?', (setlist_id,))
    c.execute('DELETE FROM setlist_cifras WHERE setlist_id = ?', (setlist_id,))
    db.commit()
    db.close()

def add_cifra_to_setlist(setlist_id, cifra_id, position=None):
    db = get_db()
    c = db.cursor()
    if position is None:
        c.execute('SELECT COALESCE(MAX(position), 0) + 1 FROM setlist_cifras WHERE setlist_id = ?', (setlist_id,))
        position = c.fetchone()[0]
    c.execute('INSERT INTO setlist_cifras (setlist_id, cifra_id, position) VALUES (?, ?, ?)', (setlist_id, cifra_id, position))
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
    c.execute('''SELECT cifras.* FROM cifras 
                 JOIN setlist_cifras ON cifras.id = setlist_cifras.cifra_id 
                 WHERE setlist_cifras.setlist_id = ? 
                 ORDER BY setlist_cifras.position''', (setlist_id,))
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]
