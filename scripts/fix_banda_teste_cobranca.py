#!/usr/bin/env python3
"""Corrige data_proxima_cobranca da Banda teste (renovação sem update de ciclo)."""

import sys

sys.path.insert(0, "/app")

from datetime import timedelta

from db import init_db, update_assinatura
from monetizacao import (
    _agora_utc,
    get_assinatura_banda,
    periodo_assinatura_ui,
    plano_badge_ui,
)

BAND_ID = "2ddf62cb-77d4-4ba2-b774-9270d4f95e3d"

init_db()
a = get_assinatura_banda(BAND_ID)
print("ANTES", a.plano, a.status, a.data_proxima_cobranca)
print(" periodo", periodo_assinatura_ui(a))

# Ciclo anterior: 04/07 → +30 dias = 03/08/2026 (mantém status ativa)
prox = a.data_proxima_cobranca
if prox is None or prox < _agora_utc():
    base = prox or _agora_utc()
    # Avança ciclos de 30 dias até ficar no futuro
    nova = base
    while nova <= _agora_utc():
        nova = nova + timedelta(days=30)
    update_assinatura(
        BAND_ID,
        data_proxima_cobranca=nova.strftime("%Y-%m-%d %H:%M:%S"),
        status="ativa",
        data_cancelamento=None,
    )
    print("ATUALIZADO para", nova)

a2 = get_assinatura_banda(BAND_ID)
print("DEPOIS", a2.plano, a2.status, a2.data_proxima_cobranca)
print(" periodo", periodo_assinatura_ui(a2))
ui = plano_badge_ui(BAND_ID)
print(
    " ui",
    ui["label_curto"],
    ui["periodo"].get("urgencia"),
    ui["periodo"].get("texto_restante"),
)
