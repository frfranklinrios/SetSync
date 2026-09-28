"""Smoke do Comando do show / pool de freela."""

from __future__ import annotations

import unittest


class ShowCommandImportTest(unittest.TestCase):
    def test_imports(self):
        from show_command import build_show_command_cards
        from models_band_team import list_band_freela_pool
        self.assertTrue(callable(build_show_command_cards))
        self.assertTrue(callable(list_band_freela_pool))

    def test_agenda_routes_registered(self):
        from app import app
        rules = {r.endpoint for r in app.url_map.iter_rules()}
        self.assertIn('agenda.comando', rules)
        self.assertIn('agenda.invite_from_pool', rules)
        self.assertIn('agenda.respond_guest_token', rules)


if __name__ == '__main__':
    unittest.main()
