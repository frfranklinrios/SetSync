from __future__ import annotations

import re

import yt_dlp

from cifras_tool.ydl_common import build_ydl_opts


def _duracao_video(video_id: str) -> int | None:
    try:
        with yt_dlp.YoutubeDL(build_ydl_opts()) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False,
            )
            return int(info.get("duration") or 0)
    except Exception:
        return None


def buscar_no_youtube(
    artista: str,
    titulo: str,
    max_duration: int = 600,
    max_resultados: int = 5,
) -> list[dict]:
    # Mesmo formato que o player do Cifra Club usa em searchVideos()
    consulta = f"{artista} - {titulo}".strip()
    if not consulta:
        return []

    try:
        with yt_dlp.YoutubeDL(build_ydl_opts(extract_flat=True)) as ydl:
            info = ydl.extract_info(
                f"ytsearch{max_resultados}:{consulta}",
                download=False,
            )
    except Exception:
        return []

    videos = []
    for entrada in info.get("entries") or []:
        if not entrada:
            continue
        video_id = entrada.get("id")
        if not video_id:
            continue
        duracao = int(entrada.get("duration") or 0)
        if duracao and duracao > max_duration:
            continue
        videos.append(
            {
                "id": video_id,
                "nome": entrada.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duracao": duracao,
            }
        )
    return videos


def resolver_youtube(
    ids_na_pagina: list[str],
    artista: str,
    titulo: str,
    max_duration: int = 600,
) -> tuple[str, list[dict]]:
    """Prioriza vídeo da página se for curto; senão busca no YouTube."""
    candidatos: list[dict] = []

    for video_id in ids_na_pagina:
        duracao = _duracao_video(video_id)
        if duracao is None:
            continue
        if duracao <= max_duration:
            candidatos.append(
                {
                    "id": video_id,
                    "nome": "(página)",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "duracao": duracao,
                }
            )

    if candidatos:
        return candidatos[0]["url"], candidatos

    busca = buscar_no_youtube(artista, titulo, max_duration=max_duration)
    if busca:
        return busca[0]["url"], busca

    return "", []
