#!/usr/bin/env python3
"""Smoke UI: clica abas, botões e links críticos (Playwright + sessão Flask)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import os

os.environ.setdefault("SESSION_COOKIE_SECURE", "0")
os.environ["SETSYNC_CANONICAL_URL"] = ""

from app import app
from db import get_band_cifras, get_user_bands, get_user_by_username
from models_setlist import get_band_setlists
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"


def get_session_cookie() -> dict | None:
    with app.test_client() as c:
        u = get_user_by_username("frfranklin.rios")
        with c.session_transaction() as sess:
            sess["user_id"] = u["id"]
            sess["_fresh"] = True
        c.get("/bands")
        for jar in c._cookies.values():
            for cobj in jar.values():
                if cobj.key == "session":
                    return {
                        "name": "session",
                        "value": cobj.value,
                        "domain": "127.0.0.1",
                        "path": "/",
                    }
    return None


def main() -> int:
    errors: list[str] = []
    actions = 0

    cookie = get_session_cookie()
    if not cookie:
        print("ERRO: não foi possível obter cookie de sessão")
        return 1

    uid = get_user_by_username("frfranklin.rios")["id"]
    bid = get_user_bands(uid)[0]["id"]
    cid = get_band_cifras(bid)[0]["id"]
    sid = get_band_setlists(bid)[0]["id"]

    def check_page(page, label: str) -> None:
        nonlocal actions
        actions += 1
        body = page.content()
        if "Internal Server Error" in body:
            errors.append(f"500: {label}")
        if "Traceback (most recent call last)" in body:
            errors.append(f"traceback: {label}")

    def safe(page, fn, label: str) -> None:
        try:
            fn()
        except Exception as e:
            errors.append(f"{label}: {type(e).__name__}: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        ctx.add_cookies([cookie])
        page = ctx.new_page()

        def go(path: str) -> None:
            page.goto(BASE + path, wait_until="domcontentloaded", timeout=20000)
            check_page(page, path)

        safe(page, lambda: go(f"/bands/{bid}"), "band")

        safe(page, lambda: go(f"/cifras/{cid}"), "cifra view")
        for tab_id in ("tab-chordsheet-btn", "tab-cifra-btn", "tab-letra-btn"):
            safe(
                page,
                lambda tid=tab_id: (
                    page.locator(f"#{tid}").click(),
                    page.wait_for_timeout(600),
                    check_page(page, tid),
                ),
                tab_id,
            )

        safe(page, lambda: go(f"/cifras/{cid}/edit?tab=chordsheet"), "edit chordsheet")
        safe(page, lambda: page.locator("#btn-render").click(timeout=8000), "render")
        page.wait_for_timeout(2500)
        check_page(page, "after render")
        preview = page.locator("#preview")
        if preview.count() and preview.inner_text().strip() and not preview.locator(".cs-chart").count():
            errors.append("prévia chord sheet sem .cs-chart após render")

        safe(page, lambda: go(f"/cifras/{cid}/edit?tab=cifra"), "edit cifra")
        safe(page, lambda: go(f"/cifras/{cid}/edit?tab=letra"), "edit letra")

        safe(page, lambda: go(f"/setlists/{sid}"), "setlist")
        safe(page, lambda: go(f"/setlists/{sid}/imprimir"), "imprimir")
        safe(page, lambda: go("/ajuda"), "ajuda")
        safe(page, lambda: go("/guia"), "guia")

        browser.close()

    print(f"Ações verificadas: {actions}")
    if errors:
        print("PROBLEMAS:")
        for e in errors:
            print(" -", e)
        return 1
    print("OK — UI autenticada sem erros 500")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
