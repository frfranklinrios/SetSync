#!/usr/bin/env python3
"""Cria conta demo de dono de estúdio para testes do módulo /estudios."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

DEMO_USERNAME = 'estudio_teste'
DEMO_PASSWORD = 'EstudioTeste2026'
DEMO_EMAIL = 'estudio.teste@setsync.com.br'
DEMO_DISPLAY = 'Carlos Estúdio'

STUDIO_NOME = 'Groove Box Ensaios'
STUDIO_CIDADE = 'Fortaleza'
STUDIO_BAIRRO = 'Aldeota'
STUDIO_ENDERECO = 'Av. Santos Dumont, 1200 — Sala 3'
STUDIO_TELEFONE = '(85) 3222-1000'
STUDIO_WHATSAPP = '85999887766'
STUDIO_DESCRICAO = (
    'Salas climatizadas com bateria acústica, PA e isolamento acústico. '
    'Ideal para bandas de rock, MPB e gospel. Conta demo do SetSync.'
)

WEEKLY_SLOTS = [
    {'dia_semana': dow, 'hora_inicio': '09:00', 'hora_fim': '22:00'}
    for dow in range(5)  # seg–sex
] + [
    {'dia_semana': 5, 'hora_inicio': '10:00', 'hora_fim': '18:00'},  # sábado
]

ROOMS = [
    {
        'nome': 'Sala A — Banda completa',
        'capacidade_pessoas': 8,
        'equipamentos': ['Bateria Pearl', 'PA 500W', 'Microfones', 'Amplificador baixo'],
    },
    {
        'nome': 'Sala B — Acústico / voz',
        'capacidade_pessoas': 4,
        'equipamentos': ['Violão disponível', 'Cadeiras', 'Gravação básica'],
    },
]


def ensure_user(username: str, email: str, password: str, display_name: str) -> str:
    from db import create_user, get_user_by_username, update_user_display_name, update_user_password_by_email

    u = get_user_by_username(username)
    if u:
        if display_name and (u.get('display_name') or '') != display_name:
            update_user_display_name(u['id'], display_name)
        update_user_password_by_email(email, password)
        return u['id']
    uid = create_user(username, email, password, display_name=display_name)
    if not uid:
        raise RuntimeError(f'Não foi possível criar usuário {username}')
    return uid


def polish_user(user_id: str) -> None:
    from db import dismiss_onboarding_checklist, touch_user_last_login, update_user_profile

    update_user_profile(
        user_id,
        display_name=DEMO_DISPLAY,
        phone=STUDIO_TELEFONE,
        whatsapp_notify=True,
        email_notify=True,
    )
    dismiss_onboarding_checklist(user_id)
    touch_user_last_login(user_id)


def ensure_studio(owner_id: str) -> str:
    from models_studio import create_room, create_studio, get_studio, list_rooms, list_studios_by_owner, replace_weekly_availability

    existing = list_studios_by_owner(owner_id)
    if existing:
        studio_id = existing[0]['id']
        studio = get_studio(studio_id)
        print(f'Estúdio já existe: {studio["nome"]} ({studio_id})')
    else:
        studio_id = create_studio(
            owner_id,
            nome=STUDIO_NOME,
            cidade=STUDIO_CIDADE,
            bairro=STUDIO_BAIRRO,
            endereco=STUDIO_ENDERECO,
            telefone=STUDIO_TELEFONE,
            whatsapp=STUDIO_WHATSAPP,
            descricao=STUDIO_DESCRICAO,
        )
        print(f'Estúdio criado: {STUDIO_NOME} ({studio_id})')

    rooms = list_rooms(studio_id, active_only=False)
    if len(rooms) >= len(ROOMS):
        for r in rooms:
            replace_weekly_availability(r['id'], WEEKLY_SLOTS)
        print(f'Salas existentes: {len(rooms)} (disponibilidade atualizada)')
        return studio_id

    for spec in ROOMS[len(rooms):]:
        room_id = create_room(
            studio_id,
            nome=spec['nome'],
            capacidade_pessoas=spec['capacidade_pessoas'],
            equipamentos=spec['equipamentos'],
        )
        replace_weekly_availability(room_id, WEEKLY_SLOTS)
        print(f'  Sala criada: {spec["nome"]} ({room_id})')

    return studio_id


def main() -> int:
    from db import init_db

    init_db()
    owner_id = ensure_user(DEMO_USERNAME, DEMO_EMAIL, DEMO_PASSWORD, DEMO_DISPLAY)
    polish_user(owner_id)
    studio_id = ensure_studio(owner_id)

    print()
    print('=== Conta estúdio de teste ===')
    print(f'Login:    {DEMO_USERNAME}')
    print(f'Senha:    {DEMO_PASSWORD}')
    print(f'E-mail:   {DEMO_EMAIL}')
    print(f'Estúdio:  /estudios/{studio_id}/painel')
    print(f'Busca:    /estudios/buscar?cidade={STUDIO_CIDADE}&bairro={STUDIO_BAIRRO}')
    print()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
