"""Webmail integrado ao SetSync — usa a sessão do superadmin (sem login separado)."""

from __future__ import annotations

import os

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from blueprints.admin import superadmin_required
from db import get_user
from email_service import send_email
from mail_server.config import DATABASE_PATH
from mail_server.server.storage import EmailStorage

mail_web_bp = Blueprint("mail_web", __name__, url_prefix="/admin/email")

_storage: EmailStorage | None = None


def _storage_instance() -> EmailStorage:
    global _storage
    if _storage is None:
        _storage = EmailStorage(DATABASE_PATH)
    return _storage


def mailbox_for_user(user_id: int | None) -> str:
    """Caixa @setsync.com.br do usuário master ou contato padrão do .env."""
    fallback = (os.getenv("MAIL_USERNAME") or "contato@setsync.com.br").strip().lower()
    if not user_id:
        return fallback
    user = get_user(user_id)
    if not user:
        return fallback
    email = (user.get("email") or "").strip().lower()
    if email.endswith("@setsync.com.br"):
        return email
    return fallback


def _owner() -> str:
    return mailbox_for_user(session.get("user_id"))


@mail_web_bp.route("/")
@superadmin_required
def inbox():
    owner = _owner()
    emails = _storage_instance().get_emails_sync(owner, "inbox")
    unread = sum(1 for e in emails if not e.get("is_read"))
    return render_template(
        "mail/inbox.html",
        emails=emails,
        folder="inbox",
        mailbox=owner,
        unread_count=unread,
    )


@mail_web_bp.route("/sent")
@superadmin_required
def sent():
    owner = _owner()
    emails = _storage_instance().get_emails_sync(owner, "sent")
    return render_template(
        "mail/inbox.html",
        emails=emails,
        folder="sent",
        mailbox=owner,
        unread_count=0,
    )


@mail_web_bp.route("/compose", methods=["GET", "POST"])
@superadmin_required
def compose():
    owner = _owner()
    if request.method == "POST":
        to_raw = (request.form.get("to") or "").strip()
        subject = (request.form.get("subject") or "").strip()
        body = (request.form.get("body") or "").strip()
        recipients = [a.strip() for a in to_raw.replace(";", ",").split(",") if a.strip()]
        if not recipients or not subject or not body:
            flash("Preencha destinatário, assunto e mensagem.", "warning")
            return render_template(
                "mail/compose.html",
                mailbox=owner,
                to=to_raw,
                subject=subject,
                body=body,
            )
        ok = send_email(recipients=recipients, subject=subject, body=body)
        if ok:
            _storage_instance().save_email_sync(
                sender=owner,
                recipients=recipients,
                subject=subject,
                body_text=body,
                body_html=None,
                owner_email=owner,
                folder="sent",
            )
            flash("E-mail enviado.", "success")
            return redirect(url_for("mail_web.sent"))
        flash("Não foi possível enviar o e-mail. Verifique MAIL_* no .env.", "danger")
        return render_template(
            "mail/compose.html",
            mailbox=owner,
            to=to_raw,
            subject=subject,
            body=body,
        )
    return render_template("mail/compose.html", mailbox=owner, to="", subject="", body="")


@mail_web_bp.route("/<int:email_id>")
@superadmin_required
def view_email(email_id: int):
    owner = _owner()
    msg = _storage_instance().get_email_sync(email_id, owner)
    if not msg:
        abort(404)
    if not msg.get("is_read"):
        _storage_instance().mark_as_read_sync(email_id, owner)
        msg["is_read"] = 1
    return render_template("mail/view.html", msg=msg, mailbox=owner)


@mail_web_bp.route("/<int:email_id>/delete", methods=["POST"])
@superadmin_required
def delete_email(email_id: int):
    owner = _owner()
    msg = _storage_instance().get_email_sync(email_id, owner)
    if not msg:
        abort(404)
    _storage_instance().delete_email_sync(email_id, owner)
    flash("Mensagem excluída.", "success")
    folder = msg.get("folder") or "inbox"
    if folder == "sent":
        return redirect(url_for("mail_web.sent"))
    return redirect(url_for("mail_web.inbox"))
