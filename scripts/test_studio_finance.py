#!/usr/bin/env python3
"""Testes unitários — financeiro de estúdios."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/studio_finance_test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-min-32-chars-long!!'
os.environ['FLASK_ENV'] = 'development'


class StudioFinanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db
        init_db()

    def test_booking_duration_hours(self):
        from studio_finance import booking_duration_hours

        self.assertEqual(booking_duration_hours('10:00', '12:30'), 2.5)
        self.assertEqual(booking_duration_hours('09:00', '09:00'), 0.0)

    def test_estimate_and_charge(self):
        from studio_finance import booking_charge_amount, estimate_booking_value

        booking = {'hora_inicio': '14:00', 'hora_fim': '16:00', 'valor_cobrado': None}
        self.assertEqual(estimate_booking_value(booking, preco_hora=80), 160.0)
        booking['valor_cobrado'] = 120
        self.assertEqual(booking_charge_amount(booking, preco_hora=80), 120.0)

    def test_room_preco_overrides_studio(self):
        from studio_finance import enrich_booking_finance, resolve_booking_preco_hora

        booking = {
            'hora_inicio': '10:00', 'hora_fim': '12:00',
            'room_preco_hora': 120, 'valor_cobrado': None,
        }
        self.assertEqual(resolve_booking_preco_hora(booking, studio_preco_hora=80), 120.0)
        row = enrich_booking_finance(booking, studio_preco_hora=80)
        self.assertEqual(row['valor_estimado'], 240.0)

    def test_build_report_totals(self):
        from studio_finance import build_studio_finance_report

        studio = {'preco_hora': 100}
        bookings = [
            {
                'hora_inicio': '10:00', 'hora_fim': '12:00',
                'valor_cobrado': None, 'pago_em': '2026-06-01',
            },
            {
                'hora_inicio': '14:00', 'hora_fim': '15:00',
                'valor_cobrado': 50, 'pago_em': None,
            },
        ]
        expenses = [{'valor': 30}]
        report = build_studio_finance_report(
            studio=studio,
            bookings=bookings,
            expenses=expenses,
            year=2026,
            month=6,
        )
        self.assertEqual(report['stats']['receita_confirmada'], 250.0)
        self.assertEqual(report['stats']['recebido'], 200.0)
        self.assertEqual(report['stats']['a_receber'], 50.0)
        self.assertEqual(report['stats']['despesas'], 30.0)
        self.assertEqual(report['stats']['liquido'], 170.0)


if __name__ == '__main__':
    unittest.main()
