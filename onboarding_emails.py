"""Sequência de 5 e-mails automáticos após cadastro."""

from __future__ import annotations

from datetime import datetime, timedelta

from db import ensure_onboarding_rows, list_onboarding_pending, mark_onboarding_sent, get_user
from monetizacao_emails import _send
from security import external_url_for

# Dias após cadastro para cada e-mail (0 = imediato)
_ONBOARDING_SCHEDULE = {
    1: 0,
    2: 1,
    3: 3,
    4: 5,
    5: 7,
}

_EMAILS = {
    1: {
        'subject': 'Bem-vindo ao SetSync! Veja como começar 🎸',
        'body': (
            'Olá! Sua conta no SetSync está pronta.\n\n'
            'Próximo passo: crie sua primeira banda e adicione uma música.\n'
            'Assista ao tour rápido e experimente o Modo Tocar.\n\n'
            'Criar banda: {bands_url}'
        ),
        'html': (
            '<h2>Bem-vindo ao SetSync!</h2>'
            '<p>Sua conta está pronta. Comece criando sua <strong>primeira banda</strong> '
            'e cadastrando uma cifra.</p>'
            '<p><a href="{bands_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Criar minha banda</a></p>'
            '<p>Depois, abra o <strong>Modo Tocar</strong> para ver a cifra em tela cheia '
            'com auto-scroll — ideal no ensaio.</p>'
        ),
    },
    2: {
        'subject': 'Sua banda já está no SetSync?',
        'body': (
            'Convide integrantes pelo link de convite da banda.\n'
            'Todos compartilham o mesmo repertório — sem PDF desatualizado.\n\n'
            '{bands_url}'
        ),
        'html': (
            '<h2>Monte sua equipe</h2>'
            '<p>Em <strong>Membros</strong>, copie o link de convite e envie no WhatsApp.</p>'
            '<p>Benefício: repertório único, tom por cantor e setlists sincronizados.</p>'
            '<p><a href="{bands_url}">Ver minhas bandas</a></p>'
        ),
    },
    3: {
        'subject': 'Monte seu primeiro setlist em 2 minutos',
        'body': (
            'Escolha músicas, ordene o roteiro e defina cantor/tom em cada faixa.\n'
            'Transposição automática por vocalista.\n\n'
            '{dashboard_url}'
        ),
        'html': (
            '<h2>Seu primeiro setlist</h2>'
            '<ol>'
            '<li>Abra uma banda</li>'
            '<li>Crie setlist → adicione músicas</li>'
            '<li>Defina cantor e tom por faixa</li>'
            '</ol>'
            '<p><a href="{dashboard_url}">Ir ao painel</a></p>'
        ),
    },
    4: {
        'subject': 'O Modo Tocar vai mudar seu ensaio',
        'body': (
            'Modo Tocar: tela cheia, auto-scroll, tema escuro, funciona offline (PWA).\n'
            'Perfeito para culto e palco.\n\n'
            '{ajuda_url}'
        ),
        'html': (
            '<h2>Modo Tocar</h2>'
            '<ul>'
            '<li>Tela cheia para o palco</li>'
            '<li>Auto-scroll ajustável</li>'
            '<li>PWA offline no celular</li>'
            '</ul>'
            '<p><a href="{ajuda_url}">Ver guia completo</a></p>'
        ),
    },
    5: {
        'subject': 'Você está chegando no limite do plano Grátis',
        'body': (
            'O plano Grátis tem limites de músicas, setlists e integrantes.\n'
            'No Pro: ilimitado + PDF por R$ 29/mês.\n\n'
            '{planos_url}'
        ),
        'html': (
            '<h2>Conheça o Pro</h2>'
            '<p>Músicas, setlists e integrantes <strong>ilimitados</strong>, '
            'exportação PDF e suporte prioritário.</p>'
            '<p><em>"Vale cada centavo — nosso ensaio nunca mais voltou ao caderno."</em></p>'
            '<p><a href="{planos_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Fazer upgrade para Pro — R$29/mês</a></p>'
        ),
    },
}


def _urls() -> dict[str, str]:
    return {
        'bands_url': external_url_for('bands.list_bands'),
        'dashboard_url': external_url_for('dashboard'),
        'ajuda_url': external_url_for('ajuda.index'),
        'planos_url': external_url_for('assinatura_bp.planos'),
    }


def registrar_onboarding_usuario(usuario_id: str) -> None:
    """Chamar após cadastro — cria filas de e-mails 1–5."""
    ensure_onboarding_rows(usuario_id)


def verificar_e_disparar_onboarding() -> int:
    """Job diário: envia e-mails de onboarding no prazo. Retorna quantidade enviada."""
    urls = _urls()
    agora = datetime.utcnow()
    enviados = 0
    for row in list_onboarding_pending():
        num = int(row['email_numero'])
        dias_necessarios = _ONBOARDING_SCHEDULE.get(num, 999)
        created = row.get('user_created_at') or row.get('created_at')
        if not created:
            continue
        if isinstance(created, str):
            try:
                cadastro = datetime.strptime(str(created)[:19], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        else:
            cadastro = created
        if (agora - cadastro).days < dias_necessarios:
            continue
        email = row.get('email')
        if not email:
            continue
        tpl = _EMAILS.get(num)
        if not tpl:
            continue
        try:
            _send(
                [email],
                tpl['subject'],
                tpl['html'].format(**urls),
                tpl['body'].format(**urls),
            )
            mark_onboarding_sent(row['id'], 'enviado')
            enviados += 1
        except Exception:
            mark_onboarding_sent(row['id'], 'erro')
    return enviados
