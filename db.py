import sqlite3
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'banda.db')


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = get_db()
    c = db.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bands (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS band_members (
            band_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (band_id, user_id),
            FOREIGN KEY (band_id) REFERENCES bands(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS cifras (
            id TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            artista TEXT NOT NULL,
            tom_original TEXT DEFAULT 'C',
            conteudo TEXT NOT NULL DEFAULT '',
            band_id TEXT NOT NULL,
            cifra_json TEXT,
            grade_json TEXT,
            bpm REAL,
            duracao_seg INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (band_id) REFERENCES bands(id)
        );

        CREATE TABLE IF NOT EXISTS setlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            band_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (band_id) REFERENCES bands(id)
        );

        CREATE TABLE IF NOT EXISTS setlist_cifras (
            setlist_id INTEGER NOT NULL,
            cifra_id TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            PRIMARY KEY (setlist_id, cifra_id),
            FOREIGN KEY (setlist_id) REFERENCES setlists(id),
            FOREIGN KEY (cifra_id) REFERENCES cifras(id)
        );
    ''')
    db.commit()

    # Migration: colunas novas em BDs já existentes
    def _add_column(table: str, col: str, typedef: str) -> None:
        cols = {row[1] for row in c.execute(f'PRAGMA table_info({table})')}
        if col not in cols:
            c.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')
            db.commit()

    _add_column('users', 'display_name', 'TEXT')
    for col, typedef in [
        ('cifra_json', 'TEXT'),
        ('grade_json', 'TEXT'),
        ('bpm', 'REAL'),
        ('duracao_seg', 'INTEGER'),
    ]:
        _add_column('cifras', col, typedef)

    db.close()


def update_user_display_name(user_id: str, display_name: str | None):
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE users SET display_name = ? WHERE id = ?', (display_name, user_id))
    db.commit()
    db.close()


# ── Users ──────────────────────────────────────────────────────────────────

def create_user(username, email, password, display_name: str | None = None):
    db = get_db()
    c = db.cursor()
    try:
        user_id = str(uuid.uuid4())
        c.execute(
            'INSERT INTO users (id, username, display_name, email, password_hash) VALUES (?, ?, ?, ?, ?)',
            (user_id, username, (display_name or None), email, generate_password_hash(password))
        )
        db.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        db.close()


def create_google_user(google_id, email, username, display_name: str | None = None):
    db = get_db()
    c = db.cursor()
    try:
        # Garantir username único
        base = username
        attempt = username
        i = 1
        while True:
            c.execute('SELECT id FROM users WHERE username = ?', (attempt,))
            if not c.fetchone():
                break
            attempt = f'{base}{i}'
            i += 1
        user_id = str(uuid.uuid4())
        c.execute(
            'INSERT INTO users (id, username, display_name, email, google_id) VALUES (?, ?, ?, ?, ?)',
            (user_id, attempt, (display_name or None), email, google_id)
        )
        db.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        db.close()


def get_user(user_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_user_by_username(username):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_user_by_email(email):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_user_by_google_id(google_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def verify_password(user_id, password):
    user = get_user(user_id)
    if not user or not user.get('password_hash'):
        return False
    return check_password_hash(user['password_hash'], password)


# ── Bands ──────────────────────────────────────────────────────────────────

def create_band(name, description, owner_id):
    db = get_db()
    c = db.cursor()
    band_id = str(uuid.uuid4())
    c.execute(
        'INSERT INTO bands (id, name, description, owner_id) VALUES (?, ?, ?, ?)',
        (band_id, name, description, owner_id)
    )
    # Owner é automaticamente membro com role 'owner'
    c.execute(
        'INSERT INTO band_members (band_id, user_id, role) VALUES (?, ?, ?)',
        (band_id, owner_id, 'owner')
    )
    db.commit()
    db.close()
    return band_id


def get_band(band_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM bands WHERE id = ?', (band_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def update_band(band_id, name, description):
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE bands SET name = ?, description = ? WHERE id = ?', (name, description, band_id))
    db.commit()
    db.close()


def delete_band(band_id):
    db = get_db()
    c = db.cursor()
    # Remover em cascata: setlist_cifras → setlists → cifras → band_members → band
    c.execute('''DELETE FROM setlist_cifras WHERE setlist_id IN
                 (SELECT id FROM setlists WHERE band_id = ?)''', (band_id,))
    c.execute('DELETE FROM setlists WHERE band_id = ?', (band_id,))
    c.execute('DELETE FROM cifras WHERE band_id = ?', (band_id,))
    c.execute('DELETE FROM band_members WHERE band_id = ?', (band_id,))
    c.execute('DELETE FROM bands WHERE id = ?', (band_id,))
    db.commit()
    db.close()


def get_user_bands(user_id):
    """Todas as bandas das quais o usuário é membro (incluindo as que é dono)."""
    db = get_db()
    c = db.cursor()
    c.execute('''
        SELECT bands.* FROM bands
        JOIN band_members ON bands.id = band_members.band_id
        WHERE band_members.user_id = ?
    ''', (user_id,))
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_owned_bands(user_id):
    """Bandas cujo dono é o usuário."""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM bands WHERE owner_id = ?', (user_id,))
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_band_members(band_id):
    db = get_db()
    c = db.cursor()
    c.execute('''
        SELECT users.*, band_members.role FROM users
        JOIN band_members ON users.id = band_members.user_id
        WHERE band_members.band_id = ?
    ''', (band_id,))
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def add_band_member(band_id, user_id, role='member'):
    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            'INSERT INTO band_members (band_id, user_id, role) VALUES (?, ?, ?)',
            (band_id, user_id, role)
        )
        db.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        db.close()


def remove_band_member(band_id, user_id):
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM band_members WHERE band_id = ? AND user_id = ?', (band_id, user_id))
    db.commit()
    db.close()


def is_band_member(band_id, user_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT 1 FROM band_members WHERE band_id = ? AND user_id = ?', (band_id, user_id))
    result = c.fetchone() is not None
    db.close()
    return result


def is_band_admin(band_id, user_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM bands WHERE id = ?', (band_id,))
    band = c.fetchone()
    if band and band['owner_id'] == user_id:
        db.close()
        return True
    c.execute(
        "SELECT 1 FROM band_members WHERE band_id = ? AND user_id = ? AND role IN ('admin', 'owner')",
        (band_id, user_id)
    )
    result = c.fetchone() is not None
    db.close()
    return result


# ── Cifras ─────────────────────────────────────────────────────────────────

def create_cifra(titulo, artista, tom_original, conteudo, band_id,
                 cifra_json=None, grade_json=None, bpm=None, duracao_seg=None):
    db = get_db()
    c = db.cursor()
    cifra_id = str(uuid.uuid4())
    c.execute(
        '''INSERT INTO cifras
           (id, titulo, artista, tom_original, conteudo, band_id,
            cifra_json, grade_json, bpm, duracao_seg)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (cifra_id, titulo, artista, tom_original, conteudo or '', band_id,
         cifra_json, grade_json, bpm, duracao_seg)
    )
    db.commit()
    db.close()
    return cifra_id


def get_cifra(cifra_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM cifras WHERE id = ?', (cifra_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_band_cifras(band_id):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM cifras WHERE band_id = ? ORDER BY titulo', (band_id,))
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def update_cifra(cifra_id, titulo, artista, tom_original, conteudo,
                 cifra_json=None, grade_json=None, bpm=None, duracao_seg=None):
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE cifras SET titulo=?, artista=?, tom_original=?, conteudo=?,
           cifra_json=?, grade_json=?, bpm=?, duracao_seg=?,
           updated_at=CURRENT_TIMESTAMP WHERE id=?''',
        (titulo, artista, tom_original, conteudo or '',
         cifra_json, grade_json, bpm, duracao_seg, cifra_id)
    )
    db.commit()
    db.close()


def delete_cifra(cifra_id):
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM setlist_cifras WHERE cifra_id = ?', (cifra_id,))
    c.execute('DELETE FROM cifras WHERE id = ?', (cifra_id,))
    db.commit()
    db.close()
