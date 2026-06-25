#!/usr/bin/env python3
"""Testes unitários — regras de agendamento de estúdios."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/studio_test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-min-32-chars-long!!'
os.environ['FLASK_ENV'] = 'development'


class StudioSchedulingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from db import init_db
        init_db()

    def test_intervals_overlap_adjacent_no_conflict(self):
        from studio_scheduling import intervals_overlap

        self.assertFalse(intervals_overlap('10:00', '11:00', '11:00', '12:00'))
        self.assertFalse(intervals_overlap('11:00', '12:00', '10:00', '11:00'))

    def test_intervals_overlap_partial(self):
        from studio_scheduling import intervals_overlap

        self.assertTrue(intervals_overlap('10:00', '12:00', '11:00', '13:00'))
        self.assertTrue(intervals_overlap('11:00', '12:00', '10:30', '11:30'))

    def test_slot_within_availability_recurring_and_exception(self):
        from studio_scheduling import slot_within_availability

        monday = date(2026, 6, 15)  # segunda
        rows = [
            {'dia_semana': 0, 'data_especifica': None, 'hora_inicio': '09:00', 'hora_fim': '18:00'},
            {'dia_semana': None, 'data_especifica': '2026-06-20', 'hora_inicio': '14:00', 'hora_fim': '16:00'},
        ]
        self.assertTrue(slot_within_availability(rows, monday, '10:00', '11:00'))
        self.assertFalse(slot_within_availability(rows, monday, '08:00', '09:30'))
        saturday = date(2026, 6, 20)
        self.assertTrue(slot_within_availability(rows, saturday, '14:30', '15:30'))
        self.assertFalse(slot_within_availability(rows, saturday, '10:00', '11:00'))

    def test_get_available_slots_ignores_pending(self):
        from studio_scheduling import get_available_slots

        target = date(2026, 6, 15)
        availability = [
            {'dia_semana': 0, 'data_especifica': None, 'hora_inicio': '10:00', 'hora_fim': '14:00'},
        ]
        bookings = [
            {'data': '2026-06-15', 'hora_inicio': '10:00', 'hora_fim': '11:00', 'status': 'pendente'},
            {'data': '2026-06-15', 'hora_inicio': '12:00', 'hora_fim': '13:00', 'status': 'confirmado'},
        ]
        blocks = [
            {'data': '2026-06-15', 'hora_inicio': '11:00', 'hora_fim': '12:00'},
        ]
        slots = get_available_slots(
            availability_rows=availability,
            bookings=bookings,
            blocks=blocks,
            target=target,
            slot_minutes=60,
        )
        starts = {s['inicio'] for s in slots}
        self.assertIn('10:00', starts)  # pendente não bloqueia
        self.assertNotIn('12:00', starts)  # confirmado bloqueia
        self.assertNotIn('11:00', starts)  # bloqueio

    def test_validate_booking_request_rejects_overlap(self):
        from studio_scheduling import validate_booking_request

        target = date(2026, 6, 15)
        availability = [
            {'dia_semana': 0, 'data_especifica': None, 'hora_inicio': '09:00', 'hora_fim': '18:00'},
        ]
        bookings = [
            {'id': 'b1', 'data': '2026-06-15', 'hora_inicio': '10:00', 'hora_fim': '11:00', 'status': 'confirmado'},
        ]
        ok, _ = validate_booking_request(
            availability_rows=availability,
            bookings=bookings,
            blocks=[],
            target=target,
            start='10:30',
            end='11:30',
        )
        self.assertFalse(ok)

    def test_integration_booking_and_cancel(self):
        from db import create_user, create_band
        from models_studio import (
            BOOKING_CANCELADO,
            BOOKING_CONFIRMADO,
            BOOKING_PENDENTE,
            add_room_block,
            create_booking,
            create_room,
            create_studio,
            replace_weekly_availability,
            update_booking_status,
            list_bookings_for_room,
        )
        from studio_scheduling import validate_booking_request, parse_booking_date

        owner = create_user('studioowner', 'owner@test.com', 'senha1234567')
        band_user = create_user('banduser', 'band@test.com', 'senha1234567')
        band_id = create_band('Banda Teste', '', band_user)

        studio_id = create_studio(owner, nome='Estúdio X', cidade='SP')
        room_id = create_room(studio_id, nome='Sala 1')
        replace_weekly_availability(room_id, [
            {'dia_semana': 0, 'hora_inicio': '10:00', 'hora_fim': '18:00'},
        ])

        target = parse_booking_date('2026-06-15')
        avail_rows = __import__('models_studio').list_room_availability(room_id)
        bookings = list_bookings_for_room(room_id)
        blocks = []

        ok, _ = validate_booking_request(
            availability_rows=avail_rows,
            bookings=bookings,
            blocks=blocks,
            target=target,
            start='10:00',
            end='11:00',
        )
        self.assertTrue(ok)

        bid1 = create_booking(
            room_id, band_id, band_user,
            data='2026-06-15', hora_inicio='10:00', hora_fim='11:00',
        )
        update_booking_status(bid1, BOOKING_CONFIRMADO)

        bookings = list_bookings_for_room(room_id)
        ok2, _ = validate_booking_request(
            availability_rows=avail_rows,
            bookings=bookings,
            blocks=blocks,
            target=target,
            start='10:00',
            end='11:00',
        )
        self.assertFalse(ok2)

        update_booking_status(bid1, BOOKING_CANCELADO)
        bookings = list_bookings_for_room(room_id)
        ok3, _ = validate_booking_request(
            availability_rows=avail_rows,
            bookings=bookings,
            blocks=blocks,
            target=target,
            start='10:00',
            end='11:00',
        )
        self.assertTrue(ok3)


if __name__ == '__main__':
    unittest.main()
