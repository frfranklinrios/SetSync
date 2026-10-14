"""Smoke do Comando do show / pool de freela."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/show_command_test.db"
os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-show-command-key-32-chars!!"


class ShowCommandImportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()

    def test_imports(self):
        from models_band_team import list_band_freela_pool
        from show_command import build_show_command_cards

        self.assertTrue(callable(build_show_command_cards))
        self.assertTrue(callable(list_band_freela_pool))

    def test_agenda_routes_registered(self):
        from app import app

        rules = {r.endpoint for r in app.url_map.iter_rules()}
        self.assertIn("agenda.comando", rules)
        self.assertIn("agenda.invite_from_pool", rules)
        self.assertIn("agenda.respond_guest_token", rules)


if __name__ == "__main__":
    unittest.main()
