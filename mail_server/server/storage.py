import hashlib
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from mail_server.config import ADMIN_EMAIL, ADMIN_PASSWORD, DATABASE_PATH


def _aiosqlite():
    import aiosqlite

    return aiosqlite


def _hash_password(password: str, salt: Optional[str] = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return secrets.compare_digest(digest.hex(), expected)


class EmailStorage:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self) -> None:
        async with _aiosqlite().connect(self.db_path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT,
                    sender TEXT NOT NULL,
                    recipients TEXT NOT NULL,
                    subject TEXT,
                    body_text TEXT,
                    body_html TEXT,
                    folder TEXT DEFAULT 'inbox',
                    is_read INTEGER DEFAULT 0,
                    owner_email TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_emails_owner ON emails(owner_email);
                CREATE INDEX IF NOT EXISTS idx_emails_folder ON emails(folder);
                """
            )
            await db.commit()

        if not await self.get_user_by_email(ADMIN_EMAIL):
            await self.create_user(ADMIN_EMAIL, ADMIN_PASSWORD, is_admin=True)

    async def create_user(self, email: str, password: str, is_admin: bool = False) -> int:
        now = datetime.now(timezone.utc).isoformat()
        async with _aiosqlite().connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?)",
                (email.lower(), _hash_password(password), int(is_admin), now),
            )
            await db.commit()
            return cursor.lastrowid

    async def authenticate(self, email: str, password: str) -> Optional[dict]:
        user = await self.get_user_by_email(email)
        if user and _verify_password(password, user["password_hash"]):
            return user
        return None

    def authenticate_sync(self, email: str, password: str) -> Optional[dict]:
        user = self.get_user_by_email_sync(email)
        if user and _verify_password(password, user["password_hash"]):
            return user
        return None

    def get_user_by_email_sync(self, email: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            row = db.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()
            return dict(row) if row else None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        async with _aiosqlite().connect(self.db_path) as db:
            db.row_factory = _aiosqlite().Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower(),)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def list_users(self) -> list[dict]:
        async with _aiosqlite().connect(self.db_path) as db:
            db.row_factory = _aiosqlite().Row
            cursor = await db.execute("SELECT id, email, is_admin, created_at FROM users ORDER BY email")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def save_email(
        self,
        sender: str,
        recipients: list[str],
        subject: str,
        body_text: str,
        body_html: Optional[str],
        owner_email: str,
        message_id: str = "",
        folder: str = "inbox",
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        async with _aiosqlite().connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO emails (message_id, sender, recipients, subject, body_text, body_html, folder, owner_email, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    sender,
                    ", ".join(recipients),
                    subject,
                    body_text,
                    body_html,
                    folder,
                    owner_email.lower(),
                    now,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_emails(self, owner_email: str, folder: str = "inbox") -> list[dict]:
        async with _aiosqlite().connect(self.db_path) as db:
            db.row_factory = _aiosqlite().Row
            cursor = await db.execute(
                """
                SELECT * FROM emails
                WHERE owner_email = ? AND folder = ?
                ORDER BY created_at DESC
                """,
                (owner_email.lower(), folder),
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_email(self, email_id: int, owner_email: str) -> Optional[dict]:
        async with _aiosqlite().connect(self.db_path) as db:
            db.row_factory = _aiosqlite().Row
            cursor = await db.execute(
                "SELECT * FROM emails WHERE id = ? AND owner_email = ?",
                (email_id, owner_email.lower()),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def mark_as_read(self, email_id: int, owner_email: str) -> None:
        async with _aiosqlite().connect(self.db_path) as db:
            await db.execute(
                "UPDATE emails SET is_read = 1 WHERE id = ? AND owner_email = ?",
                (email_id, owner_email.lower()),
            )
            await db.commit()

    async def delete_email(self, email_id: int, owner_email: str) -> None:
        async with _aiosqlite().connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM emails WHERE id = ? AND owner_email = ?",
                (email_id, owner_email.lower()),
            )
            await db.commit()

    async def move_to_folder(self, email_id: int, owner_email: str, folder: str) -> None:
        async with _aiosqlite().connect(self.db_path) as db:
            await db.execute(
                "UPDATE emails SET folder = ? WHERE id = ? AND owner_email = ?",
                (folder, email_id, owner_email.lower()),
            )
            await db.commit()

    def get_emails_sync(self, owner_email: str, folder: str = "inbox") -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                """
                SELECT * FROM emails
                WHERE owner_email = ? AND folder = ?
                ORDER BY created_at DESC
                """,
                (owner_email.lower(), folder),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_email_sync(self, email_id: int, owner_email: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            row = db.execute(
                "SELECT * FROM emails WHERE id = ? AND owner_email = ?",
                (email_id, owner_email.lower()),
            ).fetchone()
            return dict(row) if row else None

    def mark_as_read_sync(self, email_id: int, owner_email: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute(
                "UPDATE emails SET is_read = 1 WHERE id = ? AND owner_email = ?",
                (email_id, owner_email.lower()),
            )
            db.commit()

    def delete_email_sync(self, email_id: int, owner_email: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute(
                "DELETE FROM emails WHERE id = ? AND owner_email = ?",
                (email_id, owner_email.lower()),
            )
            db.commit()

    def save_email_sync(
        self,
        sender: str,
        recipients: list[str],
        subject: str,
        body_text: str,
        body_html: Optional[str],
        owner_email: str,
        message_id: str = "",
        folder: str = "inbox",
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute(
                """
                INSERT INTO emails (message_id, sender, recipients, subject, body_text, body_html, folder, owner_email, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    sender,
                    ", ".join(recipients),
                    subject,
                    body_text,
                    body_html,
                    folder,
                    owner_email.lower(),
                    now,
                ),
            )
            db.commit()
            return cursor.lastrowid
