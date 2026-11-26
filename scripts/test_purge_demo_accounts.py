#!/usr/bin/env python3
"""Testes do script de remoção de contas, bandas e estúdios demo."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

test_db = os.path.join(tempfile.mkdtemp(), "test_purge_demo.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-purge-demo-key-min-32-chars!!"
os.environ["SETSYNC_CANONICAL_URL"] = ""
os.environ["WTF_CSRF_ENABLED"] = "false"

import db  # noqa: E402
from app import app as flask_app  # noqa: E402
from models_studio import create_booking, create_room, create_studio  # noqa: E402
from scripts.purge_demo_accounts import purge_demo_accounts  # noqa: E402


class PurgeDemoAccountsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        flask_app.config["TESTING"] = True
        with flask_app.app_context():
            db.init_db()
            cls.real_user_id = db.create_user(
                "musico_real",
                "musico.real@example.com",
                "senha12345",
                display_name="Músico Real",
            )
            cls.real_band_id = db.create_band("Banda Real", "Pop", cls.real_user_id)
            cls.real_cifra_id = db.create_cifra(
                titulo="Música Real",
                artista="Artista Real",
                tom_original="G",
                conteudo="[G]Verso real",
                band_id=cls.real_band_id,
                owner_user_id=cls.real_user_id,
            )

            cls.demo1_id = db.create_user(
                "showcase",
                "showcase@unissono.app",
                "senha12345",
                display_name="Showcase",
            )
            cls.demo2_id = db.create_user(
                "carlos_groove",
                "carlos.groove@unissono.app",
                "senha12345",
                display_name="Carlos Groove",
            )
            db.set_user_is_demo(cls.demo1_id, True)
            db.set_user_is_demo(cls.demo2_id, True)

            cls.demo_band_id = db.create_band("Banda Showcase", "Rock", cls.demo1_id)
            db.create_cifra(
                titulo="Música Demo",
                artista="Artista Demo",
                tom_original="C",
                conteudo="[C]Verso demo",
                band_id=cls.demo_band_id,
                owner_user_id=cls.demo1_id,
            )
            cls.demo_studio_id = create_studio(
                cls.demo2_id,
                nome="Estúdio Demo Groove",
                cidade="Fortaleza",
            )
            room_id = create_room(cls.demo_studio_id, nome="Sala A", preco_hora=80.0)
            create_booking(
                room_id,
                cls.demo_band_id,
                cls.demo1_id,
                data="2026-12-01",
                hora_inicio="19:00",
                hora_fim="21:00",
            )

    def test_dry_run_apply_and_idempotency(self):
        with flask_app.app_context():
            dry = purge_demo_accounts(apply=False)
            self.assertFalse(dry["apply"])
            self.assertEqual(set(dry["demo_users"]), {"showcase", "carlos_groove"})
            self.assertEqual(dry["demo_bands"], ["Banda Showcase"])
            self.assertEqual(dry["demo_studios"], ["Estúdio Demo Groove"])
            self.assertEqual(dry["deleted_users"], 0)

            res = purge_demo_accounts(apply=True)
            self.assertTrue(res["apply"])
            self.assertEqual(res["deleted_users"], 2)
            self.assertEqual(res["deleted_bands"], 1)
            self.assertEqual(res["deleted_studios"], 1)

            # Dados reais 100% preservados
            self.assertIsNotNone(db.get_user(self.real_user_id))
            self.assertIsNotNone(db.get_band(self.real_band_id))
            self.assertIsNotNone(db.get_cifra(self.real_cifra_id))

            # Demos removidos
            self.assertIsNone(db.get_user(self.demo1_id))
            self.assertIsNone(db.get_user(self.demo2_id))
            self.assertIsNone(db.get_band(self.demo_band_id))

            # Segunda execução idempotente
            again = purge_demo_accounts(apply=True)
            self.assertEqual(again["deleted_users"], 0)
            self.assertEqual(again["deleted_bands"], 0)
            self.assertEqual(again["deleted_studios"], 0)


if __name__ == "__main__":
    unittest.main()
