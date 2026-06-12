#!/usr/bin/env python3
"""Testa fluxo de recuperação de senha (token + update no banco)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-min-32-chars-long!!'
os.environ['FLASK_ENV'] = 'development'


class PasswordResetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db
        init_db()

    def test_token_e_nova_senha(self):
        from db import create_user, get_user_by_email, verify_password, update_user_password_by_email
        from itsdangerous import URLSafeTimedSerializer

        uid = create_user('resetuser', 'reset@test.com', 'senhaAntiga123', display_name='Reset')
        self.assertTrue(uid)
        self.assertTrue(verify_password(uid, 'senhaAntiga123'))

        s = URLSafeTimedSerializer(os.environ['SECRET_KEY'], salt='recuperar-senha')
        token = s.dumps('reset@test.com')
        email = s.loads(token, max_age=3600)

        self.assertTrue(update_user_password_by_email(email, 'novaSenhaSegura1'))
        user = get_user_by_email('reset@test.com')
        self.assertTrue(verify_password(user['id'], 'novaSenhaSegura1'))
        self.assertFalse(verify_password(user['id'], 'senhaAntiga123'))


if __name__ == '__main__':
    unittest.main()
