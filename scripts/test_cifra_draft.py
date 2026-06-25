#!/usr/bin/env python3
"""Testes do fluxo de rascunho pessoal de cifras."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

os.environ.setdefault('DATABASE_URL', f'sqlite:///{tempfile.mkdtemp()}/test.db')


def main() -> int:
    from db import (
        init_db,
        create_user,
        create_band,
        add_band_member,
        create_cifra,
        get_cifra,
        get_cifra_user_draft,
        upsert_cifra_user_draft,
        publish_cifra_user_draft,
        delete_cifra_user_draft,
    )
    from cifra_user_draft import draft_differs_from_band, merge_cifra_with_draft

    init_db()
    uid = create_user('draftuser', 'draft@test.com', 'hash', display_name='Draft User')
    band_id = create_band('Banda Teste', '', uid)
    add_band_member(band_id, uid, 'owner')

    cid = create_cifra(
        'Amazing Grace',
        'Tradicional',
        'G',
        '[G] linha original',
        band_id,
        cifra_json=json.dumps([{'segundo': 0, 'texto_letra': 'linha', 'acorde': 'G'}]),
    )
    cifra = get_cifra(cid)
    assert cifra is not None

    draft_fields = {
        'titulo': 'Amazing Grace',
        'artista': 'Tradicional',
        'tom_original': 'A',
        'conteudo': '[A] linha editada',
        'cifra_json': json.dumps([{'segundo': 0, 'texto_letra': 'linha', 'acorde': 'A'}]),
    }
    upsert_cifra_user_draft(cid, uid, draft_fields)
    draft = get_cifra_user_draft(cid, uid)
    assert draft is not None
    assert draft_differs_from_band(draft, cifra)

    merged = merge_cifra_with_draft(cifra, draft)
    assert 'editada' in merged['conteudo']
    assert get_cifra(cid)['conteudo'] == '[G] linha original'

    assert publish_cifra_user_draft(cid, uid)
    updated = get_cifra(cid)
    assert 'editada' in updated['conteudo']
    assert get_cifra_user_draft(cid, uid) is None

    upsert_cifra_user_draft(cid, uid, draft_fields)
    assert delete_cifra_user_draft(cid, uid)
    assert get_cifra_user_draft(cid, uid) is None

    from blueprints.cifras import enrich_cifra_for_tocar

    upsert_cifra_user_draft(cid, uid, draft_fields)
    enriched = enrich_cifra_for_tocar(cifra, user_id=uid)
    assert enriched.get('has_personal_draft') is True
    assert enriched.get('html_mine')
    assert 'sp-chord">A<' in enriched['html_mine']
    assert 'sp-chord">G<' in enriched['html']

    print('ok enrich_cifra_for_tocar com rascunho pessoal')
    print('ok rascunho pessoal create/merge/publish/discard')
    print('Todos os testes cifra_draft passaram.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
