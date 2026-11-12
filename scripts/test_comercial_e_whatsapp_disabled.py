#!/usr/bin/env python3
"""Testes de validação: WhatsApp desativado e melhorias comerciais de alta conversão."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long!!"
os.environ["FLASK_ENV"] = "development"
os.environ["WHATSAPP_NOTIFICATIONS_ENABLED"] = "0"
os.environ["SETSYNC_CANONICAL_URL"] = ""

import app as flask_app
import db
import whatsapp_config
import whatsapp_service
from blueprints.assinatura import _ensure_banda_para_pro


class ComercialEWhatsappTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False

    def test_whatsapp_desativado(self):
        """Garante que as notificações e integrações do WhatsApp estão desativadas."""
        self.assertFalse(whatsapp_config.whatsapp_notifications_enabled())
        self.assertFalse(whatsapp_service.is_configured())

    def test_planos_template_comercial(self):
        """Garante que a página de planos exibe os 3 planos comerciais e garantias."""
        with flask_app.app.test_client() as client:
            user_id = db.create_user("musico_teste", "musico@teste.com", "senha123", display_name="Músico Teste")
            with client.session_transaction() as sess:
                sess["user_id"] = user_id
                sess["username"] = "musico_teste"
                sess["display_name"] = "Músico Teste"

            res = client.get("/assinatura/planos")
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            # Verifica se os três planos comerciais estão presentes
            self.assertIn("Individual", html)
            self.assertIn("Pro", html)
            self.assertIn("Worship", html)

            # Verifica elementos de alta conversão
            self.assertTrue("Garantia Blindada de 7 Dias" in html or "7 dias" in html)
            self.assertIn("Mercado Pago", html)
            self.assertTrue("Mais Vendido" in html or "Recomendado" in html)

            # Verifica que o botão flutuante de zap NÃO aparece quando zap está desativado
            self.assertNotIn('class="wa-floating-btn"', html)

    def test_worship_cria_banda_automaticamente(self):
        """Garante que o checkout do Worship garante criação automática da banda se o usuário não tiver."""
        user_id = db.create_user("pastor_teste", "pastor@igreja.com", "senha123", display_name="Pastor Teste")
        bandas_antes = db.get_user_bands(user_id)
        self.assertEqual(len(bandas_antes), 0)

        banda = _ensure_banda_para_pro(user_id)
        self.assertIsNotNone(banda)

        bandas_depois = db.get_user_bands(user_id)
        self.assertGreaterEqual(len(bandas_depois), 1)
        self.assertIn(banda["id"], [b["id"] for b in bandas_depois])


if __name__ == "__main__":
    unittest.main()
