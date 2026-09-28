"""Ao confirmar o Pix/cartão, dispara o pedido no fornecedor (CJ)."""

from __future__ import annotations

import logging

from app import config
from app.catalogo import produto_por_id
from app.cj import criar_pedido_fornecedor

log = logging.getLogger("unissono.loja.fulfillment")


def despachar(registro: dict) -> dict:
    if registro.get("fulfillment", {}).get("ok"):
        return registro["fulfillment"]
    if not config.cj_configurada():
        info = {
            "ok": False,
            "erro": "Cadastre CJ_API_KEY (conta PF no CJ Dropshipping) para o fornecedor enviar sozinho.",
        }
        registro["fulfillment"] = info
        return info
    itens_cj = []
    for item in registro.get("itens") or []:
        produto = produto_por_id(str(item.get("produto_id") or ""))
        if not produto:
            continue
        fonte = (produto.fonte or "").lower()
        sku = str(produto.sku or "")
        if fonte != "cj" and not str(produto.id).startswith("cj-"):
            continue
        itens_cj.append({"sku": sku, "quantidade": item.get("quantidade") or 1})
    if not itens_cj:
        info = {
            "ok": False,
            "erro": "Este pedido não tem produto do CJ. Sincronize o catálogo do fornecedor.",
        }
        registro["fulfillment"] = info
        return info
    try:
        info = criar_pedido_fornecedor(
            pedido_id=str(registro.get("id")),
            cliente=registro.get("cliente") or {},
            itens=itens_cj,
        )
    except Exception as exc:
        log.exception("CJ não criou o pedido %s", registro.get("id"))
        info = {"ok": False, "erro": str(exc)[:240]}
    registro["fulfillment"] = info
    if info.get("ok"):
        registro["status"] = "enviado_fornecedor"
        registro["mensagem"] = (
            "Pagamento ok. Pedido enviado ao fornecedor para despacho."
        )
    return info
