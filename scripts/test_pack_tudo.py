#!/usr/bin/env python3
"""Pacote «tudo»: clone setlist, NPS aha, filas admin."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/pack_tudo_test.db"
os.environ["SECRET_KEY"] = "test-pack-tudo-key-min-32-chars!!!!"
os.environ["FLASK_ENV"] = "development"
os.environ["WTF_CSRF_ENABLED"] = "false"


class PackTudoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db

        init_db()

    def test_clone_setlist_and_suggest(self):
        from db import create_band, create_cifra, create_user
        from models_agenda import create_band_event
        from models_setlist import (
            add_cifra_to_setlist,
            clone_setlist,
            create_setlist,
            find_suggestable_setlist,
            get_setlist_cifras,
        )

        uid = create_user("cloneu", "cloneu@test.com", "senha1234567")
        band_id = create_band("Banda Clone", "desc", uid)
        cid = create_cifra(
            band_id, "Musica A", "Artist", "C", "C G Am F", owner_user_id=uid
        )
        sid = create_setlist(band_id, "Repertório.show")
        add_cifra_to_setlist(sid, cid)
        create_band_event(
            band_id,
            title="Show antigo",
            event_type="show",
            starts_at="2024-01-01 20:00:00",
            ends_at=None,
            location=None,
            location_lat=None,
            location_lng=None,
            location_place_id=None,
            notes=None,
            setlist_id=sid,
            created_by=uid,
        )
        suggested = find_suggestable_setlist(band_id)
        self.assertIsNotNone(suggested)
        self.assertEqual(int(suggested["id"]), int(sid))
        self.assertEqual(int(suggested["n_songs"]), 1)

        new_id = clone_setlist(sid, name="Show novo (cópia)")
        self.assertIsNotNone(new_id)
        self.assertNotEqual(int(new_id), int(sid))
        self.assertEqual(len(get_setlist_cifras(new_id)), 1)

    def test_nps_after_play(self):
        from db import (
            create_user,
            get_user,
            mark_user_play_mode_used,
            user_should_see_nps,
        )

        uid = create_user("npsplay", "npsplay@test.com", "senha1234567")
        self.assertFalse(user_should_see_nps(uid))
        mark_user_play_mode_used(uid)
        self.assertTrue(get_user(uid).get("play_mode_used"))
        self.assertTrue(user_should_see_nps(uid))

    def test_engagement_queues_keys(self):
        from admin_dashboard import engagement_action_queues

        q = engagement_action_queues(limit=3)
        for key in (
            "solo_activated",
            "bands_no_events",
            "shows_no_scale",
            "trials_churned",
            "scale_champions",
        ):
            self.assertIn(key, q)


if __name__ == "__main__":
    unittest.main()
