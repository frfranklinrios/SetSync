"""Selo verificado, métricas e preview social do estúdio."""

from __future__ import annotations

from models_studio import (
    list_room_availability,
    list_rooms,
    list_studio_photos,
    studio_profile_complete,
)


def studio_is_verified(studio: dict) -> bool:
    if not studio or not studio.get('ativo'):
        return False
    if not studio_profile_complete(studio):
        return False
    if not list_studio_photos(studio['id']):
        return False
    rooms = list_rooms(studio['id'], active_only=True)
    if not rooms:
        return False
    for room in rooms:
        if list_room_availability(room['id']):
            return True
    return False


def increment_studio_page_view(studio_id: str) -> None:
    from db import get_db
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE studios SET page_views = COALESCE(page_views, 0) + 1 WHERE id = ?',
        (studio_id,),
    )
    db.commit()
    db.close()


def increment_studio_booking_click(studio_id: str) -> None:
    from db import get_db
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE studios SET booking_clicks = COALESCE(booking_clicks, 0) + 1 WHERE id = ?',
        (studio_id,),
    )
    db.commit()
    db.close()


def studio_metrics(studio: dict) -> dict:
    return {
        'page_views': int(studio.get('page_views') or 0),
        'booking_clicks': int(studio.get('booking_clicks') or 0),
        'verified': studio_is_verified(studio),
    }


def studio_og_context(studio: dict, *, photos: list | None = None) -> dict:
    from security import external_url_for
    photos = photos if photos is not None else list_studio_photos(studio['id'])
    image = None
    if photos:
        image = external_url_for(
            'studios.serve_studio_photo',
            studio_id=studio['id'],
            filename=photos[0]['filename'],
        )
    desc = (studio.get('descricao') or '').strip()
    if not desc:
        desc = f'Reserve sala de ensaio em {studio.get("cidade") or "SetSync"}.'
    return {
        'og_title': f'{studio.get("nome")} — Estúdio de ensaio',
        'og_description': desc[:200],
        'og_image': image,
        'og_url': external_url_for('studios.detail', studio_id=studio['id']),
    }
