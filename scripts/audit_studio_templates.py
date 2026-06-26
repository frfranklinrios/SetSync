#!/usr/bin/env python3
"""Tenta renderizar templates de estúdio com contexto mínimo (detecta url_for quebrado)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app import app
    from db import get_user_by_username
    from models_studio import get_studio, list_rooms, list_studios_by_owner

    u = get_user_by_username('estudio_teste')
    if not u:
        print('SKIP: usuário estudio_teste não encontrado')
        return 0

    studios = list_studios_by_owner(u['id'])
    if not studios:
        print('SKIP: sem estúdios')
        return 0

    studio = get_studio(studios[0]['id'])
    rooms = list_rooms(studio['id'], active_only=False)
    room = rooms[0] if rooms else {'id': 'x', 'nome': 'Sala', 'ativa': 1, 'equipamentos': []}

    weekday_labels = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo')
    base_ctx = dict(
        current_user={
            'id': u['id'], 'name': 'Teste', 'username': 'estudio_teste',
            'is_authenticated': True, 'is_superadmin': False,
        },
        nav_home_url='/estudios/buscar',
        is_studio_primary=True,
    )

    cases = [
        ('studios/owner/dashboard.html', dict(
            studio=studio, rooms=rooms, pending=[],
            can_add_room=True, room_limit=2,
            booking_public_url='https://example.com/estudios/x/agendar',
            studio_onboarding={
                'done_count': 1, 'total': 6, 'percent': 17, 'ready_to_share': False,
                'public_page_url': '/estudios/x', 'search_url': '/estudios/buscar',
                'steps': [
                    {'id': 'profile', 'label': 'Perfil', 'done': True, 'url': '#'},
                    {'id': 'photos', 'label': 'Fotos', 'done': False, 'url': '#'},
                ],
            },
            studio_plano_ui={
                'logo': 'img/planos/estudio-basico.svg',
                'label': 'Estúdio Básico · beta',
                'label_curto': 'Básico',
                'badge': 'secondary',
                'premium': False,
            },
        )),
        ('studios/search.html', dict(studios=[studio], my_studios=studios, cidade='X', bairro='')),
        ('studios/detail.html', dict(
            studio=studio, rooms=rooms, photos=[], is_owner=True,
            user_bands=[], full_address='Rua Teste',
        )),
        ('studios/book.html', dict(
            studio=studio, room=room, user_bands=[], selected_date='',
            slots=[], full_address='Rua Teste',
        )),
        ('studios/my_bookings.html', dict(bookings=[])),
        ('studios/owner/form.html', dict(studio=studio, photos=[])),
        ('studios/owner/rooms.html', dict(
            studio=studio, rooms=rooms, booking_counts={r['id']: 0 for r in rooms},
            can_add_room=True, room_limit=2, studio_plano_ui={
                'logo': 'img/planos/estudio-basico.svg', 'label': 'Básico', 'premium': False,
            },
        )),
        ('studios/owner/finance.html', dict(
            studio=studio, report={
                'year': 2026, 'month': 6, 'preco_hora': 80.0, 'tem_preco_sala': True,
                'bookings': [], 'expenses': [],
                'stats': {
                    'reservas': 0, 'horas': 0.0,
                    'receita_confirmada': 0.0, 'recebido': 0.0, 'a_receber': 0.0,
                    'despesas': 0.0, 'liquido': 0.0,
                },
            },
            from_date='2026-06-01', to_date='2026-06-30',
            expense_categories=[('aluguel', 'Aluguel')],
        )),
        ('studios/owner/finance_print.html', dict(
            studio=studio,
            report={
                'year': 2026, 'month': 6, 'preco_hora': 80.0, 'tem_preco_sala': False,
                'bookings': [], 'expenses': [],
                'stats': {
                    'reservas': 1, 'horas': 5.0,
                    'receita_confirmada': 400.0, 'recebido': 0.0, 'a_receber': 400.0,
                    'despesas': 350.0, 'liquido': -350.0,
                },
            },
            from_date='2026-06-01', to_date='2026-06-30',
            period_label='Junho 2026', generated_at='2026-06-25 12:00',
            expense_labels={'aluguel': 'Aluguel'}, pdfgen=False,
        )),
        ('studios/owner/room_form.html', dict(studio=studio, room=room, photos=[])),
        ('studios/owner/availability.html', dict(
            studio=studio, room=room, weekday_labels=weekday_labels, weekly_by_dow={},
        )),
        ('studios/owner/blocks.html', dict(studio=studio, room=room, blocks=[])),
        ('studios/owner/calendar.html', dict(studio=studio, rooms=rooms, events_calendar=[])),
        ('assinatura/planos.html', dict(
            bandas=[], banda_id=None, planos={}, mp_status={'pronto_checkout': True, 'pronto_checkout_estudio': True},
            plano_ui=None, planos_estudio=[], studio_plano_ui=None,
        )),
    ]

    failures = []
    with app.app_context():
        with app.test_request_context(base_url='https://setsync.com.br'):
            for tpl, ctx in cases:
                try:
                    app.jinja_env.get_template(tpl).render(**base_ctx, **ctx)
                    print('OK', tpl)
                except Exception as e:
                    failures.append((tpl, e))
                    print('FAIL', tpl, e)

    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
