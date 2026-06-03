#!/usr/bin/env python3
"""Testes rápidos da conversão de colagem Cifra Club → SetSync."""
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from cifras_tool.scraper.comum import converter_html_para_inline
from cifras_tool.scraper.cifraclub import baixar_html
from bs4 import BeautifulSoup
import re


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


def main():
    test_acordes_sobre_letra()
    test_data_chord()
    test_miaero_colunas()
    test_sanduiche_letra_acorde_letra()
    test_miaero_pagina_real()
    print("ok: test_cifraclub_paste")


if __name__ == "__main__":
    main()
