"""Recupera quem iniciou checkout MP e não concluiu."""

from __future__ import annotations

import json
import logging
from datetime import timedelta

logger = logging.getLogger("unissono.checkout_recovery")


def run_checkout_abandoned_reminders(*, hours_min: int = 2, hours_max: int = 72) -> int:
    """Notifica quem tem checkout_iniciado e ainda não tem assinatura_paga."""
    from config import app_now_naive
    from db import (
        create_notification,
        get_db,
        get_user,
        mark_retention_sent,
        retention_was_sent,
        user_wants_email_notifications,
    )
    from email_service import is_configured, send_email
    from monetizacao import user_tem_assinatura_ativa
    from notification_email_service import _html_wrapper

    now = app_now_naive()
    lo = (now - timedelta(hours=hours_max)).strftime("%Y-%m-%d %H:%M:%S")
    hi = (now - timedelta(hours=hours_min)).strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    c = db.cursor()
    c.execute(
        """SELECT user_id, meta_json, created_at
           FROM product_funnel_events
           WHERE step = 'checkout_iniciado'
             AND created_at >= ? AND created_at <= ?
             AND user_id NOT IN (
               SELECT user_id FROM product_funnel_events WHERE step = 'assinatura_paga'
             )""",
        (lo, hi),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()

    sent = 0
    for row in rows:
        uid = row.get("user_id")
        if not uid or retention_was_sent(uid, "checkout_abandoned_v1"):
            continue
        if user_tem_assinatura_ativa(uid):
            continue
        meta = {}
        try:
            meta = json.loads(row.get("meta_json") or "{}")
        except Exception:
            meta = {}
        banda_id = meta.get("banda_id") or ""
        plano = meta.get("plano") or "pro"
        qs = f"plano={plano}&go=1"
        if banda_id:
            qs = f"banda_id={banda_id}&{qs}"
        title = "Seu checkout ficou pela metade"
        body = (
            "O pagamento do Uníssono não terminou. "
            "Retome em 1 toque — setlist, PDF e offline liberam na hora."
        )
        url_path = f"/assinatura/planos?{qs}"
        try:
            create_notification(
                uid,
                band_id=banda_id or None,
                actor_user_id=None,
                type="checkout_abandoned",
                title=title,
                body=body,
                url_path=url_path,
                skip_whatsapp=False,
            )
            user = get_user(uid)
            if user and user_wants_email_notifications(user) and is_configured():
                email = (user.get("email") or "").strip()
                if email:
                    html = _html_wrapper(
                        title,
                        f"<p>{body}</p>",
                        f"https://unissono.app{url_path}",
                        "Retomar checkout",
                    )
                    send_email([email], f"Uníssono — {title}", html, body)
            mark_retention_sent(uid, "checkout_abandoned_v1", "enviado")
            sent += 1
        except Exception:
            logger.exception("checkout abandoned fail user=%s", uid)
            mark_retention_sent(uid, "checkout_abandoned_v1", "erro")
    if sent:
        logger.info("Checkout abandonado: %s lembretes", sent)
    return sent
