#!/usr/bin/env python3
"""Testes de instrumentos no perfil do usuário."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mktemp(suffix=".db")}'


class UserInstrumentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import create_user, get_user_by_username, init_db

        init_db()
        create_user('inst_tester', 'inst@test.com', 'secret')
        cls.user_id = get_user_by_username('inst_tester')['id']

    def test_catalog_has_common_instruments(self):
        from user_instruments import instrument_catalog

        ids = {item['id'] for item in instrument_catalog()}
        self.assertIn('guitarra', ids)
        self.assertIn('vocal', ids)
        self.assertIn('bateria', ids)

    def test_normalize_dedupes_and_filters(self):
        from user_instruments import normalize_instrument_ids

        out = normalize_instrument_ids(['guitarra', 'GUITARRA', 'invalid', 'baixo', ''])
        self.assertEqual(out, ['guitarra', 'baixo'])

    def test_set_and_list_preserves_order(self):
        from user_instruments import list_user_instruments, set_user_instruments

        set_user_instruments(self.user_id, ['baixo', 'vocal', 'guitarra'])
        items = list_user_instruments(self.user_id)
        self.assertEqual([i['id'] for i in items], ['baixo', 'vocal', 'guitarra'])
        self.assertEqual(items[0]['label'], 'Contrabaixo 4 cordas')

    def test_enrich_members(self):
        from user_instruments import enrich_members_with_instruments, set_user_instruments

        set_user_instruments(self.user_id, ['baixo', 'vocal', 'guitarra'])
        members = [{'id': self.user_id, 'email': 'inst@test.com'}]
        enrich_members_with_instruments(members)
        self.assertTrue(members[0]['instruments_label'])
        self.assertEqual(len(members[0]['instruments']), 3)


if __name__ == '__main__':
    unittest.main()
