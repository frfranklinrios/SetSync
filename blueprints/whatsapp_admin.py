"""Painel admin — conectar servidor WhatsApp (Evolution API)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from blueprints.admin import superadmin_required
from whatsapp_config import official_whatsapp_number, whatsapp_provider
from whatsapp_service import provider_status

whatsapp_admin_bp = Blueprint("whatsapp_admin", __name__, url_prefix="/admin/whatsapp")


@whatsapp_admin_bp.route("/")
@superadmin_required
def index():
    if whatsapp_provider() == "meta":
        status = provider_status()
        return render_template(
            "admin/whatsapp.html",
            status=status,
            qr=None,
            pairing_mode=False,
            meta_mode=True,
            official_number=official_whatsapp_number(),
        )

    from whatsapp_server.client import ensure_instance, fetch_qrcode, is_connected

    want_qr = request.args.get("qr") == "1"
    status = provider_status()
    qr = None
    pairing_mode = False
    if not status.get("connected") and want_qr:
        ensure_instance()
        if not is_connected():
            qr = fetch_qrcode()
            pairing_mode = True
        status = provider_status()
    return render_template(
        "admin/whatsapp.html",
        status=status,
        qr=qr,
        pairing_mode=pairing_mode,
        meta_mode=False,
        official_number=official_whatsapp_number(),
    )


@whatsapp_admin_bp.route("/conectar", methods=["POST"])
@superadmin_required
def conectar():
    if whatsapp_provider() == "meta":
        flash("Provider Meta: configure token no .env.", "info")
        return redirect(url_for("whatsapp_admin.index"))

    from whatsapp_server.client import ensure_instance

    ensure_instance()
    flash("Escaneie o QR Code com o WhatsApp que deseja conectar.", "info")
    return redirect(url_for("whatsapp_admin.index", qr=1))


@whatsapp_admin_bp.route("/reconectar", methods=["POST"])
@superadmin_required
def reconectar():
    if whatsapp_provider() == "meta":
        flash("Provider Meta: configure token no .env.", "info")
        return redirect(url_for("whatsapp_admin.index"))

    from whatsapp_server.client import logout_instance

    logout_instance()
    flash("Escaneie o novo QR Code com o WhatsApp do número oficial.", "info")
    return redirect(url_for("whatsapp_admin.index", qr=1))


@whatsapp_admin_bp.route("/desconectar", methods=["POST"])
@superadmin_required
def desconectar():
    if whatsapp_provider() == "meta":
        flash("Provider Meta: remova o token no .env para desativar.", "info")
        return redirect(url_for("whatsapp_admin.index"))

    from whatsapp_server.client import logout_instance

    if logout_instance():
        flash("WhatsApp desconectado com sucesso.", "success")
    else:
        flash("Sessão do WhatsApp encerrada.", "info")
    return redirect(url_for("whatsapp_admin.index"))
