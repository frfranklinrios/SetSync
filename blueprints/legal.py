"""Páginas legais e consentimento de cookies (LGPD)."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, session

from lgpd import (
    dpo_label,
    privacy_contact_email,
    set_session_tracking_consent,
    tracking_requires_consent,
)

legal_bp = Blueprint('legal', __name__)


@legal_bp.route('/privacidade')
def privacidade():
    return render_template(
        'legal/privacidade.html',
        privacy_email=privacy_contact_email(),
        dpo_name=dpo_label(),
    )


@legal_bp.route('/termos')
def termos():
    return render_template(
        'legal/termos.html',
        privacy_email=privacy_contact_email(),
    )


@legal_bp.route('/api/cookie-consent', methods=['POST'])
def cookie_consent():
    data = request.get_json(silent=True) or {}
    choice = (data.get('choice') or '').strip().lower()
    if choice not in ('accept', 'reject', 'essential'):
        return jsonify({'ok': False, 'erro': 'Escolha inválida'}), 400
    set_session_tracking_consent(choice == 'accept')
    return jsonify({'ok': True, 'tracking': choice == 'accept'})


@legal_bp.app_context_processor
def inject_lgpd():
    from lgpd import may_load_tracking, session_tracking_consent

    return dict(
        privacy_email=privacy_contact_email(),
        dpo_name=dpo_label(),
        tracking_requires_consent=tracking_requires_consent(),
        may_load_tracking=may_load_tracking(),
        cookie_consent_choice=session_tracking_consent(),
    )
