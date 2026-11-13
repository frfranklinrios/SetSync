"""Testes unitários do Gateway Roteador de Webhooks do WhatsApp (Uníssono + Finanças.tec)."""

from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_TMP_DIR = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long!!"
os.environ["FLASK_ENV"] = "development"
os.environ["WHATSAPP_NOTIFICATIONS_ENABLED"] = "0"
os.environ["SETSYNC_CANONICAL_URL"] = ""

import json
import unittest
from unittest.mock import MagicMock, patch

import db
db.init_db()

from blueprints.whatsapp_gateway import (
    classify_message,
    get_financas_phones,
    get_financas_webhook_url,
    get_routing_mode,
)


class TestWhatsAppGateway(unittest.TestCase):
    def setUp(self):
        if "FINANCAS_WHATSAPP_NUMBERS" in os.environ:
            del os.environ["FINANCAS_WHATSAPP_NUMBERS"]
        if "WHATSAPP_ROUTING_MODE" in os.environ:
            del os.environ["WHATSAPP_ROUTING_MODE"]

    def test_classify_financial_text_keywords(self):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": False, "id": "TEST1"},
                "message": {"conversation": "Gastei 45 no almoço hoje"},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_financas"])
        self.assertFalse(res["is_unissono"])
        self.assertEqual(res["sender"], "5511999998888")
        self.assertEqual(res["text"], "Gastei 45 no almoço hoje")

    def test_classify_financial_value_pattern(self):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": False, "id": "TEST2"},
                "message": {"extendedTextMessage": {"text": "35,90 padaria"}},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_financas"])
        self.assertIn("monetary_value_pattern", res["reasons_financas"])

    def test_classify_audio_media_goes_to_financas(self):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": False, "id": "TEST3"},
                "message": {"audioMessage": {"url": "https://media.test/audio.ogg"}},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_financas"])
        self.assertTrue(res["has_media"])
        self.assertIn("media_payload", res["reasons_financas"])

    def test_classify_image_receipt_media_goes_to_financas(self):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": False, "id": "TEST4"},
                "message": {"imageMessage": {"caption": "recibo almoço", "url": "https://media.test/recibo.jpg"}},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_financas"])
        self.assertTrue(res["has_media"])

    def test_classify_unissono_commands(self):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5585988881111@s.whatsapp.net", "fromMe": False, "id": "TEST5"},
                "message": {"conversation": "/setlist ensaio de sábado"},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_unissono"])
        self.assertFalse(res["is_financas"])
        self.assertTrue(any("unissono_kw" in r for r in res["reasons_unissono"]))

    def test_classify_from_me_flag(self):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": True, "id": "TEST6"},
                "message": {"conversation": "gastei 20 no uber"},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["from_me"])

    def test_known_financas_sender_override(self):
        os.environ["FINANCAS_WHATSAPP_NUMBERS"] = "5585912345678,5511987654321"
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5585912345678@s.whatsapp.net", "fromMe": False, "id": "TEST7"},
                "message": {"conversation": "olá tudo bem"},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_financas"])
        self.assertIn("known_financas_sender", res["reasons_financas"])

    def test_fanout_routing_mode(self):
        os.environ["WHATSAPP_ROUTING_MODE"] = "fanout"
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": False, "id": "TEST8"},
                "message": {"conversation": "qualquer mensagem neutra"},
            },
        }
        res = classify_message(payload)
        self.assertTrue(res["is_financas"])
        self.assertTrue(res["is_unissono"])


class TestWhatsAppGatewayFlask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()

    def test_gateway_status_endpoint(self):
        resp = self.client.get("/api/whatsapp/gateway/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("gateway"), "active")
        self.assertIn("financas_webhook_url", data)
        self.assertIn("metrics", data)

    @patch("blueprints.whatsapp_gateway._forward_to_financas")
    def test_gateway_webhook_post(self, mock_forward):
        payload = {
            "event": "messages.upsert",
            "instance": "setsync",
            "data": {
                "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": False, "id": "TEST_WEBHOOK"},
                "message": {"conversation": "paguei o condomínio 350"},
            },
        }
        resp = self.client.post(
            "/api/whatsapp/gateway",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "received")
        self.assertTrue(data.get("routed", {}).get("financas"))


if __name__ == "__main__":
    unittest.main()
