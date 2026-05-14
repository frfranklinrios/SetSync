import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

DB_PATH = "data/banda.db"

def get_db():
    """Retorna conexão com banco de dados"""
    os.makedirs("data", exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Inicializa banco de dados com schema"""
    db = get_db()
    c = db.cursor()
    
    # Tabela de usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        google_id TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Adicionar coluna google_id se não existir (migração)
    try:
        c.execute('ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE')
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    # Tabela de bandas
    c.execute('''CREATE TABLE IF NOT EXISTS bands (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        owner_id TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    
    # Tabela de membros de banda
    c.execute('''CREATE TABLE IF NOT EXISTS band_members (
        band_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT DEFAULT 'member',
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (band_id, user_id),
        FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    
    # Tabela de cifras
    c.execute('''CREATE TABLE IF NOT EXISTS cifras (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        artista TEXT NOT NULL,
        tom_original TEXT DEFAULT 'C',
        conteudo TEXT NOT NULL,
        band_id TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (band_id) REFERENCES bands(id) ON DELETE CASCADE
    )''')
    
    db.commit()
    db.close()
    print("✓ Database initialized")

# ============ USERS ============

def create_user(username, email, password):
    """Cria novo usuário"""
    try:
        db = get_db()
        c = db.cursor()
        
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        c.execute('''INSERT INTO users (id, username, email, password_hash)
                     VALUES (?, ?, ?, ?)''',
                  (user_id, username, email, password_hash))
        db.commit()
        db.close()
        return user_id
    except sqlite3.IntegrityError:
        db.close()
        return None

def get_user_by_username(username):
    """Busca usuário por username"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    db.close()
    return dict(user) if user else None

def get_user_by_email(email):
    """Busca usuário por email"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    db.close()
    return dict(user) if user else None

def get_user(user_id):
    """Busca usuário por ID"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    db.close()
    return dict(user) if user else None

def get_user_by_google_id(google_id):
    """Busca usuário por Google ID"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    user = c.fetchone()
    db.close()
    return dict(user) if user else None

def create_google_user(google_id, email, username):
    """Cria novo usuário com Google OAuth"""
    try:
        db = get_db()
        c = db.cursor()
        
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        c.execute('''INSERT INTO users (id, username, email, google_id, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, username, email, google_id, now))
        db.commit()
        db.close()
        return user_id
    except sqlite3.IntegrityError:
        db.close()
        return None

def verify_password(user_id, password):
    """Verifica senha do usuário"""
    user = get_user(user_id)
    if user:
        return check_password_hash(user['password_hash'], password)
    return False

# ============ BANDS ============

def create_band(name, description, owner_id):
    """Cria nova banda"""
    db = get_db()
    c = db.cursor()
    
    band_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    c.execute('''INSERT INTO bands (id, name, description, owner_id, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (band_id, name, description, owner_id, now, now))
    
    # Adicionar owner como membro
    c.execute('''INSERT INTO band_members (band_id, user_id, role)
                 VALUES (?, ?, ?)''',
              (band_id, owner_id, 'admin'))
    
    db.commit()
    db.close()
    return band_id

def get_band(band_id):
    """Busca banda por ID"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM bands WHERE id = ?', (band_id,))
    band = c.fetchone()
    db.close()
    return dict(band) if band else None

def get_user_bands(user_id):
    """Retorna bandas que o usuário é membro"""
    db = get_db()
    c = db.cursor()
    c.execute('''SELECT b.* FROM bands b
                 JOIN band_members bm ON b.id = bm.band_id
                 WHERE bm.user_id = ?
                 ORDER BY b.name''', (user_id,))
    bands = [dict(row) for row in c.fetchall()]
    db.close()
    return bands

def get_owned_bands(user_id):
    """Retorna bandas que o usuário é proprietário"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM bands WHERE owner_id = ? ORDER BY name', (user_id,))
    bands = [dict(row) for row in c.fetchall()]
    db.close()
    return bands

def update_band(band_id, name, description):
    """Atualiza banda"""
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().isoformat()
    
    c.execute('''UPDATE bands SET name = ?, description = ?, updated_at = ?
                 WHERE id = ?''',
              (name, description, now, band_id))
    db.commit()
    db.close()

def get_band_members(band_id):
    """Retorna membros de uma banda"""
    db = get_db()
    c = db.cursor()
    c.execute('''SELECT u.*, bm.role FROM users u
                 JOIN band_members bm ON u.id = bm.user_id
                 WHERE bm.band_id = ?
                 ORDER BY bm.role DESC, u.username''', (band_id,))
    members = [dict(row) for row in c.fetchall()]
    db.close()
    return members

def add_band_member(band_id, user_id):
    """Adiciona membro à banda"""
    try:
        db = get_db()
        c = db.cursor()
        c.execute('''INSERT INTO band_members (band_id, user_id, role)
                     VALUES (?, ?, ?)''',
                  (band_id, user_id, 'member'))
        db.commit()
        db.close()
        return True
    except sqlite3.IntegrityError:
        db.close()
        return False

def remove_band_member(band_id, user_id):
    """Remove membro da banda"""
    db = get_db()
    c = db.cursor()
    c.execute('''DELETE FROM band_members
                 WHERE band_id = ? AND user_id = ?''',
              (band_id, user_id))
    db.commit()
    db.close()

def is_band_member(band_id, user_id):
    """Verifica se usuário é membro da banda"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT 1 FROM band_members WHERE band_id = ? AND user_id = ?',
              (band_id, user_id))
    result = c.fetchone()
    db.close()
    return result is not None

