"""E-mails de retenção anti-churn (inatividade, banda vazia, trial expirado)."""

from __future__ import annotations

from db import (
    list_retention_candidates_inactive,
    list_retention_candidates_no_band,
    get_user,
    list_retention_candidates_trial_expired,
    list_retention_candidates_studio_trial_expired,
    mark_retention_sent,
    retention_was_sent,
    user_wants_email_notifications,
)
from email_service import is_configured, send_email
from notification_email_service import _html_wrapper
from security import external_url_for

_CAMPAIGNS = {
    'inactive_7': {
        'subject': 'Sentimos sua falta no SetSync 🎸',
        'body': (
            'Faz uma semana que você não entra no SetSync.\n'
            'Seu repertório e setlists continuam salvos — volte quando quiser.\n\n'
            '{dashboard_url}'
        ),
        'html_body': (
            '<p>Faz <strong>uma semana</strong> que você não entra no SetSync.</p>'
            '<p>Seu repertório e setlists continuam salvos. Que tal abrir o '
            '<strong>Modo Tocar</strong> no próximo ensaio?</p>'
        ),
        'button_label': 'Voltar ao painel',
        'button_key': 'dashboard_url',
    },
    'inactive_14': {
        'subject': 'Seu repertório está esperando',
        'body': (
            'Já faz 2 semanas sem acessar o SetSync.\n'
            'Atualize uma cifra ou monte um setlist em minutos.\n\n'
            '{dashboard_url}'
        ),
        'html_body': (
            '<p>Já faz <strong>2 semanas</strong> sem acessar o SetSync.</p>'
            '<p>Uma cifra nova ou um setlist atualizado faz toda diferença no culto.</p>'
        ),
        'button_label': 'Abrir meu painel',
        'button_key': 'dashboard_url',
    },
    'inactive_30': {
        'subject': 'Ainda dá tempo de retomar o SetSync',
        'body': (
            'Faz um mês que você não usa o SetSync.\n'
            'Este é nosso último lembrete por enquanto — estamos aqui quando precisar.\n\n'
            '{dashboard_url}'
        ),
        'html_body': (
            '<p>Faz <strong>um mês</strong> que você não usa o SetSync.</p>'
            '<p>Este é nosso último lembrete por enquanto. Sua conta e dados '
            'continuam seguros.</p>'
        ),
        'button_label': 'Retomar agora',
        'button_key': 'dashboard_url',
    },
    'no_band_3': {
        'subject': 'Crie sua primeira banda no SetSync',
        'body': (
            'Você se cadastrou mas ainda não criou uma banda.\n'
            'Em 2 minutos você organiza o repertório da equipe.\n\n'
            '{bands_url}'
        ),
        'html_body': (
            '<p>Você se cadastrou no SetSync mas ainda <strong>não criou uma banda</strong>.</p>'
            '<p>Adicione músicas, convide integrantes e use o Modo Tocar no ensaio.</p>'
        ),
        'button_label': 'Criar minha banda',
        'button_key': 'bands_url',
    },
    'trial_expired': {
        'subject': 'Seu trial Pro acabou — continue sem limites',
        'body': (
            'O trial Pro da banda {band_name} terminou.\n'
            'Assine para manter músicas, setlists e integrantes ilimitados.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Pro</strong> da banda <em>{band_name}</em> terminou.</p>'
            '<p>Volte ao Pro por R$ 29/mês e mantenha recursos ilimitados + exportação PDF.</p>'
            '<p style="font-size:14px;color:#64748b;">Ao assinar, você paga pelo <strong>Mercado Pago</strong> — '
            'seus dados de cartão não passam pelo SetSync.</p>'
        ),
        'button_label': 'Ver planos Pro',
        'button_key': 'planos_url',
    },
    'studio_trial_expired': {
        'subject': 'Trial Premium do estúdio terminou',
        'body': (
            'Seu trial Premium do estúdio {studio_name} terminou.\n'
            'O plano básico permite até 2 salas. Assine Premium por R$ 49/mês.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Premium</strong> do estúdio <em>{studio_name}</em> terminou.</p>'
            '<p>Volte a ter <strong>salas ilimitadas</strong> por R$ 49/mês.</p>'
            '<p style="font-size:14px;color:#64748b;">Pagamento via <strong>Mercado Pago</strong> — '
            'cartão não passa pelo SetSync.</p>'
        ),
        'button_label': 'Ver planos Estúdio',
        'button_key': 'planos_url',
    },
}


