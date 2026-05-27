"""Raspagem de cifras do Cifras.com.br e Cifra Club."""

from __future__ import annotations

import argparse
import json

from cifras_tool.scraper.cifraclub import raspar as raspar_cifraclub
from cifras_tool.scraper.cifras_com_br import raspar as raspar_cifras_com_br
from cifras_tool.scraper.comum import detectar_fonte, normalizar_url, normalizar_url_youtube

URL_PADRAO = "https://www.cifras.com.br/cifra/dominguinhos/gostoso-demais"


def raspar_cifra(url: str) -> dict:
    url = normalizar_url(url)
    fonte = detectar_fonte(url)
    if fonte == "cifraclub":
        return raspar_cifraclub(url)
    return raspar_cifras_com_br(url)


def salvar_saida(dados: dict) -> None:
    with open("cifra.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(dados, arquivo_json, ensure_ascii=False, indent=2)

    fonte = dados.get("fonte", "")
    cabecalho_fonte = f"Fonte: {fonte}\n" if fonte else ""

    with open("cifra.txt", "w", encoding="utf-8") as arquivo_txt:
        arquivo_txt.write(f"{dados['titulo']}\n")
        arquivo_txt.write(f"{dados['artista']}\n")
        if fonte:
            arquivo_txt.write(cabecalho_fonte)
        if dados.get("tom"):
            arquivo_txt.write(f"Tom: {dados['tom']}\n")
        if dados.get("youtube"):
            arquivo_txt.write(f"YouTube: {dados['youtube']}\n")
        arquivo_txt.write(f"\n{dados['cifra']}")

    videos = dados.get("videos_youtube", [])
    if videos:
        with open("youtube.txt", "w", encoding="utf-8") as arquivo_youtube:
            arquivo_youtube.write(f"{dados['titulo']} - {dados['artista']}\n\n")
            arquivo_youtube.write(f"Principal: {dados['youtube']}\n\n")
            if len(videos) > 1:
                arquivo_youtube.write("Outros vídeos:\n")
                for video in videos[1:]:
                    nome = video.get("nome", "")
                    arquivo_youtube.write(f"- {video['url']}")
                    if nome:
                        arquivo_youtube.write(f" ({nome})")
                    arquivo_youtube.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Raspa cifra do Cifras.com.br ou Cifra Club"
    )
    parser.add_argument("url", nargs="?", default=URL_PADRAO, help="URL da cifra")
    parser.add_argument(
        "--youtube",
        metavar="URL",
        default=None,
        help="URL do YouTube (substitui detecção automática)",
    )
    args = parser.parse_args()

    try:
        url = normalizar_url(args.url)
        detectar_fonte(url)
    except ValueError as erro:
        print(erro)
        return

    dados = raspar_cifra(url)
    if args.youtube:
        dados["youtube"] = normalizar_url_youtube(args.youtube)
    salvar_saida(dados)

    if dados["cifra"]:
        arquivos = "cifra.json, cifra.txt"
        if dados.get("videos_youtube"):
            arquivos += " e youtube.txt"
        print(f"Cifra extraída ({dados.get('fonte', '?')}). Arquivos: {arquivos}")
        if dados.get("youtube"):
            print(f"YouTube: {dados['youtube']}")
    else:
        print("Não foi possível extrair a cifra da página.")


__all__ = ["raspar_cifra", "normalizar_url", "detectar_fonte", "salvar_saida", "main"]
