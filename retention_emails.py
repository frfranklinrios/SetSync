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
        'subject': 'Comece pelo Uníssono: 1ª música (2 min)',
        'body': (
            'Você se cadastrou mas ainda não adicionou uma cifra.\n'
            'Coleção pessoal é grátis. Depois abra o Modo Tocar.\n'
            'Se for ensaio em grupo, aí sim crie a banda (trial Pro 30 dias).\n\n'
            '{cifra_url}'
        ),
        'html_body': (
            '<p>Você se cadastrou no Uníssono mas ainda <strong>não adicionou uma música</strong>.</p>'
            '<p>Comece pela coleção pessoal (grátis). Se for tocar em grupo, crie a banda depois e ganhe '
            '<strong>30 dias de Pro</strong>.</p>'
        ),
        'button_label': 'Adicionar 1ª música',
        'button_key': 'cifra_url',
    },
    'no_cifra_2': {
        'subject': 'Falta só a 1ª cifra no Uníssono',
        'body': (
            'Já faz uns dias desde o cadastro e você ainda não salvou uma música.\n'
            'Leva 2 minutos — depois o Modo Tocar faz o resto.\n\n'
            '{cifra_url}'
        ),
        'html_body': (
            '<p>Quem adiciona a <strong>primeira cifra</strong> e abre o Modo Tocar costuma ficar no Uníssono.</p>'
            '<p>Coleção pessoal é grátis e ilimitada.</p>'
        ),
        'button_label': 'Adicionar música agora',
        'button_key': 'cifra_url',
    },
    'trial_ending_7': {
        'subject': 'Faltam 7 dias de Pro — não perca o ensaio sem limites',
        'body': (
            'O trial Pro da banda {band_name} acaba em cerca de 7 dias.\n'
            'Assine Pro (R$ 29) ou Individual (R$ 15) se toca só.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Pro</strong> da banda <em>{band_name}</em> acaba em cerca de <strong>7 dias</strong>.</p>'
            '<p><strong>Pro</strong> R$ 29/mês (banda) · <strong>Individual</strong> R$ 15/mês (solo · PDF · compartilhar).</p>'
            '<p style="font-size:14px;color:#64748b;">Pagamento via Mercado Pago — cancele quando quiser.</p>'
        ),
        'button_label': 'Ver planos e assinar',
        'button_key': 'planos_url',
    },
    'trial_ending_5': {
        'subject': 'Seu próximo ensaio pode ficar sem Modo Tocar offline',
        'body': (
            'Faltam cerca de 5 dias do trial Pro da banda {band_name}.\n'
            'Sem Pro, o Modo Tocar offline e o PDF do ensaio deixam de ficar liberados.\n'
            'Assine antes do próximo culto/ensaio: Pro R$ 29 ou Individual R$ 15.\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>Faltam cerca de <strong>5 dias</strong> do trial Pro em <em>{band_name}</em>.</p>'
            '<p><strong>Seu próximo ensaio corre o risco de ficar sem o Modo Tocar offline</strong> '
            '(e sem PDF do ensaio com diagramas).</p>'
            '<p>Assine <strong>Pro R$ 29</strong> (banda) ou <strong>Individual R$ 15</strong> (solo) '
            'antes do compromisso.</p>'
        ),
        'button_label': 'Manter Modo Tocar offline',
        'button_key': 'planos_url',
    },
    'trial_ending_3': {
        'subject': 'Últimos 3 dias de Pro — continue sem limites',
        'body': (
            'Faltam cerca de 3 dias do trial Pro da banda {band_name}.\n'
            'Assine agora: Pro R$ 29 ou Individual R$ 15 (solo).\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>Faltam cerca de <strong>3 dias</strong> do trial Pro em <em>{band_name}</em>.</p>'
            '<p>Sem plano pago voltam os limites do Grátis e o PDF some.</p>'
        ),
        'button_label': 'Assinar agora',
        'button_key': 'planos_url',
    },
    'trial_ending_1': {
        'subject': 'Último dia de Pro — {band_name}',
        'body': (
            'O trial Pro da banda {band_name} termina amanhã.\n'
            '{offer_line}\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Pro</strong> de <em>{band_name}</em> termina <strong>amanhã</strong>.</p>'
            '<p>{offer_line}</p>'
        ),
        'button_label': '{button_label}',
        'button_key': 'planos_url',
    },
    'trial_expired': {
        'subject': 'Trial Pro acabou — {offer_short}',
        'body': (
            'O trial Pro da banda {band_name} terminou.\n'
            '{offer_line}\n\n'
            '{planos_url}'
        ),
        'html_body': (
            '<p>O <strong>trial Pro</strong> da banda <em>{band_name}</em> terminou.</p>'
            '<p>{offer_line}</p>'
            '<p style="font-size:14px;color:#64748b;">Pagamento via <strong>Mercado Pago</strong> — '
            'cartão não passa pelo Uníssono.</p>'
        ),
        'button_label': '{button_label}',
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
        'cifra_url': external_url_for('cifras.add_personal', welcome=1),
        'colecao_url': external_url_for('cifras.library'),
    }


def _trial_offer_extra(banda_id: str, band_name: str) -> dict:
    """Solo (1 integrante) → Individual; senão Pro."""
    from db import count_band_members

    members = count_band_members(banda_id) if banda_id else 1
    solo = members <= 1
    if solo:
        return {
            'band_name': band_name or 'sua banda',
            'offer_short': 'assine Individual (R$ 15)',
            'offer_line': (
                'Como você toca só, o plano <strong>Individual (R$ 15/mês)</strong> '
                'libera PDF e compartilhar — sem precisar de elenco.'
            ),
            'button_label': 'Assinar Individual — R$ 15/mês',
        }
    return {
        'band_name': band_name or 'sua banda',
        'offer_short': 'assine Pro (R$ 29)',
        'offer_line': (
            'Volte ao <strong>Pro (R$ 29/mês)</strong> e mantenha músicas, setlists '
            'e integrantes ilimitados + PDF.'
        ),
        'button_label': 'Assinar Pro — R$ 29/mês',
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
    raw_btn = tpl['button_label']
    try:
        button_label = raw_btn.format(**body_fmt)
    except (KeyError, ValueError):
        button_label = body_fmt.get('button_label') or raw_btn
    html = _html_wrapper(subject, html_inner, button_url, button_label)
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

    from db import list_retention_candidates_no_cifra

    for row in list_retention_candidates_no_cifra(min_days=2):
        uid = row['id']
        campaign = 'no_cifra_2'
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

    for days, campaign_key in (
        (7, 'trial_ending_7'),
        (5, 'trial_ending_5'),
        (3, 'trial_ending_3'),
        (1, 'trial_ending_1'),
    ):
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
            extra = _trial_offer_extra(row['banda_id'], row.get('band_name') or 'sua banda')
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
        extra = _trial_offer_extra(row['banda_id'], row.get('band_name') or 'sua banda')
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
