#!/usr/bin/env python3
"""Inicia apenas o servidor SMTP (recebimento + submissão autenticada)."""

import asyncio
import logging
import threading

from mail_server.config import ADMIN_EMAIL, DOMAIN, MAIL_HOSTNAME
from mail_server.server.dkim_sign import ensure_dkim_keys
from mail_server.server.smtp_server import SMTPServer
from mail_server.server.storage import EmailStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("SMTP SetSync — domínio %s, hostname %s", DOMAIN, MAIL_HOSTNAME)
    logger.info("Caixa principal: %s", ADMIN_EMAIL)

    storage = EmailStorage()
    asyncio.run(storage.init_db())
    ensure_dkim_keys()

    smtp = SMTPServer(storage)
    smtp.start()

    logger.info("SMTP ativo nas portas 25 e 587 (submissão)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        smtp.stop()


if __name__ == "__main__":
    main()
