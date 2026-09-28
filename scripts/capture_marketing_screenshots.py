#!/usr/bin/env python3
"""Captura screenshots de marketing (BR, gospel, financeiros) via Playwright."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from marketing_shots import (
    PACK_BR,
    PACK_ESTUDIO,
    PACK_GOSPEL,
    SHOT_ESTUDIO_FINANCE,
    SHOT_ESTUDIO_PAINEL,
    SHOT_FINANCE_BAND,
    SHOT_MODO_TOCAR,
    SHOT_SETLIST,
    live_shot_file,
    screenshots_live_dir,
    slot_for_date,
)

BASE_URL = os.environ.get("SCREENSHOT_BASE_URL", "https://unissono.app").rstrip("/")


def _load_seed_module():
    path = ROOT / "scripts" / "seed_marketing_screenshots.py"
    spec = importlib.util.spec_from_file_location("seed_marketing_screenshots", path)
    if not spec or not spec.loader:
        raise RuntimeError("seed_marketing_screenshots.py não encontrado")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _session_cookie_for_user(
    user_id: str, username: str, display_name: str = ""
) -> dict:
    """Cria cookie de sessão Flask assinado para o domínio do BASE_URL."""
    from app import app

    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = username
            sess["display_name"] = display_name or username
        c = client.get_cookie(cookie_name)
        if c is None:
            for item in getattr(client, "cookie_jar", []) or []:
                if getattr(item, "name", None) == cookie_name:
                    c = item
                    break
        if c is None:
            raise RuntimeError("Não foi possível criar cookie de sessão")
        host = urlparse(BASE_URL).hostname or "unissono.app"
        value = c.value if hasattr(c, "value") else str(c)
        return {
            "name": cookie_name,
            "value": value,
            "domain": host,
            "path": "/",
            "httpOnly": True,
            "secure": BASE_URL.startswith("https"),
            "sameSite": "Lax",
        }


def _authed_context(browser, info: dict, **ctx_kwargs):
    cookie = _session_cookie_for_user(
        info["owner_id"],
        info["username"],
        info.get("display") or info["username"],
    )
    ctx_kwargs.setdefault("ignore_https_errors", True)
    context = browser.new_context(**ctx_kwargs)
    context.add_cookies([cookie])
    return context


def _assert_logged_in(page, expected_path_part: str = "") -> None:
    url = page.url or ""
    if "/auth/login" in url:
        raise RuntimeError(f"Sessão inválida — redirecionou para login ({url})")
    if expected_path_part and expected_path_part not in url:
        print(f"  aviso: URL inesperada {url} (esperava {expected_path_part})")


def _save(
    page, pack: str, name: str, slot: int, *, selector: str | None = None
) -> Path:
    out = live_shot_file(pack, name, slot=slot)
    out.parent.mkdir(parents=True, exist_ok=True)
    candidates = []
    if selector:
        candidates.extend([s.strip() for s in selector.split(",") if s.strip()])
    candidates.extend(["#play-app", "main", "body"])
    last_err = None
    for sel in candidates:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=8_000)
            loc.screenshot(path=str(out), type="png")
            print(
                f"  OK {out} ({out.stat().st_size // 1024} KB) [{sel}] url={page.url}"
            )
            return out
        except Exception as exc:
            last_err = exc
            continue
    page.screenshot(path=str(out), type="png", full_page=True)
    print(
        f"  OK {out} ({out.stat().st_size // 1024} KB) [full_page] url={page.url} last={last_err}"
    )
    return out


def _dismiss_overlays(page) -> None:
    for sel in (
        'button:has-text("Pular")',
        'button:has-text("Entendi")',
        'button:has-text("Fechar")',
        'button:has-text("Continuar")',
        'button:has-text("Aceitar")',
        ".play-onboarding-skip",
        '[data-dismiss="onboarding"]',
        "#cookie-consent-accept",
        "button.cookie-accept",
    ):
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=400):
                btn.click(timeout=1000)
                page.wait_for_timeout(200)
        except Exception:
            pass


def capture_pack(browser, info: dict, pack: str, slot: int) -> None:
    context = _authed_context(
        browser,
        info,
        viewport={"width": 1440, "height": 900},
        device_scale_factor=2,
        color_scheme="dark",
        locale="pt-BR",
    )
    page = context.new_page()
    page.goto(
        f"{BASE_URL}/setlists/{info['setlist_id']}",
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_timeout(700)
    _dismiss_overlays(page)
    _assert_logged_in(page, "/setlists/")
    _save(page, pack, SHOT_SETLIST, slot, selector="main")

    mobile = _authed_context(
        browser,
        info,
        viewport={"width": 390, "height": 844},
        device_scale_factor=2,
        color_scheme="dark",
        is_mobile=True,
        has_touch=True,
        locale="pt-BR",
    )
    mp = mobile.new_page()
    mp.goto(
        f"{BASE_URL}/setlists/{info['setlist_id']}/tocar",
        wait_until="domcontentloaded",
        timeout=90_000,
    )
    mp.wait_for_timeout(2000)
    _dismiss_overlays(mp)
    _assert_logged_in(mp, "/tocar")
    _save(mp, pack, SHOT_MODO_TOCAR, slot, selector="#play-app, main, body")
    mobile.close()

    page.goto(
        f"{BASE_URL}/bands/{info['band_id']}/financeiro"
        f"?ano={info['year']}&mes={info['month']}",
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_timeout(700)
    _dismiss_overlays(page)
    _assert_logged_in(page, "/financeiro")
    _save(page, pack, SHOT_FINANCE_BAND, slot, selector="main")
    context.close()


def capture_studio(browser, info: dict, slot: int) -> None:
    context = _authed_context(
        browser,
        info,
        viewport={"width": 1440, "height": 900},
        device_scale_factor=2,
        color_scheme="dark",
        locale="pt-BR",
    )
    page = context.new_page()
    page.goto(
        f"{BASE_URL}/estudios/{info['studio_id']}/financeiro"
        f"?mes={info['month']}&ano={info['year']}",
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_timeout(800)
    _dismiss_overlays(page)
    _assert_logged_in(page, "/financeiro")
    _save(page, PACK_ESTUDIO, SHOT_ESTUDIO_FINANCE, slot, selector="main")

    mobile = _authed_context(
        browser,
        info,
        viewport={"width": 390, "height": 844},
        device_scale_factor=2,
        color_scheme="dark",
        is_mobile=True,
        has_touch=True,
        locale="pt-BR",
    )
    mp = mobile.new_page()
    mp.goto(
        f"{BASE_URL}/estudios/{info['studio_id']}/painel",
        wait_until="networkidle",
        timeout=90_000,
    )
    mp.wait_for_timeout(800)
    _dismiss_overlays(mp)
    _assert_logged_in(mp, "/painel")
    _save(mp, PACK_ESTUDIO, SHOT_ESTUDIO_PAINEL, slot, selector="main")
    mobile.close()
    context.close()


def mirror_today_aliases(slot: int) -> None:
    for pack, names in (
        (PACK_BR, (SHOT_MODO_TOCAR, SHOT_SETLIST, SHOT_FINANCE_BAND)),
        (PACK_GOSPEL, (SHOT_MODO_TOCAR, SHOT_SETLIST, SHOT_FINANCE_BAND)),
        (PACK_ESTUDIO, (SHOT_ESTUDIO_FINANCE, SHOT_ESTUDIO_PAINEL)),
    ):
        for name in names:
            src = live_shot_file(pack, name, slot=slot)
            if not src.is_file():
                continue
            dest = screenshots_live_dir() / pack / "current" / f"{name}.png"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)


def main(slot: int | None = None) -> int:
    from playwright.sync_api import sync_playwright

    seed_mod = _load_seed_module()
    slot = slot_for_date() if slot is None else int(slot)
    print(f"Seed slot {slot}…")
    info = seed_mod.main(slot)

    print(f"Capturando em {BASE_URL}…")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            capture_pack(browser, info["br"], PACK_BR, slot)
            capture_pack(browser, info["gospel"], PACK_GOSPEL, slot)
            capture_studio(browser, info["estudio"], slot)
        finally:
            browser.close()

    mirror_today_aliases(slot)
    print("Capturas concluídas.")
    return 0


if __name__ == "__main__":
    arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    raise SystemExit(main(arg))
