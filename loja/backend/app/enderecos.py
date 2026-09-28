"""Endereço de entrega salvo por conta Uníssono."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from app.db import connect, locked
from app.models import ClientePedido


def salvar_endereco(usuario_id: str, cliente: ClientePedido) -> None:
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    payload = cliente.model_dump()
    with locked():
        con = connect()
        try:
            con.execute(
                """
                INSERT INTO enderecos (usuario_id, payload, atualizado_em)
                VALUES (?, ?, ?)
                ON CONFLICT (usuario_id) DO UPDATE SET
                    payload = excluded.payload,
                    atualizado_em = excluded.atualizado_em
                """,
                [usuario_id, json.dumps(payload, ensure_ascii=False), agora],
            )
        finally:
            con.close()


def obter_endereco(usuario_id: str) -> dict | None:
    with locked():
        con = connect()
        try:
            row = con.execute(
                "SELECT payload FROM enderecos WHERE usuario_id = ?",
                [usuario_id],
            ).fetchone()
        finally:
            con.close()
    if not row:
        return None
    payload = row[0]
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict):
        return payload
    return None
