"""Contexto e métricas do painel do administrador master."""

from __future__ import annotations

from db import (
    count_bands,
    count_cifras,
    count_studios,
    count_users,
    count_users_without_band,
    list_users_without_band,
)
from product_funnel import funnel_activation_rows
from retention_metrics import build_metrics_trend, build_retention_metrics, record_metrics_snapshot
from whatsapp_service import is_configured as whatsapp_configured


def build_admin_dashboard_context() -> dict:
    """Contexto agregado (métricas/contagens) do painel admin.

    Usa COUNT(*) em vez de carregar todas as tabelas na memória — o blueprint
    já busca as listas que renderiza; aqui só precisamos de números e métricas.
    """
    users_total = count_users()
    stuck_users = list_users_without_band(10)

    _retention = build_retention_metrics()
    # Registra o ponto de hoje (idempotente) e monta a série p/ deltas/sparklines.
    try:
        record_metrics_snapshot(_retention)
    except Exception:
        pass
    _trend = build_metrics_trend()

    return {
        'stats': {
            'bands': count_bands(),
            'cifras': count_cifras(),
            'users': users_total,
            'studios': count_studios(),
            'users_no_band': count_users_without_band(),
        },
        'funnel_rows': funnel_activation_rows(users_total=users_total),
        'retention': _retention,
        'metrics_trend': _trend,
        'stuck_users': stuck_users,
        'whatsapp_configured': whatsapp_configured(),
    }
