"""Testes da proteção anti-spam no cadastro."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class SignupGuardUnitTest(unittest.TestCase):
    def test_gibberish_detects_known_bots(self):
        from signup_guard import looks_like_gibberish

        self.assertTrue(looks_like_gibberish("nqfnfmnzuq"))
        self.assertTrue(looks_like_gibberish("rhznzdzgoz"))
        self.assertTrue(looks_like_gibberish("myqogitoqp"))
        self.assertTrue(looks_like_gibberish("grnmyqhpfm"))

    def test_gibberish_allows_normal_names(self):
        from signup_guard import looks_like_gibberish

        self.assertFalse(looks_like_gibberish("amanda"))
        self.assertFalse(looks_like_gibberish("João Silva"))
        self.assertFalse(looks_like_gibberish("Marileide"))
        self.assertFalse(looks_like_gibberish("jacsonsilveira"))
        self.assertFalse(looks_like_gibberish("ab"))

    def test_blocked_domain(self):
        from signup_guard import is_blocked_email_domain

        self.assertTrue(is_blocked_email_domain("kkwrdgtz@immenseignite.info"))
        self.assertFalse(is_blocked_email_domain("pessoa@gmail.com"))

    def test_honeypot(self):
        from signup_guard import honeypot_tripped

        self.assertTrue(honeypot_tripped({"website": "http://spam"}))
        self.assertFalse(
            honeypot_tripped({"website": "", "company_url": "", "fax_number": ""})
        )

    def test_check_blocks_gibberish_pair(self):
        from signup_guard import check_signup_abuse

        with patch("security.check_rate_limit", return_value=True):
            with patch("signup_guard.signup_filled_too_fast", return_value=False):
                ok, msg, reason = check_signup_abuse(
                    username="nqfnfmnzuq",
                    display_name="rhznzdzgoz",
                    email="alguem@gmail.com",
                    form=MagicMock(get=lambda k, d="": ""),
                    remote_addr="1.2.3.4",
                )
        self.assertFalse(ok)
        self.assertEqual(reason, "gibberish")
        self.assertTrue(msg)

    def test_check_blocks_bad_domain(self):
        from signup_guard import check_signup_abuse

        with patch("security.check_rate_limit", return_value=True):
            with patch("signup_guard.signup_filled_too_fast", return_value=False):
                ok, _msg, reason = check_signup_abuse(
                    username="amanda",
                    display_name="Amanda Silva",
                    email="x@immenseignite.info",
                    form=MagicMock(get=lambda k, d="": ""),
                    remote_addr="1.2.3.4",
                )
        self.assertFalse(ok)
        self.assertEqual(reason, "email_domain")


if __name__ == "__main__":
    unittest.main()
