#!/usr/bin/env python3
"""Smoke de UI: clica links/botões críticos e detecta 500 ou traceback."""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Servidor embutido: evita redirect canônico do Gunicorn (localhost → setsync.com.br).
os.environ.setdefault("SESSION_COOKIE_SECURE", "0")
os.environ["SETSYNC_CANONICAL_URL"] = ""

from app import app  # noqa: E402
from db import get_band_cifras, get_user_bands, get_user_by_username  # noqa: E402
from models_setlist import get_band_setlists  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SMOKE_HOST = "127.0.0.1"
SMOKE_PORT = int(os.getenv("QA_SMOKE_PORT", "5099"))
BASE = f"http://{SMOKE_HOST}:{SMOKE_PORT}"

errors: list[str] = []
actions = 0
_server_ready = threading.Event()


def _run_smoke_server() -> None:
    _server_ready.set()
    app.run(host=SMOKE_HOST, port=SMOKE_PORT, threaded=True, use_reloader=False)


def start_smoke_server() -> None:
    thread = threading.Thread(target=_run_smoke_server, daemon=True)
    thread.start()
    if not _server_ready.wait(timeout=5):
        raise RuntimeError("servidor de smoke não iniciou")
    for _ in range(40):
        try:
            with app.test_client() as client:
                if client.get("/", base_url=BASE).status_code < 500:
                    return
        except OSError:
            pass
        time.sleep(0.15)
    raise RuntimeError(f"servidor de smoke não respondeu em {BASE}")


def get_session_cookie() -> dict | None:
    with app.test_client() as client:
        user = get_user_by_username("frfranklin.rios")
        if not user:
            return None
        with client.session_transaction() as sess:
            sess["user_id"] = user["id"]
            sess["_fresh"] = True
        client.get("/bands", base_url=BASE)
        for jar in client._cookies.values():
            items = jar.values() if hasattr(jar, "values") and not hasattr(jar, "key") else [jar]
            for cookie in items:
                if getattr(cookie, "key", None) == "session":
                    return {
                        "name": "session",
                        "value": cookie.value,
                        "domain": SMOKE_HOST,
                        "path": "/",
                    }
    return None


def check_page(page, label: str) -> None:
    global actions
    actions += 1
    body = page.content()
    if "Internal Server Error" in body:
        errors.append(f"500: {label}")
    if "Traceback (most recent call last)" in body:
        errors.append(f"traceback: {label}")
    if "/login" in page.url and any(x in label for x in ("edit", "setlists", "bands/")):
        errors.append(f"login inesperado: {label}")


def go(page, path: str, label: str | None = None) -> None:
    """Navega e valida a página; tolera abort por SW/recarregamento."""
    target = BASE + path
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            page.goto(target, wait_until="domcontentloaded", timeout=25000)
            break
        except Exception as exc:
            last_exc = exc
            msg = str(exc)
            if "ERR_ABORTED" in msg and path.split("?")[0] in page.url:
                break
            if attempt == 0 and "ERR_ABORTED" in msg:
                page.wait_for_timeout(400)
                continue
            raise
    else:
        if last_exc:
            raise last_exc
    check_page(page, label or path)


def safe(page, fn, label: str) -> None:
    try:
        fn()
    except Exception as exc:
        msg = str(exc)
        if "ERR_ABORTED" in msg:
            return
        errors.append(f"{label}: {type(exc).__name__}: {exc}")


def run_public(page) -> None:
    for path in ["/ajuda", "/guia", "/blog", "/igrejas", "/planos", "/assinatura/planos"]:
        safe(page, lambda p=path: page.goto(BASE + p, wait_until="domcontentloaded", timeout=20000), path)
        check_page(page, path)

    for link in page.locator("nav a[href^='/']").all()[:6]:
        href = link.get_attribute("href") or ""
        if href and "logout" not in href:
            safe(page, lambda h=href: page.goto(BASE + h, wait_until="domcontentloaded"), f"nav {href}")
            check_page(page, href)


def run_authenticated(page, bid: str, cid: str, sid: str) -> None:
    safe(page, lambda: go(page, f"/bands/{bid}", "banda"), "banda")
    safe(page, lambda: go(page, f"/cifras/{cid}", "cifra view"), "cifra view")

    for tab_id in ("tab-chordsheet-btn", "tab-cifra-btn", "tab-letra-btn"):
        if page.locator(f"#{tab_id}").count():
            safe(
                page,
                lambda tid=tab_id: (
                    page.locator(f"#{tid}").click(),
                    page.wait_for_timeout(600),
                ),
                tab_id,
            )
            check_page(page, tab_id)

    safe(page, lambda: go(page, f"/cifras/{cid}/edit?tab=chordsheet", "edit chordsheet"), "edit chordsheet")
    if page.locator("#btn-render").count():
        safe(page, lambda: page.locator("#btn-render").click(timeout=8000), "render")
        page.wait_for_timeout(2500)
        check_page(page, "after render")
        preview = page.locator("#preview")
        if preview.count():
            html = preview.inner_html()
            src = page.locator("#source").input_value() if page.locator("#source").count() else ""
            if src.strip() and "cs-chart" not in html and "Digite" not in html:
                errors.append("prévia chord sheet sem cs-chart após render")

    for tab in ("cifra", "letra"):
        safe(page, lambda t=tab: go(page, f"/cifras/{cid}/edit?tab={t}", f"edit {tab}"), f"edit {tab}")

    safe(page, lambda: go(page, f"/setlists/{sid}", "setlist"), "setlist")
    for path in (
        f"/setlists/{sid}/imprimir",
        f"/setlists/{sid}/imprimir?cols=2",
        f"/setlists/{sid}/imprimir?indice=1&cifras=1&letras=1&chordsheet=1",
    ):
        safe(page, lambda p=path: go(page, p, path), path)

    safe(page, lambda: go(page, "/ajuda#chord-sheet", "ajuda chord-sheet"), "ajuda chord-sheet")


def main() -> int:
    start_smoke_server()

    cookie = get_session_cookie()
    if not cookie:
        print("ERRO: não foi possível obter sessão de teste")
        return 1

    user = get_user_by_username("frfranklin.rios")
    bands = get_user_bands(user["id"])
    cid = get_band_cifras(bands[0]["id"])[0]["id"]
    sid = get_band_setlists(bands[0]["id"])[0]["id"]
    bid = bands[0]["id"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(service_workers="block")
        context.add_cookies([cookie])
        page = context.new_page()
        run_authenticated(page, bid, cid, sid)
        run_public(page)
        browser.close()

    print(f"Ações verificadas: {actions}")
    if errors:
        print("PROBLEMAS:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("OK — cliques críticos sem 500/traceback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
