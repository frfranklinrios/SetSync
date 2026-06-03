#!/usr/bin/env python3
"""Testa login por e-mail e por usuário."""
from __future__ import annotations

import sys
import tempfile
import os

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

from db import init_db, create_user, get_user_by_login, verify_password  # noqa: E402


def main():
    init_db()
    uid = create_user("franklin", "Franklin@Example.COM", "senha123", display_name="Franklin")
    assert uid, "create_user falhou"

    by_user = get_user_by_login("franklin")
    assert by_user and by_user["id"] == uid

    by_email = get_user_by_login("franklin@example.com")
    assert by_email and by_email["id"] == uid, by_email

    by_email_mixed = get_user_by_login("  Franklin@Example.COM  ")
    assert by_email_mixed and by_email_mixed["id"] == uid

    assert verify_password(uid, "senha123")
    assert get_user_by_login("outro@email.com") is None

    print("ok: test_login_email")


if __name__ == "__main__":
    main()
