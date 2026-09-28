"""Varre URLs selecionadas no AliExpress/Shopee com delay e User-Agent real."""

from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app import config

log = logging.getLogger("unissono.loja.scraper")

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": _UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
}


def _path_fonte() -> Path:
    persistido = Path(config.LOJA_DATA_DIR) / "fonte_produtos.json"
    if persistido.is_file():
        return persistido
    return Path(__file__).with_name("fonte_produtos.json")


def carregar_fonte() -> list[dict[str, Any]]:
    data = json.loads(_path_fonte().read_text(encoding="utf-8"))
    return list(data.get("produtos") or [])


def salvar_fonte(produtos: list[dict[str, Any]]) -> None:
    dest = Path(config.LOJA_DATA_DIR) / "fonte_produtos.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps({"produtos": produtos}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _float(valor: object, default: float = 0.0) -> float:
    if valor is None or valor == "":
        return default
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return default


def _meta(soup: BeautifulSoup, *keys: str) -> str:
    for key in keys:
        tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
        if tag and tag.get("content"):
            return str(tag["content"]).strip()
    return ""


def _json_embutido(html: str) -> dict[str, Any]:
    for padrao in (
        r"window\.runParams\s*=\s*(\{.+?\});",
        r"window\.__INIT_DATA__\s*=\s*(\{.+?\});",
        r"window\._dida_config_\s*=\s*(\{.+?\});",
    ):
        m = re.search(padrao, html, re.S)
        if not m:
            continue
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
    return {}


def _json_ld_produto(soup: BeautifulSoup) -> dict[str, Any]:
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        bruto = (tag.string or tag.get_text() or "").strip()
        if not bruto:
            continue
        try:
            data = json.loads(bruto)
        except json.JSONDecodeError:
            continue
        itens = data if isinstance(data, list) else [data]
        for item in itens:
            if not isinstance(item, dict):
                continue
            tipo = str(item.get("@type") or "")
            if "Product" in tipo:
                return item
    return {}


def _preco_valido(valor: float, *, brl: bool = False) -> float:
    teto = 4000.0 if brl else 800.0
    piso = 2.0 if brl else 0.5
    if piso <= valor <= teto:
        return valor
    return 0.0


def _precos_no_html(html: str) -> float:
    for padrao in (
        r'"actMinPrice"\s*:\s*"?(?P<p>[\d.]+)',
        r'"minActivityAmount"\s*:\s*"?(?P<p>[\d.]+)',
        r'"salePriceAmount"\s*:\s*"?(?P<p>[\d.]+)',
        r'"minPrice"\s*:\s*"?(?P<p>[\d.]+)',
        r'"formattedPrice"\s*:\s*"US\s*\$?\s*(?P<p>[\d.,]+)',
        r'"formatedPrice"\s*:\s*"US\s*\$?\s*(?P<p>[\d.,]+)',
        r'"price"\s*:\s*"?(?P<p>[\d.]+)"?',
        r"US\s*\$\s*(?P<p>[\d]+(?:\.\d{1,2})?)",
    ):
        m = re.search(padrao, html, re.I)
        if not m:
            continue
        preco = _preco_valido(_float(m.group("p").replace(",", "")))
        if preco:
            return preco
    return 0.0


def _slug(texto: str) -> str:
    bruto = re.sub(r"[^a-z0-9]+", "-", (texto or "").lower())
    return bruto.strip("-")[:48] or "produto"


def _id_da_url(url: str) -> str:
    m = re.search(r"/item/(\d+)", url)
    if m:
        return f"ali-{m.group(1)}"
    m = re.search(r"/product/(\d+)", url)
    if m:
        return f"shp-{m.group(1)}"
    m = re.search(r"(\d{10,})", url)
    if m:
        return f"item-{m.group(1)}"
    return ""


def _categoria_do_titulo(titulo: str) -> str:
    from app.categorias import categoria_do_texto

    return categoria_do_texto(titulo)


def _marca_do_titulo(titulo: str) -> str:
    t = (titulo or "").lower()
    if "m-vave" in t or "mvave" in t:
        return "M-Vave"
    if "nux" in t:
        return "NUX"
    if "joyo" in t:
        return "JOYO"
    if "d'addario" in t or "daddario" in t:
        return "D'Addario"
    primeira = re.split(r"[\s\-/|]+", titulo or "")
    if primeira and 2 <= len(primeira[0]) <= 18:
        return primeira[0][:24]
    return "Uníssono"


