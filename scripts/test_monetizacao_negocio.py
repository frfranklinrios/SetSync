#!/usr/bin/env python3
"""Testes de negócio: limites de plano, trial e onboarding."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-min-32-chars-long!!'
os.environ['FLASK_ENV'] = 'development'


class MonetizacaoNegocioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db
        init_db()

    def test_trial_pro_libera_limites(self):
        from db import create_user, create_band
        from monetizacao import iniciar_trial_banda, check_limite, dias_restantes_trial, get_plano_efetivo

        uid = create_user('trialuser', 'trial@test.com', 'senha1234567', display_name='Trial')
        self.assertTrue(uid)
        band_id = create_band('Banda Trial', '', uid)
        self.assertTrue(iniciar_trial_banda(band_id))
        band = {'id': band_id, 'owner_id': uid}
        self.assertTrue(check_limite(band, 'musica'))
        self.assertEqual(get_plano_efetivo(band_id), 'pro')
        dias = dias_restantes_trial(band_id)
        self.assertIsNotNone(dias)
        self.assertGreaterEqual(dias, 13)

    def test_trial_expirado_volta_limite_gratis(self):
        from db import create_user, create_band, update_assinatura_trial
        from monetizacao import get_plano_efetivo

        uid = create_user('expuser', 'exp@test.com', 'senha1234567')
        band_id = create_band('Banda Exp', '', uid)
        ontem = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        inicio = (datetime.utcnow() - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
        update_assinatura_trial(band_id, trial_inicio=inicio, trial_fim=ontem, trial_usado=1)
        self.assertEqual(get_plano_efetivo(band_id), 'gratis')

    def test_onboarding_rows(self):
        from db import create_user, ensure_onboarding_rows, list_onboarding_pending

        uid = create_user('onbuser', 'onb@test.com', 'senha1234567')
        ensure_onboarding_rows(uid)
        rows = [r for r in list_onboarding_pending() if r['usuario_id'] == uid]
        self.assertEqual(len(rows), 5)


if __name__ == '__main__':
    unittest.main()
