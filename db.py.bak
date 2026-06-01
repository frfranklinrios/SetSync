import sqlite3
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

def _resolve_db_path() -> str:
    """Caminho do SQLite: DATABASE_URL (sqlite:///...) ou data/banda.db."""
    url = (os.getenv('DATABASE_URL') or '').strip()
    if url.startswith('sqlite:///'):
        rel = url[len('sqlite:///'):]
        if os.path.isabs(rel):
            return rel
        return os.path.normpath(os.path.join(os.path.dirname(__file__), rel))
    return os.path.join(os.path.dirname(__file__), 'data', 'banda.db')


DB_PATH = _resolve_db_path()


def _env_superadmin_identifiers():
    """Usernames ou e-mails com privilégio de admin global (variáveis de ambiente)."""
    usernames = {
        s.strip().lower()
        for s in os.getenv('SETSYNC_SUPERADMIN_USERNAMES', '').split(',')
        if s.strip()
    }
    emails = {
        s.strip().lower()
        for s in os.getenv('SETSYNC_SUPERADMIN_EMAILS', '').split(',')
        if s.strip()
    }
    return usernames, emails


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
    _add_column('cifras', 'leadsheet_json', 'TEXT')
    _add_column('cifras', 'transpose_semitones', 'INTEGER DEFAULT 0')
    _add_column('bands', 'vocalist_user_id', 'TEXT')
    _add_column('bands', 'vocalist_name', 'TEXT')
    _add_column('setlists', 'vocalist_id', 'TEXT')
    _add_column('setlist_cifras', 'vocalist_id', 'TEXT')

    c.execute('''
        CREATE TABLE IF NOT EXISTS band_vocalists (
            id TEXT PRIMARY KEY,
            band_id TEXT NOT NULL,
            name TEXT NOT NULL,
            user_id TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cifra_vocalist_transpose (
            cifra_id TEXT NOT NULL,
            vocalist_id TEXT NOT NULL,
            transpose_semitones INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (cifra_id, vocalist_id),
            FOREIGN KEY (cifra_id) REFERENCES cifras(id) ON DELETE CASCADE,
            FOREIGN KEY (vocalist_id) REFERENCES band_vocalists(id) ON DELETE CASCADE
        )
    ''')
    _migrate_vocalists_schema(c)
    db.commit()

    db.close()


def _table_columns(cursor, table: str) -> list[str]:
    cursor.execute(f'PRAGMA table_info({table})')
    return [row[1] for row in cursor.fetchall()]


def _split_vocalist_names(raw: str) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.replace(';', ',').split(',') if p.strip()]


