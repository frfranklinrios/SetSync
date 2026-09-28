"""Câmbio USD/BRL (AwesomeAPI) com cache no DuckDB."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import httpx

from app import config
from app.db import get_meta, set_meta

log = logging.getLogger("unissono.loja.cambio")
_TTL = timedelta(hours=6)


def usd_brl() -> float:
    raw = get_meta("usd_brl")
    if raw:
        try:
            valor = float(raw)
            if valor > 0:
                return valor
        except ValueError:
            pass
    return config.USD_BRL


def _cache_fresco() -> bool:
    raw = get_meta("usd_brl_em")
    if not raw:
        return False
    try:
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - ts < _TTL


def atualizar_cambio(*, forcar: bool = False) -> float:
    if not forcar and _cache_fresco():
        return usd_brl()
    try:
        with httpx.Client(timeout=12.0, headers={"User-Agent": "UnissonoLoja/1.1"}) as client:
            res = client.get("https://economia.awesomeapi.com.br/json/last/USD-BRL")
            res.raise_for_status()
            bid = float((res.json().get("USDBRL") or {}).get("bid") or 0)
    except Exception as exc:
        log.warning("Câmbio indisponível: %s", exc)
        set_meta("usd_brl_em", datetime.now(timezone.utc).isoformat())
        return usd_brl()
    if bid <= 0:
        return usd_brl()
    set_meta("usd_brl", f"{bid:.4f}")
    set_meta("usd_brl_em", datetime.now(timezone.utc).isoformat())
    log.info("USD/BRL atualizado: %s", bid)
    return bid
