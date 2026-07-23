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
        'subject': 'Bem-vindo ao Uníssono — adicione sua 1ª música 🎸',
        'body': (
            'Olá! Sua conta no Uníssono está pronta.\n\n'
            'Próximo passo (2 min): adicione uma cifra na coleção pessoal — grátis.\n'
            'Depois abra o Modo Tocar e veja a magia no ensaio.\n\n'
            'Adicionar música: {cifra_url}'
        ),
        'html': (
            '<h2>Bem-vindo ao Uníssono!</h2>'
            '<p>Sua conta está pronta. O primeiro passo é <strong>adicionar uma música</strong> '
            'na coleção pessoal (grátis e ilimitada).</p>'
            '<p><a href="{cifra_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Adicionar 1ª música</a></p>'
            '<p>Depois, abra o <strong>Modo Tocar</strong> — tela cheia, tom e auto-scroll.</p>'
        ),
    },
    2: {
        'subject': 'Ainda sem cifra? Leva 2 minutos',
        'body': (
            'Você se cadastrou no Uníssono e ainda não adicionou uma música.\n'
            'Coleção pessoal é grátis. Depois é só abrir o Modo Tocar.\n\n'
            '{cifra_url}'
        ),
        'html': (
            '<h2>Sua 1ª música</h2>'
            '<p>Quem adiciona uma cifra e abre o <strong>Modo Tocar</strong> costuma ficar.</p>'
            '<p><a href="{cifra_url}" style="display:inline-block;padding:12px 24px;'
            'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
            'Adicionar música agora</a></p>'
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
        'subject': 'Ensaio em grupo? Crie uma banda (trial Pro)',
        'body': (
            'Se toca com outras pessoas, crie uma banda e ganhe 30 dias de Pro sem cartão.\n'
            'Se toca só, o plano Individual libera PDF e compartilhar.\n\n'
            '{bands_url}'
        ),
        'html': (
            '<h2>Banda ou solo?</h2>'
            '<p><strong>Banda:</strong> 30 dias de Pro grátis ao criar a primeira.</p>'
            '<p><strong>Solo:</strong> Individual libera PDF e compartilhar cifras.</p>'
            '<p><a href="{bands_url}">Criar banda</a> · '
            '<a href="{planos_url}">Ver planos</a></p>'
        ),
    },
    5: {
        'subject': 'Mantenha o Pro (ou Individual se toca só)',
        'body': (
            'Se o trial acabar, você volta ao Grátis com limites.\n'
            'Pro: R$ 29/mês para a banda · Individual: R$ 15/mês para solo.\n\n'
            '{planos_url}'
        ),
        'html': (
            '<h2>Continue sem limites</h2>'
            '<p><strong>Pro</strong> — R$ 29/mês (banda) · '
            '<strong>Individual</strong> — R$ 15/mês (solo, PDF e compartilhar).</p>'
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
        'cifra_url': external_url_for('cifras.add_personal', welcome=1),
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