#!/usr/bin/env python3
"""Testes de persistência do consentimento de cookies (LGPD)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

test_db = os.path.join(tempfile.mkdtemp(), "test_cookie_consent.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-cookie-consent-key-min-32-chars!!"
os.environ["SETSYNC_CANONICAL_URL"] = ""
os.environ["WTF_CSRF_ENABLED"] = "false"
os.environ["META_PIXEL_ID"] = "914092528361106"

import db  # noqa: E402
from app import app as flask_app  # noqa: E402
from lgpd import COOKIE_CONSENT_MAX_AGE, COOKIE_CONSENT_NAME  # noqa: E402


class CookieConsentPersistenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        flask_app.config["TESTING"] = True
        flask_app.config["WTF_CSRF_ENABLED"] = False
        with flask_app.app_context():
            db.init_db()
            cls.user_id = db.create_user(
                "cookie_tester",
                "cookie_tester@example.com",
                "senha12345",
                display_name="Tester Cookies",
            )

    def test_accept_sets_persistent_cookie_and_persists_across_session_loss_login_logout(self):
        client = flask_app.test_client()

        # Primeiro acesso: banner precisa aparecer
        r_first = client.get("/auth/login")
        self.assertEqual(r_first.status_code, 200)
        self.assertIn("ss-cookie-banner", r_first.get_data(as_text=True))

        # Aceita cookies -> cookie persistente de 1 ano
        r_post = client.post("/api/cookie-consent", json={"choice": "accept"})
        self.assertEqual(r_post.status_code, 200)
        payload = r_post.get_json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["tracking"])
        self.assertEqual(payload["choice"], "accept")

        set_cookies = r_post.headers.getlist("Set-Cookie")
        consent_headers = [h for h in set_cookies if f"{COOKIE_CONSENT_NAME}=accept" in h]
        self.assertTrue(consent_headers, f"Set-Cookie ausente: {set_cookies}")
        header = consent_headers[0]
        self.assertIn(f"Max-Age={COOKIE_CONSENT_MAX_AGE}", header)
        self.assertIn("HttpOnly", header)
        self.assertIn("SameSite=Lax", header)
        self.assertIn("Path=/", header)

        # Página seguinte não exibe mais o banner e ativa tracking
        r_after = client.get("/auth/login")
        html_after = r_after.get_data(as_text=True)
        self.assertNotIn('id="ss-cookie-banner"', html_after)
        self.assertIn("fbevents.js", html_after)

        # Simula expiração/perda apenas do cookie de sessão (navegador reaberto / sessão expirada)
        with client.session_transaction() as sess:
            sess.clear()
        r_reopen = client.get("/auth/login")
        self.assertNotIn('id="ss-cookie-banner"', r_reopen.get_data(as_text=True))

        # Login (que chama session.clear()) preserva o consentimento
        r_login = client.post(
            "/auth/login",
            data={"username": "cookie_tester", "password": "senha12345"},
            follow_redirects=True,
        )
        self.assertEqual(r_login.status_code, 200)
        self.assertNotIn('id="ss-cookie-banner"', r_login.get_data(as_text=True))

        # Logout (que chama session.clear()) também não volta a pedir
        r_logout = client.post("/auth/logout", follow_redirects=True)
        self.assertEqual(r_logout.status_code, 200)
        self.assertNotIn('id="ss-cookie-banner"', r_logout.get_data(as_text=True))

    def test_essential_or_reject_persists_without_tracking(self):
        for choice in ("essential", "reject"):
            with self.subTest(choice=choice):
                client = flask_app.test_client()
                r_post = client.post("/api/cookie-consent", json={"choice": choice})
                self.assertEqual(r_post.status_code, 200)
                data = r_post.get_json()
                self.assertTrue(data["ok"])
                self.assertFalse(data["tracking"])
                self.assertEqual(data["choice"], "essential")

                set_cookies = r_post.headers.getlist("Set-Cookie")
                self.assertTrue(
                    any(f"{COOKIE_CONSENT_NAME}=essential" in h for h in set_cookies),
                    set_cookies,
                )

                # Mesmo limpando a sessão, não pede de novo e não carrega tracking
                with client.session_transaction() as sess:
                    sess.clear()
                r_page = client.get("/auth/login")
                html = r_page.get_data(as_text=True)
                self.assertNotIn('id="ss-cookie-banner"', html)
                self.assertNotIn("fbevents.js", html)

    def test_invalid_choice_returns_400(self):
        client = flask_app.test_client()
        resp = client.post("/api/cookie-consent", json={"choice": "invalid"})
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
