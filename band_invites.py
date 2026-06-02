"""Tokens de convite para entrada em banda (cadastro ou login)."""
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

INVITE_SALT = 'band-invite'
INVITE_MAX_AGE = 60 * 60 * 24 * 14  # 14 dias


def _serializer() -> URLSafeTimedSerializer:
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=INVITE_SALT)


def make_band_invite_token(band_id: str) -> str:
    return _serializer().dumps({'band_id': str(band_id)})


def parse_band_invite_token(token: str | None, max_age: int = INVITE_MAX_AGE) -> str | None:
    if not token or not str(token).strip():
        return None
    try:
        data = _serializer().loads(str(token).strip(), max_age=max_age)
        band_id = data.get('band_id') if isinstance(data, dict) else None
        return str(band_id) if band_id else None
    except (BadSignature, SignatureExpired, TypeError, KeyError):
        return None


def apply_band_invite(user_id: str, band_id: str | None) -> str | None:
    """Garante membro na banda. Retorna 'added', 'already' ou None se inválido."""
    if not user_id or not band_id:
        return None
    from db import get_band, is_band_member, add_band_member
    if not get_band(band_id):
        return None
    if is_band_member(band_id, user_id):
        return 'already'
    add_band_member(band_id, user_id)
    return 'added'
