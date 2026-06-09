"""Agenda da banda — ensaios e shows."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

import band_notifications as bn
from agenda_util import (
    event_type_label,
    format_event_datetime,
    parse_event_datetime,
    split_event_datetime,
)
from blueprints.auth import login_required
from db import get_band, get_band_members, is_band_admin, is_band_member, user_display_name
from models_agenda import (
    EVENT_ENSAIO,
    EVENT_SHOW,
    EVENT_TYPES,
    create_band_event,
    delete_band_event,
    get_band_event,
    get_event_assignment_user_ids,
    get_event_assignments,
    set_event_assignments,
    update_band_event,
)
from models_setlist import get_band_setlists, get_setlist

agenda_bp = Blueprint('agenda', __name__, url_prefix='/agenda')


def _require_band_member(band_id: str):
    band = get_band(band_id)
    user_id = session.get('user_id')
    if not band or not user_id or not is_band_member(band_id, user_id):
        return None, None
    return band, user_id


def _require_event_access(event_id: str):
    event = get_band_event(event_id)
    if not event:
        return None, None, None
    band, user_id = _require_band_member(event['band_id'])
    if not band:
        return None, None, None
    return event, band, user_id


def _valid_setlist_for_band(setlist_id: int | None, band_id: str) -> int | None:
    if not setlist_id:
        return None
    sl = get_setlist(setlist_id)
    if not sl or sl['band_id'] != band_id:
        return None
    return int(setlist_id)


def _read_event_form(band_id: str) -> dict | None:
    title = (request.form.get('title') or '').strip()
    event_type = (request.form.get('event_type') or EVENT_ENSAIO).strip()
    if event_type not in EVENT_TYPES:
        event_type = EVENT_ENSAIO
    starts_at = parse_event_datetime(
        request.form.get('date', ''),
        request.form.get('time', ''),
    )
    ends_at = None
    end_date = (request.form.get('end_date') or '').strip()
    end_time = (request.form.get('end_time') or '').strip()
    if end_date:
        ends_at = parse_event_datetime(end_date, end_time or '23:59')
    location = (request.form.get('location') or '').strip() or None
    notes = (request.form.get('notes') or '').strip() or None
    setlist_raw = (request.form.get('setlist_id') or '').strip()
    setlist_id = _valid_setlist_for_band(int(setlist_raw), band_id) if setlist_raw.isdigit() else None

    if not title:
        flash('Informe um título para o evento.', 'warning')
        return None
    if not starts_at:
        flash('Data e hora inválidas.', 'warning')
        return None
    if setlist_raw and setlist_id is None:
        flash('Setlist inválida para esta banda.', 'warning')
        return None

    return {
        'title': title,
        'event_type': event_type,
        'starts_at': starts_at,
        'ends_at': ends_at,
        'location': location,
        'notes': notes,
        'setlist_id': setlist_id,
    }


@agenda_bp.route('/band/<band_id>/create', methods=['GET', 'POST'])
@login_required
def create(band_id):
    band, user_id = _require_band_member(band_id)
    if not band:
        flash('Banda não encontrada ou sem acesso.', 'danger')
        return redirect(url_for('dashboard'))
    if not is_band_admin(band_id, user_id):
        flash('Apenas administradores podem criar eventos na agenda.', 'danger')
        return redirect(url_for('bands.view', band_id=band_id))

    setlists = get_band_setlists(band_id)
    prefill_setlist = request.args.get('setlist_id', '')

    if request.method == 'POST':
        data = _read_event_form(band_id)
        if not data:
            return render_template(
                'agenda/form.html',
                band=band,
                setlists=setlists,
                event=None,
                prefill_setlist=prefill_setlist,
                event_types=EVENT_TYPES,
                split_event_datetime=split_event_datetime,
            )
        event_id = create_band_event(band_id, created_by=user_id, **data)
        bn.event_created(band_id, user_id, event_id, data['title'], data['event_type'])
        flash('Evento criado. Defina a escalação dos integrantes.', 'success')
        return redirect(url_for('agenda.escala', event_id=event_id))

    return render_template(
        'agenda/form.html',
        band=band,
        setlists=setlists,
        event=None,
        prefill_setlist=prefill_setlist,
        event_types=EVENT_TYPES,
        split_event_datetime=split_event_datetime,
    )


@agenda_bp.route('/<event_id>')
@login_required
def view(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    from models_setlist import get_setlist_cifras

    setlist_cifras = []
    if event.get('setlist_id'):
        setlist_cifras = get_setlist_cifras(int(event['setlist_id']))
    assignments = get_event_assignments(event_id)
    return render_template(
        'agenda/view.html',
        event=event,
        band=band,
        is_admin=is_band_admin(band['id'], user_id),
        assignments=assignments,
        user_is_scaled=any(a['user_id'] == user_id for a in assignments),
        setlist_cifras=setlist_cifras,
        event_type_label=event_type_label(event.get('event_type')),
        format_event_datetime=format_event_datetime,
        user_display_name=user_display_name,
    )


@agenda_bp.route('/<event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    if not is_band_admin(band['id'], user_id):
        flash('Apenas administradores podem editar eventos.', 'danger')
        return redirect(url_for('agenda.view', event_id=event_id))

    setlists = get_band_setlists(band['id'])

    if request.method == 'POST':
        data = _read_event_form(band['id'])
        if not data:
            return render_template(
                'agenda/form.html',
                band=band,
                setlists=setlists,
                event=event,
                prefill_setlist='',
                event_types=EVENT_TYPES,
                split_event_datetime=split_event_datetime,
            )
        update_band_event(event_id, **data)
        bn.event_updated(band['id'], user_id, event_id, data['title'], data['event_type'])
        flash('Evento atualizado.', 'success')
        return redirect(url_for('agenda.view', event_id=event_id))

    return render_template(
        'agenda/form.html',
        band=band,
        setlists=setlists,
        event=event,
        prefill_setlist='',
        event_types=EVENT_TYPES,
        split_event_datetime=split_event_datetime,
    )


def _read_scale_form(band_id: str) -> list[dict] | None:
    member_ids = request.form.getlist('member_ids')
    if not member_ids:
        return []
    valid_ids = {m['id'] for m in get_band_members(band_id)}
    assignments = []
    for uid in member_ids:
        if uid not in valid_ids:
            continue
        role = (request.form.get(f'role_{uid}') or '').strip() or None
        assignments.append({'user_id': uid, 'role_label': role})
    return assignments


@agenda_bp.route('/<event_id>/escala', methods=['GET', 'POST'])
@login_required
def escala(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    if not is_band_admin(band['id'], user_id):
        flash('Apenas administradores podem definir a escalação.', 'danger')
        return redirect(url_for('agenda.view', event_id=event_id))

    members = get_band_members(band['id'])
    current = {a['user_id']: a for a in get_event_assignments(event_id)}

    if request.method == 'POST':
        assignments = _read_scale_form(band['id'])
        if assignments is None:
            flash('Seleção de integrantes inválida.', 'warning')
            return redirect(url_for('agenda.escala', event_id=event_id))

        old_ids = set(get_event_assignment_user_ids(event_id))
        set_event_assignments(event_id, assignments, assigned_by=user_id)
        new_ids = {a['user_id'] for a in assignments}
        added = new_ids - old_ids
        if added:
            bn.event_scale_assigned(
                band['id'], user_id, event_id, event['title'], added,
            )
        flash('Escalação salva.', 'success')
        return redirect(url_for('agenda.view', event_id=event_id))

    return render_template(
        'agenda/escala.html',
        event=event,
        band=band,
        members=members,
        current=current,
        format_event_datetime=format_event_datetime,
        user_display_name=user_display_name,
    )


@agenda_bp.route('/<event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    if not is_band_admin(band['id'], user_id):
        flash('Apenas administradores podem excluir eventos.', 'danger')
        return redirect(url_for('agenda.view', event_id=event_id))

    bn.event_deleted(band['id'], user_id, event['title'], event.get('event_type'))
    delete_band_event(event_id)
    flash('Evento removido da agenda.', 'info')
    return redirect(url_for('bands.view', band_id=band['id']) + '#tab-agenda')
