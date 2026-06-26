"""Financeiro do estúdio — receita de reservas, pagamentos e despesas."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Any

from studio_scheduling import BOOKING_CONFIRMADO, parse_time_hhmm, time_to_minutes


def _money(v: Any) -> float:
    try:
        return max(0.0, float(v or 0))
    except (TypeError, ValueError):
        return 0.0


def parse_money_field(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = str(raw).strip().replace(',', '.')
    if not s:
        return None
    try:
        return max(0.0, float(s))
    except ValueError:
        return None


def booking_duration_hours(hora_inicio: str, hora_fim: str) -> float:
    t0, t1 = parse_time_hhmm(hora_inicio), parse_time_hhmm(hora_fim)
    if not t0 or not t1:
        return 0.0
    mins = time_to_minutes(t1) - time_to_minutes(t0)
    if mins <= 0:
        return 0.0
    return round(mins / 60.0, 2)


def estimate_booking_value(
    booking: dict,
    *,
    preco_hora: float | None,
) -> float:
    hours = booking_duration_hours(
        booking.get('hora_inicio') or '',
        booking.get('hora_fim') or '',
    )
    rate = _money(preco_hora)
    if hours <= 0 or rate <= 0:
        return 0.0
    return round(hours * rate, 2)


def booking_charge_amount(booking: dict, *, preco_hora: float | None) -> float:
    charged = booking.get('valor_cobrado')
    if charged is not None and str(charged).strip() != '':
        return round(_money(charged), 2)
    return estimate_booking_value(booking, preco_hora=preco_hora)


def resolve_booking_preco_hora(
    booking: dict,
    *,
    studio_preco_hora: float | None,
) -> float | None:
    room_rate = booking.get('room_preco_hora')
    if room_rate is not None and str(room_rate).strip() != '':
        return _money(room_rate) or None
    studio_rate = studio_preco_hora
    if studio_rate is not None and str(studio_rate).strip() != '':
        return _money(studio_rate) or None
    return None


def enrich_booking_finance(
    booking: dict,
    *,
    preco_hora: float | None = None,
    studio_preco_hora: float | None = None,
) -> dict:
    rate = preco_hora
    if rate is None:
        rate = resolve_booking_preco_hora(
            booking, studio_preco_hora=studio_preco_hora,
        )
    row = dict(booking)
    hours = booking_duration_hours(
        row.get('hora_inicio') or '',
        row.get('hora_fim') or '',
    )
    estimated = estimate_booking_value(row, preco_hora=rate)
    charged = booking_charge_amount(row, preco_hora=rate)
    row['duration_hours'] = hours
    row['valor_estimado'] = estimated
    row['valor_cobrado_efetivo'] = charged
    row['is_paid'] = bool(row.get('pago_em'))
    row['valor_customizado'] = (
        row.get('valor_cobrado') is not None and str(row.get('valor_cobrado')).strip() != ''
    )
    row['preco_hora_efetivo'] = rate
    return row


def month_bounds(year: int, month: int) -> tuple[str, str]:
    last = monthrange(year, month)[1]
    return f'{year:04d}-{month:02d}-01', f'{year:04d}-{month:02d}-{last:02d}'


def default_finance_period() -> tuple[int, int, str, str]:
    today = date.today()
    y, m = today.year, today.month
    start, end = month_bounds(y, m)
    return y, m, start, end


def build_studio_finance_report(
    *,
    studio: dict,
    bookings: list[dict],
    expenses: list[dict],
    year: int,
    month: int,
) -> dict[str, Any]:
    preco_studio = studio.get('preco_hora')
    enriched = [
        enrich_booking_finance(b, studio_preco_hora=preco_studio) for b in bookings
    ]

    receita_confirmada = sum(b['valor_cobrado_efetivo'] for b in enriched)
    recebido = sum(
        b['valor_cobrado_efetivo'] for b in enriched if b['is_paid']
    )
    a_receber = round(receita_confirmada - recebido, 2)
    total_despesas = round(sum(_money(e.get('valor')) for e in expenses), 2)
    liquido = round(recebido - total_despesas, 2)
    horas = round(sum(b['duration_hours'] for b in enriched), 2)

    return {
        'year': year,
        'month': month,
        'preco_hora': preco_studio,
        'tem_preco_sala': any(b.get('room_preco_hora') for b in bookings),
        'bookings': enriched,
        'expenses': expenses,
        'stats': {
            'reservas': len(enriched),
            'horas': horas,
            'receita_confirmada': round(receita_confirmada, 2),
            'recebido': round(recebido, 2),
            'a_receber': a_receber,
            'despesas': total_despesas,
            'liquido': liquido,
        },
    }
