import logging
import subprocess
from pathlib import Path

from mail_server.config import DATA_DIR, DOMAIN

logger = logging.getLogger(__name__)

DKIM_SELECTOR = "setsync"
DKIM_DIR = DATA_DIR / "dkim"
PRIVATE_KEY_PATH = DKIM_DIR / f"{DKIM_SELECTOR}.private"
PUBLIC_KEY_PATH = DKIM_DIR / f"{DKIM_SELECTOR}.public"


def ensure_dkim_keys() -> None:
    if PRIVATE_KEY_PATH.exists():
        return

    DKIM_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["openssl", "genrsa", "-out", str(PRIVATE_KEY_PATH), "2048"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["openssl", "rsa", "-in", str(PRIVATE_KEY_PATH), "-pubout", "-out", str(PUBLIC_KEY_PATH)],
        check=True,
        capture_output=True,
    )
    PRIVATE_KEY_PATH.chmod(0o600)
    logger.info("Chaves DKIM geradas em %s", DKIM_DIR)


def dns_record() -> str:
    if not PUBLIC_KEY_PATH.exists():
        return ""
    pub = PUBLIC_KEY_PATH.read_text()
    pub = "".join(line for line in pub.splitlines() if not line.startswith("-"))
    return f"v=DKIM1; k=rsa; p={pub}"


def dns_host() -> str:
    return f"{DKIM_SELECTOR}._domainkey.{DOMAIN}"


def _normalize_crlf(message: str) -> bytes:
    """Flask-Mail já manda \\r\\n; normaliza antes do DKIM para evitar \\r solto."""
    text = message.replace('\r\n', '\n').replace('\r', '\n')
    return text.replace('\n', '\r\n').encode('utf-8')


def sign_message(message: str) -> bytes:
    if not PRIVATE_KEY_PATH.exists():
        ensure_dkim_keys()

    try:
        import dkim
    except ImportError:
        logger.warning("dkimpy não instalado — enviando sem assinatura DKIM")
        return _normalize_crlf(message)

    privkey = PRIVATE_KEY_PATH.read_bytes()
    msg_bytes = _normalize_crlf(message)
    sig = dkim.sign(
        msg_bytes,
        selector=DKIM_SELECTOR.encode(),
        domain=DOMAIN.encode(),
        privkey=privkey,
        include_headers=[
            b"from",
            b"to",
            b"subject",
            b"date",
            b"message-id",
            b"mime-version",
        ],
    )
    return sig + msg_bytes
