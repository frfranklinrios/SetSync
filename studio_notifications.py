"""Notificações de agendamento de estúdio."""

from __future__ import annotations

from db import create_notification, get_band_members


def _notify(
    user_id: str,
    *,
    type_: str,
    title: str,
    body: str,
    url_path: str,
    band_id: str | None = None,
    actor_user_id: str | None = None,
    urgent: bool = True,
):
    create_notification(
        user_id,
        band_id=band_id,
        actor_user_id=actor_user_id,
        type=type_,
        title=title,
        body=body,
        url_path=url_path,
        urgent=urgent,
    )


def booking_requested(booking: dict, studio: dict, room: dict, band: dict) -> None:
    owner_id = studio.get('owner_user_id')
    if not owner_id:
        return
    band_name = (band or {}).get('name') or 'Banda'
    title = f'Nova solicitação — {studio.get("nome")}'
    body = (
        f'{band_name} pediu {room.get("nome")} em {booking.get("data")} '
        f'das {booking.get("hora_inicio")} às {booking.get("hora_fim")}.'
    )
    _notify(
        owner_id,
        type_='studio_booking_requested',
        title=title,
        body=body,
        url_path=f'/estudios/{studio["id"]}/painel',
        band_id=booking.get('band_id'),
        actor_user_id=booking.get('requested_by_user_id'),
        urgent=True,
    )


def booking_confirmed(booking: dict, studio: dict, room: dict, band: dict) -> None:
    title = 'Agendamento confirmado'
    body = (
        f'{studio.get("nome")} / {room.get("nome")} em {booking.get("data")} '
        f'das {booking.get("hora_inicio")} às {booking.get("hora_fim")}.'
    )
    url = f'/agenda/{booking.get("band_event_id")}' if booking.get('band_event_id') else '/agenda/minha'
    notified = set()
    requester = booking.get('requested_by_user_id')
    owner_id = studio.get('owner_user_id')
    if requester:
        _notify(
            requester,
            type_='studio_booking_confirmed',
            title=title,
            body=body,
            url_path=url,
            band_id=booking.get('band_id'),
            actor_user_id=owner_id,
        )
        notified.add(requester)
    if band:
        for m in get_band_members(band['id']):
            uid = m.get('user_id')
            if uid and uid not in notified:
                _notify(
                    uid,
                    type_='studio_booking_confirmed',
                    title=title,
                    body=body,
                    url_path=url,
                    band_id=band['id'],
                    actor_user_id=owner_id,
                )
                notified.add(uid)


def booking_rejected(booking: dict, studio: dict, room: dict) -> None:
    requester = booking.get('requested_by_user_id')
    if not requester:
        return
    title = 'Agendamento recusado'
    body = (
        f'{studio.get("nome")} recusou o pedido para {room.get("nome")} '
        f'em {booking.get("data")} ({booking.get("hora_inicio")}–{booking.get("hora_fim")}).'
    )
    _notify(
        requester,
        type_='studio_booking_rejected',
        title=title,
        body=body,
        url_path=f'/estudios/{studio["id"]}',
        band_id=booking.get('band_id'),
        actor_user_id=studio.get('owner_user_id'),
        urgent=True,
    )


def booking_cancelled(booking: dict, studio: dict, room: dict, band: dict, *, by_user_id: str) -> None:
    band_name = (band or {}).get('name') or 'Banda'
    title = 'Agendamento cancelado'
    body = (
        f'Reserva cancelada: {band_name} — {room.get("nome")} em {booking.get("data")} '
        f'({booking.get("hora_inicio")}–{booking.get("hora_fim")}).'
    )
    owner_id = studio.get('owner_user_id')
    if owner_id and owner_id != by_user_id:
        _notify(
            owner_id,
            type_='studio_booking_cancelled',
            title=title,
            body=body,
            url_path=f'/estudios/{studio["id"]}/painel',
            band_id=booking.get('band_id'),
            actor_user_id=by_user_id,
        )
    requester = booking.get('requested_by_user_id')
    if requester and requester != by_user_id:
        _notify(
            requester,
            type_='studio_booking_cancelled',
            title=title,
            body=body,
            url_path='/estudios/minhas-reservas',
            band_id=booking.get('band_id'),
            actor_user_id=by_user_id,
        )
