#!/usr/bin/env python3
"""Testes do card de período / urgência da assinatura."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long!!"
os.environ["FLASK_ENV"] = "development"


class PeriodoAssinaturaUiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()

    def test_assinatura_ativa_com_cobranca_passada_nao_parece_gratis(self):
        from config import app_now_naive
        from db import create_band, create_user, update_assinatura
        from monetizacao import (
            PLANO_PRO,
            STATUS_ATIVA,
            get_assinatura_banda,
            periodo_assinatura_ui,
            plano_badge_ui,
        )

        uid = create_user(
            "planouifix", "planouifix@test.com", "senha1234567", display_name="P"
        )
        band_id = create_band("Banda Plano UI", "", uid)
        agora = app_now_naive()
        update_assinatura(
            band_id,
            plano=PLANO_PRO,
            status=STATUS_ATIVA,
            data_inicio=(agora - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S"),
            data_proxima_cobranca=(agora - timedelta(days=10)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            data_cancelamento=None,
        )
        a = get_assinatura_banda(band_id)
        periodo = periodo_assinatura_ui(a)
        ui = plano_badge_ui(band_id)

        self.assertEqual(periodo["tipo"], "assinatura")
        self.assertEqual(periodo["urgencia"], "atencao")
        self.assertNotEqual(periodo["urgencia"], "expirado")
        self.assertIn("ativa", periodo["texto_detalhe"].lower())
        self.assertNotIn("Renovau", periodo["texto_restante"])
        self.assertNotIn("Renovou há", periodo["texto_restante"])
        self.assertIn("pendente", periodo["texto_restante"].lower())
        self.assertEqual(ui["label_curto"], "Pro")
        self.assertTrue(ui["premium"])

    def test_assinatura_ativa_futura_ok(self):
        from config import app_now_naive
        from db import create_band, create_user, update_assinatura
        from monetizacao import (
            PLANO_PRO,
            STATUS_ATIVA,
            get_assinatura_banda,
            periodo_assinatura_ui,
        )

        uid = create_user(
            "planouifix2", "planouifix2@test.com", "senha1234567", display_name="P2"
        )
        band_id = create_band("Banda Plano UI 2", "", uid)
        agora = app_now_naive()
        update_assinatura(
            band_id,
            plano=PLANO_PRO,
            status=STATUS_ATIVA,
            data_inicio=agora.strftime("%Y-%m-%d %H:%M:%S"),
            data_proxima_cobranca=(agora + timedelta(days=25)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        periodo = periodo_assinatura_ui(get_assinatura_banda(band_id))
        self.assertEqual(periodo["urgencia"], "ok")
        self.assertIn("Próxima cobrança", periodo["texto_restante"])


if __name__ == "__main__":
    unittest.main()
