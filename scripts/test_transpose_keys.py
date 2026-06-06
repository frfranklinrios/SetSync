#!/usr/bin/env python3
"""Testa a transposição ciente da armadura (sustenido vs. bemol pelo tom de destino)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util import (
    build_key_spelling,
    key_at_transpose,
    pychord_transpose_text,
    format_text_chords_br,
    get_absolute_key_list,
)

_fails = []


def check(cond, msg):
    print(('ok  ' if cond else 'FALHA ') + msg)
    if not cond:
        _fails.append(msg)


def main() -> int:
    print('=== build_key_spelling (grafia pela escala) ===')
    # Em Ré maior, o índice 1 é Dó# (7º grau), nunca Réb.
    check(build_key_spelling('D')[1] == 'C#', f"D[1] -> {build_key_spelling('D')[1]!r} (esperado C#)")
    # Em Réb maior, o índice 1 é Réb.
    check(build_key_spelling('Db')[1] == 'Db', f"Db[1] -> {build_key_spelling('Db')[1]!r} (esperado Db)")
    # Escala completa de Mi♭ maior.
    eb = build_key_spelling('Eb')
    check(eb[3] == 'Eb' and eb[8] == 'Ab' and eb[10] == 'Bb',
          f"Eb diatônicas -> {eb[3]},{eb[8]},{eb[10]} (esperado Eb,Ab,Bb)")
    # Em tom menor (Am), nada de bemóis forçados.
    check(build_key_spelling('Am')[9] == 'A', "Am tônica = A")

    print('\n=== key_at_transpose (tons canônicos) ===')
    check(key_at_transpose('C', 3) == 'Eb', f"C+3 -> {key_at_transpose('C', 3)!r} (esperado Eb)")
    check(key_at_transpose('C', 1) == 'Db', f"C+1 -> {key_at_transpose('C', 1)!r} (esperado Db)")
    check(key_at_transpose('C', 6) == 'F#', f"C+6 -> {key_at_transpose('C', 6)!r} (esperado F#)")
    check(key_at_transpose('C', 0) == 'C', "C+0 -> C")
    check(key_at_transpose('Am', 0) == 'Am', "Am+0 -> Am")
    check(key_at_transpose('Bm', -4) == 'Gm', f"Bm-4 -> {key_at_transpose('Bm', -4)!r} (esperado Gm)")

    print('\n=== pychord_transpose_text (acordes pela armadura do destino) ===')
    # Dó -> Mi♭ (+3): acordes devem sair com bemóis.
    check(pychord_transpose_text('C', 3, 'C') == 'Eb', f"C +3 -> {pychord_transpose_text('C', 3, 'C')!r} (esperado Eb)")
    check(pychord_transpose_text('F', 3, 'C') == 'Ab', f"F +3 -> {pychord_transpose_text('F', 3, 'C')!r} (esperado Ab)")
    check(pychord_transpose_text('G', 3, 'C') == 'Bb', f"G +3 -> {pychord_transpose_text('G', 3, 'C')!r} (esperado Bb)")
    # Dó -> Ré (+2): acordes com sustenidos (F#m).
    check(pychord_transpose_text('Em', 2, 'C') == 'F#m', f"Em +2 -> {pychord_transpose_text('Em', 2, 'C')!r} (esperado F#m)")
    # Acorde com baixo invertido.
    check(pychord_transpose_text('C/E', 2, 'C') == 'D/F#', f"C/E +2 -> {pychord_transpose_text('C/E', 2, 'C')!r} (esperado D/F#)")

    print('\n=== format_text_chords_br (regrafa pela armadura) ===')
    # D# pertence à grafia de Mi♭ como Eb.
    check(format_text_chords_br('D#', 'Eb') == 'Eb', f"D# em Eb -> {format_text_chords_br('D#', 'Eb')!r} (esperado Eb)")

    print('\n=== fluxo completo (transpor + formatar) ===')
    linha = 'C  Am  F  G'
    semi = 3
    out = pychord_transpose_text(linha, semi, 'C')
    out = format_text_chords_br(out, key_at_transpose('C', semi))
    check(out == 'Eb  Cm  Ab  Bb', f"linha C->Eb -> {out!r} (esperado 'Eb  Cm  Ab  Bb')")

    print('\n=== dropdown canônico ===')
    majors = get_absolute_key_list('C')
    check('Eb' in majors and 'D#' not in majors, f"lista maior usa Eb (não D#): {majors}")

    if _fails:
        print(f'\n{len(_fails)} falha(s).')
        return 1
    print('\nTodos os testes de transposição passaram.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
