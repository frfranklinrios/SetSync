"""Link público da setlist — letras para cantores/público."""
from __future__ import annotations

import re
import secrets
from typing import Any

from chordpro import parse_chordpro_directive
from db import get_band, get_band_vocalist, get_band_vocalists
from models_setlist import get_setlist, get_setlist_cifras
from util import format_text_chords_br, pychord_transpose_text, sanitize_tab_html_artifacts

CHORD_INLINE_RE = re.compile(r'\[[^\]]+\]')
PARENTHETICAL_RE = re.compile(r'\([^)]*\)')


def _new_share_token() -> str:
    return secrets.token_urlsafe(18)


def get_setlist_by_public_token(token: str) -> dict | None:
    if not token or len(token) < 12:
        return None
    from db import get_db

    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM setlists WHERE public_share_token = ? AND public_share_enabled = 1',
        (token.strip(),),
    )
    row = c.fetchone()
    db.close()
    return dict(row) if row else None


def set_setlist_public_share(setlist_id, enabled: bool) -> str | None:
    """Ativa/desativa link público. Retorna token quando ativo."""
    from db import get_db

    db = get_db()
    c = db.cursor()
    if enabled:
        c.execute('SELECT public_share_token FROM setlists WHERE id = ?', (setlist_id,))
        row = c.fetchone()
        token = (row['public_share_token'] if row else None) or _new_share_token()
        c.execute(
            'UPDATE setlists SET public_share_enabled = 1, public_share_token = ? WHERE id = ?',
            (token, setlist_id),
        )
    else:
        c.execute(
            'UPDATE setlists SET public_share_enabled = 0 WHERE id = ?',
            (setlist_id,),
        )
        token = None
    db.commit()
    db.close()
    return token if enabled else None


def rotate_setlist_public_token(setlist_id) -> str | None:
    """Gera novo token (link antigo deixa de funcionar). Só se compartilhamento ativo."""
    from db import get_db

    token = _new_share_token()
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE setlists SET public_share_token = ?, public_share_enabled = 1
           WHERE id = ?''',
        (token, setlist_id),
    )
    db.commit()
    db.close()
    return token


def clean_lyrics_for_public(text: str) -> str:
    """Remove parênteses e anotações entre parênteses das letras públicas."""
    if not text:
        return ''
    out = PARENTHETICAL_RE.sub('', text)
    out = out.replace('(', '').replace(')', '')
    lines = []
    for raw in out.split('\n'):
        line = re.sub(r'[ \t]+', ' ', raw).strip()
        lines.append(line)
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def conteudo_to_lyrics_plain(conteudo: str) -> str:
    """Remove acordes e diretivas; preserva letra e quebras de seção."""
    text = sanitize_tab_html_artifacts((conteudo or '').replace('\r\n', '\n'))
    lines_out: list[str] = []
    for raw in text.split('\n'):
        stripped = raw.strip()
        if not stripped:
            lines_out.append('')
            continue
        directive = parse_chordpro_directive(stripped)
        if directive:
            name, value = directive
            if name == 'comment' and value:
                lines_out.append(value)
            continue
        line = CHORD_INLINE_RE.sub('', raw)
        lines_out.append(line.rstrip())
    while lines_out and not lines_out[-1].strip():
        lines_out.pop()
    return clean_lyrics_for_public('\n'.join(lines_out))


def lyrics_from_cifra(cifra: dict, vocalist_id: str | None = None) -> str:
    from blueprints.cifras import (
        _group_cifra_data,
        _load_best_structured_cifra,
        cifra_transpose_semitones,
    )

    semi = cifra_transpose_semitones(cifra, vocalist_id=vocalist_id)
    data = _load_best_structured_cifra(cifra, semi)
    if data:
        blocks: list[str] = []
        for group in _group_cifra_data(data):
            parts = []
            for item in group:
                t = str(item.get('texto_letra') or '')
                if t:
                    parts.append(t)
            line = ''.join(parts).strip()
            if line:
                blocks.append(line)
        if blocks:
            return clean_lyrics_for_public('\n\n'.join(blocks))

    body = cifra.get('conteudo') or ''
    if semi:
        body = pychord_transpose_text(body, semi)
    body = format_text_chords_br(body)
    return conteudo_to_lyrics_plain(body)


def prepare_public_letras_payload(token: str) -> dict[str, Any] | None:
    setlist = get_setlist_by_public_token(token)
    if not setlist:
        return None

    band = get_band(setlist['band_id'])
    if not band:
        return None

    cifras_raw = get_setlist_cifras(setlist['id'])
    if not cifras_raw:
        return None

    from blueprints.cifras import cifra_display_key, vocalist_entry_display_name

    vocalists = get_band_vocalists(band['id'])
    default_vid = vocalists[0]['id'] if vocalists else None
    songs: list[dict[str, Any]] = []

    for i, c in enumerate(cifras_raw, start=1):
        vid = c.get('setlist_vocalist_id') or default_vid
        v = get_band_vocalist(vid) if vid else None
        songs.append({
            'index': i,
            'titulo': c.get('titulo') or 'Sem título',
            'artista': (c.get('artista') or '').strip(),
            'display_key': (
                cifra_display_key(c, vocalist_id=vid) if c.get('tom_original') else ''
            ),
            'vocalist_name': vocalist_entry_display_name(v) if v else '',
            'lyrics': lyrics_from_cifra(c, vocalist_id=vid),
        })

    from band_logos import band_has_logo, band_logo_data_uri

    return {
        'setlist': setlist,
        'band': band,
        'songs': songs,
        'band_has_logo': band_has_logo(band),
        'band_logo_data_uri': band_logo_data_uri(band),
    }
