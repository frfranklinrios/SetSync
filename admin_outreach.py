"""Convites WhatsApp enviados pelo superadmin para bandas e estúdios."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from band_invites import make_band_invite_token
from security import external_url_for
from whatsapp_service import is_configured, normalize_whatsapp_phone, send_whatsapp_text

logger = logging.getLogger('setsync.admin_outreach')


def _band_invite_message(band_name: str, invite_url: str, register_url: str) -> str:
    return (
        f'Olá! 👋\n\n'
        f'A banda *{band_name}* pode organizar repertório, setlists e palco no *SetSync* '
        f'— grátis para começar.\n\n'
        f'Crie sua conta:\n{register_url}\n\n'
        f'Link direto para entrar na banda:\n{invite_url}\n\n'
        f'— Equipe SetSync'
    )


def _studio_invite_message(studio_name: str, cidade: str, register_url: str, landing_url: str) -> str:
    local = f' em {cidade}' if cidade else ''
    return (
        f'Olá! 👋\n\n'
        f'O estúdio *{studio_name}*{local} pode receber reservas online pelo *SetSync* '
        f'— bandas buscam salas pela cidade.\n\n'
        f'Cadastre ou gerencie seu estúdio:\n{register_url}\n\n'
        f'Saiba mais:\n{landing_url}\n\n'
        f'— Equipe SetSync'
    )


def build_invite_message(target_type: str, entity: dict) -> str:
    if target_type == 'band':
        token = make_band_invite_token(entity['id'])
        invite_url = external_url_for('auth.convite', token=token)
        register_url = external_url_for('auth.register')
        return _band_invite_message(entity.get('name') or 'sua banda', invite_url, register_url)
    if target_type == 'studio':
        register_url = external_url_for('studios.register_studio')
        landing_url = external_url_for('studios.landing')
        return _studio_invite_message(
            entity.get('nome') or 'seu estúdio',
            (entity.get('cidade') or '').strip(),
            register_url,
            landing_url,
        )
    raise ValueError(f'Tipo inválido: {target_type}')


def send_admin_whatsapp_invite(
    *,
    target_type: str,
    target_id: str,
    phone: str,
    sent_by_user_id: str,
    save_phone: bool = True,
) -> dict[str, Any]:
    """Salva telefone (opcional), envia convite e registra log."""
    from db import get_band, log_admin_whatsapp_invite, set_band_contact_whatsapp
    from models_studio import get_studio, update_studio

    normalized = normalize_whatsapp_phone(phone)
    if not normalized:
        return {'ok': False, 'error': 'Número de WhatsApp inválido. Use DDD + número (ex.: 11 99999-9999).'}

    if not is_configured():
        return {
            'ok': False,
            'error': 'WhatsApp não configurado. Conecte em Admin → WhatsApp antes de enviar.',
        }

    if target_type == 'band':
        entity = get_band(target_id)
        if not entity:
            return {'ok': False, 'error': 'Banda não encontrada.'}
        if save_phone:
            set_band_contact_whatsapp(target_id, normalized)
    elif target_type == 'studio':
        entity = get_studio(target_id)
        if not entity:
            return {'ok': False, 'error': 'Estúdio não encontrado.'}
        if save_phone:
            update_studio(target_id, whatsapp=normalized)
    else:
        return {'ok': False, 'error': 'Tipo inválido.'}

    message = build_invite_message(target_type, entity)
    sent = send_whatsapp_text(normalized, message, link_preview=True)

    log_admin_whatsapp_invite(
        invite_id=str(uuid.uuid4()),
        target_type=target_type,
        target_id=target_id,
        phone=normalized,
        sent_by_user_id=sent_by_user_id,
        message_body=message,
        success=sent,
    )

    if not sent:
        return {'ok': False, 'error': 'Falha ao enviar pelo WhatsApp. Verifique a conexão em Admin → WhatsApp.'}

    return {'ok': True, 'phone': normalized, 'message': message}