def _urls() -> dict[str, str]:
    return {
        'dashboard_url': external_url_for('dashboard'),
        'bands_url': external_url_for('bands.list_bands'),
        'planos_url': external_url_for('assinatura_bp.planos'),
        'planos_estudio_url': external_url_for('assinatura_bp.planos') + '#estudio',
    }


def _send_campaign(
    email: str,
    campaign: str,
    *,
    extra: dict | None = None,
) -> bool:
    tpl = _CAMPAIGNS.get(campaign)
    if not tpl or not email:
        return False
    urls = {**_urls(), **(extra or {})}
    button_url = urls.get(tpl['button_key'])
    body_fmt = {k: urls.get(k, '') for k in urls}
    if extra:
        body_fmt.update(extra)
    subject = tpl['subject'].format(**body_fmt)
    body = tpl['body'].format(**body_fmt)
    html_inner = tpl['html_body'].format(**body_fmt)
    html = _html_wrapper(subject, html_inner, button_url, tpl['button_label'])
    return send_email([email], subject, html, body)


def verificar_e_disparar_retencao() -> int:
    """Job diário: e-mails anti-churn. Retorna quantidade enviada."""
    if not is_configured():
        return 0

    enviados = 0

    for days, campaign in ((7, 'inactive_7'), (14, 'inactive_14'), (30, 'inactive_30')):
        for row in list_retention_candidates_inactive(days):
            uid = row['id']
            if retention_was_sent(uid, campaign):
                continue
            email = (row.get('email') or '').strip()
            if not email:
                continue
            if _send_campaign(email, campaign):
                mark_retention_sent(uid, campaign, 'enviado')
                enviados += 1
            else:
                mark_retention_sent(uid, campaign, 'erro')

    for row in list_retention_candidates_no_band(min_days=3):
        uid = row['id']
        campaign = 'no_band_3'
        if retention_was_sent(uid, campaign):
            continue
        email = (row.get('email') or '').strip()
        if not email:
            continue
        if _send_campaign(email, campaign):
            mark_retention_sent(uid, campaign, 'enviado')
            enviados += 1
        else:
            mark_retention_sent(uid, campaign, 'erro')

    for row in list_retention_candidates_trial_expired():
        uid = row['owner_id']
        campaign = f"trial_expired:{row['banda_id']}"
        if retention_was_sent(uid, campaign):
            continue
        if not user_wants_email_notifications(get_user(uid)):
            continue
        email = (row.get('owner_email') or '').strip()
        if not email:
            continue
        extra = {'band_name': row.get('band_name') or 'sua banda'}
        if _send_campaign(email, 'trial_expired', extra=extra):
            mark_retention_sent(uid, campaign, 'enviado')
            enviados += 1
        else:
            mark_retention_sent(uid, campaign, 'erro')

    for row in list_retention_candidates_studio_trial_expired():
        uid = row['owner_id']
        campaign = f"studio_trial_expired:{row.get('studio_id') or uid}"
        if retention_was_sent(uid, campaign):
            continue
        if not user_wants_email_notifications(get_user(uid)):
            continue
        email = (row.get('owner_email') or '').strip()
        if not email:
            continue
        extra = {
            'studio_name': row.get('studio_nome') or 'seu estúdio',
            'planos_url': _urls()['planos_estudio_url'],
        }
        if _send_campaign(email, 'studio_trial_expired', extra=extra):
            mark_retention_sent(uid, campaign, 'enviado')
            enviados += 1
        else:
            mark_retention_sent(uid, campaign, 'erro')

    return enviados
