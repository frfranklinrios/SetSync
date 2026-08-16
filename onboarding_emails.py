"""Sequência de 5 e-mails automáticos após cadastro."""

from __future__ import annotations

from datetime import datetime, timedelta

from db import ensure_onboarding_rows, list_onboarding_pending, mark_onboarding_sent, get_user
from email_service import is_configured, send_email
from security import external_url_for
from config import app_now_naive, app_now_str

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
        'subject': 'Bem-vindo ao Uníssono — qual música do seu ensaio?',
        'body': (
            'Olá! Sua conta no Uníssono está pronta.\n\n'
            'Próximo passo (1 min): busque ou cole a cifra que você toca de verdade.\n'
            'O palco abre nessa música — exemplo não conta.\n\n'
            'Escolher minha música: {cifra_url}'
        ),
        'html': (
            '<h2>Qual música você toca no próximo ensaio?</h2>'
            '<p>Sua conta está pronta. Busque ou cole <strong>a cifra de vocês</strong> '
            '— o Modo Tocar abre nela agora.</p>'
            '<p><a href="{cifra_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Escolher minha música</a></p>'
            '<p>Tela cheia, tom e auto-scroll. Sem banda, sem cartão.</p>'
        ),
    },
    2: {
        'subject': 'Qual música do seu ensaio ainda faltou?',
        'body': (
            'Você se cadastrou no Uníssono e ainda não salvou a cifra que toca de verdade.\n'
            'Busque o título ou cole a letra — o palco abre nela.\n\n'
            '{cifra_url}'
        ),
        'html': (
            '<h2>A música do ensaio, não o exemplo</h2>'
            '<p>Quem toca <strong>a própria cifra</strong> no Modo Tocar costuma voltar.</p>'
            '<p><a href="{cifra_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Escolher minha música</a></p>'
        ),
    },
    3: {
        'subject': 'Abra o Modo Tocar no ensaio',
        'body': (
            'Com uma cifra salva, o Modo Tocar libera tela cheia, auto-scroll e funciona offline.\n\n'
            '{colecao_url}'
        ),
        'html': (
            '<h2>Modo Tocar</h2>'
            '<ul>'
            '<li>Tela cheia para o palco</li>'
            '<li>Auto-scroll ajustável</li>'
            '<li>PWA offline no celular</li>'
            '</ul>'
            '<p><a href="{colecao_url}">Abrir minha coleção e tocar</a></p>'
        ),
    },
    4: {
        'subject': 'Tem show? Marque no Uníssono (escala + freela)',
        'body': (
            'Com banda (ou sozinho ainda), o salto é marcar o próximo show:\n'
            'data → quem toca → freela por WhatsApp → setlist → fechamento de cachê.\n\n'
            'Criar banda e show: {bands_url}\n'
            'Painel: {dashboard_url}'
        ),
        'html': (
            '<h2>Do ensaio ao cachê</h2>'
            '<p>O Uníssono não é só cifra. No <strong>Comando do show</strong> você:</p>'
            '<ul>'
            '<li>Escala quem toca e confirma por link</li>'
            '<li>Convida freela avulso no WhatsApp</li>'
            '<li>Fecha o cachê da noite sem planilha</li>'
            '</ul>'
            '<p><a href="{bands_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Criar banda / marcar show</a></p>'
            '<p><a href="{dashboard_url}">Abrir meu painel</a></p>'
        ),
    },
    5: {
        'subject': 'Fechou o show? Assine e continue sem limites',
        'body': (
            'Se já escalou ou fechou cachê, o Pro (R$ 29) ou Individual (R$ 15) '
            'libera PDF e limites.\n\n'
            '{planos_url}'
        ),
        'html': (
            '<h2>Continue depois do trial</h2>'
            '<p>Quem usa escala e freela sente o valor no dia do show. '
            '<strong>Pro</strong> R$ 29/mês (banda) · <strong>Individual</strong> R$ 15/mês (solo).</p>'
            '<p><a href="{planos_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Ver planos</a></p>'
        ),
    },
}


def _urls() -> dict[str, str]:
    return {
        'bands_url': external_url_for('bands.create', bem_vindo=1),
        'dashboard_url': external_url_for('dashboard'),
        'ajuda_url': external_url_for('ajuda.index'),
        'planos_url': external_url_for('assinatura_bp.planos'),
        'cifra_url': external_url_for('cifras.comecar'),
        'colecao_url': external_url_for('cifras.library'),
    }


def registrar_onboarding_usuario(usuario_id: str) -> None:
    """Chamar após cadastro — cria filas de e-mails 1–5."""
    ensure_onboarding_rows(usuario_id)


def verificar_e_disparar_onboarding() -> int:
    """Job diário: envia e-mails de onboarding no prazo. Retorna quantidade enviada."""
    if not is_configured():
        return 0

    urls = _urls()
    agora = app_now_naive()
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
        ok = send_email(
            [email],
            tpl['subject'],
            tpl['html'].format(**urls),
            tpl['body'].format(**urls),
        )
        if ok:
            mark_onboarding_sent(row['id'], 'enviado')
            enviados += 1
        else:
            mark_onboarding_sent(row['id'], 'erro')
    return enviados