#!/usr/bin/env python3
"""Testes da API musical v1."""
from __future__ import annotations

import sys

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))

from chord_diagram.api_service import (
    build_arpeggio_document,
    build_chord_document,
    build_scale_document,
    catalog_payload,
    render_chord_svg_for_position,
)
from chord_diagram.theory.chord_parser import parse_chord_symbol


def check(cond, msg):
    if not cond:
        print('FAIL', msg)
        sys.exit(1)
    print('ok', msg)


def main():
    p = parse_chord_symbol('Fmaj7#11')
    check(p and p.root == 'F' and p.quality == 'maj7', 'parse Fmaj7#11')

    doc = build_chord_document('Am', instrument='violao')
    check('positions' in doc and doc['positions'], 'voicings Am violão')
    check(any(p.get('source') == 'Cifra clássica' for p in doc['positions']), 'real shapes Am')

    from chord_diagram.api_service import fetch_progression_for_modal
    modal = fetch_progression_for_modal('Am', instrument='violao')
    check(modal.get('chords') and modal['chords'][0].get('positions'), 'modal payload positions')

    from chord_diagram.cache import set_cached, get_cached
    set_cached('test_key', {'ok': True}, ttl=60)
    check(get_cached('test_key',) == {'ok': True}, 'memory cache')

    from chord_diagram.voicing import detect_barres
    bm = ['x', 2, 4, 4, 4, 2]
    check(len(detect_barres(bm)) == 0, 'Bm sem pestana falsa no traste 4')
    ok_barre = [2, 2, 2, 0, 0, 0]
    b = detect_barres(ok_barre)
    check(len(b) == 1 and b[0]['fret'] == 2, 'pestana válida trastes graves')
    blocked = [2, 3, 3, 3, 0, 0]
    check(len(detect_barres(blocked)) == 0, 'pestana bloqueada por corda grave em traste menor')
    check(doc['theory']['root'] == 'A', 'theory root A')

    doc_cav = build_chord_document('Gmaj7', instrument='cavaquinho')
    check(doc_cav.get('meta', {}).get('instrument') == 'cavaquinho', 'cavaquinho meta')

    scale = build_scale_document('E', 'minor_pentatonic', instrument='violao')
    check(scale.get('type') == 'scale_map', 'scale map')
    nodes = scale['fretboardMapping']['activeNodes']
    check(any(n['isRoot'] for n in nodes), 'scale has root nodes')

    arp = build_arpeggio_document('Am7', instrument='baixo')
    check(arp.get('type') == 'arpeggio' and arp.get('sequence'), 'arpeggio sequence')

    piano = build_chord_document('Cmaj9', instrument='piano')
    check('keyMappings' in piano and len(piano['keyMappings']) >= 4, 'piano Cmaj9')

    svg = render_chord_svg_for_position('C', 'violao', 0)
    check(svg and '<svg' in svg and 'circle' in svg, 'SVG fretboard')

    cat = catalog_payload()
    check(len(cat['instruments']) >= 6, 'catalog instruments')

    print('\nTodos os testes music_api passaram.')


if __name__ == '__main__':
    main()
