#!/usr/bin/env python3
"""Testes da estratégia comercial: Estúdios Parceiros Oficiais 100% Grátis."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/studio_partner_test.db"
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long!!"
os.environ["FLASK_ENV"] = "development"
os.environ["SETSYNC_CANONICAL_URL"] = ""

import app as flask_app
import db
import models_studio
import monetizacao


class StudioFreePartnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False

    def setUp(self):
        self.app = flask_app.app
        self.client = self.app.test_client()

    def _criar_dono_estudio(self, username: str):
        uid = db.create_user(
            username, f"{username}@test.com", "senha1234567", display_name=username
        )
        studio_id = models_studio.create_studio(
            uid, nome=f"Estúdio {username}", cidade="São Paulo"
        )
        return uid, studio_id

    def test_studio_room_limit_is_always_unlimited(self):
        """Donos de estúdio contam com salas ilimitadas sem barreiras de cobrança."""
        uid, studio_id = self._criar_dono_estudio("rockstar_rooms")

        # Cria 5 salas (anteriormente o básico limitava em 2 salas)
        for i in range(1, 6):
            self.assertTrue(monetizacao.check_studio_room_limit(uid))
            models_studio.create_room(studio_id, nome=f"Sala {i}", preco_hora=50.0)

        # Após 5 salas, a checagem continua permitindo novas salas
        self.assertTrue(monetizacao.check_studio_room_limit(uid))

    def test_studio_badge_ui_shows_official_partner(self):
        """O badge de plano deve exibir status de Parceiro Oficial sem aviso de trial expirado."""
        uid, _studio_id = self._criar_dono_estudio("som_gravacoes")
        badge = monetizacao.studio_plano_badge_ui(uid)

        self.assertTrue(badge["premium"])
        self.assertFalse(badge["trial_expirado"])
        self.assertIn("Parceiro Oficial", badge["label"])
        self.assertEqual(badge["badge"], "success")

    def test_studio_print_room_poster_route(self):
        """A rota /estudios/<studio_id>/cartaz-sala deve renderizar o cartaz A4 imprimível."""
        uid, studio_id = self._criar_dono_estudio("garage_sound")

        with self.client.session_transaction() as sess:
            sess["user_id"] = uid
            sess["username"] = "garage_sound"
            sess["display_name"] = "Garage Sound"

        res = self.client.get(f"/estudios/{studio_id}/cartaz-sala")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Cartaz da Sala de Ensaio", html)
        self.assertIn("Suas Cifras & Letras", html)
        self.assertIn("Aponte a câmera do seu celular aqui", html)
        self.assertIn(f"/estudios/{studio_id}/agendar-qr.png", html)

    def test_planos_page_shows_free_studios(self):
        """A página /assinatura/planos destaca estúdios 100% gratuitos."""
        uid, _studio_id = self._criar_dono_estudio("showcase_user")

        with self.client.session_transaction() as sess:
            sess["user_id"] = uid
            sess["username"] = "showcase_user"
            sess["display_name"] = "Showcase User"

        res = self.client.get("/assinatura/planos")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("100% Gratuito", html)
        self.assertIn("Cadastrar Estúdio Grátis", html)


if __name__ == "__main__":
    unittest.main()
