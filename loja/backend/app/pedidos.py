"""Pedidos + webhook: ao aprovar, grava o lucro líquido no DuckDB."""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException

from app import config
from app.catalogo import produto_por_id
from app.db import connect, exportar_parquet, locked
from app.enderecos import salvar_endereco
from app.fulfillment import despachar
from app.ledger import gravar_transacao_financeira
from app.models import ItemPedidoOut, PedidoIn, PedidoOut
from app.pagamentos import consultar_pagamento, criar_preferencia, taxa_mercadopago

log = logging.getLogger("unissono.loja.pedidos")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def _validar_cliente(pedido: PedidoIn) -> None:
    cliente = pedido.cliente
    if not _EMAIL.match(cliente.email.strip()):
        raise HTTPException(400, "Informe um e-mail válido.")
    if len(_somente_digitos(cliente.telefone)) < 10:
        raise HTTPException(400, "Informe um celular válido com DDD.")
    if len(_somente_digitos(cliente.cep)) != 8:
        raise HTTPException(400, "Informe um CEP válido.")
    if len(_somente_digitos(cliente.cpf)) != 11:
        raise HTTPException(400, "Informe um CPF válido para o pagamento.")
    if cliente.uf.strip().upper() not in {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }:
        raise HTTPException(400, "UF inválida.")


def _salvar(registro: dict) -> None:
    agora = datetime.now(UTC).replace(tzinfo=None)
    with locked():
        con = connect()
        try:
            con.execute(
                """
                INSERT INTO pedidos (id, status, pagamento, total, custo_aquisicao, payload, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    status = excluded.status,
                    pagamento = excluded.pagamento,
                    total = excluded.total,
                    custo_aquisicao = excluded.custo_aquisicao,
                    payload = excluded.payload,
                    atualizado_em = excluded.atualizado_em
                """,
                [
                    registro["id"],
                    registro.get("status"),
                    registro.get("pagamento"),
                    float(registro.get("total") or 0),
                    float(registro.get("custo_aquisicao") or 0),
                    json.dumps(registro, ensure_ascii=False, default=str),
                    registro.get("criado_em", agora),
                    agora,
                ],
            )
        finally:
            con.close()
    exportar_parquet("pedidos", "historico_pedidos.parquet")


def _ler(pedido_id: str) -> dict:
    with locked():
        con = connect()
        try:
            row = con.execute(
                "SELECT payload FROM pedidos WHERE id = ?", [pedido_id]
            ).fetchone()
        finally:
            con.close()
    if not row:
        raise HTTPException(404, "Pedido não encontrado.")
    payload = row[0]
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict):
        return payload
    return json.loads(str(payload))


def _para_out(registro: dict) -> PedidoOut:
    itens = [ItemPedidoOut(**i) for i in registro.get("itens") or []]
    return PedidoOut(
        id=registro["id"],
        status=registro.get("status") or "aguardando_pagamento",
        total=float(registro.get("total") or 0),
        total_pix=float(registro.get("total_pix") or registro.get("total") or 0),
        itens=itens,
        checkout_url=registro.get("checkout_url") or "",
        mensagem=registro.get("mensagem") or "",
    )


def criar_pedido(pedido: PedidoIn, usuario: dict | None = None) -> PedidoOut:
    if not pedido.itens:
        raise HTTPException(400, "Carrinho vazio.")
    if not usuario or not usuario.get("uid"):
        raise HTTPException(401, "Entre com sua conta Uníssono para comprar.")
    if usuario.get("email"):
        pedido.cliente.email = str(usuario["email"])
    if usuario.get("nome") and len(str(usuario["nome"]).strip()) >= 3:
        pedido.cliente.nome = str(usuario["nome"]).strip()
    if (
        usuario.get("telefone")
        and len(_somente_digitos(str(usuario["telefone"]))) >= 10
    ):
        pedido.cliente.telefone = str(usuario["telefone"])
    _validar_cliente(pedido)
    if not config.mp_configurada():
        raise HTTPException(503, "Pagamento online indisponível no momento.")

    pagamento = (pedido.pagamento or "pix").lower()
    if pagamento not in {"pix", "cartao", "boleto"}:
        pagamento = "pix"

    itens_out: list[ItemPedidoOut] = []
    total = 0.0
    custo = 0.0
    for item in pedido.itens:
        produto = produto_por_id(item.produto_id)
        if not produto:
            raise HTTPException(404, f"Produto não encontrado: {item.produto_id}")
        if produto.estoque < item.quantidade:
            raise HTTPException(409, f"Sem estoque suficiente: {produto.nome}")
        preco_total = round(produto.preco_venda * item.quantidade, 2)
        custo_item = round(produto.custo_aquisicao * item.quantidade, 2)
        total = round(total + preco_total, 2)
        custo = round(custo + custo_item, 2)
        itens_out.append(
            ItemPedidoOut(
                produto_id=produto.id,
                nome=produto.nome,
                quantidade=item.quantidade,
                preco_unitario=produto.preco_venda,
                preco_total=preco_total,
                custo_aquisicao=custo_item,
            )
        )

    agora = datetime.now()
    pedido_id = f"UNI-{agora.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    registro = {
        "id": pedido_id,
        "status": "aguardando_pagamento",
        "criado_em": datetime.now(UTC).replace(tzinfo=None),
        "pagamento": pagamento,
        "total": total,
        "total_pix": total,
        "custo_aquisicao": custo,
        "itens": [i.model_dump() for i in itens_out],
        "cliente": pedido.cliente.model_dump(),
        "usuario_id": usuario.get("uid"),
        "usuario_username": usuario.get("username") or "",
        "preference_id": "",
        "checkout_url": "",
        "payment_id": "",
        "mensagem": "Redirecionando para o pagamento seguro do Mercado Pago.",
    }
    pref = criar_preferencia(
        pedido_id=pedido_id,
        itens=registro["itens"],
        cliente=pedido.cliente,
        pagamento=pagamento,
    )
    registro["preference_id"] = pref["preference_id"]
    registro["checkout_url"] = pref["checkout_url"]
    _salvar(registro)
    salvar_endereco(str(usuario.get("uid")), pedido.cliente)
    return _para_out(registro)


