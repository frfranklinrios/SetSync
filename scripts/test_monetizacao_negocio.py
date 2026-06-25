#!/usr/bin/env python3
"""Testes de negócio: limites de plano, trial e onboarding."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from config import app_now_naive, app_now_str

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
        self.assertGreaterEqual(dias, 29)

    def test_trial_estudio_libera_salas(self):
        from db import create_user
        from models_studio import create_studio, create_room, get_studio
        from monetizacao import (
            TRIAL_DIAS,
            check_studio_room_limit,
            dias_restantes_trial_estudio,
            iniciar_trial_estudio,
            studio_tem_premium,
        )

        self.assertEqual(TRIAL_DIAS, 30)
        uid = create_user('studiotrial', 'studio@test.com', 'senha1234567', display_name='Studio')
        studio_id = create_studio(uid, nome='Meu Estúdio', cidade='Fortaleza')
        self.assertTrue(studio_tem_premium(uid))
        dias = dias_restantes_trial_estudio(uid)
        self.assertIsNotNone(dias)
        self.assertGreaterEqual(dias, 29)
        for i in range(3):
            create_room(studio_id, nome=f'Sala {i + 1}')
        self.assertTrue(check_studio_room_limit(uid))
        self.assertTrue(iniciar_trial_estudio(uid) is False)

    def test_trial_expirado_volta_limite_gratis(self):
        from db import create_user, create_band, update_assinatura_trial
        from monetizacao import get_plano_efetivo

        uid = create_user('expuser', 'exp@test.com', 'senha1234567')
        band_id = create_band('Banda Exp', '', uid)
        ontem = (app_now_naive() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        inicio = (app_now_naive() - timedelta(days=31)).strftime('%Y-%m-%d %H:%M:%S')
        update_assinatura_trial(band_id, trial_inicio=inicio, trial_fim=ontem, trial_usado=1)
        self.assertEqual(get_plano_efetivo(band_id), 'gratis')

    def test_onboarding_rows(self):
        from db import create_user, ensure_onboarding_rows, list_onboarding_pending

        uid = create_user('onbuser', 'onb@test.com', 'senha1234567')
        ensure_onboarding_rows(uid)
        rows = [r for r in list_onboarding_pending() if r['usuario_id'] == uid]
        self.assertEqual(len(rows), 5)

    def test_planos_site_desconto_anual(self):
        from monetizacao import PLANO_INDIVIDUAL, PLANO_PRO, PLANO_WORSHIP, planos_para_site

        planos = {p.id: p for p in planos_para_site()}
        individual = planos[PLANO_INDIVIDUAL]
        pro = planos[PLANO_PRO]
        worship = planos[PLANO_WORSHIP]

        self.assertEqual(individual.desconto_anual_pct, 17)
        self.assertEqual(pro.desconto_anual_pct, 28)
        self.assertEqual(worship.desconto_anual_pct, 28)
        self.assertEqual(individual.preco_mensal_equivalente_label, 'R$ 12,42/mês')
        self.assertEqual(pro.preco_mensal_equivalente_label, 'R$ 20,75/mês')
        self.assertEqual(worship.preco_mensal_equivalente_label, 'R$ 49,92/mês')
        self.assertEqual(individual.cobrado_anual_label, 'cobrado anualmente — R$ 149/ano')
        self.assertEqual(pro.cobrado_anual_label, 'cobrado anualmente — R$ 249/ano')
        self.assertEqual(worship.cobrado_anual_label, 'cobrado anualmente — R$ 599/ano')

    def test_individual_limita_integrante_e_banda(self):
        from db import create_user, create_band, update_assinatura
        from monetizacao import PLANO_INDIVIDUAL, STATUS_ATIVA, check_limite, pode_exportar_pdf

        uid = create_user('solouser', 'solo@test.com', 'senha1234567')
        band_id = create_band('Solo', '', uid)
        update_assinatura(band_id, plano=PLANO_INDIVIDUAL, status=STATUS_ATIVA)
        band = {'id': band_id, 'owner_id': uid}
        self.assertTrue(check_limite(band, 'musica'))
        self.assertTrue(check_limite(band, 'setlist'))
        self.assertTrue(pode_exportar_pdf(band_id))
        self.assertFalse(check_limite(band, 'integrante'))
        self.assertFalse(check_limite(band, 'banda'))


if __name__ == '__main__':
    unittest.main()