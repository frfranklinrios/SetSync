"""Testes do fluxo freela/convidado externo."""

from __future__ import annotations

import unittest
from datetime import timedelta


class GuestScaleTokenTest(unittest.TestCase):
    def test_guest_token_roundtrip(self):
        from app import app
        from event_scale_tokens import make_guest_scale_token, verify_guest_scale_token

        with app.app_context():
            tok = make_guest_scale_token('evt-1', 'guest-9')
            parsed = verify_guest_scale_token(tok)
            self.assertEqual(parsed, ('evt-1', 'guest-9'))
            self.assertIsNone(verify_guest_scale_token('lixo'))
            self.assertIsNone(verify_guest_scale_token(None))

    def test_guest_token_distinct_from_member(self):
        from app import app
        from event_scale_tokens import (
            make_guest_scale_token,
            make_scale_response_token,
            verify_guest_scale_token,
            verify_scale_response_token,
        )

        with app.app_context():
            member = make_scale_response_token('e', 'u')
            guest = make_guest_scale_token('e', 'g')
            self.assertIsNone(verify_guest_scale_token(member))
            self.assertIsNone(verify_scale_response_token(guest))

    def test_declined_guest_skipped_in_settlement(self):
        from config import app_now_naive
        from db import create_band, create_user
        from event_fees import compute_night_settlement
        from models_agenda import create_band_event
        from models_band_team import (
            add_event_guest,
            list_event_guests,
            respond_event_guest,
            set_event_guest_fixed_fee,
        )

        uid = create_user('freela_t3', 'freela_t3@test.com', 'senha1234567', display_name='T')
        band_id = create_band('Freela Band T3', '', uid)
        starts = (app_now_naive() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        eid = create_band_event(
            band_id,
            title='Show T3',
            event_type='show',
            starts_at=starts,
            created_by=uid,
        )
        gid_ok = add_event_guest(eid, name='OK', phone='85999990000', role_label='Baixo', invited_by=uid)
        gid_no = add_event_guest(eid, name='NO', role_label='Guitar', invited_by=uid)
        respond_event_guest(gid_ok, accepted=True)
        respond_event_guest(gid_no, accepted=False)
        set_event_guest_fixed_fee(gid_ok, eid, 150)
        set_event_guest_fixed_fee(gid_no, eid, 200)

        event = {
            'fee_total': 1000,
            'fee_transport_discount': 0,
            'fee_equipment_discount': 0,
        }
        sett = compute_night_settlement(
            event,
            [],
            [],
            guests=list_event_guests(eid),
            event_expenses=[],
            fee_lines=None,
            name_for_user=lambda u: u or '',
            amount_overrides={},
        )
        guest_ids = {
            str(p.get('guest_id'))
            for p in (sett.get('fixed_payees') or [])
            if p.get('guest_id')
        }
        self.assertIn(str(gid_ok), guest_ids)
        self.assertNotIn(str(gid_no), guest_ids)


if __name__ == '__main__':
    unittest.main()
