#!/usr/bin/env python3
"""Testes rápidos da conversão de colagem Cifra Club → SetSync."""
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from cifras_tool.scraper.comum import (
    converter_html_para_inline,
    looks_like_cifraclub_colagem,
    normalizar_colagem_cifraclub,
)
from cifras_tool.scraper.cifraclub import baixar_html
from chordpro import conteudo_to_chordpro, parse_conteudo_to_cifra_data
from bs4 import BeautifulSoup
import re

MIAERO_PLAIN = """[Intro] Bm7  Em7  G6  Bm7  D  C#m7(5-)  F#7  Bm7

Depois que eu ganhar dinheiro
                     Em7
Pro meu miaêro vazio
G6                C#m7(5-)
Vou passear no brasil
      F#7        Bm7
Vê o rio de janeiro

    Em7                 G6
Passado o meu mal passadio
    Bm7               D
Passado esse tempo de estio
             C#m7(5-)  F#7       Bm7
Eu quero brincar          no terreiro

                       F#7
Eu vou comprar uma sandália
                 Bm7
Daquela de brasileiro
                      B7
Chinela que no chão pisar
                   Em7
E faz um chiado maneiro
     G6            F#7
Também quero uma camisa

Que é feita de brisa
                C#m7(5-)       Bm7
E que deixa desnudo o tempo inteiro

      F#7       Bm7
Miaêro oh oh, miaêro
       F#7          Bm7
Miaêro oh oh oh, miaêro
      F#7       Bm7
Miaêro oh oh, miaêro
     F#7               Bm7
Miaêro oh oh oh oh, miaêro"""


def test_acordes_sobre_letra():
    html = "<b>Am</b>  <b>G</b>\n<i>Minha letra aqui</i>"
    out = converter_html_para_inline(html)
    assert "[Am]" in out and "[G]" in out, out
    assert "letra aqui" in out, out


def test_data_chord():
    html = '<span data-chord="F">F</span>\n<span>Palavra</span>'
    out = converter_html_para_inline(html)
    assert "[F]" in out and "Palavra" in out, out


def test_miaero_colunas():
    """Padrão Cifra Club: linha de acordes com espaços + letra na linha seguinte."""
    html = "<b>G6</b>                <b>C#m7(5-)</b>\nVou passear no brasil"
    out = converter_html_para_inline(html)
    assert out.startswith("[G6]Vou passear no "), out
    assert "[C#m7(5-)]" in out, out
    assert "brasil" in out, out
    assert "bra[C#m7" not in out, out


def test_sanduiche_letra_acorde_letra():
    html = (
        "Depois que eu ganhar dinheiro\n"
        "                     <b>Em7</b>\n"
        "Pro meu miaêro vazio"
    )
    out = converter_html_para_inline(html)
    linhas = [ln for ln in out.split("\n") if ln.strip()]
    assert linhas[0] == "Depois que eu ganhar dinheiro", linhas
    assert "[Em7]" in linhas[1] and "miaêro" in linhas[1], linhas


def test_miaero_pagina_real():
    html = baixar_html("https://www.cifraclub.com.br/chico-cesar/miaero/")
    if not html:
        return
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.select_one(".cifra_cnt pre") or soup.select_one("pre")
    if not pre:
        return
    inner = re.sub(r"<br\s*/?>", "\n", pre.decode_contents(), flags=re.I)
    out = converter_html_para_inline(inner)
    assert "bra[C#m7" not in out, out
    assert "brasil[Bm7]eiro" not in out, out
    assert "sand[F#7]ália" not in out, out
    assert "[G6]Vou passear" in out or "Vou passear no" in out, out
    assert "Pro meu" in out and "miaêro vazio" in out, out


def test_miaero_texto_plano():
    assert looks_like_cifraclub_colagem(MIAERO_PLAIN)
    out = normalizar_colagem_cifraclub(MIAERO_PLAIN)
    assert "bra[C#m7" not in out, out
    assert "brasil[Bm7]eiro" not in out, out
    assert "sand[F#7]ália" not in out, out
    assert "[G6]Vou passear" in out, out
    assert "Depois que eu ganhar dinheiro" in out, out
    cp = conteudo_to_chordpro(out, titulo="Miaêro", artista="Chico César", key="Bm")
    assert "{comment: Depois que eu ganhar dinheiro}" not in cp, cp
    assert "bra[C#m7" not in cp, cp
    data = parse_conteudo_to_cifra_data(MIAERO_PLAIN)
    assert any(
        "Depois que eu ganhar dinheiro" in (it.get("texto_letra") or "")
        for it in data
    ), data


def main():
    test_acordes_sobre_letra()
    test_data_chord()
    test_miaero_colunas()
    test_sanduiche_letra_acorde_letra()
    test_miaero_texto_plano()
    test_miaero_pagina_real()
    print("ok: test_cifraclub_paste")


if __name__ == "__main__":
    main()
