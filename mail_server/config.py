import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=False)

BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.getenv("MAIL_DATA_DIR", str(BASE_DIR.parent / "data" / "mail")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DOMAIN = os.getenv("MAIL_DOMAIN", os.getenv("DOMAIN", "setsync.com.br"))
MAIL_HOSTNAME = os.getenv("MAIL_HOSTNAME", f"mail.{DOMAIN}")

SMTP_BIND_HOST = os.getenv("SMTP_BIND_HOST", "0.0.0.0")
SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))
SMTP_SUBMISSION_PORT = int(os.getenv("SMTP_SUBMISSION_PORT", "587"))
SMTP_CONNECT_HOST = os.getenv("SMTP_CONNECT_HOST", "mail")

DATABASE_PATH = os.getenv("MAIL_DATABASE_PATH", str(DATA_DIR / "emails.db"))

ADMIN_EMAIL = (
    os.getenv("ADMIN_EMAIL")
    or os.getenv("MAIL_USERNAME")
    or f"contato@{DOMAIN}"
).strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or os.getenv("MAIL_PASSWORD") or ""
SENDER_NAME = os.getenv("MAIL_SENDER_NAME", os.getenv("SENDER_NAME", "SetSync"))
