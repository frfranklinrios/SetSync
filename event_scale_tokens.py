"""Tokens assinados para aceitar/recusar escalação sem login."""

from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SALT = "event-scale-response"
SALT_GUEST = "event-guest-scale-response"
MAX_AGE = 60 * 60 * 24 * 14  # 14 dias


def _serializer(salt: str = SALT) -> URLSafeTimedSerializer:
    from flask import current_app

    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=salt)


def make_scale_response_token(event_id: str, user_id: str) -> str:
    return _serializer().dumps({"event_id": str(event_id), "user_id": str(user_id)})


def verify_scale_response_token(token: str | None) -> tuple[str, str] | None:
    if not token:
        return None
    try:
        data = _serializer().loads(token, max_age=MAX_AGE)
    except (BadSignature, SignatureExpired, TypeError):
        return None
    eid = data.get("event_id")
    uid = data.get("user_id")
    if not eid or not uid:
        return None
    return str(eid), str(uid)


def make_guest_scale_token(event_id: str, guest_id: str) -> str:
    return _serializer(SALT_GUEST).dumps(
        {"event_id": str(event_id), "guest_id": str(guest_id), "kind": "guest"}
    )


def verify_guest_scale_token(token: str | None) -> tuple[str, str] | None:
    """Retorna (event_id, guest_id) ou None."""
    if not token:
        return None
    try:
        data = _serializer(SALT_GUEST).loads(token, max_age=MAX_AGE)
    except (BadSignature, SignatureExpired, TypeError):
        return None
    if data.get("kind") != "guest":
        return None
    eid = data.get("event_id")
    gid = data.get("guest_id")
    if not eid or not gid:
        return None
    return str(eid), str(gid)
