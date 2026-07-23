"""Serve screenshots de marketing gerados (BR / gospel / estúdio)."""

from __future__ import annotations

from flask import Blueprint, abort, send_file

from marketing_shots import (
    PACK_BR,
    PACK_ESTUDIO,
    PACK_GOSPEL,
    resolve_shot_path,
)

marketing_shots_bp = Blueprint('marketing_shots', __name__, url_prefix='/marketing/shots')

_ALLOWED_PACKS = frozenset({PACK_BR, PACK_GOSPEL, PACK_ESTUDIO})


@marketing_shots_bp.route('/<pack>/<name>.png')
def serve(pack: str, name: str):
    pack = (pack or '').strip().lower()
    name = (name or '').strip().lower().replace('..', '')
    if pack not in _ALLOWED_PACKS or not name or '/' in name:
        abort(404)
    path = resolve_shot_path(pack, name)
    if not path or not path.is_file():
        abort(404)
    return send_file(path, mimetype='image/png', max_age=3600, conditional=True)
