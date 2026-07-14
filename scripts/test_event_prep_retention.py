#!/usr/bin/env python3
"""Testes — alertas de evento incompleto e métricas de retenção."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import timedelta
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/retention_test.db'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'test-retention-key'


class EventPrepRemindersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db, create_user, create_band, create_cifra, add_band_member
        from models_setlist import create_setlist
        from models_agenda import create_band_event
        from config import app_now_naive

        init_db()
        cls.owner_id = create_user(
            'prep_owner', 'prep.owner@test.com', 'pass', display_name='Owner',
        )
        cls.member_id = create_user(
            'prep_member', 'prep.member@test.com', 'pass', display_name='Member',
        )
        cls.band_id = create_band('Banda Prep', '', cls.owner_id)
        add_band_member(cls.band_id, cls.member_id, role='member')

        cls.cifra_id = create_cifra('Música', 'Artista', 'G', '[G] oi', cls.band_id)
        cls.setlist_empty_id = create_setlist(cls.band_id, 'Set vazio')
        cls.setlist_full_id = create_setlist(cls.band_id, 'Set cheio')

        starts = (app_now_naive() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        cls.incomplete_event_id = create_band_event(
            cls.band_id,
            title='Ensaio incompleto',
            event_type='ensaio',
            starts_at=starts,
            setlist_id=cls.setlist_empty_id,
            created_by=cls.owner_id,
        )
        cls.ready_event_id = create_band_event(
            cls.band_id,
            title='Ensaio pronto',
            event_type='ensaio',
            starts_at=starts,
            setlist_id=cls.setlist_full_id,
            created_by=cls.owner_id,
        )

    def test_gaps_empty_setlist_and_no_scale(self):
        from event_prep_reminders import event_prep_gaps
        from models_agenda import get_band_event

        event = get_band_event(self.incomplete_event_id)
        gaps = event_prep_gaps(event)
        self.assertTrue(gaps['empty_setlist'])
        self.assertTrue(gaps['no_scale'])
        self.assertTrue(gaps['has_gaps'])

    def test_send_notifies_editors_once(self):
        from event_prep_reminders import verificar_e_enviar_alertas_evento_incompleto
        from db import retention_was_sent

        with mock.patch('event_prep_reminders.create_notification') as notify:
            notify.return_value = 'n1'
            sent = verificar_e_enviar_alertas_evento_incompleto()
            self.assertGreaterEqual(sent, 1)
            recipients = {
                (call.kwargs.get('user_id') if call.kwargs else None)
                or (call.args[0] if call.args else None)
                for call in notify.call_args_list
            }
            self.assertIn(self.owner_id, recipients)
            self.assertNotIn(self.member_id, recipients)

            sent2 = verificar_e_enviar_alertas_evento_incompleto()
            self.assertEqual(sent2, 0)

        self.assertTrue(
            retention_was_sent(self.owner_id, f'prep_event:{self.incomplete_event_id}')
        )

    def test_no_gaps_when_ready(self):
        from event_prep_reminders import event_prep_gaps
        from models_setlist import add_cifra_to_setlist
        from models_agenda import set_event_assignments, get_band_event, respond_event_assignment

        add_cifra_to_setlist(self.setlist_full_id, self.cifra_id)
        set_event_assignments(
            self.ready_event_id,
            [{'user_id': self.owner_id, 'role_label': 'Guitarra'}],
            assigned_by=self.owner_id,
        )
        respond_event_assignment(self.ready_event_id, self.owner_id, accepted=True)

        gaps = event_prep_gaps(get_band_event(self.ready_event_id))
        self.assertFalse(gaps['has_gaps'], gaps)


class RetentionMetricsTest(unittest.TestCase):
    def test_metrics_shape(self):
        from retention_metrics import build_retention_metrics

        m = build_retention_metrics()
        self.assertIn('wau', m)
        self.assertIn('mau', m)
        self.assertIn('activation_d7', m)
        self.assertIn('trial_churn', m)
        self.assertIn('nps', m)
        self.assertIn('incomplete_events_7d', m)
        self.assertGreaterEqual(m['incomplete_events_7d'], 0)


if __name__ == '__main__':
    unittest.main()
