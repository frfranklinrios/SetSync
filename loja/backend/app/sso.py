"""SSO com a mesma conta do app Uníssono (token itsdangerous, salt loja-sso)."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app import config


def _serializer() -> URLSafeTimedSerializer:
    if not config.SECRET_KEY:
        raise HTTPException(503, "SSO Uníssono não configurado.")
    return URLSafeTimedSerializer(config.SECRET_KEY, salt="loja-sso")


def verificar_token(token: str) -> dict[str, Any] | None:
    if not token:
        return None
    try:
        data = _serializer().loads(token, max_age=172800)
    except (BadSignature, SignatureExpired, TypeError, HTTPException):
        return None
    uid = data.get("uid")
    if not uid:
        return None
    data["uid"] = str(uid)
    return data


_VERDADEIRO = {True, "True", "true", 1, "1"}


def eh_admin_loja(usuario: dict[str, Any] | None) -> bool:
    """O master do Uníssono (SETSYNC_SUPERADMIN_*) administra a loja."""
    if not usuario:
        return False
    if usuario.get("is_loja_admin") in _VERDADEIRO or usuario.get("is_superadmin") in _VERDADEIRO:
        return True
    username = str(usuario.get("username") or "").strip().lower()
    email = str(usuario.get("email") or "").strip().lower()
    if username and username in config.LOJA_ADMIN_USERNAMES:
        return True
    if email and email in config.LOJA_ADMIN_EMAILS:
        return True
    return False


def exigir_admin(request: Request) -> dict[str, Any]:
    secret = request.headers.get("X-Admin-Secret") or ""
    if config.LOJA_ADMIN_SECRET and secret == config.LOJA_ADMIN_SECRET:
        return {"uid": "admin", "is_superadmin": True, "is_loja_admin": True}
    usuario = usuario_do_request(request)
    if eh_admin_loja(usuario):
        usuario["is_superadmin"] = True
        usuario["is_loja_admin"] = True
        return usuario
    raise HTTPException(403, "Área restrita ao administrador da loja.")


def usuario_do_request(request: Request) -> dict[str, Any]:
    auth = request.headers.get("Authorization") or ""
    token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    usuario = verificar_token(token)
    if usuario:
        return usuario
    cookie = request.cookies.get("session")
    if cookie:
        usuario = _usuario_via_cookie(cookie)
        if usuario:
            return usuario
    login = f"{config.UNISSONO_PUBLIC_URL}/auth/login?next={config.LOJA_PUBLIC_URL}"
    raise HTTPException(401, f"Entre com sua conta Uníssono para comprar. {login}")


def _usuario_via_cookie(cookie: str) -> dict[str, Any] | None:
    try:
        with httpx.Client(timeout=8.0) as client:
            res = client.get(
                f"{config.UNISSONO_INTERNAL_URL}/auth/me",
                cookies={"session": cookie},
                headers={"Host": "unissono.app", "Accept": "application/json"},
            )
    except httpx.HTTPError:
        return None
    if res.status_code != 200:
        return None
    data = res.json()
    if not data.get("autenticado"):
        return None
    token = str(data.get("loja_token") or "")
    return verificar_token(token) or {
        "uid": str((data.get("usuario") or {}).get("id") or ""),
        **(data.get("usuario") or {}),
    }
