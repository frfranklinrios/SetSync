#!/usr/bin/env python3
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from chordpro import conteudo_to_chordpro
from setlist_public import (
    clean_lyrics_for_public,
    compute_public_letras_revision,
    conteudo_to_lyrics_plain,
)


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


def test_revision_changes():
    base = {"name": "Show", "description": ""}
    band = {"logo_filename": ""}
    s1 = [{"index": 1, "cifra_id": "a", "titulo": "A", "artista": "", "display_key": "C",
           "vocalist_name": "", "lyrics": "Oi"}]
    s2 = [{**s1[0], "lyrics": "Tchau"}]
    r1 = compute_public_letras_revision(base, band, s1)
    r2 = compute_public_letras_revision(base, band, s2)
    assert r1 != r2, (r1, r2)


def main():
    test_lyrics_strip()
    test_remove_parentheses()
    test_revision_changes()
    print("ok: test_setlist_public")


if __name__ == "__main__":
    main()
