#!/usr/bin/env python3
"""Testes rápidos da conversão de colagem Cifra Club → SetSync."""
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from cifras_tool.scraper.comum import converter_html_para_inline


def test_acordes_sobre_letra():
    html = "<b>Am</b>  <b>G</b>\n<i>Minha letra aqui</i>"
    out = converter_html_para_inline(html)
    assert "[Am]" in out and "[G]" in out, out
    assert "letra aqui" in out, out


def test_data_chord():
    html = '<span data-chord="F">F</span>\n<span>Palavra</span>'
    out = converter_html_para_inline(html)
    assert "[F]" in out and "Palavra" in out, out


def main():
    test_acordes_sobre_letra()
    test_data_chord()
    print("ok: test_cifraclub_paste")


if __name__ == "__main__":
    main()
