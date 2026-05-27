from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

from cifras_tool.config import settings
from cifras_tool.scraper.comum import (
    extrair_pre_cifra,
    extrair_tom_do_html,
    normalizar_url,
    primeiro_texto,
)
from cifras_tool.scraper.cifraclub_player import extrair_youtube_com_playwright, extrair_youtube_do_player
from cifras_tool.scraper.youtube_resolver import resolver_youtube


def baixar_html(url: str) -> Optional[str]:
    url = normalizar_url(url)
    try:
        resposta = curl_requests.get(
            url,
            impersonate="chrome120",
            timeout=30,
            headers={
                "Accept-Language": "pt-BR,pt;q=0.9",
            },
        )
        resposta.raise_for_status()
    except Exception:
        return None
    return resposta.text


def _titulo_e_artista(soup: BeautifulSoup, url: str) -> tuple[str, str]:
    titulo = primeiro_texto(soup, [".t1", "h1.t1"])
    artista = primeiro_texto(soup, [".t3", "h2 a", ".art_mus"])

    if titulo.lower() == "cifra club":
        titulo = ""

    if not titulo or not artista:
        parsed = urlparse(url)
        partes = [p for p in parsed.path.strip("/").split("/") if p]
        if len(partes) >= 2:
            if not artista:
                artista = partes[0].replace("-", " ").title()
            if not titulo:
                titulo = partes[1].replace("-", " ").title()

    return titulo, artista


def raspar(url: str) -> dict:
    url = normalizar_url(url)
    html = baixar_html(url)
    vazio = {
        "url": url,
        "fonte": "cifraclub",
        "titulo": "",
        "artista": "",
        "cifra": "",
        "song_id": "",
        "youtube": "",
        "videos_youtube": [],
        "tom": "",
    }
    if not html:
        return vazio

    soup = BeautifulSoup(html, "html.parser")
    titulo, artista = _titulo_e_artista(soup, url)
    cifra = extrair_pre_cifra(
        soup,
        [
            ".cifra_cnt pre",
            "#cifra pre",
            "pre",
        ],
    )
    # O <a href="javascript:void(0)"> do player é preenchido via JS após busca
    # "Artista - Música" no YouTube. Tentamos ler o link já renderizado (Playwright).
    youtube_player = extrair_youtube_com_playwright(url, timeout_ms=12_000)
    if not youtube_player:
        youtube_player = extrair_youtube_do_player(html)

    ids_pagina = list(dict.fromkeys(re.findall(r"youtube\.com/watch\?v=([\w-]+)", html)))

    if youtube_player:
        match_id = re.search(r"v=([\w-]+)", youtube_player)
        video_id = match_id.group(1) if match_id else ""
        youtube = youtube_player
        videos_youtube = [
            {
                "id": video_id,
                "nome": "Vídeo do player (página)",
                "url": youtube_player,
            }
        ]
    else:
        youtube, videos_youtube = resolver_youtube(
            ids_pagina,
            artista,
            titulo,
            max_duration=settings.max_audio_duration,
        )

    tom = extrair_tom_do_html(soup)

    return {
        **vazio,
        "titulo": titulo,
        "artista": artista,
        "cifra": cifra,
        "tom": tom,
        "youtube": youtube,
        "videos_youtube": videos_youtube,
    }
