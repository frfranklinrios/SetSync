"""Painel admin — conectar servidor WhatsApp (Evolution API)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for

from blueprints.admin import superadmin_required
from whatsapp_config import official_whatsapp_number, whatsapp_provider
from whatsapp_service import provider_status

whatsapp_admin_bp = Blueprint('whatsapp_admin', __name__, url_prefix='/admin/whatsapp')


@whatsapp_admin_bp.route('/')
@superadmin_required
def index():
    if whatsapp_provider() == 'meta':
        status = provider_status()
        return render_template(
            'admin/whatsapp.html',
            status=status,
            qr=None,
            meta_mode=True,
            official_number=official_whatsapp_number(),
        )

    from whatsapp_server.client import ensure_instance, fetch_qrcode, is_connected

    ensure_instance()
    status = provider_status()
    qr = None
    if not is_connected():
        qr = fetch_qrcode()
    return render_template(
        'admin/whatsapp.html',
        status=status,
        qr=qr,
        meta_mode=False,
        official_number=official_whatsapp_number(),
    )


@whatsapp_admin_bp.route('/reconectar', methods=['POST'])
@superadmin_required
def reconectar():
    if whatsapp_provider() == 'meta':
        flash('Provider Meta: configure token no .env.', 'info')
        return redirect(url_for('whatsapp_admin.index'))

    from whatsapp_server.client import fetch_qrcode, logout_instance

    logout_instance()
    fetch_qrcode()
    flash('Escaneie o novo QR Code com o WhatsApp do número oficial.', 'info')
    return redirect(url_for('whatsapp_admin.index'))
