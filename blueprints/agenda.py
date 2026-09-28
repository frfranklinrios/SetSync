"""Agenda da banda — ensaios e shows."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

import band_notifications as bn
from agenda_maps import (
    event_maps_context,
    google_maps_api_key,
    parse_location_coords,
)
from agenda_util import (
    event_type_label,
    format_event_datetime,
    parse_event_datetime,
    split_event_datetime,
)
from blueprints.auth import login_required
from db import get_band, get_band_members, is_band_admin, is_band_editor, is_band_finance_admin, is_band_member, is_superadmin, user_display_name
from models_agenda import (
    EVENT_ENSAIO,
    EVENT_SHOW,
    EVENT_TYPES,
    create_band_event,
    delete_band_event,
    get_band_event,
    get_event_assignments,
    get_events_scale_summaries,
    get_user_agenda_events,
    get_user_event_assignment,
    set_event_assignments,
    update_band_event,
)
from models_band_team import (
    add_event_guest,
    ensure_default_band_roles,
    get_assignment_response_stats,
    get_event_guest,
    get_lineup,
    lineup_assignments,
    list_band_lineups,
    list_band_roles,
    list_event_guests,
    remove_event_guest,
    suggest_scale_assignments,
    users_blocked_on_date,
)
from models_setlist import (
    clone_setlist,
    find_suggestable_setlist,
    get_band_setlists,
    get_setlist,
)
from event_calendar import google_calendar_url, ics_content
from event_scale_tokens import verify_guest_scale_token, verify_scale_response_token
from scale_service import (
    guest_scale_token_url,
    notify_event_guest,
    process_guest_scale_response,
    process_scale_response,
    scale_token_url,
)
from security import build_canonical_url, external_url_for
from config import app_now_naive, app_now_str

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
    location = (request.form.get('location') or '').strip()[:300] or None
    location_lat, location_lng = parse_location_coords(
        request.form.get('location_lat'),
        request.form.get('location_lng'),
    )
    location_place_id = (request.form.get('location_place_id') or '').strip()[:120] or None
    if location and not location_lat and not location_place_id:
        location_lat = location_lng = location_place_id = None
    if not location:
        location_lat = location_lng = location_place_id = None
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
        'location_lat': location_lat,
        'location_lng': location_lng,
        'location_place_id': location_place_id,
        'notes': notes,
        'setlist_id': setlist_id,
    }


def _form_template_ctx(**extra):
    return {
        'google_maps_api_key': google_maps_api_key(),
        **extra,
    }


@agenda_bp.route('/band/<band_id>/create', methods=['GET', 'POST'])
@login_required
def create(band_id):
    band, user_id = _require_band_member(band_id)
    if not band:
        flash('Banda não encontrada ou sem acesso.', 'danger')
        return redirect(url_for('dashboard'))

    setlists = get_band_setlists(band_id)
    prefill_setlist = request.args.get('setlist_id', '')

    if request.method == 'POST':
        from conversion_levers import pode_criar_evento, resposta_paywall_conversao

        if not pode_criar_evento(band_id):
            return resposta_paywall_conversao(
                'No Grátis você cria 1 evento. No Pro a agenda fica ilimitada '
                'com setlist, PDF e offline no palco.',
                banda_id=band_id,
            )
        data = _read_event_form(band_id)
        if not data:
            return render_template(
                'agenda/form.html',
                **_form_template_ctx(
                    band=band,
                    setlists=setlists,
                    event=None,
                    prefill_setlist=prefill_setlist,
                    event_types=EVENT_TYPES,
                    split_event_datetime=split_event_datetime,
                ),
            )
        event_id = create_band_event(band_id, created_by=user_id, **data)
        from db import mark_user_agenda_event_used
        from product_funnel import log_funnel_step
        mark_user_agenda_event_used(user_id)
        log_funnel_step(user_id, 'primeiro_evento_agenda')
        bn.event_created(band_id, user_id, event_id, data['title'], data['event_type'])
        flash(
            'Evento criado. Abra o Comando do show: escala, freela, setlist e cachê num só lugar.',
            'success',
        )
        return redirect(url_for('agenda.comando', event_id=event_id))

    kit = request.args.get('kit') == '1'
    tipo = (request.args.get('tipo') or request.args.get('event_type') or '').strip().lower()
    default_event = None
    if tipo in EVENT_TYPES:
        default_event = {'event_type': tipo, 'title': ''}
    return render_template(
        'agenda/form.html',
        **_form_template_ctx(
            band=band,
            setlists=setlists,
            event=default_event,
            prefill_setlist=prefill_setlist,
            event_types=EVENT_TYPES,
            split_event_datetime=split_event_datetime,
            kit_mode=kit,
        ),
    )


@agenda_bp.route('/minha')
@login_required
def minha_agenda():
    """Calendário com eventos de todas as bandas do usuário."""
    from datetime import datetime

    user_id = session['user_id']
    sa = is_superadmin(user_id)
    all_events = get_user_agenda_events(user_id, all_bands=sa)

    scale_summaries = get_events_scale_summaries([e['id'] for e in all_events])
    for e in all_events:
        summary = scale_summaries.get(e['id'], {})
        e['scale_count'] = summary.get('count', 0)
        e['scale_preview'] = summary.get('preview', '')
        e['can_edit'] = is_band_editor(e['band_id'], user_id)
        e['is_admin'] = is_band_admin(e['band_id'], user_id)

    now = app_now_str()  # was strftime('%Y-%m-%d %H:%M:%S')
    events_upcoming = [e for e in all_events if str(e.get('starts_at') or '') >= now]
    events_past = [e for e in all_events if str(e.get('starts_at') or '') < now]
    events_past.reverse()

    events_calendar = [
        {
            'id': e['id'],
            'title': e.get('title') or '',
            'event_type': e.get('event_type') or 'ensaio',
            'starts_at': str(e.get('starts_at') or '')[:19],
            'location': e.get('location') or '',
            'band_name': e.get('band_name') or '',
            'scale_preview': e.get('scale_preview') or '',
            'url': url_for('agenda.view', event_id=e['id']),
        }
        for e in all_events
    ]

    return render_template(
        'agenda/minha.html',
        events_upcoming=events_upcoming,
        events_past=events_past,
        events_calendar=events_calendar,
        is_superadmin=sa,
        format_event_datetime=format_event_datetime,
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
    user_assignment = get_user_event_assignment(event_id, user_id)
    guests = list_event_guests(event_id)
    guest_invite_urls = {
        str(g['id']): guest_scale_token_url(event_id, g['id']) for g in guests
    }
    scale_stats = get_assignment_response_stats(event_id)
    gcal_url = google_calendar_url(event, band_name=band.get('name') or '')
    from event_fees import compute_event_fee_split
    from db import get_band_members, can_view_band_finance
    from models_band_finance import list_event_expenses, list_event_fee_lines

    fee_split = None
    event_expenses = list_event_expenses(event_id) if event.get('event_type') == 'show' else []
    fee_lines = list_event_fee_lines(event_id) if event.get('event_type') == 'show' else []
    can_see_full_fee = can_view_band_finance(band['id'], user_id)
    can_edit_finance = is_band_finance_admin(band['id'], user_id)
    members = get_band_members(band['id'])
    fee_amount_by_user = {
        str(line['user_id']): float(line.get('amount') or 0)
        for line in (fee_lines or [])
        if line.get('user_id') is not None
        and (line.get('kind') or '').strip().lower() == 'fixed'
    }
    settlement_member_ids = set()
    if assignments:
        for a in assignments:
            if (a.get('response_status') or 'pending') == 'accepted' and a.get('user_id'):
                settlement_member_ids.add(str(a['user_id']))
    else:
        settlement_member_ids = {
            str(m['user_id']) for m in members if m.get('user_id')
        }
    if event.get('fee_total') or event_expenses or fee_lines:
        fee_split = compute_event_fee_split(
            event,
            assignments,
            members,
            name_for_user=user_display_name,
            guests=guests,
            event_expenses=event_expenses,
            fee_lines=fee_lines or None,
        )
        if fee_split and not can_see_full_fee:
            my_payee = next(
                (p for p in (fee_split.get('payees') or []) if str(p.get('user_id')) == str(user_id)),
                None,
            )
            my_amount = (my_payee or {}).get('amount')
            my_line = next(
                (ln for ln in (fee_lines or []) if str(ln.get('user_id') or '') == str(user_id)),
                None,
            )
            personally_paid = bool(my_line and my_line.get('paid_at'))
            is_paid = personally_paid or bool(event.get('fee_settled_at'))
            wa_text = ''
            if my_amount and float(my_amount) > 0:
                from band_finance import fee_share_whatsapp_text
                wa_text = fee_share_whatsapp_text(
                    band_name=band.get('name') or 'Banda',
                    show_title=event.get('title') or 'Show',
                    date_label=(str(event.get('starts_at') or ''))[:10],
                    amount=float(my_amount),
                    status='Recebido' if is_paid else 'A receber',
                )
            fee_split = {
                **fee_split,
                'payees': [my_payee] if my_payee else [],
                'fixed_payees': [p for p in (fee_split.get('fixed_payees') or []) if str(p.get('user_id')) == str(user_id)],
                'founder_payees': [p for p in (fee_split.get('founder_payees') or []) if str(p.get('user_id')) == str(user_id)],
                'personal_only': True,
                'my_amount': my_amount,
                'my_paid': is_paid,
                'fee_line_id': (my_line or {}).get('id'),
                'wa_text': wa_text,
                'payees_count': len(fee_split.get('payees') or []),
            }
    from conversion_levers import trial_opt_in_disponivel

    return render_template(
        'agenda/view.html',
        event=event,
        band=band,
        is_admin=is_band_admin(band['id'], user_id),
        can_edit=is_band_editor(band['id'], user_id),
        can_view_finance=can_see_full_fee,
        can_edit_finance=can_edit_finance,
        assignments=assignments,
        guests=guests,
        guest_invite_urls=guest_invite_urls,
        members=members,
        settlement_member_ids=settlement_member_ids,
        event_expenses=event_expenses,
        fee_amount_by_user=fee_amount_by_user,
        scale_stats=scale_stats,
        user_assignment=user_assignment,
        user_is_scaled=user_assignment is not None,
        setlist_cifras=setlist_cifras,
        fee_split=fee_split,
        trial_opt_in_available=bool(can_edit_finance and trial_opt_in_disponivel(band['id'])),
        pro_checkout_url=url_for(
            'assinatura_bp.planos', banda_id=band['id'], plano='pro', go=1,
        ),
        event_type_label=event_type_label(event.get('event_type')),
        format_event_datetime=format_event_datetime,
        user_display_name=user_display_name,
        google_calendar_url=gcal_url,
        ics_url=url_for('agenda.event_ics', event_id=event_id),
        **event_maps_context(event),
    )


@agenda_bp.route('/<event_id>/pacote')
@login_required
def event_package(event_id):
    """Visão focada no músico escalado — confirmação, setlist e mapa."""
    return redirect(url_for('agenda.view', event_id=event_id))


@agenda_bp.route('/<event_id>/calendar.ics')
@login_required
def event_ics(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    content = ics_content(
        event,
        band_name=band.get('name') or '',
        app_url=build_canonical_url(f'/agenda/{event_id}'),
    )
    if not content:
        abort(404)
    from flask import Response
    return Response(
        content,
        mimetype='text/calendar; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="evento-{event_id[:8]}.ics"'},
    )


@agenda_bp.route('/<event_id>/fee', methods=['POST'])
@login_required
def save_event_fee(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_finance_admin(band['id'], user_id):
        flash('Somente o administrador da banda pode alterar o cachê.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))

    from conversion_levers import pode_salvar_fechamento, resposta_paywall_conversao

    if not pode_salvar_fechamento(band['id'], event_id=event_id):
        return resposta_paywall_conversao(
            'Você já fechou 1 cachê no Grátis. Assine o Pro para liquidar todos os shows, '
            'PDF do caixa e offline no palco.',
            banda_id=band['id'],
        )

    def _parse_money(name):
        from band_finance import parse_money_field
        return parse_money_field(request.form.get(name))

    fee_total = _parse_money('fee_total')
    fee_couvert = _parse_money('fee_couvert')
    fee_transport = _parse_money('fee_transport_discount')
    fee_equipment = _parse_money('fee_equipment_discount')
    fee_notes = (request.form.get('fee_notes') or '').strip() or None
    fee_settled = request.form.get('fee_settled') == '1'
    use_night = request.form.get('settlement_mode') == 'night'

    if fee_total is None:
        flash('Informe o valor total do cachê (o que a casa pagou).', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))

    from db import update_event_fees, get_band_members
    from models_band_finance import (
        replace_event_expenses,
        replace_event_fee_lines,
        clear_event_fee_lines,
        list_event_expenses,
    )
    from models_band_team import set_event_guest_fixed_fee, list_event_guests
    from event_fees import compute_night_settlement
    from models_agenda import get_event_assignments

    update_event_fees(
        event_id,
        fee_total=fee_total,
        fee_transport_discount=fee_transport or 0,
        fee_equipment_discount=fee_equipment or 0,
        fee_notes=fee_notes,
        fee_settled=fee_settled,
        fee_couvert=fee_couvert or 0,
        update_couvert=True,
    )

    event_date = (event.get('starts_at') or '')[:10] or app_now_str()[:10]

    if use_night:
        # Despesas da noite (linhas dinâmicas)
        exp_descs = request.form.getlist('expense_desc')
        exp_vals = request.form.getlist('expense_valor')
        items = []
        for desc, val in zip(exp_descs, exp_vals):
            items.append({'descricao': desc, 'valor': val, 'categoria': 'transporte'})
        replace_event_expenses(
            band['id'],
            event_id,
            data=event_date,
            items=items,
            created_by_user_id=user_id,
        )

        # Taxas fixas de convidados neste show
        for g in list_event_guests(event_id):
            raw = (request.form.get(f'guest_fee_{g["id"]}') or '').strip()
            from band_finance import parse_money_field
            fee = parse_money_field(raw)
            set_event_guest_fixed_fee(g['id'], event_id, fee)

        # Papel + valor por membro neste show (overrides)
        from db import set_member_settlement_role
        amount_overrides: dict[str, float] = {}
        for m in get_band_members(band['id']):
            uid = m.get('user_id') or m.get('id')
            if not uid:
                continue
            role_key = f'member_role_{uid}'
            fee_key = f'member_fee_{uid}'
            if role_key not in request.form and fee_key not in request.form:
                continue
            role = (request.form.get(role_key) or m.get('settlement_role') or 'founder').strip()
            raw_fee = (request.form.get(fee_key) or '').strip()
            from band_finance import parse_money_field
            fee_val = parse_money_field(raw_fee)
            if fee_val is not None:
                amount_overrides[str(uid)] = fee_val
            # Sideman: grava taxa padrão da banda; fundador não guarda fee permanente
            sideman_default = fee_val if role == 'sideman' else None
            if role == 'sideman' and sideman_default is None:
                sideman_default = m.get('default_fixed_fee') or 0
            set_member_settlement_role(
                band['id'], uid,
                settlement_role=role,
                default_fixed_fee=sideman_default if role == 'sideman' else None,
            )

        event_row = dict(event)
        event_row['fee_total'] = fee_total
        event_row['fee_couvert'] = fee_couvert or 0
        event_row['fee_transport_discount'] = fee_transport or 0
        event_row['fee_equipment_discount'] = fee_equipment or 0
        settlement = compute_night_settlement(
            event_row,
            get_event_assignments(event_id),
            get_band_members(band['id']),
            guests=list_event_guests(event_id),
            event_expenses=list_event_expenses(event_id),
            fee_lines=None,
            name_for_user=user_display_name,
            amount_overrides=amount_overrides or None,
        )
        # Sempre grava o snapshot da divisão; "liquidado" só marca como pago
        saved_lines = replace_event_fee_lines(event_id, settlement.get('payees') or [])
        from models_band_finance import mark_all_event_fee_lines_paid
        mark_all_event_fee_lines_paid(event_id, paid=bool(fee_settled))
        _notify_fee_payees(
            band=band,
            event=event,
            actor_user_id=user_id,
            lines=saved_lines,
            fee_settled=fee_settled,
        )
        if settlement.get('warning'):
            flash(settlement['warning'], 'warning')
        flash(
            'Fechamento de noite salvo'
            + (' e marcado como liquidado — músicos avisados.' if fee_settled else '.'),
            'success',
        )
    else:
        clear_event_fee_lines(event_id)
        flash('Cachê do evento atualizado.', 'success')

    return redirect(url_for('agenda.view', event_id=event_id))


def _notify_fee_payees(*, band, event, actor_user_id, lines, fee_settled: bool) -> None:
    """Avisa cada músico com valor > 0 sobre a fatia / liquidação."""
    from db import create_notification

    title_show = (event.get('title') or 'Show').strip()
    band_name = (band.get('name') or 'Banda').strip()
    for line in lines or []:
        uid = line.get('user_id')
        amount = float(line.get('amount') or 0)
        if not uid or amount <= 0:
            continue
        if str(uid) == str(actor_user_id):
            continue
        status = 'liquidado' if (fee_settled or line.get('paid_at')) else 'registrado'
        try:
            create_notification(
                str(uid),
                band_id=band['id'],
                actor_user_id=actor_user_id,
                type='fee_share',
                title=f'Sua parte · {title_show}',
                body=(
                    f'{band_name}: R$ {amount:.2f} ({status}). '
                    'Abra Meu financeiro para ver o detalhe.'
                ),
                url_path='/bands/meus-caches',
                payload={
                    'event_id': event.get('id'),
                    'amount': amount,
                    'settled': bool(fee_settled),
                },
            )
        except Exception:
            current_app.logger.exception(
                'Falha ao notificar fatia user=%s event=%s', uid, event.get('id'),
            )


@agenda_bp.route('/<event_id>/fee-line/<line_id>/pago', methods=['POST'])
@login_required
def toggle_fee_line_paid(event_id, line_id):
    """Admin marca (ou desmarca) pagamento individual de um músico."""
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_finance_admin(band['id'], user_id):
        flash('Sem permissão.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))
    paid = request.form.get('paid', '1') == '1'
    from models_band_finance import set_fee_line_paid, list_event_fee_lines

    if not set_fee_line_paid(line_id, paid=paid, event_id=event_id):
        flash('Linha de cachê não encontrada.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')
    line = next((ln for ln in list_event_fee_lines(event_id) if ln['id'] == line_id), None)
    if paid and line and line.get('user_id') and float(line.get('amount') or 0) > 0:
        _notify_fee_payees(
            band=band,
            event=event,
            actor_user_id=user_id,
            lines=[line],
            fee_settled=True,
        )
    flash(
        'Pagamento marcado.' if paid else 'Pagamento desmarcado.',
        'success',
    )
    return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')


@agenda_bp.route('/<event_id>/fee/liquidar-rapido', methods=['POST'])
@login_required
def liquidar_noite_rapido(event_id):
    """1 toque: marca a noite como liquidada com a divisão já salva e avisa a banda."""
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_finance_admin(band['id'], user_id):
        flash('Sem permissão.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))
    from conversion_levers import pode_salvar_fechamento, resposta_paywall_conversao

    if not pode_salvar_fechamento(band['id'], event_id=event_id):
        return resposta_paywall_conversao(
            'Liquidação completa de vários shows faz parte do Pro.',
            banda_id=band['id'],
        )
    from db import update_event_fees
    from models_band_finance import list_event_fee_lines, mark_all_event_fee_lines_paid

    if not event.get('fee_total'):
        flash('Salve o fechamento (bruto + divisão) antes de liquidar.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')
    lines = list_event_fee_lines(event_id)
    if not lines:
        flash('Calcule e salve a liquidação antes de marcar como paga.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')
    update_event_fees(
        event_id,
        fee_total=event.get('fee_total'),
        fee_transport_discount=event.get('fee_transport_discount') or 0,
        fee_equipment_discount=event.get('fee_equipment_discount') or 0,
        fee_notes=event.get('fee_notes'),
        fee_settled=True,
    )
    mark_all_event_fee_lines_paid(event_id, paid=True)
    _notify_fee_payees(
        band=band,
        event=event,
        actor_user_id=user_id,
        lines=lines,
        fee_settled=True,
    )
    flash('Noite liquidada — músicos avisados no app.', 'success')
    return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')


@agenda_bp.route('/<event_id>/trial-pro', methods=['POST'])
@login_required
def trial_pro_opt_in(event_id):
    """Trial Pro 7 dias opt-in a partir do fechamento do show."""
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_finance_admin(band['id'], user_id):
        flash('Sem permissão.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))
    from conversion_levers import iniciar_trial_opt_in, trial_opt_in_disponivel
    from monetizacao import TRIAL_DIAS

    if not trial_opt_in_disponivel(band['id']):
        flash('Trial indisponível para esta banda (já usado ou já paga).', 'info')
        return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')
    if iniciar_trial_opt_in(band['id'], user_id):
        flash(
            f'Trial Pro de {TRIAL_DIAS} dias ativado — setlist, PDF e offline liberados.',
            'success',
        )
    else:
        flash('Não foi possível iniciar o trial.', 'warning')
    return redirect(url_for('agenda.view', event_id=event_id) + '#fechamento-noite')


@agenda_bp.route('/<event_id>/comando')
@login_required
def comando(event_id):
    """Checklist único do show: escala, freela, setlist, cachê."""
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    from event_prep_reminders import event_prep_gaps
    from models_band_team import list_band_freela_pool

    guests = list_event_guests(event_id)
    gaps = event_prep_gaps(event)
    pool = list_band_freela_pool(band['id']) if is_band_editor(band['id'], user_id) else []
    suggest_setlist = None
    if gaps.get('missing_setlist') or gaps.get('empty_setlist'):
        exclude = int(event['setlist_id']) if event.get('setlist_id') else None
        suggest_setlist = find_suggestable_setlist(band['id'], exclude_setlist_id=exclude)
    return render_template(
        'agenda/comando.html',
        event=event,
        band=band,
        gaps=gaps,
        guests=guests,
        freela_pool=pool,
        suggest_setlist=suggest_setlist,
        can_edit=is_band_editor(band['id'], user_id),
        format_event_datetime=format_event_datetime,
        event_type_label=event_type_label(event.get('event_type')),
        guest_invite_urls={
            str(g['id']): guest_scale_token_url(event_id, g['id']) for g in guests
        },
    )


@agenda_bp.route('/<event_id>/setlist/clonar-ultima', methods=['POST'])
@login_required
def clone_last_setlist(event_id):
    """Clona setlist sugerida (último show / mais cheia) e vincula a este evento."""
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_editor(band['id'], user_id):
        abort(404)
    source_raw = (request.form.get('source_setlist_id') or '').strip()
    exclude = int(event['setlist_id']) if event.get('setlist_id') else None
    if source_raw.isdigit():
        source = get_setlist(int(source_raw))
        if not source or source.get('band_id') != band['id']:
            flash('Setlist de origem inválida.', 'warning')
            return redirect(url_for('agenda.comando', event_id=event_id))
        source_id = int(source_raw)
    else:
        suggested = find_suggestable_setlist(band['id'], exclude_setlist_id=exclude)
        if not suggested:
            flash('Não há setlist anterior com músicas para clonar.', 'info')
            return redirect(url_for('agenda.comando', event_id=event_id))
        source_id = int(suggested['id'])
        source = get_setlist(source_id)

    show_title = (event.get('title') or 'Show').strip()
    copy_name = f'{source.get("name") or "Setlist"} · {show_title}'[:120]
    new_id = clone_setlist(source_id, name=copy_name)
    if not new_id:
        flash('Não foi possível clonar a setlist.', 'danger')
        return redirect(url_for('agenda.comando', event_id=event_id))

    update_band_event(
        event_id,
        title=event['title'],
        event_type=event['event_type'],
        starts_at=event['starts_at'],
        ends_at=event.get('ends_at'),
        location=event.get('location'),
        location_lat=event.get('location_lat'),
        location_lng=event.get('location_lng'),
        location_place_id=event.get('location_place_id'),
        notes=event.get('notes'),
        setlist_id=new_id,
    )
    flash(f'Setlist «{copy_name}» criada e vinculada a este show.', 'success')
    return redirect(url_for('agenda.comando', event_id=event_id))


@agenda_bp.route('/<event_id>/freela-pool/convidar', methods=['POST'])
@login_required
def invite_from_pool(event_id):
    """Reescala freela do pool histórico da banda neste show."""
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_editor(band['id'], user_id):
        abort(404)
    from conversion_levers import pode_adicionar_freela, resposta_paywall_conversao

    if not pode_adicionar_freela(event_id, band['id']):
        return resposta_paywall_conversao(
            'No Grátis: 1 freela por show. Pro libera o pool completo.',
            banda_id=band['id'],
        )
    name = (request.form.get('guest_name') or '').strip()
    phone = (request.form.get('guest_phone') or '').strip() or None
    role = (request.form.get('guest_role') or '').strip() or None
    if not name:
        flash('Nome obrigatório.', 'warning')
        return redirect(url_for('agenda.comando', event_id=event_id))
    existing = list_event_guests(event_id)
    for g in existing:
        same_phone = phone and (g.get('phone') or '') == phone
        same_name = (g.get('name') or '').strip().lower() == name.lower()
        if same_phone or (same_name and not phone):
            flash(f'{name} já está neste show.', 'info')
            return redirect(url_for('agenda.comando', event_id=event_id))
    guest_id = add_event_guest(
        event_id, name=name, phone=phone, role_label=role, invited_by=user_id,
    )
    guest = get_event_guest(guest_id) or {
        'id': guest_id, 'name': name, 'phone': phone, 'role_label': role,
    }
    invite = notify_event_guest(
        event=event, guest=guest, actor_user_id=user_id, band_name=band.get('name'),
    )
    if invite.get('whatsapp_sent'):
        flash(f'{name} reconvidado — WhatsApp enviado.', 'success')
    else:
        flash(f'{name} adicionado. Copie o link no Comando do show se preciso.', 'info')
    return redirect(url_for('agenda.comando', event_id=event_id))


@agenda_bp.route('/<event_id>/convidado', methods=['POST'])
@login_required
def add_guest(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_editor(band['id'], user_id):
        abort(404)
    from conversion_levers import pode_adicionar_freela, resposta_paywall_conversao

    if not pode_adicionar_freela(event_id, band['id']):
        return resposta_paywall_conversao(
            'No Grátis: 1 freela por show. Pro libera convidados ilimitados + PDF e offline.',
            banda_id=band['id'],
        )
    name = (request.form.get('guest_name') or '').strip()
    phone = (request.form.get('guest_phone') or '').strip() or None
    role = (request.form.get('guest_role') or '').strip() or None
    if not name:
        flash('Informe o nome do convidado.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))
    guest_id = add_event_guest(
        event_id, name=name, phone=phone, role_label=role, invited_by=user_id,
    )
    guest = get_event_guest(guest_id) or {'id': guest_id, 'name': name, 'phone': phone, 'role_label': role}
    invite = notify_event_guest(
        event=event, guest=guest, actor_user_id=user_id, band_name=band.get('name'),
    )
    if invite.get('whatsapp_sent'):
        flash('Freela adicionado — convite enviado por WhatsApp com link de confirmação.', 'success')
    elif invite.get('has_phone'):
        flash(
            'Freela adicionado. Não foi possível enviar o WhatsApp agora — use «Reenviar» ou copie o link.',
            'warning',
        )
    else:
        flash(
            'Freela adicionado. Informe o WhatsApp ou copie o link de confirmação na lista.',
            'info',
        )
    return redirect(url_for('agenda.view', event_id=event_id))


@agenda_bp.route('/<event_id>/convidado/<guest_id>/remover', methods=['POST'])
@login_required
def remove_guest(event_id, guest_id):
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_editor(band['id'], user_id):
        abort(404)
    remove_event_guest(guest_id)
    flash('Convidado removido.', 'info')
    return redirect(url_for('agenda.view', event_id=event_id))


@agenda_bp.route('/<event_id>/convidado/<guest_id>/reenviar', methods=['POST'])
@login_required
def resend_guest_invite(event_id, guest_id):
    event, band, user_id = _require_event_access(event_id)
    if not event or not is_band_editor(band['id'], user_id):
        abort(404)
    guest = get_event_guest(guest_id)
    if not guest or str(guest.get('event_id')) != str(event_id):
        flash('Convidado não encontrado.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))
    invite = notify_event_guest(
        event=event, guest=guest, actor_user_id=user_id, band_name=band.get('name'),
    )
    if invite.get('whatsapp_sent'):
        flash('Convite reenviado por WhatsApp.', 'success')
    elif invite.get('has_phone'):
        flash('Falha ao enviar WhatsApp. Copie o link abaixo e envie manualmente.', 'warning')
    else:
        flash('Sem WhatsApp cadastrado — copie o link de confirmação.', 'info')
    return redirect(url_for('agenda.view', event_id=event_id))


@agenda_bp.route('/<event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    setlists = get_band_setlists(band['id'])

    if request.method == 'POST':
        data = _read_event_form(band['id'])
        if not data:
            return render_template(
                'agenda/form.html',
                **_form_template_ctx(
                    band=band,
                    setlists=setlists,
                    event=event,
                    prefill_setlist='',
                    event_types=EVENT_TYPES,
                    split_event_datetime=split_event_datetime,
                ),
            )
        update_band_event(event_id, **data)
        bn.event_updated(band['id'], user_id, event_id, data['title'], data['event_type'])
        flash('Evento atualizado.', 'success')
        return redirect(url_for('agenda.view', event_id=event_id))

    return render_template(
        'agenda/form.html',
        **_form_template_ctx(
            band=band,
            setlists=setlists,
            event=event,
            prefill_setlist='',
            event_types=EVENT_TYPES,
            split_event_datetime=split_event_datetime,
        ),
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
    members = get_band_members(band['id'])
    current = {a['user_id']: a for a in get_event_assignments(event_id)}

    if request.method == 'POST':
        action = (request.form.get('action') or '').strip()
        if action == 'apply_lineup':
            lineup_id = (request.form.get('lineup_id') or '').strip()
            lineup = get_lineup(lineup_id) if lineup_id else None
            if not lineup or lineup.get('band_id') != band['id']:
                flash('Formação inválida.', 'warning')
                return redirect(url_for('agenda.escala', event_id=event_id))
            assignments = lineup_assignments(lineup_id)
            added = set_event_assignments(event_id, assignments, assigned_by=user_id)
            if added:
                bn.event_scale_assigned(
                    band['id'], user_id, event_id, event['title'], added,
                )
            flash(f'Formação «{lineup["name"]}» aplicada.', 'success')
            return redirect(url_for('agenda.escala', event_id=event_id))

        if action == 'apply_suggestions':
            suggestions = suggest_scale_assignments(band['id'], event_id)
            assignments = [
                {'user_id': s['user_id'], 'role_label': s.get('role_label')}
                for s in suggestions if not s.get('blocked')
            ]
            added = set_event_assignments(event_id, assignments, assigned_by=user_id)
            if added:
                bn.event_scale_assigned(
                    band['id'], user_id, event_id, event['title'], added,
                )
            flash('Sugestão de escala aplicada.', 'success')
            return redirect(url_for('agenda.escala', event_id=event_id))

        assignments = _read_scale_form(band['id'])
        if assignments is None:
            flash('Seleção de integrantes inválida.', 'warning')
            return redirect(url_for('agenda.escala', event_id=event_id))

        added = set_event_assignments(event_id, assignments, assigned_by=user_id)
        if added:
            bn.event_scale_assigned(
                band['id'], user_id, event_id, event['title'], added,
            )
        flash('Escalação salva.', 'success')
        return redirect(url_for('agenda.view', event_id=event_id))

    ensure_default_band_roles(band['id'])
    event_date = str(event.get('starts_at') or '')[:10]
    member_ids = [m['id'] for m in members]
    blocked_ids = users_blocked_on_date(member_ids, event_date) if event_date else set()
    scale_stats = get_assignment_response_stats(event_id)
    suggestions = suggest_scale_assignments(band['id'], event_id)

    from user_instruments import enrich_members_with_instruments
    enrich_members_with_instruments(members)

    return render_template(
        'agenda/escala.html',
        event=event,
        band=band,
        members=members,
        current=current,
        band_roles=list_band_roles(band['id']),
        lineups=list_band_lineups(band['id']),
        blocked_ids=blocked_ids,
        scale_stats=scale_stats,
        suggestions=suggestions,
        format_event_datetime=format_event_datetime,
        user_display_name=user_display_name,
    )


@agenda_bp.route('/<event_id>/escala/responder', methods=['POST'])
@login_required
def respond_scale(event_id):
    event, band, user_id = _require_event_access(event_id)
    if not event:
        abort(404)
    assignment = get_user_event_assignment(event_id, user_id)
    if not assignment:
        flash('Você não está escalado para este evento.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))

    action = (request.form.get('action') or '').strip().lower()
    if action not in ('accept', 'decline'):
        flash('Resposta inválida.', 'warning')
        return redirect(url_for('agenda.view', event_id=event_id))

    note = (request.form.get('note') or '').strip()
    updated = process_scale_response(
        event_id,
        user_id,
        accepted=(action == 'accept'),
        note=note,
    )
    if not updated:
        flash('Não foi possível registrar sua resposta.', 'danger')
        return redirect(url_for('agenda.view', event_id=event_id))

    if action == 'accept':
        flash('Presença confirmada na escalação.', 'success')
    else:
        flash('Recusa registrada. Quem te escalou foi notificado.', 'info')
    return redirect(url_for('agenda.view', event_id=event_id))


@agenda_bp.route('/escala/responder/<token>', methods=['GET', 'POST'])
def respond_scale_token(token):
    """Aceitar ou recusar escalação via link (sem login)."""
    parsed = verify_scale_response_token(token)
    if not parsed:
        return render_template('agenda/scale_token_invalid.html'), 400
    event_id, user_id = parsed
    event = get_band_event(event_id)
    if not event:
        return render_template('agenda/scale_token_invalid.html'), 404
    band = get_band(event['band_id'])
    assignment = get_user_event_assignment(event_id, user_id)
    if not assignment:
        return render_template('agenda/scale_token_invalid.html'), 404

    if request.method == 'GET':
        action = (request.args.get('action') or '').strip().lower()
        if action == 'accept':
            updated = process_scale_response(event_id, user_id, accepted=True)
            if updated:
                return render_template(
                    'agenda/scale_token_result.html',
                    event=event,
                    band=band,
                    accepted=True,
                    assignment=updated,
                    format_event_datetime=format_event_datetime,
                )
        elif action == 'decline':
            return render_template(
                'agenda/scale_token_decline.html',
                event=event,
                band=band,
                token=token,
                assignment=assignment,
                format_event_datetime=format_event_datetime,
            )

    if request.method == 'POST':
        action = (request.form.get('action') or '').strip().lower()
        note = (request.form.get('note') or '').strip()
        if action not in ('accept', 'decline'):
            flash('Resposta inválida.', 'warning')
            return redirect(scale_token_url(event_id, user_id))
        updated = process_scale_response(
            event_id,
            user_id,
            accepted=(action == 'accept'),
            note=note,
        )
        if not updated:
            return render_template('agenda/scale_token_invalid.html'), 400
        return render_template(
            'agenda/scale_token_result.html',
            event=event,
            band=band,
            accepted=(action == 'accept'),
            assignment=updated,
            format_event_datetime=format_event_datetime,
        )

    st = (assignment.get('response_status') or 'pending').lower()
    return render_template(
        'agenda/scale_token.html',
        event=event,
        band=band,
        assignment=assignment,
        token=token,
        already_responded=st != 'pending',
        format_event_datetime=format_event_datetime,
        user_display_name=user_display_name,
    )



@agenda_bp.route('/freela/responder/<token>', methods=['GET', 'POST'])
def respond_guest_token(token):
    """Aceitar ou recusar convite de freela/convidado via link (sem login)."""
    parsed = verify_guest_scale_token(token)
    if not parsed:
        return render_template('agenda/scale_token_invalid.html'), 400
    event_id, guest_id = parsed
    event = get_band_event(event_id)
    if not event:
        return render_template('agenda/scale_token_invalid.html'), 404
    band = get_band(event['band_id'])
    guest = get_event_guest(guest_id)
    if not guest or str(guest.get('event_id')) != str(event_id):
        return render_template('agenda/scale_token_invalid.html'), 404

    if request.method == 'GET':
        action = (request.args.get('action') or '').strip().lower()
        if action == 'accept':
            updated = process_guest_scale_response(event_id, guest_id, accepted=True)
            if updated:
                return render_template(
                    'agenda/guest_token_result.html',
                    event=event,
                    band=band,
                    guest=updated,
                    accepted=True,
                    format_event_datetime=format_event_datetime,
                )
        elif action == 'decline':
            return render_template(
                'agenda/guest_token_decline.html',
                event=event,
                band=band,
                guest=guest,
                token=token,
                format_event_datetime=format_event_datetime,
            )

    if request.method == 'POST':
        action = (request.form.get('action') or '').strip().lower()
        note = (request.form.get('note') or '').strip()
        if action not in ('accept', 'decline'):
            flash('Resposta inválida.', 'warning')
            return redirect(guest_scale_token_url(event_id, guest_id))
        updated = process_guest_scale_response(
            event_id, guest_id, accepted=(action == 'accept'), note=note,
        )
        if not updated:
            return render_template('agenda/scale_token_invalid.html'), 400
        return render_template(
            'agenda/guest_token_result.html',
            event=event,
            band=band,
            guest=updated,
            accepted=(action == 'accept'),
            format_event_datetime=format_event_datetime,
        )

    st = (guest.get('response_status') or 'pending').lower()
    return render_template(
        'agenda/guest_token.html',
        event=event,
        band=band,
        guest=guest,
        token=token,
        already_responded=st != 'pending',
        format_event_datetime=format_event_datetime,
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