def listar_pedidos(limite: int = 50) -> list[dict]:
    with locked():
        con = connect()
        try:
            rows = con.execute(
                """
                SELECT id, status, pagamento, total, custo_aquisicao, payload, criado_em
                FROM pedidos
                ORDER BY criado_em DESC
                LIMIT ?
                """,
                [limite],
            ).fetchall()
        finally:
            con.close()
    saida = []
    for row in rows:
        payload = row[5]
        if isinstance(payload, str):
            payload = json.loads(payload)
        saida.append(
            {
                "id": row[0],
                "status": row[1],
                "pagamento": row[2],
                "total": float(row[3] or 0),
                "custo_aquisicao": float(row[4] or 0),
                "usuario_id": (payload or {}).get("usuario_id"),
                "cliente": (payload or {}).get("cliente") or {},
                "itens": (payload or {}).get("itens") or [],
                "fulfillment": (payload or {}).get("fulfillment") or {},
                "criado_em": str(row[6] or ""),
            }
        )
    return saida


def obter_pedido(pedido_id: str, payment_id: str | None = None) -> PedidoOut:
    registro = _ler(pedido_id)
    if payment_id and registro.get("status") != "pago":
        sincronizar_pagamento(pedido_id, payment_id)
        registro = _ler(pedido_id)
    return _para_out(registro)


def marcar_pago(pedido_id: str, pagamento_mp: dict) -> None:
    registro = _ler(pedido_id)
    status_mp = str(pagamento_mp.get("status") or "")
    payment_id = str(pagamento_mp.get("id") or "")
    registro["payment_id"] = payment_id
    registro["status_mp"] = status_mp
    if status_mp == "approved":
        registro["status"] = "pago"
        registro["pago_em"] = datetime.now(UTC).isoformat()
        registro["mensagem"] = "Pagamento confirmado. Pedido em separação."
        valor = float(
            pagamento_mp.get("transaction_amount") or registro.get("total") or 0
        )
        taxa = taxa_mercadopago(
            pagamento_mp, str(registro.get("pagamento") or "pix"), valor
        )
        gravar_transacao_financeira(
            pedido_id=pedido_id,
            valor_venda=valor,
            custo_aquisicao=float(registro.get("custo_aquisicao") or 0),
            taxa_mp=taxa,
            meio_pagamento=str(registro.get("pagamento") or ""),
            payment_id=payment_id,
        )
        despachar(registro)
    elif status_mp in {"pending", "in_process"}:
        registro["status"] = "aguardando_pagamento"
        registro["mensagem"] = "Pagamento em processamento."
    elif status_mp in {"rejected", "cancelled"}:
        registro["status"] = "falhou"
        registro["mensagem"] = "Pagamento não aprovado. Tente de novo pelo carrinho."
    _salvar(registro)


def sincronizar_pagamento(pedido_id: str, payment_id: str) -> PedidoOut:
    data = consultar_pagamento(payment_id)
    ref = str(data.get("external_reference") or "")
    if ref and ref != pedido_id:
        raise HTTPException(400, "Pagamento não corresponde a este pedido.")
    marcar_pago(pedido_id, data)
    return obter_pedido(pedido_id)


def processar_webhook(payload: dict, payment_id: str | None) -> None:
    pid = payment_id or str(
        (payload.get("data") or {}).get("id") or payload.get("id") or ""
    )
    if not pid or pid == "123456":
        return
    data = consultar_pagamento(pid)
    ref = str(data.get("external_reference") or "")
    if not ref:
        return
    try:
        marcar_pago(ref, data)
    except HTTPException:
        log.warning("Webhook MP pedido ausente %s", ref)
