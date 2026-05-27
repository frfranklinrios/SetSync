from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

VIDEO_ID_PATTERN = re.compile(r"(?:v=|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})")


def _id_de_url(url: str) -> Optional[str]:
    match = VIDEO_ID_PATTERN.search(url)
    return match.group(1) if match else None


def extrair_youtube_do_player(html: str) -> Optional[str]:
    """
    Extrai o link do player após o JS do site preencher o <a href="...">.
    Funciona com HTML já renderizado (ex.: Playwright).
    """
    soup = BeautifulSoup(html, "html.parser")

    seletores = [
        ".player-placeholder a[href*='youtube.com']",
        ".player-placeholder a[href*='youtu.be']",
        "a[href*='youtube.com/watch']",
        ".player-embed iframe[src*='youtube']",
        "iframe[src*='youtube.com/embed']",
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)
        if not elemento:
            continue
        url = elemento.get("href") or elemento.get("src") or ""
        video_id = _id_de_url(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

    for elemento in soup.select(
        ".player-placeholder a[href='javascript:void(0)'], "
        ".player-placeholder a[href='javascript:void(0);']"
    ):
        data_id = elemento.get("data-id", "")
        if data_id and "{{" not in data_id and len(data_id) == 11:
            return f"https://www.youtube.com/watch?v={data_id}"

    return None


def extrair_youtube_com_playwright(url: str, timeout_ms: int = 12_000) -> Optional[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(3000)

            try:
                page.locator(".player-placeholder a").click(timeout=4000)
                page.wait_for_timeout(2000)
            except Exception:
                pass

            seletores_espera = [
                ".player-placeholder a[href*='youtube.com/watch']",
                "iframe[src*='youtube.com/embed']",
                ".player-placeholder a[data-id]:not([data-id*='{{'])",
            ]
            for seletor in seletores_espera:
                try:
                    page.wait_for_selector(seletor, timeout=5000)
                    break
                except Exception:
                    continue

            link = page.evaluate(
                """() => {
                    const a = document.querySelector('.player-placeholder a');
                    if (a && a.href && a.href.includes('youtube.com/watch')) {
                        return a.href;
                    }
                    const iframe = document.querySelector('iframe[src*="youtube.com"]');
                    if (iframe && iframe.src) return iframe.src;
                    if (a && a.dataset && a.dataset.id && a.dataset.id.length === 11) {
                        return 'https://www.youtube.com/watch?v=' + a.dataset.id;
                    }
                    return null;
                }"""
            )
            if link:
                video_id = _id_de_url(link)
                if video_id:
                    return f"https://www.youtube.com/watch?v={video_id}"

            return extrair_youtube_do_player(page.content())
        finally:
            browser.close()

    return None