def extrair_da_pagina(html: str, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    ld = _json_ld_produto(soup)
    offers = ld.get("offers") if isinstance(ld.get("offers"), dict) else {}
    if isinstance(ld.get("offers"), list) and ld["offers"]:
        offers = ld["offers"][0] if isinstance(ld["offers"][0], dict) else {}

    titulo = (
        _meta(soup, "og:title", "twitter:title")
        or str(ld.get("name") or "")
        or (soup.title.string if soup.title else "")
    )
    imagem = _meta(soup, "og:image", "twitter:image")
    if not imagem and isinstance(ld.get("image"), str):
        imagem = ld["image"]
    if not imagem and isinstance(ld.get("image"), list) and ld["image"]:
        imagem = str(ld["image"][0])

    moeda = (
        _meta(soup, "product:price:currency", "og:price:currency")
        or str(offers.get("priceCurrency") or "USD")
    ).upper()
    preco = _float(_meta(soup, "product:price:amount", "og:price:amount")) or _float(offers.get("price"))
    frete = 0.0
    estoque = None
    sku = str(ld.get("sku") or "")

    blob = _json_embutido(html)
    data = blob.get("data") if isinstance(blob.get("data"), dict) else blob
    if isinstance(data, dict):
        titulo = titulo or str(data.get("title") or data.get("subject") or "")
        price_mod = data.get("priceModule") or data.get("price") or {}
        if isinstance(price_mod, dict):
            preco = preco or _float(
                price_mod.get("minActivityAmount")
                or price_mod.get("minPrice")
                or price_mod.get("formatedActivityPrice")
                or price_mod.get("formatedPrice")
            )
        ship = data.get("shippingModule") or data.get("shipping") or {}
        if isinstance(ship, dict):
            frete = _float(ship.get("freightAmount") or (ship.get("freight") or {}).get("value"))
        qty = data.get("quantityModule") or data.get("inventory") or {}
        if isinstance(qty, dict) and qty.get("totalAvailableInventory") is not None:
            estoque = int(_float(qty.get("totalAvailableInventory")))
        sku = sku or str(data.get("productId") or data.get("itemId") or "")

    if not preco:
        preco = _precos_no_html(html)

    brl = moeda in {"BRL", "R$", "REAL"} or "shopee.com.br" in url
    preco = _preco_valido(preco, brl=brl)
    if brl and preco:
        from app.cambio import usd_brl

        cambio = usd_brl() or 5.5
        preco = round(preco / cambio, 2)

    if imagem and str(imagem).startswith("//"):
        imagem = "https:" + imagem
    imagem = str(imagem or "")

    return {
        "url": url,
        "titulo": re.sub(r"\s+", " ", (titulo or "").replace("| AliExpress", "").strip())[:160],
        "imagem_url": imagem,
        "preco_base_usd": preco,
        "frete_usd": frete,
        "estoque": estoque,
        "sku": sku,
        "moeda": moeda,
    }


async def _baixar(client: httpx.AsyncClient, url: str) -> str:
    res = await client.get(url, headers=_HEADERS, follow_redirects=True)
    res.raise_for_status()
    return res.text


async def varrer_produto(seed: dict[str, Any]) -> dict[str, Any]:
    item = dict(seed)
    url = str(seed.get("url") or "").strip()
    if not url:
        item["fonte"] = "semente"
        return item
    await asyncio.sleep(random.uniform(1.8, 4.5))
    try:
        async with httpx.AsyncClient(timeout=config.SCRAPER_TIMEOUT) as client:
            html = await _baixar(client, url)
        extraido = extrair_da_pagina(html, url)
        preco_pagina = extraido.get("preco_base_usd")
        if preco_pagina and "/item/" in url:
            item["preco_base_usd"] = preco_pagina
            item["fonte"] = "aliexpress"
        else:
            item["fonte"] = "semente"
        if extraido.get("frete_usd"):
            item["frete_usd"] = extraido["frete_usd"]
        if extraido.get("estoque") is not None:
            item["estoque"] = extraido["estoque"]
        if extraido.get("imagem_url") and str(extraido["imagem_url"]).startswith("https://"):
            item["imagem_url"] = extraido["imagem_url"]
        if extraido.get("titulo") and len(extraido["titulo"]) > 8:
            item["titulo"] = extraido["titulo"][:160]
        log.info("Scrape %s fonte=%s preco=%s", item.get("id"), item.get("fonte"), item.get("preco_base_usd"))
    except Exception as exc:
        log.warning("Scrape falhou %s: %s", item.get("id"), exc)
        item["fonte"] = "semente"
    return item


async def varrer_todos() -> list[dict[str, Any]]:
    seeds = carregar_fonte()
    saida: list[dict[str, Any]] = []
    for seed in seeds:
        saida.append(await varrer_produto(seed))
    return saida


def _titulo_da_url(url: str) -> str:
    m = re.search(r"wholesale-([^/.]+)", url or "")
    if m:
        return m.group(1).replace("-", " ").title()[:160]
    m = re.search(r"/item/(\d+)", url or "")
    if m:
        return f"Produto AliExpress {m.group(1)}"
    return ""


def _montar_importado(url: str, extraido: dict[str, Any], categoria: str = "", marca: str = "") -> dict[str, Any]:
    titulo = extraido.get("titulo") or _titulo_da_url(url) or "Produto do fornecedor"
    if titulo.lower() in {"produto do fornecedor", "aliexpress", "captcha verification"}:
        titulo = _titulo_da_url(url) or titulo
    pid = _id_da_url(url) or _slug(titulo)
    preco = float(extraido.get("preco_base_usd") or 0)
    frete = float(extraido.get("frete_usd") or 0) or (7.5 if preco else 0)
    estoque = extraido.get("estoque")
    return {
        "id": pid[:80],
        "sku": str(extraido.get("sku") or pid).upper()[:40],
        "titulo": titulo[:160],
        "categoria": (categoria or _categoria_do_titulo(titulo))[:40],
        "marca": (marca or _marca_do_titulo(titulo))[:40],
        "imagem_url": extraido.get("imagem_url") or "",
        "url": url,
        "preco_base_usd": preco,
        "frete_usd": frete,
        "estoque": int(estoque if estoque is not None else 12),
        "fonte": "fornecedor" if preco else "semente",
    }


async def importar_url(url: str, *, categoria: str = "", marca: str = "") -> dict[str, Any]:
    destino = (url or "").strip()
    if not destino.startswith("http"):
        raise ValueError("Informe o link completo do produto no AliExpress ou Shopee.")
    async with httpx.AsyncClient(timeout=config.SCRAPER_TIMEOUT, follow_redirects=True, headers=_HEADERS) as client:
        res = await client.get(destino)
        res.raise_for_status()
        final = str(res.url)
        html = res.text
    extraido = extrair_da_pagina(html, final)
    produto = _montar_importado(final, extraido, categoria=categoria, marca=marca)
    log.info("Import %s preco=%s titulo=%s", produto["id"], produto["preco_base_usd"], produto["titulo"][:40])
    return produto