def _migrate_vocalists_schema(c) -> None:
    """Migra cantor único (bands.*) e transpose por user_id para band_vocalists."""
    cols = _table_columns(c, 'cifra_vocalist_transpose')
    if 'user_id' in cols and 'vocalist_id' not in cols:
        c.execute('ALTER TABLE cifra_vocalist_transpose RENAME TO _legacy_cvt_user')

    c.execute('SELECT COUNT(*) AS n FROM band_vocalists')
    if (c.fetchone()['n'] or 0) == 0:
        c.execute(
            '''SELECT id, vocalist_name, vocalist_user_id FROM bands
               WHERE COALESCE(vocalist_name, '') != '' OR vocalist_user_id IS NOT NULL'''
        )
        for row in c.fetchall():
            uid = row['vocalist_user_id']
            raw = (row['vocalist_name'] or '').strip()
            names = _split_vocalist_names(raw)
            if not names:
                if uid:
                    u = get_user(uid)
                    names = [((u.get('display_name') or '').strip() or u.get('username')) if u else 'Cantor(a)']
                else:
                    continue
            for i, name in enumerate(names):
                vid = str(uuid.uuid4())
                link_uid = uid if i == 0 else None
                c.execute(
                    '''INSERT INTO band_vocalists (id, band_id, name, user_id, sort_order)
                       VALUES (?, ?, ?, ?, ?)''',
                    (vid, row['id'], name, link_uid, i),
                )

    cols = _table_columns(c, 'cifra_vocalist_transpose')
    if 'vocalist_id' not in cols:
        c.execute('''
            CREATE TABLE IF NOT EXISTS cifra_vocalist_transpose (
                cifra_id TEXT NOT NULL,
                vocalist_id TEXT NOT NULL,
                transpose_semitones INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (cifra_id, vocalist_id),
                FOREIGN KEY (cifra_id) REFERENCES cifras(id) ON DELETE CASCADE,
                FOREIGN KEY (vocalist_id) REFERENCES band_vocalists(id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            INSERT OR IGNORE INTO cifra_vocalist_transpose
                (cifra_id, vocalist_id, transpose_semitones)
            SELECT c.id, bv.id, COALESCE(c.transpose_semitones, 0)
            FROM cifras c
            JOIN band_vocalists bv ON bv.band_id = c.band_id
            WHERE bv.sort_order = (
                SELECT MIN(bv2.sort_order) FROM band_vocalists bv2 WHERE bv2.band_id = c.band_id
            )
        ''')
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_legacy_cvt_user'")
        if c.fetchone():
            c.execute('''
                INSERT OR REPLACE INTO cifra_vocalist_transpose
                    (cifra_id, vocalist_id, transpose_semitones)
                SELECT t.cifra_id, bv.id, t.transpose_semitones
                FROM _legacy_cvt_user t
                JOIN cifras c ON c.id = t.cifra_id
                JOIN band_vocalists bv ON bv.band_id = c.band_id AND bv.user_id = t.user_id
            ''')
            c.execute('DROP TABLE IF EXISTS _legacy_cvt_user')


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


def is_superadmin(user_id):
    """Administrador global via .env — sem coluna no banco (ideal para deploy Contabo)."""
    if not user_id:
        return False
    env_users, env_emails = _env_superadmin_identifiers()
    if not env_users and not env_emails:
        return False
    user = get_user(user_id)
    if not user:
        return False
    if user.get('username', '').lower() in env_users:
        return True
    if user.get('email', '').lower() in env_emails:
        return True
    return False


def get_all_users():
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users ORDER BY username')
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_all_bands():
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM bands ORDER BY name')
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_all_cifras():
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT cifras.*, bands.name AS band_name
           FROM cifras
           JOIN bands ON bands.id = cifras.band_id
           ORDER BY bands.name, cifras.titulo'''
    )
    rows = c.fetchall()
    db.close()
    return [dict(r) for r in rows]


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


def can_delete_band(band_id, user_id):
    band = get_band(band_id)
    if not band:
        return False
    if is_superadmin(user_id):
        return True
    return band['owner_id'] == user_id


def can_edit_band_settings(band_id, user_id):
    return can_delete_band(band_id, user_id)


def update_band(band_id, name, description, **_ignored):
    """Atualiza nome e descrição da banda."""
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE bands SET name = ?, description = ? WHERE id = ?', (name, description, band_id))
    db.commit()
    db.close()


def _vocalist_row_dict(row) -> dict:
    d = dict(row)
    if d.get('user_id'):
        u = get_user(d['user_id'])
        if u:
            d['username'] = u.get('username')
            d['user_display'] = (u.get('display_name') or '').strip() or u.get('username')
    return d


def get_band_vocalists(band_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM band_vocalists WHERE band_id = ?
           ORDER BY sort_order, name COLLATE NOCASE''',
        (band_id,),
    )
    rows = [ _vocalist_row_dict(r) for r in c.fetchall() ]
    db.close()
    return rows


