#!/usr/bin/env python3
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from chordpro import conteudo_to_chordpro
from setlist_public import clean_lyrics_for_public, conteudo_to_lyrics_plain


def test_lyrics_strip():
    cp = conteudo_to_chordpro(
        "[Am]Olá [G]mundo\n\nRefrão",
        titulo="T",
        artista="A",
        key="Am",
    )
    out = conteudo_to_lyrics_plain(cp)
    assert "Olá" in out and "mundo" in out, out
    assert "[Am]" not in out, out
    assert "Refrão" in out, out


def test_remove_parentheses():
    out = clean_lyrics_for_public("Linha (2x)\nOutra (refrão) aqui")
    assert "(" not in out and ")" not in out, out
    assert "2x" not in out, out
    assert "Linha" in out and "Outra" in out, out


def main():
    test_lyrics_strip()
    test_remove_parentheses()
    print("ok: test_setlist_public")


if __name__ == "__main__":
    main()
