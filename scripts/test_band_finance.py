#!/usr/bin/env python3
"""Testes unitários — financeiro de bandas."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/band_finance_test.db'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'test-band-finance-key'


class BandFinanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db, create_user, create_band

        init_db()
        uid = create_user('band_fin', 'band.fin@test.com', 'pass', display_name='Fin')
        cls.user_id = uid
        cls.band_id = create_band('Banda Fin', '', uid)

    def test_enrich_event_finance(self):
        from band_finance import enrich_event_finance

        row = enrich_event_finance({
            'fee_total': 2000,
            'fee_transport_discount': 200,
            'fee_equipment_discount': 100,
            'fee_settled_at': '2026-06-01',
        })
        self.assertEqual(row['fee_net'], 1700.0)
        self.assertTrue(row['is_received'])

    def test_list_events_for_finance_sqlite(self):
        from models_agenda import create_band_event
        from models_band_finance import list_band_events_for_finance

        create_band_event(
            self.band_id,
            created_by=self.user_id,
            title='Show Junho',
            event_type='show',
            starts_at='2026-06-15 20:00:00',
            ends_at='2026-06-15 23:00:00',
            location='SP',
            notes='',
        )
        rows = list_band_events_for_finance(
            self.band_id, from_date='2026-06-01', to_date='2026-06-30',
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['title'], 'Show Junho')

    def test_build_report(self):
        from band_finance import build_band_finance_report

        report = build_band_finance_report(
            band={'id': self.band_id, 'name': 'Banda Fin'},
            events=[
                {
                    'id': 'e1', 'title': 'Show', 'event_type': 'show',
                    'starts_at': '2026-06-15 20:00:00',
                    'fee_total': 1500, 'fee_transport_discount': 0,
                    'fee_equipment_discount': 0, 'fee_settled_at': None,
                },
            ],
            bookings=[
                {
                    'hora_inicio': '14:00', 'hora_fim': '16:00',
                    'room_preco_hora': 80, 'studio_preco_hora': 70,
                },
            ],
            expenses=[{'valor': 50}],
            year=2026,
            month=6,
        )
        self.assertEqual(report['stats']['receita_confirmada'], 1500.0)
        self.assertEqual(report['stats']['recebido'], 0.0)
        self.assertEqual(report['stats']['custos_ensaio'], 160.0)
        self.assertEqual(report['stats']['despesas'], 50.0)
        self.assertEqual(report['stats']['liquido'], -210.0)


if __name__ == '__main__':
    unittest.main()
