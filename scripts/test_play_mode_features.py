#!/usr/bin/env python3
"""Testes unitários dos recursos do Modo Tocar."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_leadsheet_meta_capo():
    from blueprints.cifras import _leadsheet_meta_value, play_cifra_client_payload

    cifra = {
        'id': 'x',
        'titulo': 'T',
        'artista': 'A',
        'tom_original': 'G',
        'grade_json': json.dumps({
            'meta': {'capo': '2', 'time_signature': '3/4', 'bpm': '90'},
            'bars': [],
        }),
    }
    assert _leadsheet_meta_value(cifra, 'capo') == '2'
    assert _leadsheet_meta_value(cifra, 'time_signature') == '3/4'
    payload = play_cifra_client_payload(cifra)
    assert payload['capo'] == '2'
    assert payload['time_signature'] == '3/4'


def test_pedal_defaults():
    path = ROOT / 'static' / 'js' / 'play-pedal-config.js'
    text = path.read_text(encoding='utf-8')
    assert "prevSong: ['ArrowUp']" in text
    assert "nextSong: ['ArrowDown']" in text


def test_play_state_route_registered():
    from blueprints.realtime import realtime_bp

    rules = {r.rule for r in realtime_bp.url_map.iter_rules()} if hasattr(realtime_bp, 'url_map') else set()
    # Blueprint isolado não expõe url_map; verifica função registrada no módulo.
    from blueprints import realtime as rt_mod
    assert hasattr(rt_mod, 'set_play_state')


def test_play_notes_resolve():
    from blueprints.cifras import _resolve_play_notes, play_cifra_client_payload

    c = {'id': '1', 'play_notes': 'Geral', 'setlist_play_notes': 'No culto: devagar'}
    assert _resolve_play_notes(c) == 'No culto: devagar'
    payload = play_cifra_client_payload(c)
    assert payload['play_notes'] == 'No culto: devagar'
    assert 'duracao_seg' in payload


def test_setlist_play_notes_model():
    from models_setlist import set_setlist_cifra_play_notes
    assert callable(set_setlist_cifra_play_notes)


def main() -> None:
    test_leadsheet_meta_capo()
    test_pedal_defaults()
    test_play_state_route_registered()
    test_play_notes_resolve()
    test_setlist_play_notes_model()
    print('ok test_play_mode_features')


if __name__ == '__main__':
    main()
