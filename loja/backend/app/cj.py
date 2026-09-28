"""CJ Dropshipping: catálogo e pedido automático (conta PF, sem CNPJ)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app import config
from app.db import get_meta, set_meta

log = logging.getLogger("unissono.loja.cj")
_BASE = "https://developers.cjdropshipping.com/api2.0/v1"
_token_mem = {"access": "", "exp": ""}


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _token_valido() -> str:
    token = _token_mem["access"] or get_meta("cj_access_token") or ""
    exp = _token_mem["exp"] or get_meta("cj_access_exp") or ""
    if token and exp:
        try:
            ts = datetime.fromisoformat(exp.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts > _agora():
                _token_mem["access"] = token
                _token_mem["exp"] = exp
                return token
        except ValueError:
            pass
    refresh = get_meta("cj_refresh_token") or ""
    if refresh:
        try:
            data = _post("/authentication/refreshAccessToken", {"refreshToken": refresh}, auth=False)
            _guardar_token(data)
            return str(data.get("accessToken") or "")
        except Exception:
            log.warning("Refresh CJ falhou; pedindo token novo")
    data = _post("/authentication/getAccessToken", {"apiKey": config.CJ_API_KEY}, auth=False)
    _guardar_token(data)
    return str(data.get("accessToken") or "")


def _guardar_token(data: dict[str, Any]) -> None:
    if data.get("accessToken"):
        _token_mem["access"] = str(data["accessToken"])
    if data.get("accessTokenExpiryDate"):
        _token_mem["exp"] = str(data["accessTokenExpiryDate"])
    try:
        if data.get("accessToken"):
            set_meta("cj_access_token", str(data["accessToken"]))
        if data.get("refreshToken"):
            set_meta("cj_refresh_token", str(data["refreshToken"]))
        if data.get("accessTokenExpiryDate"):
            set_meta("cj_access_exp", str(data["accessTokenExpiryDate"]))
    except Exception as exc:
        log.warning("Não gravei token CJ no DuckDB: %s", exc)


def _unwrap(res: httpx.Response) -> Any:
    body = res.json()
    if not (body.get("success") or body.get("code") == 200):
        raise RuntimeError(str(body.get("message") or body.get("code") or "CJ recusou a chamada"))
    return body.get("data")


def _chamar(method: str, path: str, *, auth: bool, json_body: dict | None = None, params: dict | None = None) -> Any:
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["CJ-Access-Token"] = _token_valido()
        headers["platformToken"] = ""
    ultimo: Exception | None = None
    for tentativa in range(4):
        with httpx.Client(timeout=40.0) as client:
            res = client.request(method, f"{_BASE}{path}", headers=headers, json=json_body, params=params)
        if res.status_code == 429:
            time.sleep(2.0 * (tentativa + 1))
            ultimo = RuntimeError("CJ limitou as consultas (429)")
            continue
        res.raise_for_status()
        return _unwrap(res)
    raise ultimo or RuntimeError("CJ indisponível")


def _post(path: str, payload: dict, *, auth: bool = True) -> Any:
    return _chamar("POST", path, auth=auth, json_body=payload)


def _get(path: str, params: dict[str, Any]) -> Any:
    return _chamar("GET", path, auth=True, params=params)


def _produtos_da_busca(data: Any) -> list[dict[str, Any]]:
    grupos: list = []
    if isinstance(data, list):
        grupos = data
    elif isinstance(data, dict):
        grupos = data.get("content") or data.get("list") or data.get("records") or []
    saida: list[dict[str, Any]] = []
    for grupo in grupos:
        if not isinstance(grupo, dict):
            continue
        lista = grupo.get("productList")
        if isinstance(lista, list):
            saida.extend(x for x in lista if isinstance(x, dict))
        elif grupo.get("id") or grupo.get("pid"):
            saida.append(grupo)
    return saida


def _categoria(keyword: str, titulo: str = "") -> str:
    from app.categorias import categoria_do_texto

    return categoria_do_texto(keyword, titulo)


def _variante(item: dict[str, Any]) -> dict[str, Any] | None:
    variantes = item.get("variants") or item.get("productVariant") or item.get("variantList") or []
    if isinstance(variantes, dict):
        variantes = [variantes]
    for var in variantes:
        if not isinstance(var, dict):
            continue
        vid = str(var.get("vid") or var.get("variantId") or "")
        if not vid:
            continue
        estoque = int(float(var.get("inventoryNum") or var.get("variantQuantity") or var.get("inventory") or 0))
        preco = float(var.get("variantSellPrice") or var.get("variantPrice") or var.get("sellPrice") or 0)
        return {"vid": vid, "estoque": estoque, "preco": preco, "imagem": str(var.get("variantImage") or "")}
    return None


def _titulo(item: dict[str, Any], pid: str) -> str:
    bruto = item.get("nameEn") or item.get("productNameEn") or item.get("productName") or item.get("name") or pid
    if isinstance(bruto, list):
        bruto = next((x for x in bruto if isinstance(x, str) and x.strip()), pid)
    return str(bruto)[:160]


def _imagem(item: dict[str, Any], extra: str = "") -> str:
    img = extra or item.get("bigImage") or item.get("productImage") or ""
    if isinstance(img, list):
        img = img[0] if img else ""
    img = str(img or "")
    if img.startswith("//"):
        img = "https:" + img
    return img


def _enriquecer(item: dict[str, Any]) -> dict[str, Any]:
    pid = str(item.get("id") or item.get("pid") or "")
    if not pid:
        return item
    time.sleep(1.2)
    try:
        detalhe = _get("/product/query", {"pid": pid})
    except Exception as exc:
        log.warning("CJ detalhe %s falhou: %s", pid, exc)
        return item
    if isinstance(detalhe, dict):
        item = {**item, **detalhe, "id": pid}
    return item


def _normalizar(item: dict[str, Any], keyword: str) -> dict[str, Any] | None:
    item = _enriquecer(item)
    var = _variante(item)
    if not var or var["preco"] <= 0:
        return None
    pid = str(item.get("pid") or item.get("id") or var["vid"])
    return {
        "id": f"cj-{var['vid']}"[:80],
        "sku": var["vid"],
        "titulo": _titulo(item, pid),
        "categoria": _categoria(keyword, _titulo(item, pid)),
        "marca": "CJ",
        "imagem_url": _imagem(item, var.get("imagem") or ""),
        "url": f"https://www.cjdropshipping.com/product/{pid}.html",
        "preco_base_usd": round(float(var["preco"]), 2),
        "frete_usd": config.CJ_FRETE_USD,
        "estoque": max(int(var["estoque"] or 0), 1),
        "fonte": "cj",
    }


def preview_busca(keyword: str, *, tamanho: int = 12) -> list[dict[str, Any]]:
    if not config.cj_configurada():
        raise RuntimeError("CJ_API_KEY não configurada.")
    termo = (keyword or "").strip()
    if len(termo) < 2:
        raise ValueError("Digite pelo menos 2 letras para buscar.")
    data = _get("/product/listV2", {"page": 1, "size": max(1, min(tamanho, 20)), "keyWord": termo})
    saida = []
    for raw in _produtos_da_busca(data)[:tamanho]:
        pid = str(raw.get("id") or raw.get("pid") or "")
        preco = float(raw.get("sellPrice") or raw.get("nowPrice") or 0)
        if not pid:
            continue
        saida.append(
            {
                "pid": pid,
                "titulo": _titulo(raw, pid),
                "imagem_url": _imagem(raw),
                "preco_base_usd": round(preco, 2) if preco else 0,
                "estoque": int(float(raw.get("warehouseInventoryNum") or raw.get("listedNum") or 0)),
                "url": f"https://www.cjdropshipping.com/product/{pid}.html",
            }
        )
    return saida


def importar_pid(pid: str, *, categoria: str = "") -> dict[str, Any]:
    if not config.cj_configurada():
        raise RuntimeError("CJ_API_KEY não configurada.")
    bruto = {"id": (pid or "").strip()}
    if not bruto["id"]:
        raise ValueError("Informe o produto do CJ.")
    item = _normalizar(bruto, categoria or "produto")
    if not item:
        raise RuntimeError("Esse produto não tem preço/variante no CJ.")
    if categoria:
        item["categoria"] = categoria
    return item


def buscar_catalogo() -> list[dict[str, Any]]:
    if not config.cj_configurada():
        return []
    saida: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for i, keyword in enumerate(config.CJ_KEYWORDS):
        if i:
            time.sleep(1.2)
        try:
            data = _get(
                "/product/listV2",
                {"page": 1, "size": max(1, config.CJ_MAX_POR_BUSCA), "keyWord": keyword},
            )
        except Exception as exc:
            log.warning("CJ busca '%s' falhou: %s", keyword, exc)
            continue
        lista = _produtos_da_busca(data)
        for raw in lista[: config.CJ_MAX_POR_BUSCA]:
            if not isinstance(raw, dict):
                continue
            item = _normalizar(raw, keyword)
            if not item or item["id"] in vistos:
                continue
            vistos.add(item["id"])
            saida.append(item)
    log.info("CJ catálogo: %s produtos", len(saida))
    return saida


def criar_pedido_fornecedor(*, pedido_id: str, cliente: dict, itens: list[dict]) -> dict[str, Any]:
    if not config.cj_configurada():
        raise RuntimeError("CJ_API_KEY não configurada.")
    produtos = []
    for item in itens:
        vid = str(item.get("sku") or "")
        if not vid:
            continue
        produtos.append(
            {
                "vid": vid,
                "quantity": int(item.get("quantidade") or 1),
                "storeLineItemId": f"{pedido_id}-{vid[:12]}",
            }
        )
    if not produtos:
        raise RuntimeError("Nenhum item do pedido tem SKU do CJ.")
    cep = "".join(ch for ch in str(cliente.get("cep") or "") if ch.isdigit())
    payload = {
        "orderNumber": pedido_id,
        "shippingZip": cep,
        "shippingCountry": "Brazil",
        "shippingCountryCode": "BR",
        "shippingProvince": str(cliente.get("uf") or ""),
        "shippingCity": str(cliente.get("cidade") or ""),
        "shippingCounty": str(cliente.get("bairro") or ""),
        "shippingPhone": str(cliente.get("telefone") or ""),
        "shippingCustomerName": str(cliente.get("nome") or ""),
        "shippingAddress": f"{cliente.get('endereco') or ''} {cliente.get('numero') or ''}".strip(),
        "shippingAddress2": str(cliente.get("complemento") or ""),
        "taxId": "".join(ch for ch in str(cliente.get("cpf") or "") if ch.isdigit()),
        "email": str(cliente.get("email") or ""),
        "remark": f"Uníssono {pedido_id}",
        "payType": 2,
        "logisticName": config.CJ_LOGISTIC,
        "fromCountryCode": "CN",
        "platform": "API",
        "orderFlow": 1,
        "products": produtos,
    }
    data = _post("/shopping/order/createOrderV2", payload)
    if not isinstance(data, dict):
        data = {"raw": data}
    return {
        "ok": True,
        "fornecedor": "cj",
        "cj_order_id": str(data.get("orderId") or data.get("cjOrderId") or data.get("pid") or ""),
        "pay_url": str(data.get("cjPayUrl") or ""),
        "resposta": data,
    }
