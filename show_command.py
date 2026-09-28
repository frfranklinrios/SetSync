"""Comando do próximo show — gaps, CTAs e pool de freelas da banda."""

from __future__ import annotations

from typing import Any

from flask import url_for

from event_prep_reminders import event_prep_gaps
from models_agenda import get_upcoming_events_for_user
from models_band_team import (
    get_assignment_stats_by_events,
    list_band_freela_pool,
    list_event_guests,
)


def build_show_command_cards(user_id: str, *, limit: int = 3) -> list[dict[str, Any]]:
    """Próximos eventos do usuário com checklist acionável (setlist/escala/freela/cachê)."""
    events = get_upcoming_events_for_user(user_id, limit=12)
    if not events:
        return []

    # Preferir shows; se não houver, ensaios com gaps
    shows = [e for e in events if (e.get("event_type") or "") == "show"]
    candidates = shows or events
    candidates = candidates[: max(limit * 2, limit)]

    ids = [e["id"] for e in candidates]
    assignment_stats = get_assignment_stats_by_events(ids)
    cards: list[dict[str, Any]] = []

    for event in candidates:
        gaps = event_prep_gaps(event, assignment_stats=assignment_stats)
        guests = []
        try:
            guests = list_event_guests(event["id"])
        except Exception:
            guests = []
        pending_guests = sum(
            1
            for g in guests
            if (g.get("response_status") or "pending").lower() == "pending"
        )
        declined_guests = sum(
            1 for g in guests if (g.get("response_status") or "").lower() == "declined"
        )
        accepted_guests = sum(
            1 for g in guests if (g.get("response_status") or "").lower() == "accepted"
        )

        fee_open = (
            (event.get("event_type") or "") == "show"
            and not event.get("fee_settled_at")
            and (event.get("fee_total") or guests)
        )
        needs_fee = (event.get("event_type") or "") == "show" and not event.get(
            "fee_total"
        )

        fixes: list[dict[str, str]] = []
        if gaps.get("no_scale"):
            fixes.append(
                {
                    "label": "Montar escala",
                    "url": url_for("agenda.escala", event_id=event["id"]),
                }
            )
        elif gaps.get("pending_responses"):
            n = gaps["pending_responses"]
            fixes.append(
                {
                    "label": f"{n} resposta{'s' if n != 1 else ''} pendente{'s' if n != 1 else ''}",
                    "url": url_for("agenda.view", event_id=event["id"]) + "#escala",
                }
            )
        if gaps.get("missing_setlist") or gaps.get("empty_setlist"):
            from conversion_levers import banda_eh_paga, cta_pro
            from models_setlist import find_suggestable_setlist

            suggested = find_suggestable_setlist(
                event["band_id"],
                exclude_setlist_id=int(event["setlist_id"])
                if event.get("setlist_id")
                else None,
            )
            if not banda_eh_paga(event["band_id"]):
                cta = cta_pro(banda_id=event["band_id"])
                fixes.append(
                    {
                        "label": "Assinar Pro — setlist + PDF + offline",
                        "url": cta["upgrade_url"],
                        "primary": True,
                    }
                )
            if suggested:
                fixes.append(
                    {
                        "label": f"Clonar «{suggested['name']}»",
                        "url": url_for("agenda.comando", event_id=event["id"]),
                    }
                )
            else:
                fixes.append(
                    {
                        "label": "Vincular setlist"
                        if gaps.get("missing_setlist")
                        else "Completar setlist",
                        "url": url_for("agenda.view", event_id=event["id"]),
                    }
                )
        if not guests and (event.get("event_type") or "") == "show":
            fixes.append(
                {
                    "label": "Convidar freela",
                    "url": url_for("agenda.view", event_id=event["id"]) + "#escala",
                }
            )
        elif pending_guests:
            fixes.append(
                {
                    "label": f"{pending_guests} freela{'s' if pending_guests != 1 else ''} aguardando",
                    "url": url_for("agenda.view", event_id=event["id"]) + "#escala",
                }
            )
        if needs_fee:
            fixes.append(
                {
                    "label": "Fechar cachê da noite",
                    "url": url_for("agenda.view", event_id=event["id"])
                    + "#fechamento-noite",
                }
            )
        elif fee_open:
            fixes.append(
                {
                    "label": "Liquidar fechamento",
                    "url": url_for("agenda.view", event_id=event["id"])
                    + "#fechamento-noite",
                }
            )

        score = (
            (3 if gaps.get("no_scale") else 0)
            + (2 if gaps.get("pending_responses") else 0)
            + (2 if gaps.get("missing_setlist") or gaps.get("empty_setlist") else 0)
            + (2 if pending_guests else 0)
            + (1 if needs_fee else 0)
            + (1 if (event.get("event_type") or "") == "show" else 0)
        )
        if score <= 0 and not gaps.get("has_gaps") and not guests:
            # Show “pronto” ainda aparece se for o próximo show
            if (event.get("event_type") or "") != "show":
                continue

        cards.append(
            {
                "event": event,
                "gaps": gaps,
                "fixes": fixes[:4],
                "guest_counts": {
                    "total": len(guests),
                    "pending": pending_guests,
                    "accepted": accepted_guests,
                    "declined": declined_guests,
                },
                "score": score,
                "ready": not gaps.get("has_gaps") and pending_guests == 0,
                "view_url": url_for("agenda.view", event_id=event["id"]),
                "comando_url": url_for("agenda.comando", event_id=event["id"]),
            }
        )

    cards.sort(key=lambda c: (-c["score"], str(c["event"].get("starts_at") or "")))
    return cards[:limit]


# Re-export for callers that expect pool here
__all__ = [
    "build_show_command_cards",
    "list_band_freela_pool",
]
