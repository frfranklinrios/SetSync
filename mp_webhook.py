"""Processamento compartilhado de webhooks Mercado Pago."""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import timedelta

from db import get_assinatura, get_assinatura_by_mp_id, update_assinatura
from mercadopago_client import get_mp_sdk
from monetizacao import (
    PLANO_ESTUDIO_PREMIUM,
    PLANO_GRATIS,
    PLANO_PRO,
    PLANOS,
    PLANOS_ESTUDIO,
    STATUS_ATIVA,
    STATUS_CANCELADA,
    STATUS_INADIMPLENTE,
)
from config import app_now_naive, app_now_str

logger = logging.getLogger(__name__)

_PLANOS_PAGOS = frozenset(PLANOS.keys()) | frozenset(PLANOS_ESTUDIO.keys())


def webhook_autentico(req, secret: str) -> bool:
    """Valida notificação via query ?secret=, X-Webhook-Secret ou x-signature."""
    import os
    secret = (secret or '').strip()
    if not secret:
        if os.getenv('FLASK_ENV', 'development').lower() == 'production':
            logger.error('MP_WEBHOOK_SECRET ausente em produção — webhook rejeitado')
            return False
        logger.warning('MP_WEBHOOK_SECRET não definido (dev) — webhook rejeitado')
        return False

    # Compatível com docs/ngrok: /assinatura/webhook?secret=...
    if (req.args.get('secret') or '').strip() == secret:
        return True

    if req.headers.get('X-Webhook-Secret') == secret:
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
    request_id = req.headers.get('x-request-id', '') or req.headers.get('X-Request-Id', '')
    # MP: IDs alfanuméricos no manifest usam lowercase
    id_candidates = []
    raw = str(data_id)
    if raw:
        id_candidates.append(raw)
        if raw.lower() != raw:
            id_candidates.append(raw.lower())
    else:
        id_candidates.append('')
    for did in id_candidates:
        manifest = f'id:{did};request-id:{request_id};ts:{ts};'
        expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, v1):
            return True
    return False


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
    agora = app_now_str()
    if not proxima_cobranca:
        proxima_cobranca = (app_now_naive() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    if plano not in PLANOS or plano == PLANO_GRATIS:
        plano = PLANO_PRO
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
    try:
        from db import get_band
        from product_funnel import log_funnel_step

        band = get_band(banda_id)
        if band and band.get('owner_id'):
            log_funnel_step(
                band['owner_id'],
                'assinatura_paga',
                meta={'plano': plano, 'source': 'mp_webhook'},
            )
    except Exception:
        logger.exception('Funnel assinatura_paga (banda) falhou')


def ativar_studio_subscription_mp(
    user_id: str,
    plano: str,
    mp_id: str,
    proxima_cobranca: str | None = None,
) -> None:
    from models_studio import update_studio_subscription

    if not proxima_cobranca:
        proxima_cobranca = (app_now_naive() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    if plano not in PLANOS_ESTUDIO:
        plano = PLANO_ESTUDIO_PREMIUM
    update_studio_subscription(
        user_id,
        plano=plano,
        status=STATUS_ATIVA,
        mp_subscription_id=mp_id,
        mp_preapproval_id=mp_id,
        data_proxima_cobranca=proxima_cobranca,
    )
    try:
        from product_funnel import log_funnel_step

        log_funnel_step(
            user_id,
            'assinatura_paga',
            meta={'plano': plano, 'tipo': 'studio', 'source': 'mp_webhook'},
        )
    except Exception:
        logger.exception('Funnel assinatura_paga (estúdio) falhou')


def _parse_band_ref(ref: str) -> tuple[str | None, str]:
    ref = (ref or '').strip()
    if not ref or ref.startswith('studio:'):
        return None, PLANO_PRO
    if ':' in ref:
        banda_id, plano = ref.split(':', 1)
        plano = (plano or PLANO_PRO).strip()
        if plano not in PLANOS:
            plano = PLANO_PRO
        return banda_id.strip() or None, plano
    return ref, PLANO_PRO


def _processar_preapproval_studio(body: dict, data_id: str) -> bool:
    """Retorna True se o evento foi tratado como assinatura de estúdio."""
    ref = body.get('external_reference', '')
    if not ref.startswith('studio:'):
        return False

    parts = ref.split(':', 2)
    user_id = parts[1] if len(parts) > 1 else ''
    plano = parts[2] if len(parts) > 2 else PLANO_ESTUDIO_PREMIUM
    if not user_id:
        from models_studio import get_studio_subscription_by_mp_id
        row = get_studio_subscription_by_mp_id(data_id)
        if row:
            user_id = row['user_id']
            plano = row.get('plano', PLANO_ESTUDIO_PREMIUM)

    if not user_id:
        logger.warning('Webhook preapproval estúdio sem user_id (id=%s)', data_id)
        return True

    status_mp = (body.get('status') or '').lower()
    from models_studio import update_studio_subscription

    if status_mp in ('authorized', 'active', 'approved'):
        next_charge = body.get('next_payment_date')
        ativar_studio_subscription_mp(user_id, plano, data_id, next_charge)
        logger.info('Assinatura estúdio ativada user=%s plano=%s', user_id, plano)
    elif status_mp == 'cancelled':
        update_studio_subscription(user_id, status=STATUS_CANCELADA)
    elif status_mp == 'paused':
        update_studio_subscription(user_id, status=STATUS_INADIMPLENTE)
    return True


def _ativar_de_pagamento_aprovado(pbody: dict, data_id: str) -> None:
    """Ativa/renova assinatura a partir de um payment approved (com plano correto)."""
    meta = pbody.get('metadata') or {}
    preapproval_id = (
        meta.get('preapproval_id')
        or meta.get('preapprovalId')
        or ''
    )
    ref = str(pbody.get('external_reference') or '')

    # Estúdio
    if ref.startswith('studio:'):
        parts = ref.split(':', 2)
        user_id = parts[1] if len(parts) > 1 else ''
        plano = parts[2] if len(parts) > 2 else PLANO_ESTUDIO_PREMIUM
        if user_id:
            mp_id = str(preapproval_id or data_id)
            ativar_studio_subscription_mp(user_id, plano, mp_id)
            logger.info('Pagamento estúdio aprovado user=%s plano=%s', user_id, plano)
            return
        from models_studio import get_studio_subscription_by_mp_id
        row = get_studio_subscription_by_mp_id(str(preapproval_id)) if preapproval_id else None
        if row:
            ativar_studio_subscription_mp(
                row['user_id'],
                row.get('plano') or PLANO_ESTUDIO_PREMIUM,
                str(preapproval_id or data_id),
            )
            return

    row = get_assinatura_by_mp_id(str(preapproval_id)) if preapproval_id else None
    banda_id, plano = _parse_band_ref(ref)
    if not row and banda_id:
        row = get_assinatura(banda_id)
        if row:
            row = dict(row)
            row['banda_id'] = banda_id

    if not row:
        logger.warning(
            'Pagamento aprovado sem assinatura local (payment=%s preapproval=%s ref=%s)',
            data_id,
            preapproval_id,
            ref,
        )
        return

    banda_id = row['banda_id']
    plano_local = (row.get('plano') or '').strip()
    if plano in _PLANOS_PAGOS and plano != PLANO_GRATIS:
        pass
    elif plano_local in PLANOS and plano_local != PLANO_GRATIS:
        plano = plano_local
    else:
        plano = PLANO_PRO

    mp_id = str(preapproval_id or row.get('mp_preapproval_id') or data_id)
    next_dt = (app_now_naive() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    ativar_assinatura_mp(banda_id, plano, mp_id, next_dt)
    logger.info('Pagamento aprovado: ativou banda=%s plano=%s', banda_id, plano)
    try:
        import admin_notifications as an
        an.subscription_activated(banda_id, plano, source='payment')
    except Exception:
        logger.exception('Notificação admin (pagamento) falhou')


def processar_notificacao_mp(topic: str, data_id: str) -> None:
    """Busca recurso no MP e atualiza assinatura local."""
    if not data_id:
        logger.info('Webhook MP sem data_id (topic=%s)', topic)
        return

    sdk = get_mp_sdk()
    topic_l = topic.lower()

    # authorized_payment NÃO é preapproval — o data.id é outro recurso
    if topic_l == 'subscription_authorized_payment':
        logger.info('Webhook MP authorized_payment id=%s — ignorado (usa payment/preapproval)', data_id)
        return

    if 'preapproval' in topic_l or topic_l == 'subscription_preapproval':
        info = sdk.preapproval().get(data_id)
        if info.get('status') not in (200, 201):
            logger.error('MP preapproval.get(%s): %s', data_id, info)
            return
        body = info.get('response') or {}
        if _processar_preapproval_studio(body, data_id):
            return

        banda_id, plano = _parse_band_ref(body.get('external_reference', ''))
        status_mp = (body.get('status') or '').lower()
        if not banda_id:
            row = get_assinatura_by_mp_id(data_id)
            if row:
                banda_id = row['banda_id']
                local_plano = (row.get('plano') or '').strip()
                if local_plano in PLANOS and local_plano != PLANO_GRATIS:
                    plano = local_plano

        if not banda_id:
            logger.warning('Webhook preapproval sem banda_id (id=%s)', data_id)
            return

        if status_mp in ('authorized', 'active', 'approved'):
            next_charge = body.get('next_payment_date')
            ativar_assinatura_mp(banda_id, plano, data_id, next_charge)
            logger.info('Assinatura ativada banda=%s plano=%s', banda_id, plano)
            try:
                import admin_notifications as an
                an.subscription_activated(banda_id, plano)
            except Exception:
                logger.exception('Notificação admin (assinatura ativa) falhou')
        elif status_mp == 'cancelled':
            update_assinatura(
                banda_id,
                status=STATUS_CANCELADA,
                data_cancelamento=app_now_str(),
            )
            try:
                import admin_notifications as an
                an.subscription_cancelled(banda_id)
            except Exception:
                logger.exception('Notificação admin (cancelamento) falhou')
        elif status_mp == 'paused':
            update_assinatura(banda_id, status=STATUS_INADIMPLENTE)
            try:
                import admin_notifications as an
                an.subscription_inadimplente(banda_id)
            except Exception:
                logger.exception('Notificação admin (inadimplente) falhou')

    elif topic_l == 'payment' or 'payment' in topic_l:
        pay = sdk.payment().get(data_id)
        if pay.get('status') not in (200, 201):
            logger.error('MP payment.get(%s): %s', data_id, pay)
            return
        pbody = pay.get('response') or {}
        if pbody.get('status') == 'approved':
            _ativar_de_pagamento_aprovado(pbody, data_id)
    else:
        logger.info('Webhook MP ignorado: topic=%s id=%s', topic, data_id)
