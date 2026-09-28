"""Livro-caixa PF: lucro líquido tributável para Carnê-Leão."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.db import connect, exportar_linha_parquet, exportar_parquet, locked
from app.models import LedgerLinha

log = logging.getLogger("unissono.loja.ledger")


def gravar_transacao_financeira(
    *,
    pedido_id: str,
    valor_venda: float,
    custo_aquisicao: float,
    taxa_mp: float,
    meio_pagamento: str = "",
    payment_id: str = "",
) -> LedgerLinha:
    """Valor recebido − taxa MP − custo do fornecedor = lucro líquido tributável."""
    venda = round(float(valor_venda), 2)
    custo = round(float(custo_aquisicao), 2)
    taxa = round(float(taxa_mp), 2)
    lucro = round(venda - taxa - custo, 2)
    agora = datetime.now(UTC)
    competencia = agora.strftime("%Y-%m")
    lid = f"LED-{uuid.uuid4().hex[:10].upper()}"

    with locked():
        con = connect()
        try:
            existente = con.execute(
                "SELECT id, lucro_liquido FROM ledger WHERE pedido_id = ?",
                [pedido_id],
            ).fetchone()
            if existente:
                log.info("Ledger já existe para %s", pedido_id)
                return LedgerLinha(
                    pedido_id=pedido_id,
                    valor_venda=venda,
                    custo_aquisicao=custo,
                    taxa_mp=taxa,
                    lucro_liquido=float(existente[1]),
                    meio_pagamento=meio_pagamento,
                    payment_id=payment_id,
                )
            con.execute(
                """
                INSERT INTO ledger (
                    id, pedido_id, payment_id, meio_pagamento, valor_venda,
                    custo_aquisicao, taxa_mp, lucro_liquido, competencia, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    lid,
                    pedido_id,
                    payment_id,
                    meio_pagamento,
                    venda,
                    custo,
                    taxa,
                    lucro,
                    competencia,
                    agora.replace(tzinfo=None),
                ],
            )
        finally:
            con.close()

    exportar_parquet("ledger", "ledger.parquet")
    exportar_linha_parquet(
        "SELECT * FROM ledger WHERE pedido_id = ?",
        [pedido_id],
        f"pedidos/{pedido_id}.parquet",
    )
    log.info(
        "Ledger %s venda=%.2f custo=%.2f taxa=%.2f lucro=%.2f",
        pedido_id,
        venda,
        custo,
        taxa,
        lucro,
    )
    return LedgerLinha(
        pedido_id=pedido_id,
        valor_venda=venda,
        custo_aquisicao=custo,
        taxa_mp=taxa,
        lucro_liquido=lucro,
        meio_pagamento=meio_pagamento,
        payment_id=payment_id,
    )


def resumo_competencia(competencia: str | None = None) -> dict[str, float | str | int]:
    mes = competencia or datetime.now(UTC).strftime("%Y-%m")
    with locked():
        con = connect()
        try:
            row = con.execute(
                """
                SELECT COUNT(*),
                       COALESCE(SUM(valor_venda), 0),
                       COALESCE(SUM(custo_aquisicao), 0),
                       COALESCE(SUM(taxa_mp), 0),
                       COALESCE(SUM(lucro_liquido), 0)
                FROM ledger
                WHERE competencia = ?
                """,
                [mes],
            ).fetchone()
        finally:
            con.close()
    return {
        "competencia": mes,
        "qtd_vendas": int(row[0] or 0),
        "valor_venda": float(row[1] or 0),
        "custo_aquisicao": float(row[2] or 0),
        "taxa_mp": float(row[3] or 0),
        "lucro_liquido": float(row[4] or 0),
    }
