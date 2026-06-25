"""Validação de formulários e serialização — estúdios."""

from __future__ import annotations

import json
from typing import Any

from agenda_maps import parse_location_coords

WEEKDAY_LABELS = (
    'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo',
)


def _clean(value: Any, max_len: int = 500) -> str:
    return str(value or '').strip()[:max_len]


def parse_studio_form(form) -> dict | None:
    nome = _clean(form.get('nome'), 120)
    cidade = _clean(form.get('cidade'), 80)
    if not nome or not cidade:
        return None
    preco_raw = _clean(form.get('preco_hora'), 20)
    preco = None
    if preco_raw:
        try:
            preco = float(preco_raw.replace(',', '.'))
        except ValueError:
            preco = None
    lat, lng = parse_location_coords(
        form.get('endereco_lat'),
        form.get('endereco_lng'),
    )
    place_id = _clean(form.get('endereco_place_id'), 120) or None
    out = {
        'nome': nome,
        'descricao': _clean(form.get('descricao'), 2000) or None,
        'cidade': cidade,
        'bairro': _clean(form.get('bairro'), 80) or None,
        'endereco': _clean(form.get('endereco'), 200) or None,
        'telefone': _clean(form.get('telefone'), 30) or None,
        'whatsapp': _clean(form.get('whatsapp'), 30) or None,
        'preco_hora': preco,
        'endereco_lat': lat,
        'endereco_lng': lng,
        'endereco_place_id': place_id,
    }
    if 'ativo' in form:
        out['ativo'] = 1 if form.get('ativo') else 0
    return out


def parse_room_form(form) -> dict | None:
    nome = _clean(form.get('nome'), 120)
    if not nome:
        return None
    cap_raw = _clean(form.get('capacidade_pessoas'), 10)
    capacidade = None
    if cap_raw:
        try:
            capacidade = int(cap_raw)
        except ValueError:
            capacidade = None
    equip_raw = _clean(form.get('equipamentos'), 500)
    equipamentos = [e.strip() for e in equip_raw.split(',') if e.strip()] if equip_raw else []
    out = {
        'nome': nome,
        'capacidade_pessoas': capacidade,
        'equipamentos': equipamentos,
    }
    if 'ativa' in form:
        out['ativa'] = 1 if form.get('ativa') else 0
    return out


def parse_weekly_availability_form(form) -> list[dict]:
    """Lê campos dow_{0-6}_inicio / dow_{0-6}_fim."""
    slots = []
    for dow in range(7):
        hi = _clean(form.get(f'dow_{dow}_inicio'), 5)
        hf = _clean(form.get(f'dow_{dow}_fim'), 5)
        if hi and hf:
            slots.append({
                'dia_semana': dow,
                'hora_inicio': hi,
                'hora_fim': hf,
            })
    return slots


def parse_block_form(form) -> dict | None:
    data = _clean(form.get('data'), 10)
    hi = _clean(form.get('hora_inicio'), 5)
    hf = _clean(form.get('hora_fim'), 5)
    if not data or not hi or not hf:
        return None
    return {
        'data': data,
        'hora_inicio': hi,
        'hora_fim': hf,
        'motivo': _clean(form.get('motivo'), 200) or None,
    }


def parse_booking_form(form) -> dict | None:
    data = _clean(form.get('data'), 10)
    hi = _clean(form.get('hora_inicio'), 5)
    hf = _clean(form.get('hora_fim'), 5)
    band_id = _clean(form.get('band_id'), 64)
    if not data or not hi or not hf or not band_id:
        return None
    setlist_raw = _clean(form.get('setlist_id'), 12)
    setlist_id = None
    if setlist_raw:
        try:
            setlist_id = int(setlist_raw)
        except ValueError:
            setlist_id = None
    return {
        'band_id': band_id,
        'data': data,
        'hora_inicio': hi,
        'hora_fim': hf,
        'observacao': _clean(form.get('observacao'), 500) or None,
        'setlist_id': setlist_id,
    }


def available_slots_to_api(slots: list[dict]) -> list[dict]:
    return [{'inicio': s['inicio'], 'fim': s['fim']} for s in slots]


def booking_to_api(booking: dict, studio: dict | None = None, room: dict | None = None) -> dict:
    out = {
        'id': booking.get('id'),
        'status': booking.get('status'),
        'data': booking.get('data'),
        'hora_inicio': booking.get('hora_inicio'),
        'hora_fim': booking.get('hora_fim'),
        'observacao': booking.get('observacao'),
        'band_id': booking.get('band_id'),
    }
    if studio:
        out['studio_nome'] = studio.get('nome')
    if room:
        out['room_nome'] = room.get('nome')
    return out


def calendar_events_from_bookings(bookings: list[dict], *, url_builder) -> list[dict]:
    events = []
    for b in bookings:
        starts = f"{b['data']} {b['hora_inicio']}:00"
        events.append({
            'id': b['id'],
            'title': f"{b.get('room_nome', 'Sala')} — {b.get('status', '')}",
            'event_type': 'ensaio',
            'starts_at': starts[:19],
            'location': b.get('status', ''),
            'url': url_builder(b['id']) if url_builder else '',
        })
    return events
