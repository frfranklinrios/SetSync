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
    if hasattr(value, "strftime"):
        if (
            getattr(value, "hour", None) is not None
            or getattr(value, "minute", None) is not None
        ):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.strftime("%Y-%m-%d")
    return value


def _coerce_finance_row(row: dict) -> dict:
    out = dict(row)
    for key in (
        "starts_at",
        "ends_at",
        "data",
        "created_at",
        "fee_settled_at",
        "paid_at",
    ):
        if key in out:
            out[key] = _coerce_db_value(out[key])
    return out


__all__ = [
    "build_band_finance_report",
    "build_member_fee_report",
    "build_platform_finance_totals",
    "default_finance_period",
    "enrich_event_finance",
    "fee_share_whatsapp_text",
    "month_bounds",
    "parse_money_field",
]


def enrich_event_finance(event: dict) -> dict:
    total = _money(event.get("fee_total"))
    couvert = _money(event.get("fee_couvert"))
    transport = _money(event.get("fee_transport_discount"))
    equipment = _money(event.get("fee_equipment_discount"))
    # Despesas ligadas ao evento entram no líquido do show quando disponíveis
    night = _money(event.get("fee_night_expenses"))
    gross = total + couvert
    net = max(0.0, gross - transport - equipment - night) if gross > 0 else 0.0
    row = _coerce_finance_row(event)
    row["fee_couvert"] = round(couvert, 2)
    row["fee_gross"] = round(gross, 2)
    row["fee_net"] = round(net, 2)
    row["has_fee"] = gross > 0
    row["is_received"] = bool(row.get("fee_settled_at"))
    return row


def build_band_finance_report(
    *,
    band: dict,
    events: list[dict],
    bookings: list[dict],
    expenses: list[dict],
    year: int,
    month: int,
    gorjetas_total: float = 0.0,
    gorjetas: list[dict] | None = None,
) -> dict[str, Any]:
    from models_band_finance import list_event_expenses

    enriched_events = []
    for e in events:
        night = 0.0
        if e.get("id") and (e.get("fee_total") or e.get("fee_couvert")):
            night = sum(_money(x.get("valor")) for x in list_event_expenses(e["id"]))
        e = dict(e)
        e["fee_night_expenses"] = night
        enriched_events.append(enrich_event_finance(e))
    fee_events = [e for e in enriched_events if e["has_fee"]]

    receita_confirmada = round(sum(e["fee_net"] for e in fee_events), 2)
    recebido = round(
        sum(e["fee_net"] for e in fee_events if e["is_received"]),
        2,
    )
    a_receber = round(receita_confirmada - recebido, 2)
    tips = round(_money(gorjetas_total), 2)

    enriched_bookings = [
        _coerce_finance_row(
            enrich_booking_finance(
                b,
                studio_preco_hora=b.get("studio_preco_hora"),
            ),
        )
        for b in bookings
    ]
    custos_ensaio = round(
        sum(b["valor_cobrado_efetivo"] for b in enriched_bookings),
        2,
    )
    horas_ensaio = round(sum(b["duration_hours"] for b in enriched_bookings), 2)
    # Despesas da noite já entram no líquido do show — não contar de novo
    despesas_banda = [e for e in expenses if not e.get("event_id")]
    despesas_noite = [e for e in expenses if e.get("event_id")]
    total_despesas = round(sum(_money(e.get("valor")) for e in despesas_banda), 2)
    total_custos = round(custos_ensaio + total_despesas, 2)
    liquido = round(recebido + tips - total_custos, 2)

    return {
        "year": year,
        "month": month,
        "events": enriched_events,
        "bookings": enriched_bookings,
        "expenses": [_coerce_finance_row(e) for e in despesas_banda],
        "night_expenses": [_coerce_finance_row(e) for e in despesas_noite],
        "gorjetas": [_coerce_finance_row(g) for g in (gorjetas or [])],
        "stats": {
            "eventos": len(enriched_events),
            "shows_com_cache": len(fee_events),
            "receita_confirmada": receita_confirmada,
            "recebido": recebido,
            "a_receber": a_receber,
            "gorjetas": tips,
            "custos_ensaio": custos_ensaio,
            "horas_ensaio": horas_ensaio,
            "reservas_estudio": len(enriched_bookings),
            "despesas": total_despesas,
            "despesas_noite": round(
                sum(_money(e.get("valor")) for e in despesas_noite), 2
            ),
            "custos_totais": total_custos,
            "liquido": liquido,
        },
    }


