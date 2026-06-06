#!/usr/bin/env python3
"""Envia um e-mail de teste para validar a configuração SMTP.

Uso:
    python scripts/send_test_email.py destino@exemplo.com

Lê as variáveis MAIL_* do ambiente (.env) e tenta enviar de verdade,
imprimindo o resultado. Útil para conferir credenciais (Zoho, Gmail etc.)
antes de confiar nos e-mails automáticos do app.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: python scripts/send_test_email.py destino@exemplo.com')
        return 2
    destino = sys.argv[1].strip()

    from flask import Flask
    from flask_mail import Mail
    import email_config
    from email_service import is_configured, send_email

    app = Flask(__name__)
    app.config.from_object(email_config)
    Mail(app)

    with app.app_context():
        print(f"Servidor:  {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}")
        print(f"TLS:       {app.config.get('MAIL_USE_TLS')}")
        print(f"Usuário:   {app.config.get('MAIL_USERNAME') or '(vazio)'}")
        print(f"Senha:     {'(definida)' if app.config.get('MAIL_PASSWORD') else '(vazia)'}")
        print(f"Remetente: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"Destino:   {destino}\n")

        if not is_configured():
            print('ERRO: SMTP não configurado (defina MAIL_USERNAME e MAIL_PASSWORD no .env).')
            return 1

        ok = send_email(
            [destino],
            'Teste de e-mail — SetSync',
            html='<p>Este é um <strong>e-mail de teste</strong> do SetSync. '
                 'Se você recebeu, o SMTP está funcionando. 🎸</p>',
            body='Este é um e-mail de teste do SetSync. Se você recebeu, o SMTP está funcionando.',
        )

    if ok:
        print('OK: e-mail enviado. Verifique a caixa de entrada (e o spam).')
        return 0
    print('FALHOU: veja o log acima para o motivo (credenciais, porta, TLS).')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
