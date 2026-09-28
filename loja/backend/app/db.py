"""DuckDB + exportação Parquet (catálogo, pedidos e ledger Carnê-Leão)."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

import duckdb

from app import config

log = logging.getLogger("unissono.loja.db")
_lock = threading.RLock()
_inicializado = False


def _garantir_dirs() -> None:
    Path(config.LOJA_DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.PARQUET_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.DUCKDB_PATH).parent.mkdir(parents=True, exist_ok=True)


def connect() -> duckdb.DuckDBPyConnection:
    _garantir_dirs()
    return duckdb.connect(config.DUCKDB_PATH)


def init_db() -> None:
    global _inicializado
    with _lock:
        con = connect()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS catalogo (
                    id VARCHAR PRIMARY KEY,
                    sku VARCHAR,
                    titulo VARCHAR,
                    categoria VARCHAR,
                    marca VARCHAR,
                    imagem_url VARCHAR,
                    url_fornecedor VARCHAR,
                    preco_base DOUBLE,
                    custo_frete DOUBLE,
                    custo_aquisicao DOUBLE,
                    preco_venda DOUBLE,
                    estoque INTEGER,
                    fonte VARCHAR,
                    atualizado_em TIMESTAMP
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS pedidos (
                    id VARCHAR PRIMARY KEY,
                    status VARCHAR,
                    pagamento VARCHAR,
                    total DOUBLE,
                    custo_aquisicao DOUBLE,
                    payload JSON,
                    criado_em TIMESTAMP,
                    atualizado_em TIMESTAMP
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS ledger (
                    id VARCHAR PRIMARY KEY,
                    pedido_id VARCHAR UNIQUE,
                    payment_id VARCHAR,
                    meio_pagamento VARCHAR,
                    valor_venda DOUBLE,
                    custo_aquisicao DOUBLE,
                    taxa_mp DOUBLE,
                    lucro_liquido DOUBLE,
                    competencia VARCHAR,
                    criado_em TIMESTAMP
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    chave VARCHAR PRIMARY KEY,
                    valor VARCHAR
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS enderecos (
                    usuario_id VARCHAR PRIMARY KEY,
                    payload JSON,
                    atualizado_em TIMESTAMP
                )
                """
            )
        finally:
            con.close()
        _inicializado = True
        log.info("DuckDB pronto em %s", config.DUCKDB_PATH)


def locked() -> threading.Lock:
    return _lock


def exportar_parquet(tabela: str, arquivo: str) -> Path:
    destino = Path(config.PARQUET_DIR) / arquivo
    destino.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        con = connect()
        try:
            con.execute(
                f"COPY (SELECT * FROM {tabela}) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
                [str(destino)],
            )
        finally:
            con.close()
    return destino


def exportar_linha_parquet(sql: str, params: list, arquivo: str) -> Path:
    destino = Path(config.PARQUET_DIR) / arquivo
    destino.parent.mkdir(parents=True, exist_ok=True)
    path = str(destino).replace("'", "")
    with _lock:
        con = connect()
        try:
            con.execute(
                f"COPY ({sql}) TO '{path}' (FORMAT PARQUET, COMPRESSION ZSTD)",
                params,
            )
        finally:
            con.close()
    return destino


def set_meta(chave: str, valor: str) -> None:
    with _lock:
        con = connect()
        try:
            con.execute(
                """
                INSERT INTO meta (chave, valor) VALUES (?, ?)
                ON CONFLICT (chave) DO UPDATE SET valor = excluded.valor
                """,
                [chave, valor],
            )
        finally:
            con.close()


def get_meta(chave: str) -> str | None:
    with _lock:
        con = connect()
        try:
            row = con.execute(
                "SELECT valor FROM meta WHERE chave = ?", [chave]
            ).fetchone()
            return str(row[0]) if row else None
        finally:
            con.close()
