from __future__ import annotations

import os
from pathlib import Path


def _csv(name: str) -> set[str]:
    return {s.strip().lower() for s in os.getenv(name, "").split(",") if s.strip()}


def _float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return default


LOJA_DATA_DIR = os.getenv("LOJA_DATA_DIR", "/app/data")
DUCKDB_PATH = os.getenv("DUCKDB_PATH") or str(Path(LOJA_DATA_DIR) / "loja.duckdb")
PARQUET_DIR = os.getenv("PARQUET_DIR") or str(
    Path(LOJA_DATA_DIR) / "parquets_individuais"
)
LOJA_PUBLIC_URL = os.getenv("LOJA_PUBLIC_URL", "https://loja.unissono.app").rstrip("/")
LOJA_ADMIN_SECRET = os.getenv("LOJA_ADMIN_SECRET", "").strip()
LOJA_ADMIN_USERNAMES = _csv("LOJA_ADMIN_USERNAMES") | _csv(
    "SETSYNC_SUPERADMIN_USERNAMES"
)
LOJA_ADMIN_EMAILS = _csv("LOJA_ADMIN_EMAILS") | _csv("SETSYNC_SUPERADMIN_EMAILS")
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
UNISSONO_PUBLIC_URL = os.getenv("UNISSONO_PUBLIC_URL", "https://unissono.app").rstrip(
    "/"
)
UNISSONO_INTERNAL_URL = os.getenv(
    "UNISSONO_INTERNAL_URL", "http://setsync-web-1:5000"
).rstrip("/")

USD_BRL = _float("USD_BRL", 5.5)
MARGEM_LUCRO = _float("MARGEM_LUCRO", 1.30)
TAXA_MP_PIX = _float("TAXA_MP_PIX", 0.0099)
TAXA_MP_CARTAO = _float("TAXA_MP_CARTAO", 0.0499)
TAXA_MP_BOLETO = _float("TAXA_MP_BOLETO", 0.0349)

SCRAPER_INTERVALO_H = int(os.getenv("SCRAPER_INTERVALO_H", "24") or 24)
SCRAPER_HORA = int(os.getenv("SCRAPER_HORA", "3") or 3)
SCRAPER_TIMEOUT = float(os.getenv("SCRAPER_TIMEOUT", "25") or 25)

MP_ENVIRONMENT = (os.getenv("MP_ENVIRONMENT") or "production").strip().lower()
MP_WEBHOOK_SECRET = os.getenv("MP_WEBHOOK_SECRET", "").strip()

CJ_API_KEY = os.getenv("CJ_API_KEY", "").strip()
CJ_KEYWORDS = [
    s.strip()
    for s in os.getenv(
        "CJ_KEYWORDS",
        "guitar pick,guitar capo,guitar tuner,guitar cable,guitar pedal,guitar strap,bass strings,instrument bag",
    ).split(",")
    if s.strip()
]
CJ_FRETE_USD = _float("CJ_FRETE_USD", 8.0)
CJ_LOGISTIC = (
    os.getenv("CJ_LOGISTIC", "CJPacket Ordinary").strip() or "CJPacket Ordinary"
)
CJ_MAX_POR_BUSCA = int(os.getenv("CJ_MAX_POR_BUSCA", "8") or 8)


def cj_configurada() -> bool:
    return bool(CJ_API_KEY)


def mp_access_token() -> str:
    if MP_ENVIRONMENT == "production":
        return os.getenv("MP_ACCESS_TOKEN", "").strip()
    return (
        os.getenv("MP_ACCESS_TOKEN_TEST") or os.getenv("MP_ACCESS_TOKEN") or ""
    ).strip()


def mp_configurada() -> bool:
    return bool(mp_access_token())
