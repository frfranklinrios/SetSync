"""Reativação de quem cadastrou e sumiu — e-mail + WhatsApp + in-app."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from config import app_now_naive
from db import (
    IS_POSTGRES,
    create_notification,
    get_db,
    is_superadmin,
    mark_retention_sent,
    retention_was_sent,
    user_wants_email_notifications,
    user_wants_whatsapp_notifications,
)
from email_service import is_configured as email_configured
from email_service import send_email
from notification_email_service import _html_wrapper
from security import external_url_for

logger = logging.getLogger("unissono.winback")

# Uma vez por usuário — não reenvia se rodar de novo.
CAMPAIGN = "winback_v2"

_SEGMENTS = {
    "cold": {
        "subject": "Sua conta no Uníssono ainda está aí — 1 minuto para voltar",
        "preview": "Escolha a música do próximo ensaio e abra o Modo Tocar.",
        "body": (
            "Olá{nome}!\n\n"
            "Você criou conta no Uníssono e ainda não voltou. "
            "Em 1 minuto você escolhe a cifra do ensaio e abre o Modo Tocar.\n\n"
            "Para a banda: Pro R$ 29/mês (setlist + PDF + offline).\n\n"
            "{cta_url}\n"
        ),
        "html": (
            "<h2>Sentimos sua falta</h2>\n"
            "<p>Sua conta no Uníssono continua ativa. O próximo passo é simples:</p>\n"
            "<ol>\n"
            "<li>Escolha a <strong>música do ensaio</strong></li>\n"
            "<li>Abra o <strong>Modo Tocar</strong> (demo grátis)</li>\n"
            "<li>Para a banda: assine o <strong>Pro R$ 29/mês</strong>"
            " (setlist + PDF + offline)</li>\n"
            "</ol>\n"
        ),
        "button_label": "Escolher minha música",
        "cta": "cifra",
        "wa": (
            "Olá{nome}! 👋\n\n"
            "Sua conta no *Uníssono* está pronta — falta só escolher a música do ensaio "
            "e abrir o Modo Tocar.\n\n"
            "Para ensaiar em banda: *Pro R$ 29/mês* (PDF + offline).\n\n"
            "{cta_url}"
        ),
    },
    "idle_band": {
        "subject": "Sua banda no Uníssono está esperando o próximo ensaio",
        "preview": "Abra o Modo Tocar ou monte a setlist do show.",
        "body": (
            "Olá{nome}!\n\n"
            "Sua banda já está no Uníssono, mas faz tempo que ninguém entra.\n"
            "Abra o Modo Tocar ou monte a setlist do próximo show — "
            "PDF e offline liberam no Pro (incluso no trial).\n\n"
            "{cta_url}\n"
        ),
        "html": (
            "<h2>A banda está pronta — falta o ensaio</h2>\n"
            "<p>Faz um tempo que você não entra. Em poucos toques:</p>\n"
            "<ul>\n"
            "<li>Abra o <strong>Modo Tocar</strong> com a setlist</li>\n"
            "<li>Marque o próximo show no Comando</li>\n"
            "<li>Use PDF e offline enquanto o trial Pro estiver ativo</li>\n"
            "</ul>\n"
        ),
        "button_label": "Abrir meu painel",
        "cta": "dashboard",
        "wa": (
            "Olá{nome}! 👋\n\n"
            "Sua banda no *Uníssono* está esperando o próximo ensaio.\n"
            "Abra o Modo Tocar ou monte a setlist — PDF e offline no Pro/trial.\n\n"
            "{cta_url}"
        ),
    },
    "unpaid": {
        "subject": "Você já tocou no Uníssono — falta só assinar",
        "preview": "Pro R$ 29 ou Individual R$ 15 · Mercado Pago",
        "body": (
            "Olá{nome}!\n\n"
            "Você já usou o Modo Tocar de verdade. Para PDF, offline no palco "
            "e limites ilimitados:\n"
            "• Pro R$ 29/mês (banda) — anual sai ~R$ 21/mês\n"
            "• Individual R$ 15/mês (solo)\n\n"
            "{cta_url}\n"
        ),
        "html": (
            "<h2>Você já sentiu o valor — agora é só assinar</h2>\n"
            "<p>Quem toca de verdade no Uníssono costuma querer PDF e offline no show.</p>\n"
            "<p><strong>Pro</strong> R$ 29/mês · <strong>Individual</strong> R$ 15/mês ·\n"
            "pagamento via Mercado Pago · cancele quando quiser.</p>\n"
        ),
        "button_label": "Assinar agora",
        "cta": "planos",
        "wa": (
            "Olá{nome}! 👋\n\n"
            "Você já tocou no *Uníssono*. Para PDF + offline + limites ilimitados:\n"
            "Pro R$ 29/mês ou Individual R$ 15/mês (Mercado Pago).\n\n"
            "{cta_url}"
        ),
    },
}


def _cta_url(segment: str) -> str:
    cta = (_SEGMENTS.get(segment) or {}).get("cta") or "dashboard"
    if cta == "cifra":
        return external_url_for("cifras.comecar")
    if cta == "planos":
        return external_url_for("assinatura_bp.planos", plano="pro", go=1)
    return external_url_for("dashboard")


def _display_name(user: dict) -> str:
    nome = (
        user.get("display_name") or user.get("name") or user.get("username") or ""
    ).strip()
    if not nome:
        return ""
    return f" {nome.split()[0]}"


def list_dormant_users(*, min_inactive_days: int = 5) -> list[dict[str, Any]]:
    """Contas com e-mail, sem plano pago, inativas há N dias (exclui admin/demo)."""
    cutoff = (app_now_naive() - timedelta(days=min_inactive_days)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    db = get_db()
    c = db.cursor()
    sql = """
        SELECT u.*
        FROM users u
        WHERE COALESCE(u.email, '') != ''
          AND COALESCE(u.is_demo, 0) = 0
          AND COALESCE(u.last_login_at, u.created_at) <= {cutoff}
          AND NOT EXISTS (
              SELECT 1 FROM bands b
              JOIN assinaturas a ON a.banda_id = b.id
              WHERE b.owner_id = u.id
                AND a.status = 'ativa'
                AND a.plano IN ('individual', 'pro', 'worship')
                AND COALESCE(a.mp_preapproval_id, '') != ''
          )
        ORDER BY COALESCE(u.last_login_at, u.created_at) ASC
    """
    if IS_POSTGRES:
        c.execute(sql.format(cutoff="?::timestamp"), (cutoff,))
    else:
        c.execute(sql.format(cutoff="datetime(?)"), (cutoff,))
    rows = [dict(r) for r in c.fetchall()]
    db.close()

    out: list[dict[str, Any]] = []
    for u in rows:
        if is_superadmin(u["id"]):
            continue
        if retention_was_sent(u["id"], CAMPAIGN):
            continue
        seg = classify_segment(u["id"])
        u["winback_segment"] = seg
        out.append(u)
    return out


def classify_segment(user_id: str) -> str:
    db = get_db()
    c = db.cursor()
    c.execute(
        """SELECT 1 FROM product_funnel_events
           WHERE user_id = ? AND step = 'play_mode_real' LIMIT 1""",
        (user_id,),
    )
    played = bool(c.fetchone())
    c.execute(
        """SELECT 1 FROM product_funnel_events
           WHERE user_id = ? AND step = 'assinatura_paga' LIMIT 1""",
        (user_id,),
    )
    paid_funnel = bool(c.fetchone())
    c.execute(
        """SELECT 1 FROM bands WHERE owner_id = ?
           UNION SELECT 1 FROM band_members WHERE user_id = ? LIMIT 1""",
        (user_id, user_id),
    )
    has_band = bool(c.fetchone())
    db.close()
    if paid_funnel:
        return "idle_band" if has_band else "cold"
    if played:
        return "unpaid"
    if has_band:
        return "idle_band"
    return "cold"


def preview_winback(*, min_inactive_days: int = 5) -> dict[str, Any]:
    users = list_dormant_users(min_inactive_days=min_inactive_days)
    by_seg: dict[str, int] = {}
    with_phone = 0
    for u in users:
        seg = u.get("winback_segment") or "cold"
        by_seg[seg] = by_seg.get(seg, 0) + 1
        if (u.get("phone") or "").strip():
            with_phone += 1
    return {
        "campaign": CAMPAIGN,
        "total": len(users),
        "by_segment": by_seg,
        "with_phone": with_phone,
        "email_ok": email_configured(),
    }


def _send_email(user: dict, segment: str) -> bool:
    if not email_configured():
        return False
    if not user_wants_email_notifications(user):
        return False
    tpl = _SEGMENTS[segment]
    email = (user.get("email") or "").strip()
    if not email:
        return False
    nome = _display_name(user)
    cta = _cta_url(segment)
    subject = tpl["subject"]
    body = tpl["body"].format(nome=nome, cta_url=cta)
    html_inner = tpl["html"]
    html = _html_wrapper(subject, html_inner, cta, tpl["button_label"])
    return send_email([email], subject, html, body)


def _send_whatsapp(user: dict, segment: str) -> bool:
    if not user_wants_whatsapp_notifications(user):
        return False
    phone = (user.get("phone") or "").strip()
    if not phone:
        return False
    try:
        from whatsapp_service import is_configured, send_whatsapp_text
    except Exception:
        return False
    if not is_configured():
        return False
    tpl = _SEGMENTS[segment]
    text = tpl["wa"].format(nome=_display_name(user), cta_url=_cta_url(segment))
    try:
        return bool(send_whatsapp_text(phone, text))
    except Exception:
        logger.exception("WhatsApp winback falhou user=%s", user.get("id"))
        return False


def disparar_winback(
    *,
    min_inactive_days: int = 5,
    dry_run: bool = False,
    limit: int | None = None,
    whatsapp: bool = True,
) -> dict[str, int]:
    """Dispara reativação. dry_run só conta."""
    users = list_dormant_users(min_inactive_days=min_inactive_days)
    if limit is not None:
        users = users[: max(0, int(limit))]

    stats = {
        "total": len(users),
        "email": 0,
        "whatsapp": 0,
        "inapp": 0,
        "erros": 0,
        "pulados": 0,
    }
    if dry_run:
        stats["email"] = sum(
            1
            for u in users
            if user_wants_email_notifications(u) and (u.get("email") or "").strip()
        )
        stats["whatsapp"] = sum(
            1
            for u in users
            if whatsapp
            and user_wants_whatsapp_notifications(u)
            and (u.get("phone") or "").strip()
        )
        stats["inapp"] = len(users)
        return stats

    for user in users:
        uid = user["id"]
        if retention_was_sent(uid, CAMPAIGN):
            stats["pulados"] += 1
            continue
        segment = user.get("winback_segment") or classify_segment(uid)
        ok_any = False
        try:
            create_notification(
                uid,
                band_id=None,
                actor_user_id=None,
                type="product_update",
                title="Sentimos sua falta no Uníssono",
                body=(
                    "Escolha a música do ensaio, abra o Modo Tocar ou assine o Pro "
                    "para PDF e offline no palco."
                ),
                url_path=(
                    "/dashboard"
                    if segment != "unpaid"
                    else "/assinatura/planos?plano=pro&go=1"
                ),
                skip_whatsapp=True,
                skip_email=True,
            )
            stats["inapp"] += 1
            ok_any = True
        except Exception:
            logger.exception("in-app winback falhou user=%s", uid)

        if _send_email(user, segment):
            stats["email"] += 1
            ok_any = True
        if whatsapp and _send_whatsapp(user, segment):
            stats["whatsapp"] += 1
            ok_any = True

        if ok_any:
            mark_retention_sent(uid, CAMPAIGN, "enviado")
        else:
            mark_retention_sent(uid, CAMPAIGN, "erro")
            stats["erros"] += 1

    return stats
