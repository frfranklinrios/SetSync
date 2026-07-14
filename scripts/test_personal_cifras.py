#!/usr/bin/env python3
"""Testes — coleção pessoal e compartilhamento de cifras."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/personal_cifras_test.db'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'test-personal-cifras-key'


class PersonalCifrasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db, create_user, create_band, update_assinatura
        from monetizacao import PLANO_PRO, STATUS_ATIVA

        init_db()
        cls.uid = create_user('pc_owner', 'pc.owner@test.com', 'pass', display_name='Owner')
        cls.friend = create_user('pc_friend', 'pc.friend@test.com', 'pass', display_name='Friend')
        cls.band_id = create_band('Banda PC', '', cls.uid)
        update_assinatura(cls.band_id, plano=PLANO_PRO, status=STATUS_ATIVA)

    def test_personal_create_and_share_user(self):
        from db import (
            create_personal_cifra,
            get_user_personal_cifras,
            share_cifra_with_user,
            user_can_access_cifra,
            get_cifra,
        )
        from monetizacao import user_pode_compartilhar_cifras

        cid = create_personal_cifra(self.uid, 'Song A', 'Artist', 'C', '[C] hello')
        cifra = get_cifra(cid)
        self.assertTrue(cifra.get('owner_user_id') == self.uid)
        self.assertIsNone(cifra.get('band_id'))
        self.assertEqual(len(get_user_personal_cifras(self.uid)), 1)
        self.assertTrue(user_pode_compartilhar_cifras(self.uid))
        self.assertTrue(share_cifra_with_user(cid, self.friend, self.uid))
        self.assertTrue(user_can_access_cifra(get_cifra(cid), self.friend))

    def test_share_to_band_copy(self):
        from db import create_personal_cifra, copy_cifra_to_band, get_band_cifras, get_cifra

        cid = create_personal_cifra(self.uid, 'Song B', 'Artist', 'G', '[G] yo')
        new_id = copy_cifra_to_band(get_cifra(cid), self.band_id, owner_user_id=self.uid)
        band_cifras = get_band_cifras(self.band_id)
        self.assertTrue(any(c['id'] == new_id for c in band_cifras))
        self.assertEqual(get_cifra(new_id)['band_id'], self.band_id)

    def test_free_user_cannot_share(self):
        from db import create_user, create_band
        from monetizacao import user_pode_compartilhar_cifras

        free = create_user('pc_free', 'pc.free@test.com', 'pass', display_name='Free')
        create_band('Banda Free', '', free)
        self.assertFalse(user_pode_compartilhar_cifras(free))


if __name__ == '__main__':
    unittest.main()
