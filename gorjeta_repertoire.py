"""Repertório público + pedidos de música na página de gorjeta."""

from __future__ import annotations

from typing import Any

from db import get_band_cifras
from models_setlist import get_band_setlists, get_setlist, get_setlist_cifras


def _song_row(c: dict) -> dict[str, Any]:
    if not isinstance(c, dict):
        c = dict(c)
    return {
        'id': str(c.get('id') or ''),
        'titulo': (c.get('titulo') or 'Sem título').strip(),
        'artista': (c.get('artista') or '').strip(),
    }


def resolve_public_repertoire(
    band: dict,
    *,
    setlist_id: str | None = None,
    event_id: str | None = None,
) -> dict[str, Any]:
    """Resolve setlist/repertório para a página pública do QR."""
    band_id = band['id']
    setlist = None

    sid = (setlist_id or '').strip() or None
    if not sid and event_id:
        try:
            from models_agenda import get_band_event
            ev = get_band_event(event_id)
            if ev and ev.get('band_id') == band_id and ev.get('setlist_id'):
                sid = str(ev['setlist_id'])
        except Exception:
            sid = None

    if sid:
        setlist = get_setlist(sid)
        if setlist and setlist.get('band_id') == band_id:
            songs = [_song_row(c) for c in get_setlist_cifras(sid)]
            return {
                'setlist_id': str(setlist['id']),
                'setlist_name': setlist.get('name') or 'Repertório',
                'songs': songs,
                'source': 'setlist',
            }

    setlists = [dict(s) for s in (get_band_setlists(band_id) or [])]
    if setlists:
        # Preferir a com mais músicas; fallback a primeira
        ranked = []
        for s in setlists:
            songs = [_song_row(c) for c in get_setlist_cifras(s['id'])]
            ranked.append((len(songs), s, songs))
        ranked.sort(key=lambda x: x[0], reverse=True)
        if ranked and ranked[0][0] > 0:
            _, chosen, songs = ranked[0]
            return {
                'setlist_id': str(chosen['id']),
                'setlist_name': chosen.get('name') or 'Repertório',
                'songs': songs,
                'source': 'latest_setlist',
            }

    songs = [_song_row(c) for c in get_band_cifras(band_id)]
    return {
        'setlist_id': None,
        'setlist_name': 'Repertório da banda',
        'songs': songs,
        'source': 'band' if songs else 'none',
    }
