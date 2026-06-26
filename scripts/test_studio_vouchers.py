#!/usr/bin/env python3
"""Testes de vouchers para conta de estúdio."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import timedelta
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-min-32-chars-long!!'
os.environ['FLASK_ENV'] = 'development'


class StudioVouchersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db
        init_db()

    def _criar_dono_estudio(self, username: str):
        from db import create_user
        from models_studio import create_studio

        uid = create_user(username, f'{username}@test.com', 'senha1234567', display_name=username)
        create_studio(uid, nome=f'Estúdio {username}', cidade='Fortaleza')
        return uid

    def test_criar_e_resgatar_voucher_estudio(self):
        from db import create_user, create_voucher
        from monetizacao import studio_tem_premium, PLANO_ESTUDIO_PREMIUM
        from models_studio import get_studio_subscription
        from vouchers import (
            VOUCHER_DESTINO_ESTUDIO,
            resgatar_voucher_estudio,
            voucher_destino,
        )

        admin_id = create_user('adminv', 'adminv@test.com', 'senha1234567')
        codigo = 'ESTUDIO-TEST01'
        create_voucher(
            codigo=codigo,
            plano=PLANO_ESTUDIO_PREMIUM,
            dias=30,
            criado_por_id=admin_id,
            destino=VOUCHER_DESTINO_ESTUDIO,
        )
        uid = self._criar_dono_estudio('dono1')
        ok, msg, info = resgatar_voucher_estudio(codigo, uid, 'Dono 1')
        self.assertTrue(ok, msg)
        self.assertEqual(info['destino'], VOUCHER_DESTINO_ESTUDIO)
        self.assertTrue(studio_tem_premium(uid))
        sub = get_studio_subscription(uid)
        self.assertEqual(sub['plano'], PLANO_ESTUDIO_PREMIUM)
        self.assertEqual(sub['status'], 'voucher')

    def test_nao_resgata_duas_vezes(self):
        from db import create_user, create_voucher
        from monetizacao import PLANO_ESTUDIO_PREMIUM
        from vouchers import VOUCHER_DESTINO_ESTUDIO, resgatar_voucher_estudio

        admin_id = create_user('adminv2', 'adminv2@test.com', 'senha1234567')
        codigo = 'ESTUDIO-TEST02'
        create_voucher(
            codigo=codigo,
            plano=PLANO_ESTUDIO_PREMIUM,
            dias=15,
            criado_por_id=admin_id,
            destino=VOUCHER_DESTINO_ESTUDIO,
        )
        uid = self._criar_dono_estudio('dono2')
        self.assertTrue(resgatar_voucher_estudio(codigo, uid, 'Dono 2')[0])
        ok, msg, _ = resgatar_voucher_estudio(codigo, uid, 'Dono 2')
        self.assertFalse(ok)
        self.assertIn('já utilizou', msg.lower())

    def test_voucher_banda_rejeitado_no_fluxo_estudio(self):
        from db import create_user, create_voucher, get_voucher_by_codigo
        from monetizacao import PLANO_PRO
        from vouchers import validar_resgate_voucher_estudio, voucher_destino

        admin_id = create_user('adminv3', 'adminv3@test.com', 'senha1234567')
        codigo = 'BANDA-TEST01'
        create_voucher(codigo=codigo, plano=PLANO_PRO, dias=30, criado_por_id=admin_id)
        voucher = get_voucher_by_codigo(codigo)
        self.assertEqual(voucher_destino(voucher), 'banda')
        uid = self._criar_dono_estudio('dono3')
        ok, msg = validar_resgate_voucher_estudio(codigo, uid)
        self.assertFalse(ok)
        self.assertIn('banda', msg.lower())

    def test_expira_voucher_estudio(self):
        from config import app_now_naive
        from db import create_user, create_voucher, get_voucher_by_codigo, insert_studio_voucher_uso
        from monetizacao import PLANO_ESTUDIO_PREMIUM, studio_tem_premium
        from models_studio import get_studio_subscription, update_studio_subscription, update_studio_subscription_trial
        from scheduler_jobs import verificar_studio_vouchers_vencidos
        from vouchers import STATUS_VOUCHER

        admin_id = create_user('adminv4', 'adminv4@test.com', 'senha1234567')
        codigo = 'ESTUDIO-EXP01'
        create_voucher(
            codigo=codigo,
            plano=PLANO_ESTUDIO_PREMIUM,
            dias=7,
            criado_por_id=admin_id,
            destino='estudio',
        )
        uid = self._criar_dono_estudio('dono4')
        voucher = get_voucher_by_codigo(codigo)
        ontem = app_now_naive() - timedelta(days=1)
        inicio_trial = ontem - timedelta(days=31)
        update_studio_subscription_trial(
            uid,
            trial_inicio=inicio_trial.strftime('%Y-%m-%d %H:%M:%S'),
            trial_fim=ontem.strftime('%Y-%m-%d %H:%M:%S'),
            trial_usado=1,
        )
        insert_studio_voucher_uso(
            voucher_id=voucher['id'],
            user_id=uid,
            usado_em=ontem,
            expira_em=ontem,
        )
        update_studio_subscription(
            uid,
            plano=PLANO_ESTUDIO_PREMIUM,
            status=STATUS_VOUCHER,
            data_proxima_cobranca=ontem.strftime('%Y-%m-%d %H:%M:%S'),
        )
        self.assertFalse(studio_tem_premium(uid))
        with patch('scheduler_jobs.send_voucher_expirado_email', return_value=True):
            verificar_studio_vouchers_vencidos()
        sub = get_studio_subscription(uid)
        self.assertEqual(sub['status'], 'expirado')
        self.assertEqual(sub['plano'], 'estudio_basico')
        self.assertFalse(studio_tem_premium(uid))


if __name__ == '__main__':
    unittest.main()
