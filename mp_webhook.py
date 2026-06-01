"""Processamento compartilhado de webhooks Mercado Pago."""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timedelta

from db import get_assinatura_by_mp_id, update_assinatura
from mercadopago_client import get_mp_sdk
from monetizacao import PLANO_PRO, STATUS_ATIVA, STATUS_CANCELADA, STATUS_INADIMPLENTE

logger = logging.getLogger(__name__)


def webhook_autentico(req, secret: str) -> bool:
    """Valida notificação via X-Webhook-Secret ou cabeçalho x-signature."""
    secret = (secret or '').strip()
    if not secret:
        logger.warning('MP_WEBHOOK_SECRET não definido — webhook aceito sem validação')
        return True

    if req.headers.get('X-Webhook-Secret') == secret or req.args.get('secret') == secret:
        return True

    x_sig = req.headers.get('x-signature') or req.headers.get('X-Signature') or ''
    if not x_sig:
        return False

    parts = {}
    for part in x_sig.split(','):
        if '=' in part:
            k, v = part.split('=', 1)
            parts[k.strip()] = v.strip()
    ts = parts.get('ts', '')
    v1 = parts.get('v1', '')
    payload = req.get_json(silent=True) or {}
    data_id = (
        req.args.get('data.id')
        or req.args.get('id')
        or (payload.get('data') or {}).get('id')
        or payload.get('id')
        or ''
    )
    request_id = req.headers.get('x-request-id', '')
    manifest = f'id:{data_id};request-id:{request_id};ts:{ts};'
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)


def extrair_topic_id(req) -> tuple[str, str]:
    """Extrai tipo de evento e ID do recurso (query string ou JSON)."""
    payload = req.get_json(silent=True) or {}
    data_id = (
        req.args.get('data.id')
        or req.args.get('id')
        or (payload.get('data') or {}).get('id')
        or payload.get('id')
        or ''
    )
    topic = (
        payload.get('type')
        or payload.get('topic')
        or payload.get('action')
        or req.args.get('type')
        or req.args.get('topic')
        or req.args.get('action')
        or ''
    )
    return str(topic).lower(), str(data_id)


def ativar_assinatura_mp(banda_id: str, plano: str, mp_id: str, proxima_cobranca: str | None = None) -> None:
    agora = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    if not proxima_cobranca:
        proxima_cobranca = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    update_assinatura(
        banda_id,
        plano=plano,
        status=STATUS_ATIVA,
        mp_subscription_id=mp_id,
        mp_preapproval_id=mp_id,
        data_inicio=agora,
        data_proxima_cobranca=proxima_cobranca,
        data_cancelamento=None,
    )


def processar_notificacao_mp(topic: str, data_id: str) -> None:
    """Busca recurso no MP e atualiza assinatura local."""
    if not data_id:
        logger.info('Webhook MP sem data_id (topic=%s)', topic)
        return

    sdk = get_mp_sdk()
    topic_l = topic.lower()

    if 'preapproval' in topic_l or topic_l in ('subscription_preapproval', 'subscription_authorized_payment'):
        info = sdk.preapproval().get(data_id)
        if info.get('status') not in (200, 201):
            logger.error('MP preapproval.get(%s): %s', data_id, info)
            return
        body = info.get('response') or {}
        ref = body.get('external_reference', '')
        banda_id, plano = (ref.split(':', 1) + [PLANO_PRO])[:2] if ':' in ref else (None, PLANO_PRO)
        status_mp = (body.get('status') or '').lower()
        if not banda_id:
            row = get_assinatura_by_mp_id(data_id)
            if row:
                banda_id = row['banda_id']
                plano = row.get('plano', PLANO_PRO)

        if not banda_id:
            logger.warning('Webhook preapproval sem banda_id (id=%s)', data_id)
            return

        if status_mp in ('authorized', 'active', 'approved'):
            next_charge = body.get('next_payment_date')
            ativar_assinatura_mp(banda_id, plano, data_id, next_charge)
            logger.info('Assinatura ativada banda=%s plano=%s', banda_id, plano)
        elif status_mp == 'cancelled':
            update_assinatura(
                banda_id,
                status=STATUS_CANCELADA,
                data_cancelamento=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            )
        elif status_mp == 'paused':
            update_assinatura(banda_id, status=STATUS_INADIMPLENTE)

    elif topic_l == 'payment' or 'payment' in topic_l:
        pay = sdk.payment().get(data_id)
        if pay.get('status') not in (200, 201):
            logger.error('MP payment.get(%s): %s', data_id, pay)
            return
        pbody = pay.get('response') or {}
        if pbody.get('status') == 'approved':
            preapproval_id = (
                pbody.get('metadata', {}).get('preapproval_id')
                or pbody.get('external_reference')
            )
            row = get_assinatura_by_mp_id(str(preapproval_id)) if preapproval_id else None
            if row:
                next_dt = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
                update_assinatura(row['banda_id'], data_proxima_cobranca=next_dt, status=STATUS_ATIVA)
    else:
        logger.info('Webhook MP ignorado: topic=%s id=%s', topic, data_id)
