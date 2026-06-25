"""Integração Google Maps — local dos eventos da agenda."""

from __future__ import annotations

import os
from urllib.parse import quote


def google_maps_api_key() -> str:
    return (os.getenv('GOOGLE_MAPS_API_KEY') or '').strip()


def parse_location_coords(lat_raw: str | None, lng_raw: str | None) -> tuple[float | None, float | None]:
    lat = lng = None
    try:
        if (lat_raw or '').strip():
            lat = float(str(lat_raw).strip().replace(',', '.'))
        if (lng_raw or '').strip():
            lng = float(str(lng_raw).strip().replace(',', '.'))
    except ValueError:
        return None, None
    if lat is not None and not (-90 <= lat <= 90):
        lat = None
    if lng is not None and not (-180 <= lng <= 180):
        lng = None
    return lat, lng


def maps_open_url(
    *,
    location: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    place_id: str | None = None,
) -> str | None:
    if place_id:
        return f'https://www.google.com/maps/search/?api=1&query=place_id:{quote(place_id)}'
    if lat is not None and lng is not None:
        return f'https://www.google.com/maps/search/?api=1&query={lat},{lng}'
    text = (location or '').strip()
    if text:
        return f'https://www.google.com/maps/search/?api=1&query={quote(text)}'
    return None


def maps_embed_url(
    *,
    api_key: str,
    location: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    place_id: str | None = None,
) -> str | None:
    key = (api_key or '').strip()
    if not key:
        return None
    if place_id:
        q = f'place_id:{place_id}'
    elif lat is not None and lng is not None:
        q = f'{lat},{lng}'
    elif (location or '').strip():
        q = (location or '').strip()
    else:
        return None
    return (
        'https://www.google.com/maps/embed/v1/place'
        f'?key={quote(key)}&q={quote(q)}&language=pt-BR'
    )


def studio_maps_context(studio: dict | None) -> dict:
    """URLs de mapa para templates do estúdio."""
    if not studio:
        return {
            'google_maps_api_key': google_maps_api_key(),
            'maps_open_url': None,
            'maps_embed_url': None,
        }
    key = google_maps_api_key()
    lat = studio.get('endereco_lat')
    lng = studio.get('endereco_lng')
    try:
        lat = float(lat) if lat is not None and str(lat).strip() != '' else None
    except (TypeError, ValueError):
        lat = None
    try:
        lng = float(lng) if lng is not None and str(lng).strip() != '' else None
    except (TypeError, ValueError):
        lng = None
    place_id = (studio.get('endereco_place_id') or '').strip() or None
    from models_studio import studio_full_address
    location = studio_full_address(studio) or None
    return {
        'google_maps_api_key': key,
        'maps_open_url': maps_open_url(
            location=location, lat=lat, lng=lng, place_id=place_id,
        ),
        'maps_embed_url': maps_embed_url(
            api_key=key,
            location=location,
            lat=lat,
            lng=lng,
            place_id=place_id,
        ) if location or (lat is not None and lng is not None) or place_id else None,
    }


def event_maps_context(event: dict | None) -> dict:
    """URLs de mapa para templates do evento."""
    if not event:
        return {'maps_open_url': None, 'maps_embed_url': None, 'google_maps_api_key': ''}
    key = google_maps_api_key()
    lat = event.get('location_lat')
    lng = event.get('location_lng')
    try:
        lat = float(lat) if lat is not None and str(lat).strip() != '' else None
    except (TypeError, ValueError):
        lat = None
    try:
        lng = float(lng) if lng is not None and str(lng).strip() != '' else None
    except (TypeError, ValueError):
        lng = None
    place_id = (event.get('location_place_id') or '').strip() or None
    location = (event.get('location') or '').strip() or None
    return {
        'google_maps_api_key': key,
        'maps_open_url': maps_open_url(
            location=location, lat=lat, lng=lng, place_id=place_id,
        ),
        'maps_embed_url': maps_embed_url(
            api_key=key,
            location=location,
            lat=lat,
            lng=lng,
            place_id=place_id,
        ) if location or (lat is not None and lng is not None) or place_id else None,
    }
