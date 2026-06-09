import logging

from aiosmtpd.controller import Controller

from mail_server.config import (
    MAIL_HOSTNAME,
    SMTP_BIND_HOST,
    SMTP_PORT,
    SMTP_SUBMISSION_PORT,
)
from mail_server.server.smtp_handler import EmailHandler, SMTPAuthenticator
from mail_server.server.storage import EmailStorage

logger = logging.getLogger(__name__)


class SMTPServer:
    def __init__(self, storage: EmailStorage):
        self.storage = storage
        self.controllers: list[Controller] = []

    def start(self) -> None:
        handler = EmailHandler(self.storage)
        authenticator = SMTPAuthenticator(self.storage)

        inbound = Controller(
            handler,
            hostname=SMTP_BIND_HOST,
            port=SMTP_PORT,
            server_hostname=MAIL_HOSTNAME,
            auth_required=False,
        )
        inbound.start()
        self.controllers.append(inbound)
        logger.info("SMTP (recebimento) em %s:%d [%s]", SMTP_BIND_HOST, SMTP_PORT, MAIL_HOSTNAME)

        submission = Controller(
            handler,
            hostname=SMTP_BIND_HOST,
            port=SMTP_SUBMISSION_PORT,
            server_hostname=MAIL_HOSTNAME,
            authenticator=authenticator,
            auth_required=True,
            auth_require_tls=False,
        )
        submission.start()
        self.controllers.append(submission)
        logger.info("SMTP (submissão) em %s:%d", SMTP_BIND_HOST, SMTP_SUBMISSION_PORT)

    def stop(self) -> None:
        for controller in self.controllers:
            controller.stop()
        self.controllers.clear()
        logger.info("Servidores SMTP encerrados")
