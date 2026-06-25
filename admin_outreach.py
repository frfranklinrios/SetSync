"""Convites WhatsApp enviados pelo superadmin para bandas e estúdios."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from security import external_url_for
from whatsapp_service import is_configured, normalize_whatsapp_phone, send_whatsapp_text

logger = logging.getLogger('setsync.admin_outreach')

_PROSPECT_MARK_SENT = {
    'band_prospect': 'mark_band_prospect_invite_sent',
    'studio_prospect': 'mark_studio_prospect_invite_sent',
}


def _band_signup_invite_message(band_name: str, cidade: str, register_url: str, create_band_url: str) -> str:
    nome = (band_name or '').strip() or 'sua banda'
    local = f' em *{cidade}*' if (cidade or '').strip() else ''
    return (
        f'Olá! 👋\n\n'
        f'Você foi convidado a cadastrar a banda *{nome}*{local} no *SetSync*.\n\n'
        f'Organize repertório, setlists, agenda e Modo Tocar no palco — '
        f'grátis para começar, com trial Pro de 30 dias na primeira banda.\n\n'
        f'1) Crie sua conta:\n{register_url}\n\n'
        f'2) Depois crie sua banda:\n{create_band_url}\n\n'
        f'— Equipe SetSync'
    )


def _studio_signup_invite_message(
    studio_name: str, cidade: str, register_url: str, signup_studio_url: str, landing_url: str,
) -> str:
    nome = (studio_name or '').strip() or 'seu estúdio'
    local = f' em *{cidade}*' if (cidade or '').strip() else ''
    return (
        f'Olá! 👋\n\n'
        f'Você foi convidado a cadastrar o estúdio *{nome}*{local} no *SetSync*.\n\n'
        f'Bandas da região buscam salas de ensaio e podem reservar horário online — '
        f'com fotos, agenda, QR na recepção e trial de 30 dias no primeiro cadastro.\n\n'
        f'1) Crie sua conta:\n{register_url}\n\n'
        f'2) Cadastre o estúdio:\n{signup_studio_url}\n\n'
        f'Saiba mais:\n{landing_url}\n\n'
        f'— Equipe SetSync'
    )


def build_invite_message(target_type: str, entity: dict) -> str:
    if target_type == 'band_prospect':
        return _band_signup_invite_message(
            entity.get('nome') or '',
            (entity.get('cidade') or '').strip(),
            external_url_for('auth.register'),
            external_url_for('bands.create'),
        )
    if target_type == 'studio_prospect':
        return _studio_signup_invite_message(
            entity.get('nome') or '',
            (entity.get('cidade') or '').strip(),
            external_url_for('auth.register'),
            external_url_for('studios.register_studio'),
            external_url_for('studios.landing'),
        )
    raise ValueError(f'Tipo inválido: {target_type}')


def _get_prospect(target_type: str, target_id: str) -> dict | None:
    from db import get_band_prospect, get_studio_prospect

    if target_type == 'band_prospect':
        return get_band_prospect(target_id)
    if target_type == 'studio_prospect':
        return get_studio_prospect(target_id)
    return None


def _mark_prospect_sent(target_type: str, target_id: str) -> None:
    from db import mark_band_prospect_invite_sent, mark_studio_prospect_invite_sent

    if target_type == 'band_prospect':
        mark_band_prospect_invite_sent(target_id)
    elif target_type == 'studio_prospect':
        mark_studio_prospect_invite_sent(target_id)


def resend_prospect_invite(
    *,
    target_type: str,
    target_id: str,
    sent_by_user_id: str,
) -> dict[str, Any]:
    """Reenvia convite para prospect já salvo."""
    from db import log_admin_whatsapp_invite

    if target_type not in _PROSPECT_MARK_SENT:
        return {'ok': False, 'error': 'Tipo inválido.'}

    entity = _get_prospect(target_type, target_id)
    if not entity:
        return {'ok': False, 'error': 'Convite não encontrado.'}

    normalized = normalize_whatsapp_phone(entity.get('phone') or '')
    if not normalized:
        return {'ok': False, 'error': 'Telefone do prospect inválido.'}

    if not is_configured():
        return {
            'ok': False,
            'error': 'WhatsApp não configurado. Conecte em Admin → WhatsApp antes de enviar.',
        }

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

    if sent:
        _mark_prospect_sent(target_type, target_id)

    if not sent:
        return {'ok': False, 'error': 'Falha ao enviar pelo WhatsApp. Verifique a conexão em Admin → WhatsApp.'}

    return {'ok': True, 'phone': normalized, 'message': message}


def _send_new_prospect_invite(
    *,
    target_type: str,
    phone: str,
    nome: str,
    cidade: str,
    sent_by_user_id: str,
    notes: str,
    upsert_fn,
) -> dict[str, Any]:
    from db import log_admin_whatsapp_invite

    normalized = normalize_whatsapp_phone(phone)
    if not normalized:
        return {'ok': False, 'error': 'Número de WhatsApp inválido. Use DDD + número (ex.: 11 99999-9999).'}

    nome = (nome or '').strip()
    if not nome:
        label = 'estúdio' if target_type == 'studio_prospect' else 'banda'
        return {'ok': False, 'error': f'Informe o nome da {label} para personalizar o convite.'}

    if not is_configured():
        return {
            'ok': False,
            'error': 'WhatsApp não configurado. Conecte em Admin → WhatsApp antes de enviar.',
        }

    prospect_id = str(uuid.uuid4())
    cidade_val = (cidade or '').strip() or None
    upsert_fn(
        prospect_id=prospect_id,
        nome=nome,
        cidade=cidade_val,
        phone=normalized,
        created_by_user_id=sent_by_user_id,
        notes=(notes or '').strip() or None,
    )

    entity = {'id': prospect_id, 'nome': nome, 'cidade': cidade_val or ''}
    message = build_invite_message(target_type, entity)
    sent = send_whatsapp_text(normalized, message, link_preview=True)

    log_admin_whatsapp_invite(
        invite_id=str(uuid.uuid4()),
        target_type=target_type,
        target_id=prospect_id,
        phone=normalized,
        sent_by_user_id=sent_by_user_id,
        message_body=message,
        success=sent,
    )

    if sent:
        _mark_prospect_sent(target_type, prospect_id)

    if not sent:
        return {'ok': False, 'error': 'Falha ao enviar pelo WhatsApp. Verifique a conexão em Admin → WhatsApp.'}

    return {'ok': True, 'phone': normalized, 'prospect_id': prospect_id, 'message': message}


def send_studio_prospect_invite(
    *,
    phone: str,
    nome: str,
    cidade: str,
    sent_by_user_id: str,
    notes: str = '',
) -> dict[str, Any]:
    from db import upsert_studio_prospect

    return _send_new_prospect_invite(
        target_type='studio_prospect',
        phone=phone,
        nome=nome,
        cidade=cidade,
        sent_by_user_id=sent_by_user_id,
        notes=notes,
        upsert_fn=upsert_studio_prospect,
    )


def send_band_prospect_invite(
    *,
    phone: str,
    nome: str,
    cidade: str,
    sent_by_user_id: str,
    notes: str = '',
) -> dict[str, Any]:
    from db import upsert_band_prospect

    return _send_new_prospect_invite(
        target_type='band_prospect',
        phone=phone,
        nome=nome,
        cidade=cidade,
        sent_by_user_id=sent_by_user_id,
        notes=notes,
        upsert_fn=upsert_band_prospect,
    )
