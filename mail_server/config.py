import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=False)

BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.getenv("MAIL_DATA_DIR", str(BASE_DIR.parent / "data" / "mail")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DOMAIN = (
    (os.getenv("MAIL_DOMAIN") or os.getenv("DOMAIN") or "unissono.app").strip().lower()
)
MAIL_HOSTNAME = (os.getenv("MAIL_HOSTNAME") or f"mail.{DOMAIN}").strip().lower()

# Domínios legados aceitos no SMTP/webmail e reescritos para DOMAIN (ex.: @setsync.com.br → @unissono.app).
_legacy_raw = (os.getenv("MAIL_LEGACY_DOMAINS") or "setsync.com.br").strip().lower()
LEGACY_DOMAINS: frozenset[str] = frozenset(
    d.strip() for d in _legacy_raw.split(",") if d.strip() and d.strip() != DOMAIN
)
LOCAL_DOMAINS: frozenset[str] = frozenset({DOMAIN}) | LEGACY_DOMAINS


def is_local_address(addr: str) -> bool:
    email = (addr or "").strip().lower()
    if "@" not in email:
        return False
    return email.rsplit("@", 1)[-1] in LOCAL_DOMAINS


def canonical_mailbox(addr: str) -> str:
    """Normaliza caixas legado → domínio canônico (unissono.app)."""
    email = (addr or "").strip().lower()
    if "@" not in email:
        return email
    local, _, domain = email.partition("@")
    if domain in LEGACY_DOMAINS:
        return f"{local}@{DOMAIN}"
    return email


SMTP_BIND_HOST = os.getenv("SMTP_BIND_HOST", "0.0.0.0")
SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))
SMTP_SUBMISSION_PORT = int(os.getenv("SMTP_SUBMISSION_PORT", "587"))
SMTP_CONNECT_HOST = os.getenv("SMTP_CONNECT_HOST", "mail")

DATABASE_PATH = os.getenv("MAIL_DATABASE_PATH", str(DATA_DIR / "emails.db"))

ADMIN_EMAIL = canonical_mailbox(
    os.getenv("ADMIN_EMAIL") or os.getenv("MAIL_USERNAME") or f"contato@{DOMAIN}"
)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or os.getenv("MAIL_PASSWORD") or ""
SENDER_NAME = os.getenv("MAIL_SENDER_NAME", os.getenv("SENDER_NAME", "Uníssono"))
