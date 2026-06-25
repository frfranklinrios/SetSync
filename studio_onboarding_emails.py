"""Sequência de e-mails para donos de estúdio."""

from __future__ import annotations

from datetime import datetime

from db import (
    ensure_studio_onboarding_rows,
    get_user,
    list_studio_onboarding_pending,
    mark_studio_onboarding_sent,
)
from email_service import is_configured, send_email
from security import external_url_for
from config import app_now_naive

_SCHEDULE = {1: 0, 2: 2, 3: 5, 4: 7, 5: 10}

_EMAILS = {
    1: {
        'subject': 'Seu estúdio no SetSync — primeiros passos',
        'html': (
            '<h2>Bem-vindo ao painel do estúdio</h2>'
            '<p>Complete o perfil, cadastre salas e defina horários de disponibilidade.</p>'
            '<p><a href="{painel_url}">Abrir painel</a></p>'
        ),
        'body': 'Complete perfil, salas e horários: {painel_url}',
    },
    2: {
        'subject': 'Fotos e QR na recepção',
        'html': (
            '<h2>Divulgue seu espaço</h2>'
            '<p>Envie fotos do estúdio e imprima o <strong>QR de agendamento</strong> na recepção.</p>'
            '<p><a href="{painel_url}#studio-qr-agendamento">Baixar QR</a></p>'
        ),
        'body': 'QR de agendamento: {painel_url}',
    },
    3: {
        'subject': 'Bandas encontram seu estúdio na busca',
        'html': (
            '<h2>Apareça na busca</h2>'
            '<p>Com perfil completo e estúdio ativo, bandas reservam pelo app.</p>'
            '<p><a href="{busca_url}">Ver busca de estúdios</a></p>'
        ),
        'body': 'Busca: {busca_url}',
    },
    4: {
        'subject': 'Confirme reservas e sincronize a agenda da banda',
        'html': (
            '<h2>Fluxo de reservas</h2>'
            '<p>Bandas solicitam horário; você confirma no painel. O ensaio entra na agenda delas.</p>'
            '<p><a href="{ajuda_url}#estudios">Guia de estúdios</a></p>'
        ),
        'body': 'Ajuda: {ajuda_url}',
    },
    5: {
        'subject': 'Trial Premium — salas ilimitadas',
        'html': (
            '<h2>Aproveite o trial</h2>'
            '<p>Cadastre quantas salas precisar durante o trial Premium de 30 dias.</p>'
            '<p><a href="{planos_url}">Ver planos Estúdio</a></p>'
        ),
        'body': 'Planos: {planos_url}',
    },
}


def _urls(studio_id: str) -> dict[str, str]:
    return {
        'painel_url': external_url_for('studios.owner_dashboard', studio_id=studio_id),
        'busca_url': external_url_for('studios.search'),
        'ajuda_url': external_url_for('ajuda.index'),
        'planos_url': external_url_for('assinatura_bp.planos') + '#estudio',
    }


def registrar_onboarding_estudio(owner_user_id: str, studio_id: str) -> None:
    ensure_studio_onboarding_rows(owner_user_id, studio_id)


def verificar_e_disparar_onboarding_estudio() -> int:
    if not is_configured():
        return 0
    agora = app_now_naive()
    enviados = 0
    for row in list_studio_onboarding_pending():
        num = int(row['email_numero'])
        dias = _SCHEDULE.get(num, 999)
        created = row.get('studio_created_at') or row.get('created_at')
        if not created:
            continue
        if isinstance(created, str):
            try:
                cadastro = datetime.strptime(str(created)[:19], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        else:
            cadastro = created
        if (agora - cadastro).days < dias:
            continue
        email = row.get('email')
        studio_id = row.get('studio_id')
        if not email or not studio_id:
            continue
        tpl = _EMAILS.get(num)
        if not tpl:
            continue
        urls = _urls(studio_id)
        ok = send_email(
            [email],
            tpl['subject'],
            tpl['html'].format(**urls),
            tpl['body'].format(**urls),
        )
        mark_studio_onboarding_sent(row['id'], 'enviado' if ok else 'erro')
        if ok:
            enviados += 1
    return enviados
