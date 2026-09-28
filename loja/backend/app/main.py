"""Orquestração FastAPI: catálogo Parquet, Mercado Pago e ledger DuckDB."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.cambio import atualizar_cambio, usd_brl
from app.catalogo import (
    listar_admin,
    listar_produtos,
    remover_produto,
    salvar_produto_admin,
    sincronizar_catalogo,
    status_catalogo,
    upsert_produtos,
)
from app.cj import importar_pid, preview_busca
from app.db import init_db
from app.enderecos import obter_endereco, salvar_endereco
from app.ledger import gravar_transacao_financeira, resumo_competencia
from app.models import (
    CatalogoStatus,
    CjDisponibilizarIn,
    ClientePedido,
    ImportarUrlIn,
    LedgerLinha,
    PedidoIn,
    PedidoOut,
    Produto,
    ProdutoAdminIn,
)
from app.pedidos import criar_pedido, listar_pedidos, obter_pedido, processar_webhook
from app.scraper import carregar_fonte, importar_url
from app.sso import eh_admin_loja, exigir_admin, usuario_do_request

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("unissono.loja")


async def _rotina_scraper() -> None:
    await asyncio.sleep(2)
    if not listar_produtos():
        try:
            await sincronizar_catalogo()
        except Exception:
            log.exception("Falha no scrape inicial; usando semente")
            if not listar_produtos():
                upsert_produtos([{**p, "fonte": "semente"} for p in carregar_fonte()])
    while True:
        agora = datetime.now()
        alvo = agora.replace(
            hour=config.SCRAPER_HORA, minute=15, second=0, microsecond=0
        )
        if agora >= alvo:
            alvo += timedelta(hours=max(config.SCRAPER_INTERVALO_H, 1))
        await asyncio.sleep(max(30.0, (alvo - agora).total_seconds()))
        try:
            await sincronizar_catalogo()
        except Exception:
            log.exception("Falha no scrape agendado")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    try:
        await asyncio.to_thread(atualizar_cambio)
    except Exception:
        log.warning("Câmbio inicial indisponível")
    if not listar_produtos():
        upsert_produtos([{**p, "fonte": "semente"} for p in carregar_fonte()])
    task = asyncio.create_task(_rotina_scraper(), name="scraper-madrugada")
    yield
    task.cancel()


app = FastAPI(
    title="Uníssono Loja",
    description="Dropshipping PF: catálogo Parquet, Mercado Pago e Carnê-Leão via DuckDB.",
    version="1.1.0",
    lifespan=lifespan,
)

_cors = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8011,https://loja.unissono.app",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "unissono-loja",
        "mp_configurada": config.mp_configurada(),
        "cj_configurada": config.cj_configurada(),
        "fonte": "parquet",
    }


@app.get("/api/loja/status", response_model=CatalogoStatus)
def get_status() -> CatalogoStatus:
    return status_catalogo()


@app.get("/api/loja/produtos", response_model=list[Produto])
def get_produtos() -> list[Produto]:
    return listar_produtos()


@app.get("/api/loja/me")
def get_me(request: Request) -> dict[str, object]:
    try:
        usuario = usuario_do_request(request)
    except HTTPException:
        return {
            "autenticado": False,
            "login_url": f"{config.UNISSONO_PUBLIC_URL}/auth/login?next={config.LOJA_PUBLIC_URL}",
        }
    return {
        "autenticado": True,
        "usuario": {
            "id": usuario.get("uid"),
            "nome": usuario.get("nome") or usuario.get("username") or "",
            "email": usuario.get("email") or "",
            "telefone": usuario.get("telefone") or "",
            "username": usuario.get("username") or "",
            "is_superadmin": eh_admin_loja(usuario),
            "is_loja_admin": eh_admin_loja(usuario),
        },
        "token": request.headers.get("Authorization", "")
        .removeprefix("Bearer ")
        .strip(),
    }


@app.get("/api/loja/endereco")
def get_endereco(request: Request) -> dict[str, object]:
    usuario = usuario_do_request(request)
    data = obter_endereco(str(usuario.get("uid")))
    return {"ok": True, "endereco": data}


@app.put("/api/loja/endereco")
def put_endereco(cliente: ClientePedido, request: Request) -> dict[str, object]:
    usuario = usuario_do_request(request)
    salvar_endereco(str(usuario.get("uid")), cliente)
    return {"ok": True}


@app.get("/api/loja/admin/produtos")
def admin_produtos(request: Request) -> list[dict]:
    exigir_admin(request)
    return listar_admin()


@app.post("/api/loja/admin/produtos")
def admin_salvar_produto(item: ProdutoAdminIn, request: Request) -> dict:
    exigir_admin(request)
    return salvar_produto_admin(item)


@app.post("/api/loja/admin/importar")
async def admin_importar(body: ImportarUrlIn, request: Request) -> dict:
    exigir_admin(request)
    try:
        produto = await importar_url(
            body.url, categoria=body.categoria, marca=body.marca
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        log.warning("Importação falhou: %s", exc)
        raise HTTPException(
            502,
            "Não consegui ler essa página do fornecedor. Tente o link do produto, não o da busca.",
        ) from exc
    if body.preco_base_usd is not None:
        produto["preco_base_usd"] = float(body.preco_base_usd)
    if body.frete_usd is not None:
        produto["frete_usd"] = float(body.frete_usd)
    publicado = False
    if body.publicar and float(produto.get("preco_base_usd") or 0) > 0:
        salvo = salvar_produto_admin(
            ProdutoAdminIn(**{k: produto[k] for k in ProdutoAdminIn.model_fields})
        )
        publicado = True
        produto = {**produto, **salvo}
    return {
        "ok": True,
        "publicado": publicado,
        "produto": produto,
        "aviso": None
        if publicado
        else "Achei o produto, mas sem preço. Confira o USD e clique em Salvar.",
    }


@app.delete("/api/loja/admin/produtos/{produto_id}")
def admin_remover_produto(produto_id: str, request: Request) -> dict[str, bool]:
    exigir_admin(request)
    remover_produto(produto_id)
    return {"ok": True}


@app.get("/api/loja/admin/pedidos")
def admin_pedidos(request: Request) -> list[dict]:
    exigir_admin(request)
    return listar_pedidos()


@app.get("/api/loja/admin/resumo")
def admin_resumo(request: Request) -> dict[str, object]:
    exigir_admin(request)
    return {
        **resumo_competencia(),
        "usd_brl": usd_brl(),
        **status_catalogo().model_dump(),
    }


@app.post("/api/loja/admin/cambio")
def admin_cambio(request: Request) -> dict[str, float]:
    exigir_admin(request)
    return {"usd_brl": atualizar_cambio(forcar=True)}


@app.get("/api/loja/admin/cj/buscar")
def admin_cj_buscar(request: Request, q: str = "", tamanho: int = 12) -> dict:
    exigir_admin(request)
    if not config.cj_configurada():
        raise HTTPException(503, "CJ ainda não está conectado.")
    try:
        itens = preview_busca(q, tamanho=tamanho)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        log.warning("Busca CJ falhou: %s", exc)
        raise HTTPException(
            502, "O CJ não respondeu. Tente de novo em alguns segundos."
        ) from exc
    return {"ok": True, "itens": itens}


@app.post("/api/loja/admin/cj/disponibilizar")
def admin_cj_disponibilizar(body: CjDisponibilizarIn, request: Request) -> dict:
    exigir_admin(request)
    try:
        produto = importar_pid(body.pid, categoria=body.categoria)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        log.warning("Import CJ falhou: %s", exc)
        raise HTTPException(502, "Não consegui importar esse produto do CJ.") from exc
    salvo = salvar_produto_admin(
        ProdutoAdminIn(**{k: produto[k] for k in ProdutoAdminIn.model_fields})
    )
    return {"ok": True, "produto": {**produto, **salvo}}


@app.post("/api/loja/admin/scraper")
async def admin_scraper(request: Request) -> dict[str, object]:
    exigir_admin(request)

    async def _job() -> None:
        try:
            n = await sincronizar_catalogo()
            log.info("Sincronização em segundo plano: %s itens", n)
        except Exception:
            log.exception("Sincronização em segundo plano falhou")

    asyncio.create_task(_job(), name="sync-catalogo")
    return {
        "ok": True,
        "mensagem": "Sincronização iniciada. Atualize o resumo em um minuto.",
        **status_catalogo().model_dump(),
    }


@app.post("/api/loja/pedidos", response_model=PedidoOut)
def post_pedido(pedido: PedidoIn, request: Request) -> PedidoOut:
    return criar_pedido(pedido, usuario_do_request(request))


@app.get("/api/loja/pedidos/{pedido_id}", response_model=PedidoOut)
def get_pedido(pedido_id: str, payment_id: str | None = None) -> PedidoOut:
    return obter_pedido(pedido_id, payment_id=payment_id)


@app.post("/webhook/mercadopago")
@app.post("/api/loja/mp/webhook")
async def webhook_mercadopago(
    request: Request,
    secret: str = "",
    x_webhook_secret: str = Header(default="", alias="X-Webhook-Secret"),
    data_id: str = Query(default="", alias="data.id"),
    id: str = Query(default=""),
) -> dict[str, str]:
    esperado = config.MP_WEBHOOK_SECRET
    if esperado and secret != esperado and x_webhook_secret != esperado:
        raise HTTPException(401, "Webhook não autorizado.")
    payload: dict = {}
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    payment_id = data_id or id or str((payload.get("data") or {}).get("id") or "")
    topic = (
        request.query_params.get("topic")
        or request.query_params.get("type")
        or payload.get("type")
        or ""
    ).lower()
    if topic in {"", "payment", "payments"}:
        processar_webhook(payload, payment_id)
    return {"status": "ok"}


@app.post("/api/loja/ledger", response_model=LedgerLinha)
def post_ledger(linha: LedgerLinha) -> LedgerLinha:
    return gravar_transacao_financeira(
        pedido_id=linha.pedido_id,
        valor_venda=linha.valor_venda,
        custo_aquisicao=linha.custo_aquisicao,
        taxa_mp=linha.taxa_mp,
        meio_pagamento=linha.meio_pagamento,
        payment_id=linha.payment_id,
    )


@app.get("/api/loja/ledger/resumo")
def get_ledger_resumo(competencia: str | None = None) -> dict[str, float | str | int]:
    return resumo_competencia(competencia)


@app.post("/api/loja/scraper/rodar")
async def post_scraper(request: Request) -> dict[str, object]:
    exigir_admin(request)
    n = await sincronizar_catalogo()
    return {"ok": True, "quantidade": n, **status_catalogo().model_dump()}
