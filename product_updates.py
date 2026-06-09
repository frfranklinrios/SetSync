"""Comunicados de produto para todos os usuários (in-app + e-mail + WhatsApp)."""

from __future__ import annotations

from db import create_notification, get_all_users, mark_retention_sent, retention_was_sent

# Identificador único — não reenvia se o script rodar de novo.
CAMPAIGN_NOTIFICACOES_2026_06 = 'product_notificacoes_2026_06'
CAMPAIGN_NOTIFICACOES_2026_06_RETRY = 'product_notificacoes_2026_06_retry'
CAMPAIGN_AGENDA_2026_06 = 'product_agenda_2026_06'
CAMPAIGN_MAPS_AGENDA_2026_06 = 'product_maps_agenda_2026_06'

_ANNOUNCEMENTS = {
    CAMPAIGN_NOTIFICACOES_2026_06: {
        'type': 'product_update',
        'title': 'Novidades: alertas por e-mail e WhatsApp',
        'body': (
            'Agora você recebe alertas da banda por e-mail e WhatsApp — novas cifras, '
            'setlists, convites e mudanças na equipe.\n\n'
            'No próximo login, cadastre seu WhatsApp em Meu perfil para não perder nada. '
            'Os e-mails saem de contato@setsync.com.br.'
        ),
        'url_path': '/auth/perfil',
    },
    CAMPAIGN_NOTIFICACOES_2026_06_RETRY: {
        'type': 'product_update',
        'title': 'Novidades: alertas por e-mail e WhatsApp',
        'body': (
            'Agora você recebe alertas da banda por e-mail e WhatsApp — novas cifras, '
            'setlists, convites e mudanças na equipe.\n\n'
            'Cadastre seu WhatsApp em Meu perfil para não perder nada. '
            'Os e-mails saem de contato@setsync.com.br.'
        ),
        'url_path': '/auth/perfil',
    },
    CAMPAIGN_AGENDA_2026_06: {
        'type': 'product_update',
        'title': 'Novidade: Agenda da banda com calendário e escalação',
        'body': (
            'Organize ensaios e cultos na nova Agenda da banda:\n\n'
            '• Calendário mensal na aba Agenda\n'
            '• Vincule uma setlist a cada evento\n'
            '• Escale integrantes por evento (ideal para ministérios grandes)\n'
            '• Próximos eventos no painel inicial\n'
            '• Lembrete automático 24h antes (e-mail, WhatsApp e notificação)\n\n'
            'Abra sua banda → aba Agenda para começar.'
        ),
        'url_path': '/dashboard',
    },
    CAMPAIGN_MAPS_AGENDA_2026_06: {
        'type': 'product_update',
        'title': 'Agenda: local com Google Maps',
        'body': (
            'Ao criar ou editar um evento na Agenda, o campo Local agora tem '
            'sugestões do Google Maps — igreja, estúdio ou endereço.\n\n'
            'No detalhe do evento você abre o mapa e vê a localização embutida. '
            'Ideal para o time chegar certo no ensaio ou culto.'
        ),
        'url_path': '/dashboard',
    },
}


def enviar_comunicado(
    campaign: str,
    *,
    dry_run: bool = False,
) -> dict[str, int]:
    """Dispara in-app + e-mail + WhatsApp (via create_notification)."""
    tpl = _ANNOUNCEMENTS.get(campaign)
    if not tpl:
        raise ValueError(f'Campanha desconhecida: {campaign}')

    stats = {'total': 0, 'enviados': 0, 'pulados': 0, 'erros': 0}

    for user in get_all_users():
        uid = user['id']
        stats['total'] += 1
        if retention_was_sent(uid, campaign):
            stats['pulados'] += 1
            continue
        if dry_run:
            stats['enviados'] += 1
            continue
        try:
            create_notification(
                uid,
                band_id=None,
                actor_user_id=None,
                type=tpl['type'],
                title=tpl['title'],
                body=tpl['body'],
                url_path=tpl['url_path'],
            )
            mark_retention_sent(uid, campaign, 'enviado')
            stats['enviados'] += 1
        except Exception:
            mark_retention_sent(uid, campaign, 'erro')
            stats['erros'] += 1

    return stats
