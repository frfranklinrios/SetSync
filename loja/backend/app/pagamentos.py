"""Preferências de checkout Mercado Pago (Pix, cartão e boleto) via SDK oficial."""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urlencode

import mercadopago
from fastapi import HTTPException

from app import config

log = logging.getLogger("unissono.loja.mp")


def _somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def _sdk() -> mercadopago.SDK:
    token = config.mp_access_token()
    if not token:
        raise HTTPException(503, "Pagamento online indisponível no momento.")
    return mercadopago.SDK(token)


def _telefone(raw: str) -> dict[str, str]:
    d = _somente_digitos(raw)
    if d.startswith("55") and len(d) >= 12:
        d = d[2:]
    if len(d) < 10:
        return {"area_code": "11", "number": d or "999999999"}
    return {"area_code": d[:2], "number": d[2:]}


def _metodos(pagamento: str) -> dict[str, Any]:
    meio = (pagamento or "pix").lower()
    if meio == "pix":
        return {
            "excluded_payment_types": [
                {"id": "credit_card"},
                {"id": "debit_card"},
                {"id": "ticket"},
                {"id": "atm"},
            ],
            "default_payment_method_id": "pix",
        }
    if meio == "boleto":
        return {
            "excluded_payment_types": [
                {"id": "credit_card"},
                {"id": "debit_card"},
                {"id": "bank_transfer"},
                {"id": "atm"},
            ],
            "default_payment_method_id": "bolbradesco",
        }
    return {
        "excluded_payment_types": [{"id": "ticket"}, {"id": "atm"}],
        "installments": 12,
    }


def criar_preferencia(
    *,
    pedido_id: str,
    itens: list[dict[str, Any]],
    cliente: Any,
    pagamento: str,
) -> dict[str, str]:
    mp_itens = [
        {
            "id": str(item["produto_id"])[:64],
            "title": str(item["nome"])[:120],
            "quantity": int(item["quantidade"]),
            "currency_id": "BRL",
            "unit_price": float(item["preco_unitario"]),
        }
        for item in itens
    ]
    cep = _somente_digitos(cliente.cep)
    cpf = _somente_digitos(cliente.cpf)
    base = config.LOJA_PUBLIC_URL
    qs = urlencode({"pedido": pedido_id})
    notification = f"{base}/webhook/mercadopago"
    if config.MP_WEBHOOK_SECRET:
        notification += f"?secret={config.MP_WEBHOOK_SECRET}"

    payer: dict[str, Any] = {
        "name": cliente.nome.strip()[:80],
        "email": cliente.email.strip(),
        "phone": _telefone(cliente.telefone),
        "address": {
            "zip_code": cep,
            "street_name": cliente.endereco.strip()[:80],
            "street_number": str(cliente.numero).strip()[:10],
        },
    }
    if len(cpf) == 11:
        payer["identification"] = {"type": "CPF", "number": cpf}

    body: dict[str, Any] = {
        "items": mp_itens,
        "payer": payer,
        "external_reference": pedido_id,
        "statement_descriptor": "UNISSONO",
        "binary_mode": False,
        "auto_return": "approved",
        "back_urls": {
            "success": f"{base}/?pagamento=sucesso&{qs}",
            "failure": f"{base}/?pagamento=falha&{qs}",
            "pending": f"{base}/?pagamento=pendente&{qs}",
        },
        "notification_url": notification,
        "metadata": {"loja": "unissono", "pedido_id": pedido_id, "cpf": True},
        "payment_methods": _metodos(pagamento),
        "shipments": {
            "receiver_address": {
                "zip_code": cep,
                "street_name": cliente.endereco.strip()[:80],
                "street_number": str(cliente.numero).strip()[:10],
                "city_name": cliente.cidade.strip()[:60],
                "state_name": cliente.uf.strip().upper(),
            }
        },
    }

    data = _sdk().preference().create(body)
    resp = data.get("response") or {}
    if int(data.get("status") or 0) >= 400:
        log.warning("MP preference: %s", resp)
        detalhe = (
            resp.get("message") or resp.get("error") or "Falha ao iniciar pagamento."
        )
        raise HTTPException(502, f"Mercado Pago: {detalhe}")

    if config.MP_ENVIRONMENT == "sandbox":
        url = resp.get("sandbox_init_point") or resp.get("init_point") or ""
    else:
        url = resp.get("init_point") or resp.get("sandbox_init_point") or ""
    if not url:
        raise HTTPException(502, "Mercado Pago não retornou o link de pagamento.")
    return {"preference_id": str(resp.get("id") or ""), "checkout_url": url}


def consultar_pagamento(payment_id: str) -> dict[str, Any]:
    data = _sdk().payment().get(payment_id)
    resp = data.get("response") or {}
    if int(data.get("status") or 0) >= 400:
        raise HTTPException(502, "Não foi possível consultar o pagamento.")
    return resp


def taxa_mercadopago(pagamento: dict[str, Any], meio: str, valor: float) -> float:
    detalhes = pagamento.get("fee_details") or []
    if detalhes:
        return round(sum(float(f.get("amount") or 0) for f in detalhes), 2)
    liquido = (pagamento.get("transaction_details") or {}).get("net_received_amount")
    bruto = float(pagamento.get("transaction_amount") or valor or 0)
    if liquido is not None:
        return round(bruto - float(liquido), 2)
    aliquota = {
        "pix": config.TAXA_MP_PIX,
        "boleto": config.TAXA_MP_BOLETO,
        "cartao": config.TAXA_MP_CARTAO,
    }.get((meio or "pix").lower(), config.TAXA_MP_CARTAO)
    return round(bruto * aliquota, 2)
