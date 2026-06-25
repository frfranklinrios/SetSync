"""Checklist de configuração e divulgação para donos de estúdio."""

from __future__ import annotations

from flask import url_for

from models_studio import (
    dismiss_studio_onboarding as _dismiss,
    list_room_availability,
    list_rooms,
    list_studio_photos,
    studio_onboarding_dismissed,
    studio_profile_complete,
)


def _first_room_needing_availability(studio_id: str) -> dict | None:
    for room in list_rooms(studio_id, active_only=True):
        if not list_room_availability(room['id']):
            return room
    return None


def get_studio_onboarding_progress(studio: dict) -> dict | None:
    """Checklist no painel do estúdio. None se oculto ou concluído."""
    studio_id = studio['id']
    if studio_onboarding_dismissed(studio_id):
        return None

    rooms = list_rooms(studio_id, active_only=True)
    photos = list_studio_photos(studio_id)
    profile_ok = studio_profile_complete(studio)
    has_photos = len(photos) > 0
    has_rooms = len(rooms) > 0
    room_avail = _first_room_needing_availability(studio_id)
    has_availability = has_rooms and room_avail is None
    visible_search = bool(studio.get('ativo'))
    ready_to_share = profile_ok and has_photos and has_rooms and has_availability

    first_room = rooms[0] if rooms else None
    avail_url = (
        url_for('studios.room_availability', studio_id=studio_id, room_id=room_avail['id'])
        if room_avail
        else (
            url_for('studios.room_availability', studio_id=studio_id, room_id=first_room['id'])
            if first_room
            else url_for('studios.new_room', studio_id=studio_id)
        )
    )

    steps = [
        {
            'id': 'profile',
            'label': 'Completar perfil (descrição, endereço e contato)',
            'done': profile_ok,
            'url': url_for('studios.edit_studio', studio_id=studio_id),
        },
        {
            'id': 'photos',
            'label': 'Enviar fotos do espaço',
            'done': has_photos,
            'url': url_for('studios.owner_dashboard', studio_id=studio_id, _anchor='studio-fotos'),
        },
        {
            'id': 'rooms',
            'label': 'Cadastrar salas de ensaio',
            'done': has_rooms,
            'url': url_for('studios.new_room', studio_id=studio_id),
        },
        {
            'id': 'availability',
            'label': 'Definir horários de disponibilidade',
            'done': has_availability,
            'url': avail_url,
        },
        {
            'id': 'qr',
            'label': 'Cole o QR na recepção para agendamento',
            'done': ready_to_share,
            'url': url_for('studios.owner_dashboard', studio_id=studio_id, _anchor='studio-qr-agendamento'),
        },
        {
            'id': 'search',
            'label': 'Manter estúdio visível na busca',
            'done': visible_search,
            'url': url_for('studios.edit_studio', studio_id=studio_id),
        },
    ]

    done_count = sum(1 for s in steps if s['done'])
    if done_count == len(steps):
        return None

    return {
        'steps': steps,
        'done_count': done_count,
        'total': len(steps),
        'percent': round(100 * done_count / len(steps)) if steps else 0,
        'ready_to_share': ready_to_share,
        'public_page_url': url_for('studios.detail', studio_id=studio_id),
        'search_url': url_for('studios.search'),
    }
