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


def _studio_signup_invite_message(studio_name: str, cidade: str, register_url: str, landing_url: str) -> str:
    nome = (studio_name or '').strip() or 'seu estúdio'
    local = f' em *{cidade}*' if (cidade or '').strip() else ''
    return (
        f'Olá! 👋\n\n'
        f'Você foi convidado a cadastrar o estúdio *{nome}*{local} no *SetSync*.\n\n'
        f'Bandas da região buscam salas de ensaio e podem reservar horário online — '
        f'com fotos, agenda, QR na recepção e trial de 30 dias no primeiro cadastro.\n\n'
        f'Cadastre seu estúdio (crie sua conta e complete o perfil):\n{register_url}\n\n'
        f'Saiba mais:\n{landing_url}\n\n'
        f'— Equipe SetSync'
    )


def build_invite_message(target_type: str, entity: dict) -> str:
    if target_type == 'band':
        token = make_band_invite_token(entity['id'])
        invite_url = external_url_for('auth.convite', token=token)
        register_url = external_url_for('auth.register')
        return _band_invite_message(entity.get('name') or 'sua banda', invite_url, register_url)
    if target_type == 'studio_prospect':
        register_url = external_url_for('studios.register_studio')
        landing_url = external_url_for('studios.landing')
        return _studio_signup_invite_message(
            entity.get('nome') or '',
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
    """Convite para banda existente (membro) ou reenvio de prospect de estúdio."""
    from db import get_band, log_admin_whatsapp_invite, set_band_contact_whatsapp

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
        message = build_invite_message(target_type, entity)
    elif target_type == 'studio_prospect':
        from db import get_studio_prospect, mark_studio_prospect_invite_sent

        entity = get_studio_prospect(target_id)
        if not entity:
            return {'ok': False, 'error': 'Prospect de estúdio não encontrado.'}
        message = build_invite_message(target_type, entity)
        phone = entity.get('phone') or normalized
        normalized = normalize_whatsapp_phone(phone) or normalized
    else:
        return {'ok': False, 'error': 'Tipo inválido.'}

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

    if target_type == 'studio_prospect' and sent:
        mark_studio_prospect_invite_sent(target_id)

    if not sent:
        return {'ok': False, 'error': 'Falha ao enviar pelo WhatsApp. Verifique a conexão em Admin → WhatsApp.'}

    return {'ok': True, 'phone': normalized, 'message': message}


def send_studio_prospect_invite(
    *,
    phone: str,
    nome: str,
    cidade: str,
    sent_by_user_id: str,
    notes: str = '',
) -> dict[str, Any]:
    """Convida dono de estúdio que ainda não está no SetSync a se cadastrar."""
    from db import (
        log_admin_whatsapp_invite,
        mark_studio_prospect_invite_sent,
        upsert_studio_prospect,
    )

    normalized = normalize_whatsapp_phone(phone)
    if not normalized:
        return {'ok': False, 'error': 'Número de WhatsApp inválido. Use DDD + número (ex.: 11 99999-9999).'}

    nome = (nome or '').strip()
    if not nome:
        return {'ok': False, 'error': 'Informe o nome do estúdio para personalizar o convite.'}

    if not is_configured():
        return {
            'ok': False,
            'error': 'WhatsApp não configurado. Conecte em Admin → WhatsApp antes de enviar.',
        }

    prospect_id = str(uuid.uuid4())
    cidade = (cidade or '').strip() or None
    upsert_studio_prospect(
        prospect_id=prospect_id,
        nome=nome,
        cidade=cidade,
        phone=normalized,
        created_by_user_id=sent_by_user_id,
        notes=(notes or '').strip() or None,
    )

    entity = {'id': prospect_id, 'nome': nome, 'cidade': cidade or ''}
    message = build_invite_message('studio_prospect', entity)
    sent = send_whatsapp_text(normalized, message, link_preview=True)

    log_admin_whatsapp_invite(
        invite_id=str(uuid.uuid4()),
        target_type='studio_prospect',
        target_id=prospect_id,
        phone=normalized,
        sent_by_user_id=sent_by_user_id,
        message_body=message,
        success=sent,
    )

    if sent:
        mark_studio_prospect_invite_sent(prospect_id)

    if not sent:
        return {'ok': False, 'error': 'Falha ao enviar pelo WhatsApp. Verifique a conexão em Admin → WhatsApp.'}

    return {'ok': True, 'phone': normalized, 'prospect_id': prospect_id, 'message': message}
