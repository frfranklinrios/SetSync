"""E-mails de retenção anti-churn (inatividade, banda vazia, trial expirado)."""

from __future__ import annotations

from db import (
    list_retention_candidates_inactive,
    list_retention_candidates_no_band,
    get_user,
    list_retention_candidates_trial_expired,
    list_retention_candidates_studio_trial_expired,
    list_trials_expiring_soon,
    list_studio_trials_expiring_soon,
    mark_retention_sent,
    retention_was_sent,
    user_wants_email_notifications,
)
from email_service import is_configured, send_email
from notification_email_service import _html_wrapper
from security import external_url_for

_CAMPAIGNS = {
    'inactive_7': {
        'subject': 'Sentimos sua falta no Uníssono 🎸',
        'body': (
            'Faz uma semana que você não entra no Uníssono.\n'
            'Seu repertório e setlists continuam salvos — volte quando quiser.\n\n'
            '{dashboard_url}'
        ),
        'html_body': (
            '<p>Faz <strong>uma semana</strong> que você não entra no Uníssono.</p>'
            '<p>Seu repertório e setlists continuam salvos. Que tal abrir o '
            '<strong>Modo Tocar</strong> no próximo ensaio?</p>'
        ),
        'button_label': 'Abrir Modo Tocar',
        'button_key': 'dashboard_url',
    },
    'inactive_14': {
        'subject': 'Seu repertório está esperando',
        'body': (
            'Já faz 2 semanas sem acessar o Uníssono.\n'
            'Atualize uma cifra ou monte um setlist em minutos.\n\n'
            '{dashboard_url}'
        ),
        'html_body': (
            '<p>Já faz <strong>2 semanas</strong> sem acessar o Uníssono.</p>'
            '<p>Abra sua setlist e use o <strong>Modo Tocar</strong> no próximo ensaio.</p>'
        ),
        'button_label': 'Abrir minha setlist',
        'button_key': 'dashboard_url',
    },
    'inactive_30': {
        'subject': 'Ainda dá tempo de retomar o Uníssono',
        'body': (
            'Faz um mês que você não usa o Uníssono.\n'
            'Este é nosso último lembrete por enquanto — estamos aqui quando precisar.\n\n'
            '{dashboard_url}'
        ),
        'html_body': (
            '<p>Faz <strong>um mês</strong> que você não usa o Uníssono.</p>'
            '<p>Este é nosso último lembrete por enquanto. Sua conta e dados '
            'continuam seguros.</p>'
        ),
        'button_label': 'Retomar e tocar',
        'button_key': 'dashboard_url',
    },
    'no_band_3': {
        'subject': 'Crie sua primeira banda no Uníssono',
        'body': (
            'Você se cadastrou mas ainda não criou uma banda.\n'
            'Em 2 minutos você organiza o repertório e libera 30 dias de Pro.\n\n'
            '{bands_url}'
        ),
        'html_body': (
            '<p>Você se cadastrou no Uníssono mas ainda <strong>não criou uma banda</strong>.</p>'
            '<p>Crie agora, liberamos <strong>30 dias de Pro</strong> e você chega no Modo Tocar.</p>'
        ),
        'button_label': 'Criar banda · liberar Pro',
        'button_key': 'bands_url',
    },
    'trial_ending_7': {
        'subject': 'Faltam 7 dias de Pro — não perca o ensaio sem limites',
        'body': (
            'O trial Pro da banda {band_name} acaba em cerca de 7 dias.\n'
            'Assine por R$ 29/mês e mantenha PDF + músicas ilimitadas.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Pro</strong> da banda <em>{band_name}</em> acaba em cerca de <strong>7 dias</strong>.</p>'
            '<p>Assine Pro por <strong>R$ 29/mês</strong> e mantenha PDF, setlists e integrantes ilimitados.</p>'
            '<p style="font-size:14px;color:#64748b;">Pagamento via Mercado Pago — cancele quando quiser.</p>'
        ),
        'button_label': 'Assinar Pro — R$ 29',
        'button_key': 'planos_url',
    },
    'trial_ending_3': {
        'subject': 'Últimos 3 dias de Pro — continue sem limites',
        'body': (
            'Faltam cerca de 3 dias do trial Pro da banda {band_name}.\n'
            'Assine agora por R$ 29/mês.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>Faltam cerca de <strong>3 dias</strong> do trial Pro em <em>{band_name}</em>.</p>'
            '<p>Sem o Pro, voltam os limites do Grátis e o PDF some. Continue por <strong>R$ 29/mês</strong>.</p>'
        ),
        'button_label': 'Assinar Pro agora — R$ 29',
        'button_key': 'planos_url',
    },
    'trial_expired': {
        'subject': 'Seu trial Pro acabou — continue sem limites',
        'body': (
            'O trial Pro da banda {band_name} terminou.\n'
            'Sem Pro: limites do Grátis e sem PDF. Assine por R$ 29/mês.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Pro</strong> da banda <em>{band_name}</em> terminou.</p>'
            '<p>Volte ao Pro por <strong>R$ 29/mês</strong> e mantenha recursos ilimitados + exportação PDF.</p>'
            '<p style="font-size:14px;color:#64748b;">Ao assinar, você paga pelo <strong>Mercado Pago</strong> — '
            'seus dados de cartão não passam pelo Uníssono.</p>'
        ),
        'button_label': 'Assinar Pro — R$ 29/mês',
        'button_key': 'planos_url',
    },
    'studio_trial_ending_3': {
        'subject': 'Trial Premium do estúdio acaba em 3 dias',
        'body': (
            'O trial Premium de {studio_name} acaba em breve.\n'
            'Premium = salas ilimitadas + destaque na busca por R$ 49/mês.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Premium</strong> do estúdio <em>{studio_name}</em> acaba em cerca de 3 dias.</p>'
            '<p>Assine Premium por <strong>R$ 49/mês</strong>: salas ilimitadas e mais visibilidade na busca.</p>'
        ),
        'button_label': 'Assinar Premium — R$ 49',
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
            '<p>Volte a ter <strong>salas ilimitadas</strong> e destaque na busca por R$ 49/mês.</p>'
            '<p style="font-size:14px;color:#64748b;">Pagamento via <strong>Mercado Pago</strong> — '
            'cartão não passa pelo Uníssono.</p>'
        ),
        'button_label': 'Assinar Premium — R$ 49',
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

    for days, campaign_key in ((7, 'trial_ending_7'), (3, 'trial_ending_3')):
        for row in list_trials_expiring_soon(days):
            uid = row['owner_id']
            campaign = f"{campaign_key}:{row['banda_id']}"
            if retention_was_sent(uid, campaign):
                continue
            if not user_wants_email_notifications(get_user(uid)):
                continue
            email = (row.get('owner_email') or '').strip()
            if not email:
                continue
            extra = {'band_name': row.get('band_name') or 'sua banda'}
            if _send_campaign(email, campaign_key, extra=extra):
                mark_retention_sent(uid, campaign, 'enviado')
                enviados += 1
            else:
                mark_retention_sent(uid, campaign, 'erro')

    for row in list_studio_trials_expiring_soon(3):
        uid = row['user_id']
        campaign = f"studio_trial_ending_3:{uid}"
        if retention_was_sent(uid, campaign):
            continue
        if not user_wants_email_notifications(get_user(uid)):
            continue
        email = (row.get('owner_email') or '').strip()
        if not email:
            continue
        extra = {
            'studio_name': 'seu estúdio',
            'planos_url': _urls()['planos_estudio_url'],
        }
        if _send_campaign(email, 'studio_trial_ending_3', extra=extra):
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
