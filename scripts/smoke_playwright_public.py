#!/usr/bin/env python3
"""Smoke Playwright: home, health, login page, planos (sem login).

Uso:
  SCREENSHOT_BASE_URL=https://unissono.app python3 scripts/smoke_playwright_public.py
  # ou contra o container local:
  SCREENSHOT_BASE_URL=http://127.0.0.1:5001 python3 scripts/smoke_playwright_public.py
"""

from __future__ import annotations

import os
import sys

BASE = (os.environ.get("SCREENSHOT_BASE_URL") or "http://127.0.0.1:5001").rstrip("/")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERRO: playwright não instalado")
        return 1

    fails: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        for path, must_contain in (
            ("/health", "ok"),
            ("/", "Uníssono"),
            ("/auth/login", "Entrar"),
            ("/auth/register", "Criar"),
            ("/assinatura/planos", "Pro"),
        ):
            url = BASE + path
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                status = resp.status if resp else 0
                body = page.content()
                if status >= 400:
                    fails.append(f"{path} status={status}")
                elif must_contain.lower() not in body.lower() and path != "/health":
                    # /health pode ser JSON puro
                    if path == "/health":
                        text = page.inner_text("body")
                        if "ok" not in text.lower() and '"status"' not in text.lower():
                            fails.append(f"{path} sem ok")
                    else:
                        fails.append(f"{path} sem texto '{must_contain}'")
                else:
                    print(f"OK {path} ({status})")
            except Exception as exc:
                fails.append(f"{path}: {exc}")
        # A11y smoke: skip link present on home
        page.goto(BASE + "/", wait_until="domcontentloaded", timeout=30000)
        if not page.query_selector("a.skip-to-content"):
            fails.append("home sem skip-to-content")
        else:
            print("OK skip-to-content")
        browser.close()

    if fails:
        print("FALHAS:")
        for f in fails:
            print(" -", f)
        return 1
    print("Smoke público OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