def fee_share_whatsapp_text(
    *,
    band_name: str,
    show_title: str,
    date_label: str,
    amount: float,
    status: str,
    link: str = "https://unissono.app/bands/meus-caches",
) -> str:
    """Texto pronto para compartilhar a fatia no WhatsApp."""
    return (
        f"*Uníssono* — minha parte no show\n"
        f"{band_name} · {show_title}\n"
        f"{date_label}\n"
        f"Valor: *R$ {amount:.2f}*\n"
        f"Status: {status}\n"
        f"{link}"
    )


def build_member_fee_report(
    *,
    user_id: str,
    events: list[dict],
    year: int,
    month: int,
    name_for_user,
) -> dict[str, Any]:
    """Agrega a fatia do músico nos shows com cachê."""
    from db import get_band_members
    from event_fees import compute_event_fee_split
    from models_agenda import get_event_assignments
    from models_band_finance import list_event_expenses, list_event_fee_lines
    from models_band_team import list_event_guests

    rows: list[dict] = []
    for raw in events:
        event = enrich_event_finance(raw)
        band_id = event.get("band_id")
        if not band_id or not event.get("has_fee"):
            continue
        eid = event["id"]
        expenses = list_event_expenses(eid)
        event["fee_night_expenses"] = sum(_money(e.get("valor")) for e in expenses)
        event = enrich_event_finance(event)
        fee_lines = list_event_fee_lines(eid) or []
        split = compute_event_fee_split(
            event,
            get_event_assignments(eid),
            get_band_members(band_id),
            name_for_user=name_for_user,
            guests=list_event_guests(eid),
            event_expenses=expenses,
            fee_lines=fee_lines or None,
        )
        mine = next(
            (
                p
                for p in (split.get("payees") or [])
                if str(p.get("user_id")) == str(user_id)
            ),
            None,
        )
        my_line = next(
            (ln for ln in fee_lines if str(ln.get("user_id") or "") == str(user_id)),
            None,
        )
        if not mine:
            amount = 0.0
            included = False
        else:
            amount = float(mine.get("amount") or 0)
            included = True
        personally_paid = bool(my_line and my_line.get("paid_at"))
        night_settled = bool(event.get("fee_settled_at"))
        is_received = personally_paid or night_settled
        date_label = (str(event.get("starts_at") or ""))[:10]
        status = "Recebido" if is_received else "A receber"
        wa_text = ""
        if amount > 0:
            wa_text = fee_share_whatsapp_text(
                band_name=event.get("band_name") or "Banda",
                show_title=event.get("title") or "Show",
                date_label=date_label,
                amount=amount,
                status=status,
            )
        rows.append(
            {
                **event,
                "my_amount": round(amount, 2),
                "included_in_split": included,
                "fee_net_band": split.get("net") or event.get("fee_net") or 0,
                "payees_count": len(split.get("payees") or []),
                "is_received": is_received,
                "personally_paid": personally_paid,
                "fee_line_id": (my_line or {}).get("id"),
                "wa_text": wa_text,
            }
        )

    total = round(sum(r["my_amount"] for r in rows), 2)
    received = round(sum(r["my_amount"] for r in rows if r.get("is_received")), 2)
    pending = round(total - received, 2)
    pending_rows = [
        r for r in rows if r.get("my_amount", 0) > 0 and not r.get("is_received")
    ]
    bands = sorted({(r.get("band_id"), r.get("band_name") or "") for r in rows})

    return {
        "year": year,
        "month": month,
        "rows": rows,
        "pending_rows": pending_rows,
        "stats": {
            "shows": len(rows),
            "total": total,
            "recebido": received,
            "a_receber": pending,
            "bandas": len({b[0] for b in bands if b[0]}),
            "a_receber_count": len(pending_rows),
        },
    }


def build_platform_finance_totals(*, year: int, month: int) -> dict[str, Any]:
    """Totais agregados de todas as bandas (visão master) — sem detalhe por show/membro.

    Usado no painel admin: o superadmin não vê lançamentos individuais.
    """
    from models_band_finance import aggregate_platform_band_finance

    from_date, to_date = month_bounds(year, month)
    raw = aggregate_platform_band_finance(from_date=from_date, to_date=to_date)
    return {
        "year": year,
        "month": month,
        "from_date": from_date,
        "to_date": to_date,
        "stats": {
            "bandas_com_movimento": int(raw.get("bandas_com_movimento") or 0),
            "shows_com_cache": int(raw.get("shows_com_cache") or 0),
            "receita_confirmada": round(float(raw.get("receita_confirmada") or 0), 2),
            "recebido": round(float(raw.get("recebido") or 0), 2),
            "a_receber": round(float(raw.get("a_receber") or 0), 2),
            "despesas": round(float(raw.get("despesas") or 0), 2),
            "demo_excluded_shows": int(raw.get("demo_excluded_shows") or 0),
            "demo_excluded_bands": int(raw.get("demo_excluded_bands") or 0),
        },
    }
