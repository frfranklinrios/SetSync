import os
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from database import (
    IS_POSTGRES,
    IntegrityError,
    SQLITE_PATH,
    add_column_if_missing,
    get_db,
    table_columns,
    table_exists,
)

DB_PATH = SQLITE_PATH


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


def _init_postgres_schema(c) -> None:
    """Schema completo para PostgreSQL (instalação nova)."""
    statements = [
        '''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id TEXT,
            is_superadmin INTEGER NOT NULL DEFAULT 0,
            phone TEXT,
            whatsapp_notify INTEGER NOT NULL DEFAULT 1,
            email_notify INTEGER NOT NULL DEFAULT 1,
            last_login_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS bands (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            vocalist_user_id TEXT,
            vocalist_name TEXT,
            logo_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS band_members (
            band_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (band_id, user_id),
            FOREIGN KEY (band_id) REFERENCES bands(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS cifras (
            id TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            artista TEXT NOT NULL,
            tom_original TEXT DEFAULT 'C',
            conteudo TEXT NOT NULL DEFAULT '',
            band_id TEXT NOT NULL,
            cifra_json TEXT,
            grade_json TEXT,
            leadsheet_json TEXT,
            bpm REAL,
            duracao_seg INTEGER,
            transpose_semitones INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (band_id) REFERENCES bands(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS setlists (
            id SERIAL PRIMARY KEY,
            band_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            vocalist_id TEXT,
            public_share_token TEXT,
            public_share_enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (band_id) REFERENCES bands(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS setlist_cifras (
            setlist_id INTEGER NOT NULL,
            cifra_id TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            vocalist_id TEXT,
            PRIMARY KEY (setlist_id, cifra_id),
            FOREIGN KEY (setlist_id) REFERENCES setlists(id) ON DELETE CASCADE,
            FOREIGN KEY (cifra_id) REFERENCES cifras(id) ON DELETE CASCADE
        )''',
        '''CREATE TABLE IF NOT EXISTS band_events (
            id TEXT PRIMARY KEY,
            band_id TEXT NOT NULL,
            setlist_id INTEGER,
            event_type TEXT NOT NULL DEFAULT 'ensaio',
            title TEXT NOT NULL,
            starts_at TIMESTAMP NOT NULL,
            ends_at TIMESTAMP,
            location TEXT,
            notes TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (setlist_id) REFERENCES setlists(id) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS band_vocalists (
            id TEXT PRIMARY KEY,
            band_id TEXT NOT NULL,
            name TEXT NOT NULL,
            user_id TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS cifra_vocalist_transpose (
            cifra_id TEXT NOT NULL,
            vocalist_id TEXT NOT NULL,
            transpose_semitones INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (cifra_id, vocalist_id),
            FOREIGN KEY (cifra_id) REFERENCES cifras(id) ON DELETE CASCADE,
            FOREIGN KEY (vocalist_id) REFERENCES band_vocalists(id) ON DELETE CASCADE
        )''',
        '''CREATE TABLE IF NOT EXISTS assinaturas (
            id TEXT PRIMARY KEY,
            banda_id TEXT NOT NULL UNIQUE,
            plano TEXT NOT NULL DEFAULT 'gratis',
            status TEXT NOT NULL DEFAULT 'ativa',
            mp_subscription_id TEXT,
            mp_preapproval_id TEXT,
            data_inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            data_proxima_cobranca TIMESTAMP,
            data_cancelamento TIMESTAMP,
            trial_inicio TIMESTAMP,
            trial_fim TIMESTAMP,
            trial_usado INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (banda_id) REFERENCES bands(id) ON DELETE CASCADE
        )''',
        '''CREATE TABLE IF NOT EXISTS vouchers (
            id TEXT PRIMARY KEY,
            codigo TEXT NOT NULL UNIQUE,
            plano TEXT NOT NULL,
            dias INTEGER NOT NULL,
            criado_por_id TEXT,
            max_usos INTEGER,
            usos_atual INTEGER NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            eh_indicacao INTEGER NOT NULL DEFAULT 0,
            eh_vitalicio INTEGER NOT NULL DEFAULT 0,
            data_expiracao TIMESTAMP,
            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (criado_por_id) REFERENCES users(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS voucher_usos (
            id TEXT PRIMARY KEY,
            voucher_id TEXT NOT NULL,
            banda_id TEXT NOT NULL,
            usado_em TIMESTAMP NOT NULL,
            expira_em TIMESTAMP NOT NULL,
            aviso_3d_enviado INTEGER NOT NULL DEFAULT 0,
            UNIQUE (voucher_id, banda_id),
            FOREIGN KEY (voucher_id) REFERENCES vouchers(id),
            FOREIGN KEY (banda_id) REFERENCES bands(id)
        )''',
        '''CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            band_id TEXT,
            actor_user_id TEXT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT,
            url_path TEXT,
            payload_json TEXT,
            read_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
        )''',
        '''CREATE INDEX IF NOT EXISTS idx_notifications_user_created
           ON notifications(user_id, created_at DESC)''',
        '''CREATE TABLE IF NOT EXISTS testimonials (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            cidade TEXT,
            descricao TEXT,
            texto TEXT NOT NULL,
            foto_url TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            ordem INTEGER NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS blog_posts (
            id SERIAL PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            titulo TEXT NOT NULL,
            resumo TEXT,
            conteudo TEXT,
            autor TEXT,
            publicado INTEGER NOT NULL DEFAULT 0,
            publicado_em TIMESTAMP,
            atualizado_em TIMESTAMP,
            meta_title TEXT,
            meta_description TEXT,
            imagem_capa TEXT,
            tags TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS onboarding_emails (
            id SERIAL PRIMARY KEY,
            usuario_id TEXT NOT NULL,
            email_numero INTEGER NOT NULL,
            enviado_em TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pendente',
            UNIQUE (usuario_id, email_numero),
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
        )''',
        '''CREATE TABLE IF NOT EXISTS retention_emails (
            id SERIAL PRIMARY KEY,
            usuario_id TEXT NOT NULL,
            campaign TEXT NOT NULL,
            enviado_em TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pendente',
            UNIQUE (usuario_id, campaign),
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
        )''',
    ]
    for sql in statements:
        c.execute(sql)


