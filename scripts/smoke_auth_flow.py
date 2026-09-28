#!/usr/bin/env python3
"""Smoke autenticado: sessão → dashboard / coleção / bandas / agenda.

Uso:
  docker compose -f docker-compose.prod.yml exec web python3 scripts/smoke_auth_flow.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main() -> int:
    from flask.sessions import SecureCookieSessionInterface

    from app import app
    from db import get_user_by_username

    user = get_user_by_username("franklin") or get_user_by_username("showcase")
    if not user:
        print("FAIL: sem usuário franklin/showcase")
        return 1

    fails: list[str] = []
    paths = [
        ("/dashboard", None),  # superadmin pode ir p/ /admin/
        ("/cifras/minha-colecao", "coleção"),
        ("/bands/", "banda"),
        ("/agenda/minha", None),
    ]

    serializer = SecureCookieSessionInterface().get_signing_serializer(app)
    if not serializer:
        print("FAIL: sem serializer de sessão")
        return 1
    cookie_val = serializer.dumps({"_permanent": True, "user_id": user["id"]})

    with app.test_client() as client:
        # Domínio canônico + cookie Secure alinhado (produção).
        client.set_cookie(
            "session",
            cookie_val,
            domain="unissono.app",
            path="/",
            secure=True,
            httponly=True,
            samesite="Lax",
        )

        for path, must in paths:
            r = client.get(path, base_url="https://unissono.app", follow_redirects=True)
            body = r.get_data(as_text=True).lower()
            if r.status_code >= 400:
                fails.append(f"{path} status={r.status_code}")
            elif 'name="password"' in body:
                fails.append(f"{path} redirecionou para login")
            elif must and must not in body:
                fails.append(f"{path} sem '{must}'")
            else:
                print(f"OK {path} ({r.status_code})")

        # A11y: página de login sem sessão
        client.delete_cookie("session", domain="unissono.app", path="/")
        r = client.get("/auth/login", base_url="https://unissono.app")
        if "skip-to-content" not in r.get_data(as_text=True):
            fails.append("login sem skip-to-content")
        else:
            print("OK skip-to-content")

    if fails:
        print("FALHAS:")
        for f in fails:
            print(" -", f)
        return 1
    print("Smoke auth OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
