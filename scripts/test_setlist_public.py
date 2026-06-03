#!/usr/bin/env python3
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from chordpro import conteudo_to_chordpro
from setlist_public import conteudo_to_lyrics_plain, set_setlist_public_share


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


def main():
    test_lyrics_strip()
    print("ok: test_setlist_public")


if __name__ == "__main__":
    main()
