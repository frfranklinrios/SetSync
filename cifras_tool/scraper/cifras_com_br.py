from __future__ import annotations

import html as html_module
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from cifras_tool.scraper.comum import (
    extrair_pre_cifra,
    normalizar_url,
    primeiro_texto,
)


def baixar_html(url: str) -> Optional[str]:
    url = normalizar_url(url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
    }
    try:
        resposta = requests.get(url, headers=headers, timeout=30)
        resposta.raise_for_status()
    except requests.RequestException:
        return None
    return resposta.text


def extrair_song_id(html: str) -> Optional[str]:
    padroes = [
        r"window\.SONG_METADATA\s*=\s*\{[^}]*\bID:\s*(\d+)",
        r'model-id="(\d+)"\s+model="chord"',
        r"/contribuir/cifra/(\d+)",
    ]
    for padrao in padroes:
        match = re.search(padrao, html)
        if match:
            return match.group(1)
    return None


def extrair_videos_youtube(song_id: str) -> list[dict]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        resposta = requests.get(
            "https://www.cifras.com.br/api/song/videos",
            params={"song_id": song_id},
            headers=headers,
            timeout=30,
        )
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError):
        return []

    videos = []
    for video in dados.get("videos", []):
        video_id = video.get("id")
        if not video_id:
            continue
        videos.append(
            {
                "id": video_id,
                "nome": html_module.unescape(video.get("name", "")),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )
    return videos


def raspar(url: str) -> dict:
    url = normalizar_url(url)
    html = baixar_html(url)
    vazio = {
        "url": url,
        "fonte": "cifras.com.br",
        "titulo": "",
        "artista": "",
        "cifra": "",
        "song_id": "",
        "youtube": "",
        "videos_youtube": [],
    }
    if not html:
        return vazio

    soup = BeautifulSoup(html, "html.parser")
    titulo = primeiro_texto(soup, ["h1.component-song-show-header__song-title", "h1"])
    artista = primeiro_texto(
        soup,
        [
            "h2.component-song-show-header__artist",
            "h2",
            'a[href*="/artista/"]',
        ],
    )
    cifra = extrair_pre_cifra(
        soup,
        [
            "pre",
            ".component-song-show-chord-content",
            "article pre",
        ],
    )
    song_id = extrair_song_id(html) or ""
    videos_youtube = extrair_videos_youtube(song_id) if song_id else []
    youtube = videos_youtube[0]["url"] if videos_youtube else ""

    return {
        **vazio,
        "titulo": titulo,
        "artista": artista,
        "cifra": cifra,
        "song_id": song_id,
        "youtube": youtube,
        "videos_youtube": videos_youtube,
    }