def init_db():
    if not IS_POSTGRES:
        os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    db = get_db()
    c = db.cursor()
    if IS_POSTGRES:
        _init_postgres_schema(c)
        db.commit()
        add_column_if_missing(c, 'bands', 'updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        add_column_if_missing(c, 'users', 'is_superadmin', 'INTEGER NOT NULL DEFAULT 0')
        add_column_if_missing(c, 'users', 'phone', 'TEXT')
        add_column_if_missing(c, 'users', 'whatsapp_notify', 'INTEGER NOT NULL DEFAULT 1')
        add_column_if_missing(c, 'users', 'email_notify', 'INTEGER NOT NULL DEFAULT 1')
        add_column_if_missing(c, 'users', 'last_login_at', 'TIMESTAMP')
        add_column_if_missing(c, 'assinaturas', 'trial_inicio', 'TIMESTAMP')
        add_column_if_missing(c, 'assinaturas', 'trial_fim', 'TIMESTAMP')
        add_column_if_missing(c, 'assinaturas', 'trial_usado', 'INTEGER NOT NULL DEFAULT 0')
        _migrate_assinaturas_schema(c)
        _migrate_notifications_schema(c)
        _migrate_content_schema(c)
        _migrate_agenda_schema(c)
        _ensure_perf_indexes(c)
        db.commit()
        db.close()
        return

    db.executescript('''
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

    # Migration: colunas novas em BDs SQLite já existentes
    add_column_if_missing(c, 'users', 'display_name', 'TEXT')
    for col, typedef in [
        ('cifra_json', 'TEXT'),
        ('grade_json', 'TEXT'),
        ('bpm', 'REAL'),
        ('duracao_seg', 'INTEGER'),
    ]:
        add_column_if_missing(c, 'cifras', col, typedef)
    add_column_if_missing(c, 'cifras', 'leadsheet_json', 'TEXT')
    add_column_if_missing(c, 'cifras', 'transpose_semitones', 'INTEGER DEFAULT 0')
    add_column_if_missing(c, 'bands', 'vocalist_user_id', 'TEXT')
    add_column_if_missing(c, 'bands', 'vocalist_name', 'TEXT')
    add_column_if_missing(c, 'bands', 'logo_filename', 'TEXT')
    add_column_if_missing(c, 'setlists', 'vocalist_id', 'TEXT')
    add_column_if_missing(c, 'setlists', 'public_share_token', 'TEXT')
    add_column_if_missing(c, 'setlists', 'public_share_enabled', 'INTEGER DEFAULT 0')
    add_column_if_missing(c, 'setlist_cifras', 'vocalist_id', 'TEXT')

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
    _migrate_assinaturas_schema(c)
    _migrate_vouchers_schema(c)
    add_column_if_missing(c, 'vouchers', 'eh_vitalicio', 'INTEGER NOT NULL DEFAULT 0')
    _migrate_notifications_schema(c)
    add_column_if_missing(c, 'users', 'is_superadmin', 'INTEGER NOT NULL DEFAULT 0')
    add_column_if_missing(c, 'users', 'phone', 'TEXT')
    add_column_if_missing(c, 'users', 'whatsapp_notify', 'INTEGER NOT NULL DEFAULT 1')
    add_column_if_missing(c, 'users', 'email_notify', 'INTEGER NOT NULL DEFAULT 1')
    add_column_if_missing(c, 'users', 'last_login_at', 'TIMESTAMP')
    add_column_if_missing(c, 'assinaturas', 'trial_inicio', 'TIMESTAMP')
    add_column_if_missing(c, 'assinaturas', 'trial_fim', 'TIMESTAMP')
    add_column_if_missing(c, 'assinaturas', 'trial_usado', 'INTEGER NOT NULL DEFAULT 0')
    _migrate_content_schema(c)
    _migrate_agenda_schema(c)
    _ensure_perf_indexes(c)
    db.commit()

    db.close()


def _migrate_agenda_schema(c) -> None:
    c.execute('''
        CREATE TABLE IF NOT EXISTS band_events (
            id TEXT PRIMARY KEY,
            band_id TEXT NOT NULL,
            setlist_id INTEGER,
            event_type TEXT NOT NULL DEFAULT 'ensaio',
            title TEXT NOT NULL,
            starts_at TIMESTAMP NOT NULL,
            ends_at TIMESTAMP,
            location TEXT,
            notes TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (setlist_id) REFERENCES setlists(id) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS event_reminders (
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES band_events(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS band_event_assignments (
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role_label TEXT,
            assigned_by TEXT,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES band_events(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_by) REFERENCES users(id)
        )
    ''')


def _migrate_content_schema(c) -> None:
    """Tabelas de conteúdo (depoimentos, blog, onboarding) e seeds iniciais."""
    if not IS_POSTGRES:
        c.execute('''
            CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cidade TEXT,
                descricao TEXT,
                texto TEXT NOT NULL,
                foto_url TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                ordem INTEGER NOT NULL DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                titulo TEXT NOT NULL,
                resumo TEXT,
                conteudo TEXT,
                autor TEXT,
                publicado INTEGER NOT NULL DEFAULT 0,
                publicado_em TIMESTAMP,
                atualizado_em TIMESTAMP,
                meta_title TEXT,
                meta_description TEXT,
                imagem_capa TEXT,
                tags TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS onboarding_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT NOT NULL,
                email_numero INTEGER NOT NULL,
                enviado_em TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'pendente',
                UNIQUE (usuario_id, email_numero),
                FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS retention_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT NOT NULL,
                campaign TEXT NOT NULL,
                enviado_em TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'pendente',
                UNIQUE (usuario_id, campaign),
                FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
    if IS_POSTGRES:
        c.execute('''
            CREATE TABLE IF NOT EXISTS retention_emails (
                id SERIAL PRIMARY KEY,
                usuario_id TEXT NOT NULL,
                campaign TEXT NOT NULL,
                enviado_em TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'pendente',
                UNIQUE (usuario_id, campaign),
                FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
    _sync_superadmins_from_env(c)
    from content_seed import seed_testimonials, seed_blog_posts
    seed_testimonials(c)
    seed_blog_posts(c)


def _split_vocalist_names(raw: str) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.replace(';', ',').split(',') if p.strip()]


def _migrate_vocalists_schema(c) -> None:
    """Migra cantor único (bands.*) e transpose por user_id para band_vocalists."""
    cols = table_columns(c, 'cifra_vocalist_transpose')
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
                    names = [((u.get('display_name') or '').strip() or u.get('username')) if u else 'Cantora/cantor']
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

    cols = table_columns(c, 'cifra_vocalist_transpose')
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
        if table_exists(c, '_legacy_cvt_user'):
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


def update_user_profile(
    user_id: str,
    *,
    display_name: str | None = None,
    phone: str | None = None,
    whatsapp_notify: bool | None = None,
    email_notify: bool | None = None,
) -> None:
    from whatsapp_service import normalize_whatsapp_phone

    db = get_db()
    c = db.cursor()
    if display_name is not None:
        c.execute('UPDATE users SET display_name = ? WHERE id = ?', (display_name, user_id))
    if phone is not None:
        normalized = normalize_whatsapp_phone(phone) if phone.strip() else None
        c.execute('UPDATE users SET phone = ? WHERE id = ?', (normalized, user_id))
    if whatsapp_notify is not None:
        c.execute(
            'UPDATE users SET whatsapp_notify = ? WHERE id = ?',
            (1 if whatsapp_notify else 0, user_id),
        )
    if email_notify is not None:
        c.execute(
            'UPDATE users SET email_notify = ? WHERE id = ?',
            (1 if email_notify else 0, user_id),
        )
    db.commit()
    db.close()


def touch_user_last_login(user_id: str) -> None:
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE users SET last_login_at = ? WHERE id = ?', (now, user_id))
    db.commit()
    db.close()


def user_wants_whatsapp_notifications(user: dict | None) -> bool:
    if not user:
        return False
    return int(user.get('whatsapp_notify') or 0) == 1


def user_has_phone(user: dict | None) -> bool:
    if not user:
        return False
    return bool((user.get('phone') or '').strip())


def user_wants_email_notifications(user: dict | None) -> bool:
    if not user:
        return False
    if user.get('email_notify') is None:
        return True
    return int(user.get('email_notify') or 0) == 1


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
    except IntegrityError:
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
    except IntegrityError:
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


def user_display_name(user: dict | None) -> str:
    """Nome amigável: display_name informado pelo usuário, senão username."""
    if not user:
        return 'Alguém'
    return (user.get('display_name') or '').strip() or (user.get('username') or 'Alguém')


def get_user_by_username(username):
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_user_by_login(identifier: str) -> dict | None:
    """
    Busca usuário pelo username ou pelo e-mail (mesmo campo do formulário de login).
    E-mail é comparado sem diferenciar maiúsculas/minúsculas.
    """
    ident = (identifier or '').strip()
    if not ident:
        return None
    if '@' in ident:
        user = get_user_by_email(ident)
        if user:
            return user
    user = get_user_by_username(ident)
    if user:
        return user
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE LOWER(username) = LOWER(?)', (ident,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def get_user_by_email(email):
    email = (email or '').strip()
    if not email:
        return None
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE LOWER(email) = LOWER(?)', (email,))
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
    """Administrador global via coluna no banco ou variáveis SETSYNC_SUPERADMIN_* no .env."""
    if not user_id:
        return False
    user = get_user(user_id)
    if not user:
        return False
    if user.get('is_superadmin'):
        return True
    env_users, env_emails = _env_superadmin_identifiers()
    if not env_users and not env_emails:
        return False
    if user.get('username', '').lower() in env_users:
        return True
    if user.get('email', '').lower() in env_emails:
        return True
    return False


def _sync_superadmins_from_env(c) -> None:
    """Marca is_superadmin=1 para contas listadas no .env (idempotente)."""
    env_users, env_emails = _env_superadmin_identifiers()
    if not env_users and not env_emails:
        return
    c.execute('SELECT id, username, email FROM users')
    for row in c.fetchall():
        uname = (row['username'] or '').lower()
        email = (row['email'] or '').lower()
        if uname in env_users or email in env_emails:
            c.execute('UPDATE users SET is_superadmin = 1 WHERE id = ?', (row['id'],))


def set_user_superadmin(user_id: str, enabled: bool) -> bool:
    """Promove ou revoga admin global persistente no banco."""
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE users SET is_superadmin = ? WHERE id = ?',
        (1 if enabled else 0, user_id),
    )
    ok = c.rowcount > 0
    db.commit()
    db.close()
    return ok


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


# ── Assinaturas / monetização ───────────────────────────────────────────────

def _migrate_assinaturas_schema(c) -> None:
    """Cria tabela de assinaturas e preenche bandas existentes com plano grátis."""
    c.execute('''
        CREATE TABLE IF NOT EXISTS assinaturas (
            id TEXT PRIMARY KEY,
            banda_id TEXT NOT NULL UNIQUE,
            plano TEXT NOT NULL DEFAULT 'gratis',
            status TEXT NOT NULL DEFAULT 'ativa',
            mp_subscription_id TEXT,
            mp_preapproval_id TEXT,
            data_inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            data_proxima_cobranca TIMESTAMP,
            data_cancelamento TIMESTAMP,
            FOREIGN KEY (banda_id) REFERENCES bands(id) ON DELETE CASCADE
        )
    ''')
    c.execute('SELECT id FROM bands')
    for row in c.fetchall():
        c.execute('SELECT 1 FROM assinaturas WHERE banda_id = ?', (row['id'],))
        if not c.fetchone():
            create_assinatura_gratis(row['id'], cursor=c, commit=False)
    c.connection.commit()


def create_assinatura_gratis(banda_id: str, *, cursor=None, commit: bool = True) -> dict:
    """Cria assinatura grátis ativa para uma banda."""
    assinatura_id = str(uuid.uuid4())
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    row = {
        'id': assinatura_id,
        'banda_id': banda_id,
        'plano': 'gratis',
        'status': 'ativa',
        'mp_subscription_id': None,
        'mp_preapproval_id': None,
        'data_inicio': now,
        'data_proxima_cobranca': None,
        'data_cancelamento': None,
    }
    if cursor is not None:
        c = cursor
        c.execute(
            '''INSERT INTO assinaturas
               (id, banda_id, plano, status, data_inicio)
               VALUES (?, ?, ?, ?, ?)''',
            (assinatura_id, banda_id, 'gratis', 'ativa', now),
        )
        if commit:
            c.connection.commit()
        return row

    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            '''INSERT INTO assinaturas
               (id, banda_id, plano, status, data_inicio)
               VALUES (?, ?, ?, ?, ?)''',
            (assinatura_id, banda_id, 'gratis', 'ativa', now),
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = get_assinatura(banda_id)
        db.close()
        return existing if existing else row
    finally:
        if cursor is None:
            db.close()
    return row


def get_assinatura(banda_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM assinaturas WHERE banda_id = ?', (banda_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def owner_has_worship_ativa(owner_id: str) -> bool:
    """True se o usuário possui alguma banda com plano Worship ativo."""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT 1 FROM assinaturas a
           JOIN bands b ON b.id = a.banda_id
           WHERE b.owner_id = ? AND a.plano = 'worship' AND a.status = 'ativa'
           LIMIT 1''',
        (owner_id,),
    )
    found = c.fetchone() is not None
    db.close()
    return found


def count_band_cifras(band_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM cifras WHERE band_id = ?', (band_id,))
    n = c.fetchone()['n']
    db.close()
    return int(n or 0)


def count_band_members(band_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM band_members WHERE band_id = ?', (band_id,))
    n = c.fetchone()['n']
    db.close()
    return int(n or 0)


def count_band_setlists(band_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM setlists WHERE band_id = ?', (band_id,))
    n = c.fetchone()['n']
    db.close()
    return int(n or 0)


def count_owned_bands(user_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM bands WHERE owner_id = ?', (user_id,))
    n = c.fetchone()['n']
    db.close()
    return int(n or 0)


def update_assinatura(banda_id: str, **fields) -> dict | None:
    """Atualiza campos da assinatura da banda."""
    allowed = {
        'plano', 'status', 'mp_subscription_id', 'mp_preapproval_id',
        'data_inicio', 'data_proxima_cobranca', 'data_cancelamento',
    }
    parts, vals = [], []
    for key, value in fields.items():
        if key in allowed:
            parts.append(f'{key} = ?')
            vals.append(value)
    if not parts:
        return get_assinatura(banda_id)
    vals.append(banda_id)
    db = get_db()
    c = db.cursor()
    c.execute(f'UPDATE assinaturas SET {", ".join(parts)} WHERE banda_id = ?', vals)
    db.commit()
    db.close()
    return get_assinatura(banda_id)


def get_assinatura_by_mp_id(mp_subscription_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM assinaturas WHERE mp_subscription_id = ? OR mp_preapproval_id = ?',
        (mp_subscription_id, mp_subscription_id),
    )
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def _migrate_vouchers_schema(c) -> None:
    c.execute('''
        CREATE TABLE IF NOT EXISTS vouchers (
            id TEXT PRIMARY KEY,
            codigo TEXT NOT NULL UNIQUE,
            plano TEXT NOT NULL,
            dias INTEGER NOT NULL,
            criado_por_id TEXT,
            max_usos INTEGER,
            usos_atual INTEGER NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            eh_indicacao INTEGER NOT NULL DEFAULT 0,
            eh_vitalicio INTEGER NOT NULL DEFAULT 0,
            data_expiracao TIMESTAMP,
            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (criado_por_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS voucher_usos (
            id TEXT PRIMARY KEY,
            voucher_id TEXT NOT NULL,
            banda_id TEXT NOT NULL,
            usado_em TIMESTAMP NOT NULL,
            expira_em TIMESTAMP NOT NULL,
            aviso_3d_enviado INTEGER NOT NULL DEFAULT 0,
            UNIQUE (voucher_id, banda_id),
            FOREIGN KEY (voucher_id) REFERENCES vouchers(id),
            FOREIGN KEY (banda_id) REFERENCES bands(id)
        )
    ''')


def create_voucher(
    codigo: str,
    plano: str,
    dias: int,
    criado_por_id: str | None = None,
    max_usos: int | None = None,
    data_expiracao: str | None = None,
    eh_indicacao: bool = False,
    eh_vitalicio: bool = False,
) -> dict:
    vid = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO vouchers
           (id, codigo, plano, dias, criado_por_id, max_usos, eh_indicacao, eh_vitalicio, data_expiracao)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            vid, codigo.upper(), plano, dias, criado_por_id, max_usos,
            int(eh_indicacao), int(eh_vitalicio), data_expiracao,
        ),
    )
    db.commit()
    db.close()
    return get_voucher_by_codigo(codigo) or {'id': vid, 'codigo': codigo}


def get_voucher_by_codigo(codigo: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM vouchers WHERE codigo = ?', (codigo.upper(),))
    row = c.fetchone()
    db.close()
    if not row:
        return None
    d = dict(row)
    d['ativo'] = bool(d.get('ativo'))
    d['eh_indicacao'] = bool(d.get('eh_indicacao'))
    d['eh_vitalicio'] = bool(d.get('eh_vitalicio'))
    return d


def list_vouchers() -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM vouchers ORDER BY criado_em DESC')
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    for d in rows:
        d['ativo'] = bool(d.get('ativo'))
        d['eh_indicacao'] = bool(d.get('eh_indicacao'))
        d['eh_vitalicio'] = bool(d.get('eh_vitalicio'))
    return rows


def set_voucher_ativo(codigo: str, ativo: bool) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE vouchers SET ativo = ? WHERE codigo = ?', (int(ativo), codigo.upper()))
    db.commit()
    ok = c.rowcount > 0
    db.close()
    return ok


def increment_voucher_usos(voucher_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE vouchers SET usos_atual = usos_atual + 1 WHERE id = ?', (voucher_id,))
    db.commit()
    db.close()


def get_voucher_uso_banda(voucher_id: str, banda_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM voucher_usos WHERE voucher_id = ? AND banda_id = ?',
        (voucher_id, banda_id),
    )
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def insert_voucher_uso(voucher_id: str, banda_id: str, usado_em, expira_em) -> str:
    uso_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO voucher_usos (id, voucher_id, banda_id, usado_em, expira_em)
           VALUES (?, ?, ?, ?, ?)''',
        (
            uso_id,
            voucher_id,
            banda_id,
            usado_em.strftime('%Y-%m-%d %H:%M:%S'),
            expira_em.strftime('%Y-%m-%d %H:%M:%S'),
        ),
    )
    db.commit()
    db.close()
    return uso_id


def list_voucher_usos(voucher_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT vu.*, b.name AS banda_nome
           FROM voucher_usos vu
           JOIN bands b ON b.id = vu.banda_id
           WHERE vu.voucher_id = ?
           ORDER BY vu.usado_em DESC''',
        (voucher_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def count_vouchers_indicacao_ativos(criado_por_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT COUNT(*) AS n FROM vouchers
           WHERE criado_por_id = ? AND eh_indicacao = 1 AND ativo = 1
           AND (max_usos IS NULL OR usos_atual < max_usos)''',
        (criado_por_id,),
    )
    n = c.fetchone()['n']
    db.close()
    return int(n or 0)


def list_voucher_usos_vencendo(antes_de: str) -> list[dict]:
    """Usos com expira_em <= antes_de e assinatura ainda em voucher."""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT vu.*, v.plano, a.status AS assinatura_status,
                  b.name AS banda_nome, b.owner_id,
                  u.email AS owner_email
           FROM voucher_usos vu
           JOIN vouchers v ON v.id = vu.voucher_id
           JOIN assinaturas a ON a.banda_id = vu.banda_id
           JOIN bands b ON b.id = vu.banda_id
           JOIN users u ON u.id = b.owner_id
           WHERE vu.expira_em <= ? AND a.status = 'voucher'
           AND COALESCE(v.eh_vitalicio, 0) = 0''',
        (antes_de,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_voucher_usos_aviso(ate: str) -> list[dict]:
    """Usos que expiram em até 3 dias e ainda não receberam aviso."""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT vu.*, v.plano, b.name AS banda_nome, u.email AS owner_email
           FROM voucher_usos vu
           JOIN vouchers v ON v.id = vu.voucher_id
           JOIN assinaturas a ON a.banda_id = vu.banda_id
           JOIN bands b ON b.id = vu.banda_id
           JOIN users u ON u.id = b.owner_id
           WHERE a.status = 'voucher' AND vu.aviso_3d_enviado = 0
           AND vu.expira_em <= ? AND vu.expira_em > datetime('now')
           AND COALESCE(v.eh_vitalicio, 0) = 0''',
        (ate,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def marcar_aviso_voucher_enviado(uso_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE voucher_usos SET aviso_3d_enviado = 1 WHERE id = ?', (uso_id,))
    db.commit()
    db.close()


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
    create_assinatura_gratis(band_id)
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


def set_band_logo_filename(band_id: str, filename: str | None) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE bands SET logo_filename = ? WHERE id = ?', (filename, band_id))
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
           ORDER BY sort_order, LOWER(name)''',
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
        raise ValueError('Nome de cantora/cantor é obrigatório')
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
    try:
        from band_logos import delete_band_logo_files
        delete_band_logo_files(band_id)
    except Exception:
        pass
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
    c.execute('DELETE FROM voucher_usos WHERE banda_id = ?', (band_id,))
    c.execute('DELETE FROM assinaturas WHERE banda_id = ?', (band_id,))
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


def _in_placeholders(ids: list) -> tuple[str, tuple]:
    if not ids:
        return '', ()
    return ','.join('?' * len(ids)), tuple(ids)


def _ensure_perf_indexes(c) -> None:
    """Índices em FKs usadas em quase toda listagem."""
    for sql in (
        'CREATE INDEX IF NOT EXISTS idx_band_members_band ON band_members(band_id)',
        'CREATE INDEX IF NOT EXISTS idx_band_members_user ON band_members(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_cifras_band ON cifras(band_id)',
        'CREATE INDEX IF NOT EXISTS idx_setlists_band ON setlists(band_id)',
        'CREATE INDEX IF NOT EXISTS idx_band_events_band_starts ON band_events(band_id, starts_at)',
        'CREATE INDEX IF NOT EXISTS idx_band_event_assignments_event ON band_event_assignments(event_id)',
        'CREATE INDEX IF NOT EXISTS idx_setlist_cifras_setlist ON setlist_cifras(setlist_id)',
        'CREATE INDEX IF NOT EXISTS idx_assinaturas_banda ON assinaturas(banda_id)',
    ):
        c.execute(sql)


def _members_by_band_ids(band_ids: list[str]) -> dict[str, list[dict]]:
    if not band_ids:
        return {}
    ph, params = _in_placeholders(band_ids)
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT users.*, band_members.role, band_members.band_id AS band_id
            FROM users
            JOIN band_members ON users.id = band_members.user_id
            WHERE band_members.band_id IN ({ph})''',
        params,
    )
    rows = c.fetchall()
    db.close()
    out: dict[str, list[dict]] = {bid: [] for bid in band_ids}
    for row in rows:
        out[row['band_id']].append(dict(row))
    return out


def _cifra_summaries_by_band_ids(band_ids: list[str]) -> dict[str, list[dict]]:
    """Metadados leves das cifras (sem conteudo/json) para cards do dashboard."""
    if not band_ids:
        return {}
    ph, params = _in_placeholders(band_ids)
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT id, band_id, titulo, artista, tom_original, created_at, updated_at
            FROM cifras WHERE band_id IN ({ph}) ORDER BY titulo''',
        params,
    )
    rows = c.fetchall()
    db.close()
    out: dict[str, list[dict]] = {bid: [] for bid in band_ids}
    for row in rows:
        out[row['band_id']].append(dict(row))
    return out


def _users_by_ids(user_ids: list[str]) -> dict[str, dict]:
    if not user_ids:
        return {}
    ph, params = _in_placeholders(user_ids)
    db = get_db()
    c = db.cursor()
    c.execute(f'SELECT * FROM users WHERE id IN ({ph})', params)
    rows = c.fetchall()
    db.close()
    return {row['id']: dict(row) for row in rows}


def enrich_bands_for_display(bands) -> list[dict]:
    """Anexa members, cifras, owner e flag de logo para cards de listagem/dashboard."""
    from band_logos import band_has_logo

    if not bands:
        return []

    band_ids = [b['id'] for b in bands]
    owner_ids = list({b.get('owner_id') for b in bands if b.get('owner_id')})
    members_map = _members_by_band_ids(band_ids)
    cifras_map = _cifra_summaries_by_band_ids(band_ids)
    owners_map = _users_by_ids(owner_ids)

    result = []
    for band in bands:
        b = dict(band)
        bid = b['id']
        b['members'] = members_map.get(bid, [])
        b['cifras'] = cifras_map.get(bid, [])
        b['owner'] = owners_map.get(b.get('owner_id'), {})
        b['has_logo'] = band_has_logo(b)
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
    except IntegrityError:
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
    from util import normalize_transpose_semitones

    cifra = get_cifra(cifra_id)
    if not cifra:
        return
    semi = normalize_transpose_semitones(semitones)
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


def _migrate_notifications_schema(c) -> None:
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            band_id TEXT,
            actor_user_id TEXT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT,
            url_path TEXT,
            payload_json TEXT,
            read_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
            FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_user_created
        ON notifications(user_id, created_at DESC)
    ''')


def create_notification(
    user_id: str,
    *,
    band_id: str | None,
    actor_user_id: str | None,
    type: str,
    title: str,
    body: str = '',
    url_path: str | None = None,
    payload: dict | None = None,
) -> str:
    import json
    if url_path and (not url_path.startswith('/') or url_path.startswith('//')):
        url_path = None
    nid = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO notifications
           (id, user_id, band_id, actor_user_id, type, title, body, url_path, payload_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            nid,
            user_id,
            band_id,
            actor_user_id,
            type,
            title,
            body or '',
            url_path,
            json.dumps(payload, ensure_ascii=False) if payload else None,
        ),
    )
    db.commit()
    db.close()
    try:
        from whatsapp_service import dispatch_notification_whatsapp
        dispatch_notification_whatsapp(
            user_id,
            title=title,
            body=body or '',
            url_path=url_path,
        )
    except Exception:
        import logging
        logging.getLogger('setsync.whatsapp').exception(
            'Falha ao enviar notificação WhatsApp para %s', user_id,
        )
    try:
        from notification_email_service import dispatch_notification_email
        dispatch_notification_email(
            user_id,
            title=title,
            body=body or '',
            url_path=url_path,
        )
    except Exception:
        import logging
        logging.getLogger('setsync.email_notify').exception(
            'Falha ao enviar notificação por e-mail para %s', user_id,
        )
    return nid


def create_notifications_for_users(
    user_ids,
    *,
    band_id: str | None,
    actor_user_id: str | None,
    type: str,
    title: str,
    body: str = '',
    url_path: str | None = None,
    payload: dict | None = None,
) -> int:
    seen = set()
    count = 0
    for uid in user_ids or []:
        if not uid or uid in seen:
            continue
        seen.add(uid)
        create_notification(
            uid,
            band_id=band_id,
            actor_user_id=actor_user_id,
            type=type,
            title=title,
            body=body,
            url_path=url_path,
            payload=payload,
        )
        count += 1
    return count


def list_notifications(user_id: str, *, limit: int = 30, unread_only: bool = False) -> list[dict]:
    import json
    db = get_db()
    c = db.cursor()
    sql = '''
        SELECT n.*, b.name AS band_name,
               u.display_name AS actor_display_name, u.username AS actor_username
        FROM notifications n
        LEFT JOIN bands b ON b.id = n.band_id
        LEFT JOIN users u ON u.id = n.actor_user_id
        WHERE n.user_id = ?
    '''
    params: list = [user_id]
    if unread_only:
        sql += ' AND n.read_at IS NULL'
    sql += ' ORDER BY n.created_at DESC LIMIT ?'
    params.append(int(limit))
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    for row in rows:
        row['actor_name'] = (
            (row.get('actor_display_name') or '').strip()
            or row.get('actor_username')
            or ''
        )
        if row.get('payload_json'):
            try:
                row['payload'] = json.loads(row['payload_json'])
            except (TypeError, ValueError):
                row['payload'] = {}
        else:
            row['payload'] = {}
    return rows


def count_unread_notifications(user_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT COUNT(*) AS n FROM notifications WHERE user_id = ? AND read_at IS NULL',
        (user_id,),
    )
    n = c.fetchone()['n'] or 0
    db.close()
    return int(n)


def mark_notification_read(notification_id: str, user_id: str) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE notifications SET read_at = CURRENT_TIMESTAMP
           WHERE id = ? AND user_id = ? AND read_at IS NULL''',
        (notification_id, user_id),
    )
    ok = c.rowcount > 0
    db.commit()
    db.close()
    return ok


def mark_all_notifications_read(user_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE notifications SET read_at = CURRENT_TIMESTAMP
           WHERE user_id = ? AND read_at IS NULL''',
        (user_id,),
    )
    n = c.rowcount
    db.commit()
    db.close()
    return n


# ── Estatísticas públicas ───────────────────────────────────────────────────

def count_bands() -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM bands')
    n = int(c.fetchone()['n'] or 0)
    db.close()
    return n


def count_cifras() -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM cifras')
    n = int(c.fetchone()['n'] or 0)
    db.close()
    return n


def count_setlists() -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM setlists')
    n = int(c.fetchone()['n'] or 0)
    db.close()
    return n


# ── Depoimentos ─────────────────────────────────────────────────────────────

def list_testimonials(active_only: bool = True) -> list[dict]:
    db = get_db()
    c = db.cursor()
    if active_only:
        c.execute(
            'SELECT * FROM testimonials WHERE ativo = 1 ORDER BY ordem ASC, id ASC'
        )
    else:
        c.execute('SELECT * FROM testimonials ORDER BY ordem ASC, id ASC')
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def get_testimonial(testimonial_id: int) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM testimonials WHERE id = ?', (testimonial_id,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def create_testimonial(data: dict) -> int:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO testimonials (nome, cidade, descricao, texto, foto_url, ativo, ordem)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            data['nome'], data.get('cidade'), data.get('descricao'),
            data['texto'], data.get('foto_url'),
            1 if data.get('ativo', True) else 0,
            int(data.get('ordem') or 0),
        ),
    )
    tid = c.lastrowid
    db.commit()
    db.close()
    return int(tid)


def update_testimonial(testimonial_id: int, data: dict) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE testimonials SET nome=?, cidade=?, descricao=?, texto=?,
           foto_url=?, ativo=?, ordem=? WHERE id=?''',
        (
            data['nome'], data.get('cidade'), data.get('descricao'),
            data['texto'], data.get('foto_url'),
            1 if data.get('ativo', True) else 0,
            int(data.get('ordem') or 0),
            testimonial_id,
        ),
    )
    ok = c.rowcount > 0
    db.commit()
    db.close()
    return ok


def delete_testimonial(testimonial_id: int) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM testimonials WHERE id = ?', (testimonial_id,))
    ok = c.rowcount > 0
    db.commit()
    db.close()
    return ok


# ── Blog ────────────────────────────────────────────────────────────────────

def list_blog_posts(published_only: bool = True) -> list[dict]:
    db = get_db()
    c = db.cursor()
    if published_only:
        c.execute(
            'SELECT * FROM blog_posts WHERE publicado = 1 ORDER BY publicado_em DESC, id DESC'
        )
    else:
        c.execute('SELECT * FROM blog_posts ORDER BY publicado_em DESC, id DESC')
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def get_blog_post_by_slug(slug: str, published_only: bool = True) -> dict | None:
    db = get_db()
    c = db.cursor()
    if published_only:
        c.execute(
            'SELECT * FROM blog_posts WHERE slug = ? AND publicado = 1', (slug,)
        )
    else:
        c.execute('SELECT * FROM blog_posts WHERE slug = ?', (slug,))
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def upsert_blog_post(data: dict) -> None:
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('SELECT id FROM blog_posts WHERE slug = ?', (data['slug'],))
    existing = c.fetchone()
    pub = 1 if data.get('publicado') else 0
    pub_em = data.get('publicado_em') or (now if pub else None)
    if existing:
        c.execute(
            '''UPDATE blog_posts SET titulo=?, resumo=?, conteudo=?, autor=?,
               publicado=?, publicado_em=?, atualizado_em=?, meta_title=?,
               meta_description=?, imagem_capa=?, tags=? WHERE slug=?''',
            (
                data['titulo'], data.get('resumo'), data.get('conteudo'),
                data.get('autor'), pub, pub_em, now,
                data.get('meta_title'), data.get('meta_description'),
                data.get('imagem_capa'), data.get('tags'), data['slug'],
            ),
        )
    else:
        c.execute(
            '''INSERT INTO blog_posts
               (slug, titulo, resumo, conteudo, autor, publicado, publicado_em,
                atualizado_em, meta_title, meta_description, imagem_capa, tags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['slug'], data['titulo'], data.get('resumo'),
                data.get('conteudo'), data.get('autor'), pub, pub_em, now,
                data.get('meta_title'), data.get('meta_description'),
                data.get('imagem_capa'), data.get('tags'),
            ),
        )
    db.commit()
    db.close()


# ── Onboarding e-mails ──────────────────────────────────────────────────────

def ensure_onboarding_rows(usuario_id: str) -> None:
    db = get_db()
    c = db.cursor()
    for n in range(1, 6):
        try:
            c.execute(
                '''INSERT INTO onboarding_emails (usuario_id, email_numero, status)
                   VALUES (?, ?, 'pendente')''',
                (usuario_id, n),
            )
        except IntegrityError:
            pass
    db.commit()
    db.close()


def list_onboarding_pending() -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT oe.*, u.email, u.username, u.display_name, u.created_at AS user_created_at
           FROM onboarding_emails oe
           JOIN users u ON u.id = oe.usuario_id
           WHERE oe.status = 'pendente'
           ORDER BY oe.usuario_id, oe.email_numero'''
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def mark_onboarding_sent(row_id: int, status: str = 'enviado') -> None:
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        'UPDATE onboarding_emails SET status = ?, enviado_em = ? WHERE id = ?',
        (status, now, row_id),
    )
    db.commit()
    db.close()


def update_assinatura_trial(
    banda_id: str,
    *,
    trial_inicio: str | None = None,
    trial_fim: str | None = None,
    trial_usado: int | None = None,
) -> None:
    parts: list[str] = []
    vals: list = []
    if trial_inicio is not None:
        parts.append('trial_inicio = ?')
        vals.append(trial_inicio)
    if trial_fim is not None:
        parts.append('trial_fim = ?')
        vals.append(trial_fim)
    if trial_usado is not None:
        parts.append('trial_usado = ?')
        vals.append(trial_usado)
    if not parts:
        return
    vals.append(banda_id)
    db = get_db()
    c = db.cursor()
    c.execute(f'UPDATE assinaturas SET {", ".join(parts)} WHERE banda_id = ?', vals)
    db.commit()
    db.close()


def list_trials_expiring_soon(days: int = 3) -> list[dict]:
    db = get_db()
    c = db.cursor()
    limite = (datetime.utcnow() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    agora = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''SELECT a.*, b.name AS band_name, b.owner_id, u.email AS owner_email
           FROM assinaturas a
           JOIN bands b ON b.id = a.banda_id
           JOIN users u ON u.id = b.owner_id
           WHERE a.trial_usado = 1 AND a.trial_fim IS NOT NULL
             AND a.trial_fim > ? AND a.trial_fim <= ?
             AND a.plano = 'gratis' AND a.status = 'ativa' ''',
        (agora, limite),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_expired_trials() -> list[dict]:
    agora = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT a.*, b.name AS band_name, b.owner_id, u.email AS owner_email
           FROM assinaturas a
           JOIN bands b ON b.id = a.banda_id
           JOIN users u ON u.id = b.owner_id
           WHERE a.trial_usado = 1 AND a.trial_fim IS NOT NULL
             AND a.trial_fim <= ? AND a.plano = 'gratis' AND a.status = 'ativa' ''',
        (agora,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


# ── Retenção anti-churn ───────────────────────────────────────────────────────

def retention_was_sent(usuario_id: str, campaign: str) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT 1 FROM retention_emails
           WHERE usuario_id = ? AND campaign = ? AND status = 'enviado' LIMIT 1''',
        (usuario_id, campaign),
    )
    found = c.fetchone() is not None
    db.close()
    return found


def mark_retention_sent(usuario_id: str, campaign: str, status: str = 'enviado') -> None:
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    try:
        c.execute(
            '''INSERT INTO retention_emails (usuario_id, campaign, status, enviado_em)
               VALUES (?, ?, ?, ?)''',
            (usuario_id, campaign, status, now),
        )
    except IntegrityError:
        c.execute(
            '''UPDATE retention_emails SET status = ?, enviado_em = ?
               WHERE usuario_id = ? AND campaign = ?''',
            (status, now, usuario_id, campaign),
        )
    db.commit()
    db.close()


def list_retention_candidates_inactive(min_days: int) -> list[dict]:
    cutoff = (datetime.utcnow() - timedelta(days=min_days)).strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    if IS_POSTGRES:
        c.execute(
            '''SELECT u.*
               FROM users u
               WHERE COALESCE(u.email, '') != ''
                 AND COALESCE(u.email_notify, 1) = 1
                 AND COALESCE(u.last_login_at, u.created_at) <= ?::timestamp
               ORDER BY u.created_at''',
            (cutoff,),
        )
    else:
        c.execute(
            '''SELECT u.*
               FROM users u
               WHERE COALESCE(u.email, '') != ''
                 AND COALESCE(u.email_notify, 1) = 1
                 AND datetime(COALESCE(u.last_login_at, u.created_at)) <= datetime(?)
               ORDER BY u.created_at''',
            (cutoff,),
        )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_retention_candidates_no_band(*, min_days: int) -> list[dict]:
    cutoff = (datetime.utcnow() - timedelta(days=min_days)).strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    if IS_POSTGRES:
        c.execute(
            '''SELECT u.*
               FROM users u
               WHERE COALESCE(u.email, '') != ''
                 AND COALESCE(u.email_notify, 1) = 1
                 AND u.created_at <= ?::timestamp
                 AND NOT EXISTS (
                     SELECT 1 FROM band_members bm WHERE bm.user_id = u.id
                 )
                 AND NOT EXISTS (
                     SELECT 1 FROM bands b WHERE b.owner_id = u.id
                 )
               ORDER BY u.created_at''',
            (cutoff,),
        )
    else:
        c.execute(
            '''SELECT u.*
               FROM users u
               WHERE COALESCE(u.email, '') != ''
                 AND COALESCE(u.email_notify, 1) = 1
                 AND datetime(u.created_at) <= datetime(?)
                 AND NOT EXISTS (
                     SELECT 1 FROM band_members bm WHERE bm.user_id = u.id
                 )
                 AND NOT EXISTS (
                     SELECT 1 FROM bands b WHERE b.owner_id = u.id
                 )
               ORDER BY u.created_at''',
            (cutoff,),
        )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_retention_candidates_trial_expired() -> list[dict]:
    return list_expired_trials()
