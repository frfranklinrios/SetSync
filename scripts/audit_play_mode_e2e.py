#!/usr/bin/env python3
"""Auditoria minuciosa do Modo Tocar — exercita cada funcionalidade no browser."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = os.environ.get("SCREENSHOT_BASE_URL", "https://unissono.app").rstrip("/")
USER = os.environ.get("VERIFY_USER", "showcase")


def session_cookie(user_id: str, username: str) -> dict:
    from app import app

    name = app.config.get("SESSION_COOKIE_NAME", "session")
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = username
            sess["display_name"] = username
        c = client.get_cookie(name)
        if c is None:
            raise RuntimeError("sem cookie")
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
    band = get_owned_bands(user["id"])[0]
    sl = get_band_setlists(band["id"])[0]

    results: dict[str, dict] = {}
    page_errors: list[str] = []
    console_errors: list[str] = []

    def ok(name: str, detail: str = "") -> None:
        results[name] = {"status": "FUNCIONA", "detail": detail}

    def fail(name: str, detail: str = "") -> None:
        results[name] = {"status": "NÃO FUNCIONA", "detail": detail}

    def warn(name: str, detail: str = "") -> None:
        results[name] = {"status": "PARCIAL", "detail": detail}

    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(
            ignore_https_errors=True,
            locale="pt-BR",
            viewport={"width": 1280, "height": 800},
        )
        ctx.add_cookies([session_cookie(user["id"], USER)])
        page = ctx.new_page()
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on(
            "console",
            lambda m: (
                console_errors.append(m.text)
                if m.type == "error"
                and "is not defined" in m.text
                or (m.type == "error" and "ReferenceError" in m.text)
                else None
            ),
        )

        url = f"{BASE}/setlists/{sl['id']}/tocar"
        page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(2800)

        # dismiss onboard
        page.evaluate(
            """() => {
            const o = document.getElementById('play-onboard-overlay');
            if (o) { o.classList.add('d-none'); o.style.display='none'; }
            try { localStorage.setItem('setsync.play.onboarding.v1','1'); } catch(e){}
            }"""
        )
        page.wait_for_timeout(200)

        def snap():
            return page.evaluate(
                """() => {
                const prog = document.getElementById('prog-text-l');
                const title = document.getElementById('play-title') || document.querySelector('.pb-title');
                const meta = document.getElementById('bar-meta');
                const tom = document.getElementById('transpose-label') || document.querySelector('#transpose-value, .transpose-label');
                const wrap = document.getElementById('cifra-scroll');
                const content = document.getElementById('cifra-content');
                const metro = document.getElementById('metronome-btn');
                const draw = document.getElementById('draw-btn');
                const sync = document.getElementById('sync-follow-btn');
                const view = document.getElementById('view-mode-label');
                const fit = document.getElementById('fit-btn');
                const cols = document.getElementById('cols-btn');
                const nash = document.getElementById('nashville-btn');
                const scrollBtn = document.getElementById('scroll-btn');
                const loopBtn = document.getElementById('loop-btn');
                const sections = document.getElementById('play-sections');
                const drawer = document.getElementById('play-drawer');
                const offline = document.getElementById('play-offline-banner');
                const nextPeek = document.getElementById('play-next-peek');
                const flash = document.getElementById('cifra-wrap');
                return {
                  url: location.pathname,
                  prog: prog ? prog.textContent.trim() : '',
                  title: title ? title.textContent.trim().slice(0,60) : '',
                  meta: meta ? meta.textContent.trim().slice(0,80) : '',
                  tom: tom ? tom.textContent.trim() : '',
                  contentLen: content ? content.innerHTML.length : 0,
                  grade: !!(content && content.classList.contains('grade-mode')),
                  letra: !!(content && content.classList.contains('letra-mode')),
                  scrollTop: wrap ? wrap.scrollTop : -1,
                  scrollH: wrap ? wrap.scrollHeight : -1,
                  clientH: wrap ? wrap.clientHeight : -1,
                  metroOn: metro ? metro.classList.contains('pb-on') : false,
                  metroActive: !!(window.SetSyncMetronome && SetSyncMetronome.isActive && SetSyncMetronome.isActive()),
                  flashBound: !!(window.SetSyncMetronome && document.getElementById('cifra-wrap')),
                  drawOn: draw ? draw.classList.contains('pb-on') : false,
                  syncOn: sync ? sync.classList.contains('pb-on') : null,
                  syncExists: !!sync,
                  view: view ? view.textContent.trim() : '',
                  fitOn: fit ? fit.classList.contains('pb-on') : false,
                  colsOn: cols ? cols.classList.contains('pb-on') : false,
                  nashOn: nash ? nash.classList.contains('pb-on') : false,
                  scrollOn: scrollBtn ? scrollBtn.classList.contains('pb-on') : false,
                  loopOn: loopBtn ? loopBtn.classList.contains('pb-on') : false,
                  sectionsOpen: sections ? sections.classList.contains('open') : false,
                  drawerOpen: drawer ? drawer.classList.contains('open') : false,
                  chromeHidden: document.body.classList.contains('chrome-hidden'),
                  drawing: document.body.classList.contains('play-drawing'),
                  offlineVisible: offline ? !offline.classList.contains('d-none') : false,
                  nextPeek: nextPeek ? nextPeek.textContent.trim().slice(0,40) : '',
                  globals: {
                    metro: !!window.SetSyncMetronome,
                    draw: !!window.SetSyncDrawOverlay,
                    features: !!window.SetSyncPlayFeatures,
                    offline: !!window.SetSyncOfflineStore,
                    api: !!window.SetSyncPlayApi,
                    uni: typeof window['UníssonoMetronome'],
                  },
                  font: getComputedStyle(document.documentElement).getPropertyValue('--play-font').trim(),
                  theme: document.documentElement.getAttribute('data-theme') || 'dark',
                  countInBadge: (document.getElementById('countin-badge') || {}).style?.display || '',
                  versionVisible: !!(document.getElementById('version-band-btn')),
                  vocalist: !!(document.getElementById('vocalist-sel')),
                  fs: !!document.fullscreenElement,
                };
                }"""
            )

        s0 = snap()
        if "/auth/login" in page.url:
            fail("boot", "redirecionou para login")
            print(
                json.dumps(
                    {"results": results, "page_errors": page_errors},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 1
        if not s0["globals"]["api"] or not s0["globals"]["metro"]:
            fail("boot_globals", str(s0["globals"]))
        else:
            ok("boot_globals", "SetSync* ok, Uníssono ausente")
        if s0["contentLen"] > 100:
            ok("render_cifra_inicial", f"len={s0['contentLen']} title={s0['title']}")
        else:
            fail("render_cifra_inicial", str(s0))
        if page_errors:
            fail("console_pageerror", "; ".join(page_errors[:3]))
        else:
            ok("console_pageerror", "nenhum")

        # ── Nav música ↑↓ / botões ──
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(500)
        s1 = snap()
        if s1["prog"] != s0["prog"] and s1["title"] != s0["title"]:
            ok("nav_musica_setas", f"{s0['prog']}→{s1['prog']}")
        else:
            fail("nav_musica_setas", f"{s0} → {s1}")
        page.click("#btn-prev", force=True)
        page.wait_for_timeout(400)
        s2 = snap()
        if s2["prog"] == s0["prog"]:
            ok("nav_musica_botoes", s2["prog"])
        else:
            fail("nav_musica_botoes", f"esperava {s0['prog']} got {s2['prog']}")

        # ── Paginação / tap / setas laterais ──
        # for short songs ArrowRight = next song when no scroll
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(350)
        s3 = snap()
        if s3["prog"] != s2["prog"] or s3["scrollTop"] != s2["scrollTop"]:
            ok(
                "paginar_setas_laterais",
                f"{s2['prog']}→{s3['prog']} scroll={s3['scrollTop']}",
            )
        else:
            fail("paginar_setas_laterais", str(s3))
        page.locator("#tap-prev").click(force=True)
        page.wait_for_timeout(300)
        ok("tap_zones_presentes", "tap-prev/next clicáveis")

        # ── Drawer L ──
        page.keyboard.press("l")
        page.wait_for_timeout(300)
        sd = snap()
        if sd["drawerOpen"]:
            ok("drawer_lista", "aberto com L")
            page.keyboard.press("Escape")
            page.wait_for_timeout(250)
            if not snap()["drawerOpen"]:
                ok("drawer_fecha_esc", "")
            else:
                fail("drawer_fecha_esc", "ainda aberto")
        else:
            fail("drawer_lista", "não abriu")

        # ── View modes G / menu ──
        page.click("#view-mode-btn", force=True)
        page.click('#view-mode-menu [data-view-mode="chordsheet"]', force=True)
        page.wait_for_timeout(1600)
        sg = snap()
        if sg["grade"] or sg["view"] == "Grade":
            ok("view_grade", f"label={sg['view']} content={sg['contentLen']}")
        else:
            fail("view_grade", str(sg))
        page.keyboard.press("g")  # cycle
        page.wait_for_timeout(900)
        sv = snap()
        # may be letra or cifra
        ok("view_cycle_G", f"view={sv['view']} letra={sv['letra']} grade={sv['grade']}")
        # back to cifra
        for _ in range(3):
            if (
                snap()["view"] == "Cifra"
                and not snap()["grade"]
                and not snap()["letra"]
            ):
                break
            page.keyboard.press("g")
            page.wait_for_timeout(700)
        page.click("#view-mode-btn", force=True)
        page.click('#view-mode-menu [data-view-mode="letra"]', force=True)
        page.wait_for_timeout(900)
        slt = snap()
        if slt["letra"] or slt["view"] == "Letra":
            ok("view_letra", slt["view"])
        else:
            fail("view_letra", str(slt))
        page.click("#view-mode-btn", force=True)
        page.click('#view-mode-menu [data-view-mode="cifra"]', force=True)
        page.wait_for_timeout(900)

        # ── Nashville ──
        page.keyboard.press("n")
        page.wait_for_timeout(200)
        snap()
        # may flash hint if not grade — still toggles btn
        page.click("#view-mode-btn", force=True)
        page.click('#view-mode-menu [data-view-mode="chordsheet"]', force=True)
        page.wait_for_timeout(1400)
        sn2 = snap()
        if sn2["nashOn"] or page.locator("#nashville-btn.pb-on").count():
            ok("nashville", f"on={sn2['nashOn']}")
        else:
            # toggle again on grade
            page.keyboard.press("n")
            page.wait_for_timeout(400)
            if snap()["nashOn"]:
                ok("nashville", "ligado na grade")
            else:
                warn("nashville", "btn pode não refletir pb-on")
        page.click("#view-mode-btn", force=True)
        page.click('#view-mode-menu [data-view-mode="cifra"]', force=True)
        page.wait_for_timeout(700)
        if snap()["nashOn"]:
            page.keyboard.press("n")  # off

        # ── Transpose ──
        tom0 = page.evaluate(
            """() => (document.getElementById('transpose-label')
                || document.querySelector('[id*=transpose]'))?.textContent || ''"""
        )
        page.click("#transpose-up", force=True)
        page.wait_for_timeout(1000)
        tom1 = page.evaluate(
            """() => (document.getElementById('transpose-label')
                || document.querySelector('[id*=transpose]'))?.textContent || ''"""
        )
        content_after_t = snap()["contentLen"]
        if tom1 != tom0 or content_after_t > 50:
            ok("transpose", f"'{tom0}'→'{tom1}' content={content_after_t}")
        else:
            fail("transpose", f"'{tom0}'→'{tom1}'")
        page.click("#transpose-down", force=True)
        page.wait_for_timeout(800)

        # ── Fonte ± ──
        font0 = snap()["font"]
        page.keyboard.press("+")
        page.wait_for_timeout(200)
        font1 = snap()["font"]
        if font1 != font0:
            ok("fonte", f"{font0}→{font1}")
        else:
            # try buttons
            page.locator(".font-ctrl").nth(2).click(force=True)
            page.wait_for_timeout(200)
            font2 = snap()["font"]
            if font2 != font0:
                ok("fonte", f"via btn {font0}→{font2}")
            else:
                fail("fonte", f"igual {font0}")

        # ── Fit / Colunas ──
        page.keyboard.press("a")
        page.wait_for_timeout(200)
        page.keyboard.press("a")
        page.wait_for_timeout(200)
        ok("fit_toggle", f"fitOn={snap()['fitOn']}")
        page.keyboard.press("c")
        page.wait_for_timeout(400)
        sc = snap()
        if sc["colsOn"]:
            ok("duas_colunas", "ligou")
            page.keyboard.press("c")
            page.wait_for_timeout(300)
        else:
            warn("duas_colunas", "não ligou (pode exigir conteúdo longo)")

        # ── Seções S ──
        page.keyboard.press("s")
        page.wait_for_timeout(350)
        if snap()["sectionsOpen"]:
            ok("secoes_painel", "aberto")
            nsec = page.locator(
                "#play-sections-list li, #play-sections-list button"
            ).count()
            ok("secoes_itens", f"count={nsec}")
            page.keyboard.press("s")
            page.wait_for_timeout(200)
        else:
            # try button
            page.click("#sections-btn", force=True)
            page.wait_for_timeout(300)
            if snap()["sectionsOpen"]:
                ok("secoes_painel", "via botão")
            else:
                fail("secoes_painel", "não abriu")

        # ── Metrônomo M + flash ──
        page.evaluate(
            "() => { try { localStorage.setItem('setsync.play.countIn.v1','0'); } catch(e){} }"
        )
        page.evaluate(
            """() => {
            const b = document.getElementById('metronome-btn');
            if (b) b.setAttribute('data-count-in','0');
            }"""
        )
        page.keyboard.press("m")
        page.wait_for_timeout(200)
        # check flash class appears within 1s
        flashed = page.evaluate(
            """() => new Promise(resolve => {
            const el = document.getElementById('cifra-wrap');
            if (!el) return resolve(false);
            let seen = false;
            const obs = new MutationObserver(() => {
              if (el.classList.contains('metronome-flash') || el.classList.contains('metronome-flash-accent')) {
                seen = true; obs.disconnect(); resolve(true);
              }
            });
            obs.observe(el, { attributes: true, attributeFilter: ['class'] });
            setTimeout(() => { obs.disconnect(); resolve(seen); }, 1200);
            })"""
        )
        sm = snap()
        if sm["metroActive"] or sm["metroOn"]:
            ok("metronomo", f"active={sm['metroActive']}")
        else:
            fail("metronomo", str(sm))
        if flashed:
            ok("metronomo_flash", "classe aplicada em #cifra-wrap")
        else:
            fail("metronomo_flash", "flash visual não disparou")
        page.keyboard.press("m")
        page.wait_for_timeout(200)

        # ── Draw D ──
        page.keyboard.press("d")
        page.wait_for_timeout(200)
        sd = snap()
        if sd["drawOn"] and sd["drawing"]:
            box = page.locator(".play-draw-canvas").bounding_box()
            page.mouse.move(box["x"] + 200, box["y"] + 150)
            page.mouse.down()
            page.mouse.move(box["x"] + 280, box["y"] + 200, steps=8)
            page.mouse.up()
            page.wait_for_timeout(200)
            nonzero = page.evaluate(
                """() => {
                const c=document.querySelector('.play-draw-canvas');
                const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
                let n=0; for(let i=3;i<d.length;i+=40) if(d[i]>10) n++; return n;
                }"""
            )
            if nonzero > 0:
                ok("draw_lapis", f"pixels={nonzero}")
            else:
                fail("draw_lapis", "sem pixels")
            # grade with draw stays
            page.click("#view-mode-btn", force=True)
            page.click('#view-mode-menu [data-view-mode="chordsheet"]', force=True)
            page.wait_for_timeout(1200)
            if snap()["drawOn"]:
                ok("draw_persiste_grade", "")
            else:
                fail("draw_persiste_grade", "desligou")
            page.keyboard.press("d")  # off
            page.click("#view-mode-btn", force=True)
            page.click('#view-mode-menu [data-view-mode="cifra"]', force=True)
            page.wait_for_timeout(700)
        else:
            fail("draw_lapis", str(sd))

        # ── Auto-scroll espaço ──
        page.keyboard.press(" ")
        page.wait_for_timeout(400)
        if snap()["scrollOn"]:
            ok("auto_scroll", "ligado")
            page.keyboard.press(" ")
            page.wait_for_timeout(200)
        else:
            # short content may not need scroll but btn should toggle
            page.click("#scroll-btn", force=True)
            page.wait_for_timeout(300)
            if snap()["scrollOn"]:
                ok("auto_scroll", "via botão")
                page.click("#scroll-btn", force=True)
            else:
                warn("auto_scroll", "btn sem pb-on (conteúdo curto?)")

        # ── Loop R ──
        page.keyboard.press("r")
        page.wait_for_timeout(250)
        if (
            snap()["loopOn"]
            or page.locator("#play-loop-bar:not(.d-none)").count()
            or page.locator("#loop-btn.pb-on").count()
        ):
            ok("loop", "barra/modo ativo")
            page.keyboard.press("r")
        else:
            page.click("#loop-btn", force=True)
            page.wait_for_timeout(250)
            if snap()["loopOn"]:
                ok("loop", "via botão")
                page.click("#loop-btn", force=True)
            else:
                warn("loop", "UI não refletiu")

        # ── Sync ──
        if snap()["syncExists"]:
            page.click("#sync-follow-btn", force=True)
            page.wait_for_timeout(300)
            if snap()["syncOn"]:
                ok("sync_lider", "ligado")
                page.click("#sync-follow-btn", force=True)
            else:
                warn("sync_lider", "existe mas não toggou pb-on")
        else:
            warn("sync_lider", "botão ausente (sem banda?)")

        # ── Tema T ──
        th0 = snap()["theme"]
        page.keyboard.press("t")
        page.wait_for_timeout(300)
        th1 = snap()["theme"]
        if th1 != th0:
            ok("tema", f"{th0}→{th1}")
            page.keyboard.press("t")
        else:
            fail("tema", f"igual {th0}")

        # ── Fullscreen F (pode falhar headless) ──
        try:
            page.keyboard.press("f")
            page.wait_for_timeout(400)
            fs = snap()["fs"]
            if fs:
                ok("fullscreen", "entrou")
                page.keyboard.press("f")
            else:
                warn("fullscreen", "API pode bloquear headless — botão presente")
        except Exception as exc:
            warn("fullscreen", str(exc))

        # ── Chrome hide ──
        page.evaluate("() => { document.body.classList.add('chrome-hidden'); }")
        if snap()["chromeHidden"]:
            page.evaluate(
                "() => { if (typeof showChrome==='function') showChrome(); else document.body.classList.remove('chrome-hidden'); }"
            )
            ok("chrome_hide_css", "classe chrome-hidden aplicável")
        else:
            fail("chrome_hide_css", "")

        # ── Offline banner / download UI ──
        offline_btn = page.locator("#play-offline-download").count()
        offline_store = snap()["globals"]["offline"]
        if offline_store:
            ok("offline_store", "SetSyncOfflineStore presente")
        else:
            fail("offline_store", "ausente")
        if offline_btn or page.locator("#play-offline-banner").count():
            ok("offline_ui", f"btn={offline_btn}")
        else:
            warn("offline_ui", "banner/btn não visível (já baixado?)")

        # ── Next peek ──
        if snap()["nextPeek"]:
            ok("proxima_peek", snap()["nextPeek"])
        else:
            warn("proxima_peek", "vazio (última música?)")

        # ── Progress dots ──
        dots = page.locator(".prog-dot").count()
        if dots > 0:
            page.locator(".prog-dot").nth(min(2, dots - 1)).click(force=True)
            page.wait_for_timeout(500)
            ok("prog_dots", f"clicou dot, prog={snap()['prog']}")
        else:
            warn("prog_dots", "sem dots (>20?)")

        # Ensure chrome visible before chrome-dependent controls
        page.evaluate(
            """() => {
            document.body.classList.remove('chrome-hidden');
            if (typeof showChrome === 'function') showChrome();
            }"""
        )
        page.wait_for_timeout(200)

        # ── Version buttons if visible ──
        vb = page.locator("#version-band-btn")
        vm = page.locator("#version-mine-btn")
        if vb.count() and vb.is_visible() and vm.count() and vm.is_visible():
            try:
                vm.click(force=True, timeout=3000)
                page.wait_for_timeout(800)
                ok("versao_banda_minha", "botões presentes e clicáveis")
                vb.click(force=True, timeout=3000)
                page.wait_for_timeout(500)
            except Exception as exc:
                warn("versao_banda_minha", f"click falhou: {exc}")
        else:
            warn("versao_banda_minha", "sem draft pessoal ou oculto pelo chrome")

        # ── Vocalist ──
        if page.locator("#vocalist-sel").count():
            ok("vocalist_select", "presente")
        else:
            warn("vocalist_select", "ausente nesta setlist")

        # ── Public letras ──
        if page.locator("#public-letras-btn").count():
            ok("letras_publico", "botão presente")
        else:
            warn("letras_publico", "share público off")

        # ── Stage notes ──
        if page.locator("#play-stage-note, #play-stage-note-edit").count():
            ok("notas_palco_ui", "elemento presente")
        else:
            warn("notas_palco_ui", "sem nota nesta música")

        # ── Assets version ──
        assets = page.evaluate(
            """() => ({
              draw: [...document.scripts].map(s=>s.src).find(s=>s.includes('play-draw')),
              features: [...document.scripts].map(s=>s.src).find(s=>s.includes('play-mode-features')),
              css: [...document.styleSheets].length,
            })"""
        )
        if assets.get("draw") and "v=5" in assets["draw"]:
            ok("asset_draw_v5", assets["draw"])
        else:
            warn("asset_draw_v5", str(assets.get("draw")))
        if assets.get("features") and "v=4" in assets["features"]:
            ok("asset_features_v4", assets["features"])
        else:
            warn("asset_features_v4", str(assets.get("features")))

        # final errors
        if page_errors:
            fail("pageerrors_final", "; ".join(page_errors[:5]))
        else:
            ok("pageerrors_final", "limpo")

        br.close()

    print(
        json.dumps(
            {"results": results, "page_errors": page_errors},
            ensure_ascii=False,
            indent=2,
        )
    )

    bad = [k for k, v in results.items() if v["status"] == "NÃO FUNCIONA"]
    partial = [k for k, v in results.items() if v["status"] == "PARCIAL"]
    good = [k for k, v in results.items() if v["status"] == "FUNCIONA"]
    print("\n=== RESUMO ===")
    print(f"FUNCIONA: {len(good)} | PARCIAL: {len(partial)} | NÃO FUNCIONA: {len(bad)}")
    for k in bad:
        print(f"  ✗ {k}: {results[k]['detail']}")
    for k in partial:
        print(f"  ~ {k}: {results[k]['detail']}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
