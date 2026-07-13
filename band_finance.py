"""Financeiro da banda — cachês de shows, ensaios em estúdio e despesas."""

from __future__ import annotations

from typing import Any

from event_fees import _money
from studio_finance import (
    default_finance_period,
    enrich_booking_finance,
    month_bounds,
    parse_money_field,
)


def _coerce_db_value(value):
    """Converte date/datetime do Postgres em str para templates Jinja."""
    if value is None:
        return None
    if hasattr(value, 'strftime'):
        if getattr(value, 'hour', None) is not None or getattr(value, 'minute', None) is not None:
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value.strftime('%Y-%m-%d')
    return value


def _coerce_finance_row(row: dict) -> dict:
    out = dict(row)
    for key in ('starts_at', 'ends_at', 'data', 'created_at', 'fee_settled_at'):
        if key in out:
            out[key] = _coerce_db_value(out[key])
    return out

__all__ = [
    'build_band_finance_report',
    'build_member_fee_report',
    'default_finance_period',
    'enrich_event_finance',
    'month_bounds',
    'parse_money_field',
]


def enrich_event_finance(event: dict) -> dict:
    total = _money(event.get('fee_total'))
    transport = _money(event.get('fee_transport_discount'))
    equipment = _money(event.get('fee_equipment_discount'))
    net = max(0.0, total - transport - equipment) if total > 0 else 0.0
    row = _coerce_finance_row(event)
    row['fee_net'] = round(net, 2)
    row['has_fee'] = total > 0
    row['is_received'] = bool(row.get('fee_settled_at'))
    return row


def build_band_finance_report(
    *,
    band: dict,
    events: list[dict],
    bookings: list[dict],
    expenses: list[dict],
    year: int,
    month: int,
) -> dict[str, Any]:
    enriched_events = [enrich_event_finance(e) for e in events]
    fee_events = [e for e in enriched_events if e['has_fee']]

    receita_confirmada = round(sum(e['fee_net'] for e in fee_events), 2)
    recebido = round(
        sum(e['fee_net'] for e in fee_events if e['is_received']),
        2,
    )
    a_receber = round(receita_confirmada - recebido, 2)

    enriched_bookings = [
        _coerce_finance_row(
            enrich_booking_finance(
                b,
                studio_preco_hora=b.get('studio_preco_hora'),
            ),
        )
        for b in bookings
    ]
    custos_ensaio = round(
        sum(b['valor_cobrado_efetivo'] for b in enriched_bookings),
        2,
    )
    horas_ensaio = round(sum(b['duration_hours'] for b in enriched_bookings), 2)
    total_despesas = round(sum(_money(e.get('valor')) for e in expenses), 2)
    total_custos = round(custos_ensaio + total_despesas, 2)
    liquido = round(recebido - total_custos, 2)

    return {
        'year': year,
        'month': month,
        'events': enriched_events,
        'bookings': enriched_bookings,
        'expenses': [_coerce_finance_row(e) for e in expenses],
        'stats': {
            'eventos': len(enriched_events),
            'shows_com_cache': len(fee_events),
            'receita_confirmada': receita_confirmada,
            'recebido': recebido,
            'a_receber': a_receber,
            'custos_ensaio': custos_ensaio,
            'horas_ensaio': horas_ensaio,
            'reservas_estudio': len(enriched_bookings),
            'despesas': total_despesas,
            'custos_totais': total_custos,
            'liquido': liquido,
        },
    }


def build_member_fee_report(
    *,
    user_id: str,
    events: list[dict],
    year: int,
    month: int,
    name_for_user,
) -> dict[str, Any]:
    """Agrega a fatia do músico nos shows com cachê."""
    from event_fees import compute_event_fee_split
    from db import get_band_members
    from models_agenda import get_event_assignments

    rows: list[dict] = []
    for raw in events:
        event = enrich_event_finance(raw)
        band_id = event.get('band_id')
        if not band_id or not event.get('has_fee'):
            continue
        split = compute_event_fee_split(
            event,
            get_event_assignments(event['id']),
            get_band_members(band_id),
            name_for_user=name_for_user,
        )
        mine = next(
            (p for p in (split.get('payees') or []) if str(p.get('user_id')) == str(user_id)),
            None,
        )
        if not mine:
            # Músico na banda mas não na divisão (não confirmou) — ainda lista com 0
            amount = 0.0
            included = False
        else:
            amount = float(mine.get('amount') or 0)
            included = True
        rows.append({
            **event,
            'my_amount': round(amount, 2),
            'included_in_split': included,
            'fee_net_band': split.get('net') or event.get('fee_net') or 0,
            'payees_count': len(split.get('payees') or []),
        })

    total = round(sum(r['my_amount'] for r in rows), 2)
    received = round(sum(r['my_amount'] for r in rows if r.get('is_received')), 2)
    pending = round(total - received, 2)
    bands = sorted({(r.get('band_id'), r.get('band_name') or '') for r in rows})

    return {
        'year': year,
        'month': month,
        'rows': rows,
        'stats': {
            'shows': len(rows),
            'total': total,
            'recebido': received,
            'a_receber': pending,
            'bandas': len({b[0] for b in bands if b[0]}),
        },
    }
