"""Comunicados de produto para todos os usuários (in-app + e-mail + WhatsApp)."""

from __future__ import annotations

from db import create_notification, get_all_users, mark_retention_sent, retention_was_sent

# Identificador único — não reenvia se o script rodar de novo.
CAMPAIGN_NOTIFICACOES_2026_06 = 'product_notificacoes_2026_06'
CAMPAIGN_NOTIFICACOES_2026_06_RETRY = 'product_notificacoes_2026_06_retry'

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
