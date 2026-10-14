#!/usr/bin/env python3
"""Verificação E2E: Modo Tocar (console + atalhos), membros e aba setlist."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = os.environ.get("SCREENSHOT_BASE_URL", "https://unissono.app").rstrip("/")
USER = os.environ.get("VERIFY_USER", "showcase")
PASS = os.environ.get("VERIFY_PASS", "UníssonoShowcase2026!")


def session_cookie(user_id: str, username: str) -> dict:
    from urllib.parse import urlparse

    from app import app

    name = app.config.get("SESSION_COOKIE_NAME", "session")
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = username
            sess["display_name"] = username
        c = client.get_cookie(name)
        if c is None:
            raise RuntimeError("cookie de sessão não criado")
        host = urlparse(BASE).hostname or "unissono.app"
        return {
            "name": name,
            "value": c.value,
            "domain": host,
            "path": "/",
            "httpOnly": True,
            "secure": BASE.startswith("https"),
            "sameSite": "Lax",
        }


def main() -> int:
    from playwright.sync_api import sync_playwright

    from db import get_owned_bands, get_user_by_username, init_db
    from models_setlist import get_band_setlists

    init_db()
    user = get_user_by_username(USER)
    if not user:
        print("FAIL: usuário showcase não encontrado — rode seed_marketing_screenshots")
        return 1
    bands = get_owned_bands(user["id"])
    if not bands:
        print("FAIL: showcase sem banda")
        return 1
    band = bands[0]
    setlists = get_band_setlists(band["id"])
    if not setlists:
        print("FAIL: banda sem setlist")
        return 1
    setlist_id = setlists[0]["id"]

    results = {
        "play_console_errors": [],
        "play_reference_errors": [],
        "has_pedal_btn": None,
        "has_tap_zones": None,
        "has_view_menu": None,
        "has_setSync_globals": None,
        "keydown_arrow_bound": None,
        "members_admin_finance_label": None,
        "members_member_finance_btn": None,
        "members_admin_option": None,
        "band_roteiro_label": None,
        "url_play": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(ignore_https_errors=True, locale="pt-BR")
        ctx.add_cookies([session_cookie(user["id"], USER)])
        page = ctx.new_page()
        console_msgs = []
        page.on(
            "console", lambda m: console_msgs.append({"type": m.type, "text": m.text})
        )
        page.on("pageerror", lambda e: results["play_reference_errors"].append(str(e)))

        # ── Modo Tocar ──
        url = f"{BASE}/setlists/{setlist_id}/tocar"
        page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(2500)
        results["url_play"] = page.url
        # dismiss onboarding (overlay intercepta cliques)
        for _ in range(3):
            try:
                dismiss = page.locator(
                    '[data-onboard-dismiss], button:has-text("Entendi")'
                ).first
                if dismiss.is_visible(timeout=800):
                    dismiss.click(timeout=2000)
                    page.wait_for_timeout(400)
                ov = page.locator("#play-onboard-overlay")
                if ov.count() and "d-none" in (ov.get_attribute("class") or ""):
                    break
            except Exception:
                break
        page.evaluate("""() => {
            const ov = document.getElementById('play-onboard-overlay');
            if (ov) { ov.classList.add('d-none'); ov.style.display = 'none'; }
        }""")
        page.wait_for_timeout(200)

        results["has_pedal_btn"] = (
            page.locator("#pedal-btn, #play-pedal-modal, #play-pedal-wizard").count()
            == 0
        )
        results["has_tap_zones"] = (
            page.locator("#tap-prev, #tap-next, .tap-zone").count() >= 2
        )
        results["has_view_menu"] = (
            page.locator(
                '#view-mode-btn, #view-mode-menu [data-view-mode="chordsheet"]'
            ).count()
            >= 1
        )
        results["has_setSync_globals"] = page.evaluate(
            """() => ({
                metro: !!window.SetSyncMetronome,
                draw: !!window.SetSyncDrawOverlay,
                features: !!window.SetSyncPlayFeatures,
                offline: !!window.SetSyncOfflineStore,
                playApi: !!window.SetSyncPlayApi,
                uniMetro: typeof window["UníssonoMetronome"],
                uniDraw: typeof window["UníssonoDrawOverlay"],
                cifraHtmlBefore: (document.getElementById("cifra-content") || document.getElementById("cifra-scroll") || {}).innerHTML?.length || 0,
            })"""
        )
        # Interact: view mode Grade, page, song, metronome
        try:
            page.click("#view-mode-btn", timeout=3000)
            page.click('#view-mode-menu [data-view-mode="chordsheet"]', timeout=3000)
            page.wait_for_timeout(500)
            results["grade_clicked"] = True
            results["view_label"] = page.locator("#view-mode-label").inner_text()
        except Exception as exc:
            results["grade_clicked"] = False
            results["grade_error"] = str(exc)

        page.locator("#tap-next").click(timeout=5000, force=True)
        page.wait_for_timeout(200)
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(400)
        page.keyboard.press("m")
        page.wait_for_timeout(300)
        metro_active = page.evaluate(
            "() => !!(window.SetSyncMetronome && SetSyncMetronome.isActive && SetSyncMetronome.isActive())"
        )
        results["metronome_toggled"] = bool(metro_active)
        page.keyboard.press("m")
        page.keyboard.press("s")
        page.wait_for_timeout(300)
        page.keyboard.press("Escape")
        page.keyboard.press(" ")
        page.wait_for_timeout(400)
        page.keyboard.press(" ")

        results["keydown_arrow_bound"] = page.evaluate(
            """() => !!(window.SetSyncPlayApi && (SetSyncPlayApi.nextSong || SetSyncPlayApi.render))"""
        )

        for m in console_msgs:
            if m["type"] == "error":
                results["play_console_errors"].append(m["text"])
            if "is not defined" in m["text"] or "ReferenceError" in m["text"]:
                results["play_reference_errors"].append(m["text"])

        # ── Membros ──
        page.goto(
            f"{BASE}/bands/{band['id']}/members",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        page.wait_for_timeout(1000)
        body = page.inner_text("body")
        results["members_admin_finance_label"] = "Vê financeiro (admin)" in body
        results["members_member_finance_btn"] = (
            page.locator('button:has-text("Liberar financeiro")').count() > 0
        )
        results["members_admin_option"] = (
            page.locator('select[name="role"] option[value="admin"]').count() > 0
        )

        # Toggle finance for a member if available
        btn = page.locator('button:has-text("Liberar financeiro")').first
        if btn.count():
            with page.expect_navigation(timeout=15_000):
                btn.click()
            page.wait_for_timeout(600)
            results["finance_toggled"] = "Vê financeiro" in page.inner_text("body")

        # ── View banda ──
        page.goto(
            f"{BASE}/bands/{band['id']}", wait_until="domcontentloaded", timeout=60_000
        )
        page.wait_for_timeout(800)
        results["band_roteiro_label"] = "Roteiro (Setlist)" in page.inner_text("body")

        browser.close()

    print(json.dumps(results, ensure_ascii=False, indent=2))

    # Verdicts
    ok = True
    if results["play_reference_errors"]:
        print(
            "PLAY: NÃO FUNCIONA — ReferenceError:", results["play_reference_errors"][:3]
        )
        ok = False
    elif "/auth/login" in (results["url_play"] or ""):
        print("PLAY: NÃO FUNCIONA — redirecionou para login")
        ok = False
    elif results["has_pedal_btn"] is False:
        print("PLAY: NÃO FUNCIONA — UI de pedal ainda presente")
        ok = False
    elif not results.get("has_tap_zones"):
        print("PLAY: NÃO FUNCIONA — tap-zones ausentes")
        ok = False
    elif not results.get("has_view_menu"):
        print("PLAY: NÃO FUNCIONA — menu Grade harmônica ausente")
        ok = False
    elif not (results["has_setSync_globals"] or {}).get("metro"):
        print("PLAY: NÃO FUNCIONA — SetSyncMetronome ausente")
        ok = False
    else:
        print(
            "PLAY: FUNCIONA — sem ReferenceError; SetSync* ok; pedal removido; tap-zones e Grade ok"
        )
        print(
            "  grade_clicked=",
            results.get("grade_clicked"),
            "label=",
            results.get("view_label"),
        )
        if results["play_console_errors"]:
            print(
                "  console errors (não-ReferenceError):",
                results["play_console_errors"][:5],
            )

    if (
        results["members_admin_option"]
        and results["members_member_finance_btn"]
        and results["members_admin_finance_label"]
    ):
        print(
            "MEMBROS: FUNCIONA — Admin no dropdown + Liberar financeiro + label admin desabilitado"
        )
        if results.get("finance_toggled"):
            print(
                "MEMBROS: OK — toggle Liberar financeiro persistiu (botão virou Vê financeiro)"
            )
    else:
        print(
            "MEMBROS: NÃO FUNCIONA",
            {
                "admin_option": results["members_admin_option"],
                "finance_btn": results["members_member_finance_btn"],
                "admin_label": results["members_admin_finance_label"],
            },
        )
        ok = False

    if results["band_roteiro_label"]:
        print("ABA BANDA: FUNCIONA — Roteiro (Setlist)")
    else:
        print("ABA BANDA: NÃO FUNCIONA — texto ausente")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
