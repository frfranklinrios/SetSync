#!/usr/bin/env python3
"""Testes de conversão ChordPro."""
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from chordpro import (
    conteudo_to_chordpro,
    is_comment_line,
    parse_conteudo_to_cifra_data,
    strip_comment_lines_from_text,
)


def test_save_chordpro():
    body = "[Am]Olá [G]mundo\n\nRefrão\n[C]Fim"
    out = conteudo_to_chordpro(
        body,
        titulo="Música",
        artista="Artista",
        key="Am",
    )
    assert "{title: Música}" in out, out
    assert "{comment:" not in out.lower(), out
    assert "[Am]Olá [G]mundo" in out, out
    assert "[C]Fim" in out, out


def test_strip_comments():
    raw = "{comment: São João está dormindo}\n[Am] Linha\n{comment: Intro}"
    stripped = strip_comment_lines_from_text(raw)
    assert "comment" not in stripped.lower()
    assert "[Am] Linha" in stripped


def test_parse_skips_comments():
    data = parse_conteudo_to_cifra_data(
        "{comment: São João está dormindo}\n[Am] teste"
    )
    assert len(data) == 1
    assert data[0].get("acorde") == "Am"
    assert is_comment_line("{comment: x}")


def test_parse_roundtrip():
    cp = conteudo_to_chordpro("[D]Linha", titulo="T", artista="A", key="D")
    data = parse_conteudo_to_cifra_data(cp)
    assert any(d.get("acorde") == "D" for d in data), data


def main():
    test_save_chordpro()
    test_strip_comments()
    test_parse_skips_comments()
    test_parse_roundtrip()
    print("ok: test_chordpro")


if __name__ == "__main__":
    main()
