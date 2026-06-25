#!/usr/bin/env python3
"""Testes do convite WhatsApp admin (sem envio real)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-admin-outreach')

from flask import Flask

from admin_outreach import build_invite_message

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


def main() -> None:
    with app.app_context():
        studio_msg = build_invite_message(
            'studio_prospect', {'id': 'p1', 'nome': 'Studio Forte', 'cidade': 'Fortaleza'}
        )
        assert 'Studio Forte' in studio_msg
        assert 'cadastrar' in studio_msg.lower() or 'Cadastre' in studio_msg

    print('OK: admin_outreach messages')


if __name__ == '__main__':
    main()
