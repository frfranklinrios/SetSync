"""Catálogo: ingestão do scraper → DuckDB → Parquet → JSON da API."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app import config
from app.cambio import atualizar_cambio, usd_brl
from app.cj import buscar_catalogo as buscar_catalogo_cj
from app.db import connect, exportar_parquet, get_meta, locked, set_meta
from app.models import CatalogoStatus, Produto, ProdutoAdminIn
from app.scraper import carregar_fonte, salvar_fonte, varrer_todos

log = logging.getLogger("unissono.loja.catalogo")


def _preco_venda(base_usd: float, frete_usd: float) -> tuple[float, float]:
    custo = round((float(base_usd) + float(frete_usd)) * usd_brl(), 2)
    venda = round(custo * config.MARGEM_LUCRO, 2)
    return custo, venda


def upsert_produtos(itens: list[dict[str, Any]]) -> int:
    agora = datetime.now(UTC).replace(tzinfo=None)
    cambio = usd_brl()
    with locked():
        con = connect()
        try:
            for raw in itens:
                base = float(raw.get("preco_base_usd") or 0)
                frete = float(raw.get("frete_usd") or 0)
                custo = round((base + frete) * cambio, 2)
                venda = round(custo * config.MARGEM_LUCRO, 2)
                if venda <= 0:
                    continue
                con.execute(
                    """
                    INSERT INTO catalogo (
                        id, sku, titulo, categoria, marca, imagem_url, url_fornecedor,
                        preco_base, custo_frete, custo_aquisicao, preco_venda, estoque,
                        fonte, atualizado_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (id) DO UPDATE SET
                        sku = excluded.sku,
                        titulo = excluded.titulo,
                        categoria = excluded.categoria,
                        marca = excluded.marca,
                        imagem_url = excluded.imagem_url,
                        url_fornecedor = excluded.url_fornecedor,
                        preco_base = excluded.preco_base,
                        custo_frete = excluded.custo_frete,
                        custo_aquisicao = excluded.custo_aquisicao,
                        preco_venda = excluded.preco_venda,
                        estoque = excluded.estoque,
                        fonte = excluded.fonte,
                        atualizado_em = excluded.atualizado_em
                    """,
                    [
                        raw["id"],
                        raw.get("sku") or raw["id"],
                        raw.get("titulo") or raw["id"],
                        raw.get("categoria") or "Acessórios",
                        raw.get("marca") or "Uníssono",
                        raw.get("imagem_url") or "",
                        raw.get("url") or raw.get("url_fornecedor") or "",
                        base,
                        frete,
                        custo,
                        venda,
                        int(raw.get("estoque") or 0),
                        raw.get("fonte") or "semente",
                        agora,
                    ],
                )
        finally:
            con.close()
    exportar_parquet("catalogo", "catalogo.parquet")
    set_meta("ultimo_scrape", agora.isoformat())
    return len(itens)


async def sincronizar_catalogo() -> int:
    await asyncio.to_thread(atualizar_cambio)
    itens: list[dict] = []
    if config.cj_configurada():
        itens = await asyncio.to_thread(buscar_catalogo_cj)
        if not itens:
            log.warning("CJ não devolveu produtos; mantendo catálogo atual")
            return len(listar_produtos())
    if not itens:
        itens = await varrer_todos()
    n = await asyncio.to_thread(upsert_produtos, itens)
    log.info(
        "Catálogo sincronizado: %s itens fonte=%s",
        n,
        "cj" if config.cj_configurada() else "scrape",
    )
    return n


def listar_admin() -> list[dict]:
    with locked():
        con = connect()
        try:
            rows = con.execute(
                """
                SELECT id, sku, titulo, categoria, marca, imagem_url, url_fornecedor,
                       preco_base, custo_frete, custo_aquisicao, preco_venda, estoque, fonte
                FROM catalogo
                ORDER BY categoria, titulo
                """
            ).fetchall()
        finally:
            con.close()
    chaves = (
        "id",
        "sku",
        "titulo",
        "categoria",
        "marca",
        "imagem_url",
        "url",
        "preco_base_usd",
        "frete_usd",
        "custo_aquisicao",
        "preco_venda",
        "estoque",
        "fonte",
    )
    return [dict(zip(chaves, row)) for row in rows]


def salvar_produto_admin(item: ProdutoAdminIn) -> dict:
    raw = item.model_dump()
    raw["fonte"] = "manual"
    upsert_produtos([raw])
    atuais = carregar_fonte()
    resto = [p for p in atuais if p.get("id") != item.id]
    resto.append(raw)
    salvar_fonte(resto)
    return next(p for p in listar_admin() if p["id"] == item.id)


def remover_produto(produto_id: str) -> None:
    with locked():
        con = connect()
        try:
            con.execute("DELETE FROM catalogo WHERE id = ?", [produto_id])
        finally:
            con.close()
    exportar_parquet("catalogo", "catalogo.parquet")
    salvar_fonte([p for p in carregar_fonte() if p.get("id") != produto_id])


def _rows() -> list[tuple]:
    with locked():
        con = connect()
        try:
            return list(
                con.execute(
                    """
                    SELECT id, sku, titulo, categoria, marca, imagem_url,
                           preco_venda, custo_aquisicao, estoque, fonte
                    FROM catalogo
                    ORDER BY categoria, titulo
                    """
                ).fetchall()
            )
        finally:
            con.close()


def listar_produtos() -> list[Produto]:
    produtos: list[Produto] = []
    for row in _rows():
        venda = float(row[6] or 0)
        produtos.append(
            Produto(
                id=str(row[0]),
                sku=str(row[1] or row[0]),
                nome=str(row[2]),
                categoria=str(row[3] or "Acessórios"),
                marca=str(row[4] or "Uníssono"),
                imagem_url=str(row[5] or ""),
                preco_venda=venda,
                preco_de=round(venda * 1.18, 2) if venda else None,
                custo_aquisicao=float(row[7] or 0),
                estoque=float(row[8] or 0),
                fonte=str(row[9] or "fornecedor"),
            )
        )
    return produtos


def produto_por_id(produto_id: str) -> Produto | None:
    for item in listar_produtos():
        if item.id == produto_id:
            return item
    return None


def status_catalogo() -> CatalogoStatus:
    produtos = listar_produtos()
    return CatalogoStatus(
        fonte="parquet",
        quantidade=len(produtos),
        mp_configurada=config.mp_configurada(),
        ultimo_scrape=get_meta("ultimo_scrape"),
        usd_brl=usd_brl(),
        cj_configurada=config.cj_configurada(),
        erro=None if produtos else "Catálogo vazio. Rode o scraper.",
    )
