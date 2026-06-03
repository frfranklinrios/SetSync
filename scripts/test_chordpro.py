#!/usr/bin/env python3
"""Testes de conversão ChordPro."""
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from chordpro import conteudo_to_chordpro, parse_conteudo_to_cifra_data


def test_save_chordpro():
    body = "[Am]Olá [G]mundo\n\nRefrão\n[C]Fim"
    out = conteudo_to_chordpro(
        body,
        titulo="Música",
        artista="Artista",
        key="Am",
    )
    assert "{title: Música}" in out, out
    assert "{artist: Artista}" in out, out
    assert "{key: Am}" in out, out
    assert "[Am]Olá [G]mundo" in out, out
    assert "{comment: Refrão}" in out, out
    assert "[C]Fim" in out, out


def test_parse_roundtrip():
    cp = conteudo_to_chordpro("[D]Linha", titulo="T", artista="A", key="D")
    data = parse_conteudo_to_cifra_data(cp)
    assert any(d.get("acorde") == "D" for d in data), data


def main():
    test_save_chordpro()
    test_parse_roundtrip()
    print("ok: test_chordpro")


if __name__ == "__main__":
    main()