def is_band_admin(band_id, user_id):
    """Verifica se usuário é admin da banda"""
    db = get_db()
    c = db.cursor()
    
    # Owner é sempre admin
    c.execute('SELECT owner_id FROM bands WHERE id = ?', (band_id,))
    band = c.fetchone()
    if band and band['owner_id'] == user_id:
        db.close()
        return True
    
    # Verificar role
    c.execute('''SELECT role FROM band_members
                 WHERE band_id = ? AND user_id = ?''',
              (band_id, user_id))
    member = c.fetchone()
    db.close()
    return member and member['role'] == 'admin'

# ============ CIFRAS ============

def create_cifra(titulo, artista, tom_original, conteudo, band_id):
    """Cria nova cifra"""
    db = get_db()
    c = db.cursor()
    
    cifra_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    c.execute('''INSERT INTO cifras (id, titulo, artista, tom_original, conteudo, band_id, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (cifra_id, titulo, artista, tom_original, conteudo, band_id, now, now))
    db.commit()
    db.close()
    return cifra_id

def get_cifra(cifra_id):
    """Busca cifra por ID"""
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM cifras WHERE id = ?', (cifra_id,))
    cifra = c.fetchone()
    db.close()
    return dict(cifra) if cifra else None

def get_band_cifras(band_id):
    """Retorna todas as cifras de uma banda"""
    db = get_db()
    c = db.cursor()
    c.execute('''SELECT * FROM cifras WHERE band_id = ?
                 ORDER BY titulo''', (band_id,))
    cifras = [dict(row) for row in c.fetchall()]
    db.close()
    return cifras

def update_cifra(cifra_id, titulo, artista, tom_original, conteudo):
    """Atualiza cifra"""
    db = get_db()
    c = db.cursor()
    now = datetime.utcnow().isoformat()
    
    c.execute('''UPDATE cifras SET titulo = ?, artista = ?, tom_original = ?, conteudo = ?, updated_at = ?
                 WHERE id = ?''',
              (titulo, artista, tom_original, conteudo, now, cifra_id))
    db.commit()
    db.close()

def delete_cifra(cifra_id):
    """Deleta cifra"""
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM cifras WHERE id = ?', (cifra_id,))
    db.commit()
    db.close()