def get_band_vocalist(vocalist_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM band_vocalists WHERE id = ?', (vocalist_id,))
    row = c.fetchone()
    db.close()
    return _vocalist_row_dict(row) if row else None


def band_vocalist_belongs_to_band(vocalist_id: str, band_id: str) -> bool:
    v = get_band_vocalist(vocalist_id)
    return bool(v and v.get('band_id') == band_id)


def band_has_vocalist(band_id: str) -> bool:
    return len(get_band_vocalists(band_id)) > 0


def vocalist_entry_display_name(vocalist: dict) -> str:
    if not vocalist:
        return ''
    if vocalist.get('user_display'):
        return vocalist['user_display']
    return (vocalist.get('name') or '').strip()


def vocalists_summary_label(band_id: str) -> str | None:
    vocalists = get_band_vocalists(band_id)
    if not vocalists:
        return None
    return ', '.join(vocalist_entry_display_name(v) for v in vocalists)


def add_band_vocalist(band_id: str, name: str, user_id: str | None = None) -> str:
    name = name.strip()
    if not name:
        raise ValueError('Nome do cantor(a) é obrigatório')
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COALESCE(MAX(sort_order), -1) + 1 AS n FROM band_vocalists WHERE band_id = ?', (band_id,))
    sort_order = c.fetchone()['n']
    vid = str(uuid.uuid4())
    c.execute(
        '''INSERT INTO band_vocalists (id, band_id, name, user_id, sort_order)
           VALUES (?, ?, ?, ?, ?)''',
        (vid, band_id, name, user_id or None, sort_order),
    )
    c.execute(
        '''INSERT OR IGNORE INTO cifra_vocalist_transpose (cifra_id, vocalist_id, transpose_semitones)
           SELECT id, ?, COALESCE(transpose_semitones, 0) FROM cifras WHERE band_id = ?''',
        (vid, band_id),
    )
    db.commit()
    db.close()
    return vid


def add_band_vocalists_from_text(band_id: str, raw_names: str, user_id: str | None = None) -> list[str]:
    """Aceita vários nomes separados por vírgula."""
    ids = []
    names = _split_vocalist_names(raw_names)
    if not names:
        raise ValueError('Informe pelo menos um nome')
    for i, name in enumerate(names):
        link = user_id if i == 0 else None
        ids.append(add_band_vocalist(band_id, name, link))
    return ids


_UNSET = object()


def update_band_vocalist(vocalist_id: str, name: str | None = None, user_id=_UNSET):
    db = get_db()
    c = db.cursor()
    parts, vals = [], []
    if name is not None:
        parts.append('name = ?')
        vals.append(name.strip())
    if user_id is not _UNSET:
        parts.append('user_id = ?')
        vals.append(user_id or None)
    if not parts:
        db.close()
        return
    vals.append(vocalist_id)
    c.execute(f'UPDATE band_vocalists SET {", ".join(parts)} WHERE id = ?', vals)
    db.commit()
    db.close()


def delete_band_vocalist(vocalist_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM cifra_vocalist_transpose WHERE vocalist_id = ?', (vocalist_id,))
    c.execute('DELETE FROM band_vocalists WHERE id = ?', (vocalist_id,))
    db.commit()
    db.close()


def get_cifra_vocalist_transpose(cifra_id: str, vocalist_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT transpose_semitones FROM cifra_vocalist_transpose WHERE cifra_id = ? AND vocalist_id = ?',
        (cifra_id, vocalist_id),
    )
    row = c.fetchone()
    db.close()
    if not row:
        return 0
    try:
        return int(row['transpose_semitones'])
    except (TypeError, ValueError):
        return 0


def get_cifra_transpose_by_vocalists(cifra_id: str, band_id: str) -> dict[str, int]:
    vocalists = get_band_vocalists(band_id)
    return {v['id']: get_cifra_vocalist_transpose(cifra_id, v['id']) for v in vocalists}


def set_cifra_vocalist_transpose(cifra_id: str, vocalist_id: str, semitones: int) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO cifra_vocalist_transpose (cifra_id, vocalist_id, transpose_semitones)
           VALUES (?, ?, ?)
           ON CONFLICT(cifra_id, vocalist_id) DO UPDATE SET
               transpose_semitones = excluded.transpose_semitones''',
        (cifra_id, vocalist_id, int(semitones)),
    )
    c.execute('UPDATE cifras SET updated_at=CURRENT_TIMESTAMP WHERE id=?', (cifra_id,))
    db.commit()
    db.close()


def delete_band(band_id):
    db = get_db()
    c = db.cursor()
    # Remover em cascata: setlist_cifras → setlists → cifras → band_members → band
    c.execute('''DELETE FROM setlist_cifras WHERE setlist_id IN
                 (SELECT id FROM setlists WHERE band_id = ?)''', (band_id,))
    c.execute('DELETE FROM setlists WHERE band_id = ?', (band_id,))
    c.execute(
        '''DELETE FROM cifra_vocalist_transpose WHERE cifra_id IN
           (SELECT id FROM cifras WHERE band_id = ?)''',
        (band_id,),
    )
    c.execute('DELETE FROM cifras WHERE band_id = ?', (band_id,))
    c.execute('DELETE FROM band_vocalists WHERE band_id = ?', (band_id,))
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


def enrich_bands_for_display(bands) -> list[dict]:
    """Anexa members, cifras e owner para cards de listagem/dashboard."""
    result = []
    for band in bands:
        b = dict(band)
        b['members'] = get_band_members(b['id'])
        b['cifras'] = get_band_cifras(b['id'])
        owner = get_user(b.get('owner_id'))
        b['owner'] = owner or {}
        result.append(b)
    return result


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
    if is_superadmin(user_id):
        return True
    db = get_db()
    c = db.cursor()
    c.execute('SELECT 1 FROM band_members WHERE band_id = ? AND user_id = ?', (band_id, user_id))
    result = c.fetchone() is not None
    db.close()
    return result


def is_band_admin(band_id, user_id):
    if is_superadmin(user_id):
        return True
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
                 cifra_json=None, grade_json=None, leadsheet_json=None,
                 bpm=None, duracao_seg=None):
    db = get_db()
    c = db.cursor()
    cifra_id = str(uuid.uuid4())
    c.execute(
        '''INSERT INTO cifras
           (id, titulo, artista, tom_original, conteudo, band_id,
            cifra_json, grade_json, leadsheet_json, bpm, duracao_seg)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (cifra_id, titulo, artista, tom_original, conteudo or '', band_id,
         cifra_json, grade_json, leadsheet_json, bpm, duracao_seg)
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
                 cifra_json=None, grade_json=None, leadsheet_json=None,
                 bpm=None, duracao_seg=None):
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE cifras SET titulo=?, artista=?, tom_original=?, conteudo=?,
           cifra_json=?, grade_json=?, leadsheet_json=?, bpm=?, duracao_seg=?,
           updated_at=CURRENT_TIMESTAMP WHERE id=?''',
        (titulo, artista, tom_original, conteudo or '',
         cifra_json, grade_json, leadsheet_json, bpm, duracao_seg, cifra_id)
    )
    db.commit()
    db.close()


def delete_cifra(cifra_id):
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM cifra_vocalist_transpose WHERE cifra_id = ?', (cifra_id,))
    c.execute('DELETE FROM setlist_cifras WHERE cifra_id = ?', (cifra_id,))
    c.execute('DELETE FROM cifras WHERE id = ?', (cifra_id,))
    db.commit()
    db.close()


def set_cifra_transpose_semitones(cifra_id, semitones: int, vocalist_id: str | None = None) -> None:
    """Tom de performance por cantor(a); sem cantores, grava na cifra."""
    cifra = get_cifra(cifra_id)
    if not cifra:
        return
    semi = int(semitones)
    band_id = cifra['band_id']
    vocalists = get_band_vocalists(band_id)
    if vocalists:
        vid = vocalist_id or vocalists[0]['id']
        if vid and band_vocalist_belongs_to_band(vid, band_id):
            set_cifra_vocalist_transpose(cifra_id, vid, semi)
            return
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE cifras SET transpose_semitones=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
        (semi, cifra_id),
    )
    db.commit()
    db.close()
