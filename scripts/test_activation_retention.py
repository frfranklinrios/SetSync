#!/usr/bin/env python3
"""Testes do plano de ativação: demo onboarding, trial por valor, surveys."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/activation_test.db'
os.environ['SECRET_KEY'] = 'test-activation-key-min-32-chars!!'
os.environ['FLASK_ENV'] = 'development'
os.environ['WTF_CSRF_ENABLED'] = 'false'
# CI usa ALLOWED_HOSTS=localhost; HTTP tests usam o host canônico
_hosts = (os.environ.get('SETSYNC_ALLOWED_HOSTS') or '').strip()
if 'unissono.app' not in _hosts.split(','):
    os.environ['SETSYNC_ALLOWED_HOSTS'] = (
        f'{_hosts},unissono.app' if _hosts else 'localhost,unissono.app'
    )
os.environ.setdefault('SETSYNC_CANONICAL_URL', 'https://unissono.app')


class DemoOnboardingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()

    def test_seed_demo_library_idempotent(self):
        from db import count_user_personal_cifras, create_user, get_user_personal_cifras
        from demo_onboarding import seed_demo_library_for_user, user_has_demo_library

        uid = create_user('demo1', 'demo1@test.com', 'senha1234567', display_name='Demo')
        created = seed_demo_library_for_user(uid)
        self.assertEqual(len(created), 4)
        self.assertTrue(user_has_demo_library(uid))
        self.assertEqual(count_user_personal_cifras(uid), 4)

        again = seed_demo_library_for_user(uid)
        self.assertEqual(again, [])
        self.assertEqual(count_user_personal_cifras(uid), 4)

        cifras = get_user_personal_cifras(uid)
        self.assertTrue(any('Porque Ele Vive' in (c.get('titulo') or '') for c in cifras))

    def test_seed_skips_when_user_already_has_cifras(self):
        from db import create_personal_cifra, create_user
        from demo_onboarding import seed_demo_library_for_user

        uid = create_user('demo2', 'demo2@test.com', 'senha1234567', display_name='Demo2')
        create_personal_cifra(uid, 'Minha', 'Eu', 'C', '[C] oi')
        self.assertEqual(seed_demo_library_for_user(uid), [])


class TrialOnValueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()

    def test_create_band_does_not_start_trial(self):
        from db import create_band, create_user, get_assinatura
        from monetizacao import dias_restantes_trial

        uid = create_user('novatrial', 'novatrial@test.com', 'senha1234567', display_name='N')
        band_id = create_band('Banda Sem Trial', '', uid)
        row = get_assinatura(band_id)
        self.assertTrue(row)
        self.assertFalse(row.get('trial_usado'))
        self.assertIsNone(dias_restantes_trial(band_id))

    def test_maybe_start_trial_on_play(self):
        from db import create_band, create_user
        from demo_onboarding import maybe_start_trial_on_value
        from monetizacao import dias_restantes_trial, get_plano_efetivo

        uid = create_user('playtrial', 'playtrial@test.com', 'senha1234567', display_name='P')
        band_id = create_band('Banda Play', '', uid)
        started = maybe_start_trial_on_value(uid, reason='play_mode')
        self.assertEqual(started, band_id)
        self.assertEqual(get_plano_efetivo(band_id), 'pro')
        self.assertGreaterEqual(dias_restantes_trial(band_id) or 0, 29)

        # segunda chamada não reinicia
        self.assertIsNone(maybe_start_trial_on_value(uid, reason='play_mode'))

    def test_maybe_start_without_band_is_noop(self):
        from db import create_user
        from demo_onboarding import maybe_start_trial_on_value

        uid = create_user('sembanda', 'sembanda@test.com', 'senha1234567', display_name='S')
        self.assertIsNone(maybe_start_trial_on_value(uid, reason='play_mode'))


class SurveysTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()

    def test_play_csat_and_churn_survey(self):
        from config import app_now_naive
        from db import (
            create_band,
            create_user,
            get_user,
            save_user_churn_survey,
            save_user_play_csat,
            update_assinatura_trial,
            user_should_see_churn_survey,
        )
        from monetizacao import iniciar_trial_banda

        uid = create_user('csat1', 'csat1@test.com', 'senha1234567', display_name='C')
        self.assertTrue(save_user_play_csat(uid, 'excelente'))
        self.assertFalse(save_user_play_csat(uid, 'excelente'))  # só 1×
        self.assertFalse(save_user_play_csat(uid, 'invalido'))
        u = get_user(uid)
        self.assertEqual(u.get('play_csat_answer'), 'excelente')
        self.assertTrue(u.get('play_csat_submitted_at'))

        band_id = create_band('Banda Churn', '', uid)
        self.assertTrue(iniciar_trial_banda(band_id))
        passado = (app_now_naive().replace(microsecond=0)).strftime('%Y-%m-%d %H:%M:%S')
        update_assinatura_trial(band_id, trial_fim=passado, trial_usado=1)
        self.assertTrue(user_should_see_churn_survey(uid))
        self.assertTrue(save_user_churn_survey(uid, 'caro'))
        self.assertFalse(user_should_see_churn_survey(uid))


class ActivationHttpTest(unittest.TestCase):
    """Fluxos HTTP: cadastro → demo → tocar; surveys API."""

    BASE = 'https://unissono.app'

    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()
        from app import app

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.app = app

    def test_register_seeds_demo_and_tocar_colecao(self):
        from db import count_user_personal_cifras, get_user_by_username

        client = self.app.test_client()
        r = client.post(
            '/auth/register',
            data={
                'username': 'httpdemo',
                'email': 'httpdemo@test.com',
                'password': 'senha1234567',
                'confirm': 'senha1234567',
                'display_name': 'Http Demo',
                'aceite_privacidade': '1',
            },
            base_url=self.BASE,
            follow_redirects=False,
        )
        self.assertIn(r.status_code, (302, 303), r.get_data(as_text=True)[:300])
        user = get_user_by_username('httpdemo')
        self.assertTrue(user)
        self.assertGreaterEqual(count_user_personal_cifras(user['id']), 4)

        with client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['username'] = user['username']

        r2 = client.get(
            '/cifras/minha-colecao/tocar',
            base_url=self.BASE,
            follow_redirects=True,
        )
        self.assertLess(r2.status_code, 400, r2.get_data(as_text=True)[:400])
        body = r2.get_data(as_text=True)
        self.assertTrue(
            'play-mode' in body.lower()
            or 'cifras-data' in body
            or 'pb-exit' in body,
            'página de tocar sem markers esperados',
        )

    def test_play_csat_endpoint(self):
        from db import create_user, get_user
        from flask.sessions import SecureCookieSessionInterface

        uid = create_user('api_csat', 'api_csat@test.com', 'senha1234567', display_name='Api')
        serializer = SecureCookieSessionInterface().get_signing_serializer(self.app)
        cookie_val = serializer.dumps({'_permanent': True, 'user_id': uid})
        client = self.app.test_client()
        client.set_cookie(
            'session',
            cookie_val,
            domain='unissono.app',
            path='/',
            secure=True,
            httponly=True,
            samesite='Lax',
        )
        r = client.post(
            '/ajuda/play-csat',
            json={'answer': 'problemas'},
            content_type='application/json',
            base_url=self.BASE,
        )
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True)[:200])
        self.assertTrue(r.get_json().get('ok'))
        self.assertEqual(get_user(uid).get('play_csat_answer'), 'problemas')


if __name__ == '__main__':
    unittest.main()
