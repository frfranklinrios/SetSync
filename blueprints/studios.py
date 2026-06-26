"""Estúdios de ensaio — cadastro, disponibilidade e agendamentos."""

from __future__ import annotations

import os
import re
import sys
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from blueprints.auth import login_required
from db import get_band, get_user_bands, is_band_member
from models_agenda import EVENT_ENSAIO, create_band_event, delete_band_event
from models_setlist import get_band_setlists
from models_studio import (
    BOOKING_CANCELADO,
    BOOKING_CONFIRMADO,
    BOOKING_PENDENTE,
    BOOKING_RECUSADO,
    add_room_block,
    add_studio_photo,
    add_room_photo,
    count_room_photos,
    count_studio_photos,
    create_booking,
    create_room,
    create_studio,
    count_bookings_for_room,
    delete_room,
    delete_room_block,
    delete_room_photo,
    delete_studio_photo,
    get_booking,
    get_booking_enriched,
    get_room,
    get_room_with_studio,
    get_studio,
    list_bookings_for_band,
    list_bookings_for_studio,
    list_room_availability,
    list_room_blocks,
    list_room_photos,
    list_rooms,
    list_studio_calendar_bookings,
    list_studio_photos,
    list_studios_by_owner,
    replace_weekly_availability,
    search_studios,
    studio_full_address,
    update_booking_status,
    update_room,
    update_studio,
)
from monetizacao import (
    LIMITES_ESTUDIO_BASICO,
    check_studio_room_limit,
    resposta_limite_estudio,
    studio_plano_badge_ui,
)
import studio_notifications as sn
from studio_photos import (
    MAX_ROOM_PHOTOS,
    MAX_STUDIO_PHOTOS,
    delete_room_photo_file,
    delete_studio_photo_file,
    photo_mimetype,
    room_photo_path,
    save_room_photo_upload,
    save_studio_photo_upload,
    studio_photo_path,
)
from studio_scheduling import (
    get_available_slots,
    parse_booking_date,
    validate_booking_request,
    booking_datetime_range,
)
from studio_schemas import (
    WEEKDAY_LABELS,
    calendar_events_from_bookings,
    parse_block_form,
    parse_booking_form,
    parse_room_form,
    parse_studio_form,
    parse_weekly_availability_form,
    available_slots_to_api,
)

studios_bp = Blueprint('studios', __name__, url_prefix='/estudios')


def _studio_form_ctx(studio=None) -> dict:
    from agenda_maps import google_maps_api_key, studio_maps_context

    ctx = studio_maps_context(studio)
    ctx['google_maps_api_key'] = google_maps_api_key()
    ctx['full_address'] = studio_full_address(studio) if studio else ''
    return ctx


def _render_studio_form(studio=None):
    return render_template(
        'studios/owner/form.html',
        studio=studio,
        **_studio_form_ctx(studio),
    )


def _user_id() -> str:
    return session['user_id']


def _require_studio_owner(studio_id: str):
    from db import is_superadmin
    studio = get_studio(studio_id)
    uid = _user_id()
    if not studio:
        return None, None
    if studio.get('owner_user_id') != uid and not is_superadmin(uid):
        return None, None
    return studio, uid


def _require_room_in_studio(studio_id: str, room_id: str):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        return None, None, None
    room = get_room(room_id)
    if not room or room.get('studio_id') != studio_id:
        return None, None, None
    return studio, room, uid


def _scheduling_context(room_id: str, target_date):
    availability = list_room_availability(room_id)
    from models_studio import list_bookings_for_room
    bookings = list_bookings_for_room(room_id)
    blocks = list_room_blocks(room_id)
    return availability, bookings, blocks


def _slots_for_room_date(room_id: str, date_iso: str, slot_minutes: int = 60):
    target = parse_booking_date(date_iso)
    if not target:
        return []
    avail, bookings, blocks = _scheduling_context(room_id, target)
    return get_available_slots(
        availability_rows=avail,
        bookings=bookings,
        blocks=blocks,
        target=target,
        slot_minutes=slot_minutes,
    )


# ── Landing pública ───────────────────────────────────────────────────────

@studios_bp.route('/')
def landing():
    """Landing page para donos de estúdio de ensaio."""
    from config import whatsapp_message, whatsapp_number
    from monetizacao import PRECO_ESTUDIO_PREMIUM, planos_estudio_para_site

    return render_template(
        'estudios.html',
        planos_estudio=planos_estudio_para_site(),
        premium_mensal=PRECO_ESTUDIO_PREMIUM,
        whatsapp=whatsapp_number(),
        whatsapp_message=whatsapp_message(),
    )


# ── Busca (bandas) ────────────────────────────────────────────────────────

@studios_bp.route('/buscar')
@login_required
def search():
    cidade = (request.args.get('cidade') or '').strip()
    bairro = (request.args.get('bairro') or '').strip()
    studios = search_studios(cidade=cidade or None, bairro=bairro or None) if (cidade or bairro) else []
    from studio_growth import studio_is_verified
    studios = [{**s, 'verified': studio_is_verified(s)} for s in studios]
    my_studios = list_studios_by_owner(_user_id())
    return render_template(
        'studios/search.html',
        studios=studios,
        my_studios=my_studios,
        cidade=cidade,
        bairro=bairro,
    )


@studios_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def register_studio():
    if request.method == 'POST':
        data = parse_studio_form(request.form)
        if not data:
            flash('Preencha nome e cidade.', 'danger')
            return _render_studio_form(None)
        studio_id = create_studio(_user_id(), **data)
        from monetizacao import dias_restantes_trial_estudio
        dias = dias_restantes_trial_estudio(_user_id())
        if dias is not None:
            flash(
                f'Estúdio cadastrado! Trial Premium de 30 dias ativado ({dias} dias). '
                'Siga o guia no painel para configurar salas e divulgar seu espaço.',
                'info',
            )
        else:
            flash(
                'Estúdio cadastrado! Siga o guia no painel para configurar salas e divulgar seu espaço.',
                'success',
            )
        return redirect(url_for('studios.owner_dashboard', studio_id=studio_id, bem_vindo=1))
    return _render_studio_form(None)


@studios_bp.route('/meus')
@login_required
def my_studios():
    return redirect(url_for('studios.search'))


# ── Agendamento público (QR) ──────────────────────────────────────────────

@studios_bp.route('/<studio_id>/agendar')
def booking_landing(studio_id):
    """Página pública para QR na recepção — bandas entram para reservar."""
    from studio_growth import increment_studio_booking_click
    increment_studio_booking_click(studio_id)
    studio = get_studio(studio_id)
    if not studio or not studio.get('ativo'):
        abort(404)
    if 'user_id' in session:
        return redirect(url_for('studios.detail', studio_id=studio_id))
    rooms = [r for r in list_rooms(studio_id) if r.get('ativa')]
    photos = list_studio_photos(studio_id)
    from agenda_maps import studio_maps_context
    maps_ctx = studio_maps_context(studio)
    book_next = url_for('studios.detail', studio_id=studio_id)
    return render_template(
        'studios/booking_landing.html',
        studio=studio,
        rooms=rooms,
        photos=photos,
        full_address=studio_full_address(studio),
        login_url=url_for('auth.login', next=book_next),
        register_url=url_for('auth.register', next=book_next),
        **maps_ctx,
    )


@studios_bp.route('/<studio_id>/agendar-qr.png')
@login_required
def booking_qr(studio_id):
    """QR Code PNG para agendamento (dono do estúdio)."""
    studio, _uid = _require_studio_owner(studio_id)
    if not studio:
        abort(404)
    from qr_util import qrcode_png_bytes
    from security import external_url_for

    public_url = external_url_for('studios.booking_landing', studio_id=studio_id)
    try:
        png = qrcode_png_bytes(public_url)
    except Exception:
        current_app.logger.exception('Falha ao gerar QR agendamento estúdio %s', studio_id)
        abort(500)

    as_download = request.args.get('download', '').lower() in ('1', 'true', 'yes')
    safe_name = re.sub(r'[^\w\s-]+', '', studio.get('nome') or 'estudio', flags=re.UNICODE)
    safe_name = re.sub(r'\s+', '-', safe_name.strip())[:60] or 'estudio'
    return send_file(
        BytesIO(png),
        mimetype='image/png',
        max_age=300,
        as_attachment=as_download,
        download_name=f'{safe_name}-agendamento-qr.png',
    )


# ── Detalhe público (bandas) ──────────────────────────────────────────────

@studios_bp.route('/<studio_id>')
@login_required
def detail(studio_id):
    studio = get_studio(studio_id)
    if not studio or not studio.get('ativo'):
        flash('Estúdio não encontrado.', 'danger')
        return redirect(url_for('studios.search'))
    from studio_growth import increment_studio_page_view, studio_is_verified, studio_og_context
    increment_studio_page_view(studio_id)
    studio = get_studio(studio_id) or studio
    rooms = list_rooms(studio_id)
    photos = list_studio_photos(studio_id)
    is_owner = studio.get('owner_user_id') == _user_id()
    user_bands = get_user_bands(_user_id()) if 'user_id' in session else []
    from agenda_maps import studio_maps_context
    maps_ctx = studio_maps_context(studio)
    og = studio_og_context(studio, photos=photos)
    return render_template(
        'studios/detail.html',
        studio=studio,
        rooms=rooms,
        photos=photos,
        is_owner=is_owner,
        user_bands=user_bands,
        full_address=studio_full_address(studio),
        studio_verified=studio_is_verified(studio),
        **og,
        **maps_ctx,
    )


# ── Dono: painel e edição ─────────────────────────────────────────────────

@studios_bp.route('/<studio_id>/onboarding/dismiss', methods=['POST'])
@login_required
def dismiss_studio_onboarding(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        abort(404)
    from models_studio import dismiss_studio_onboarding as _dismiss
    _dismiss(studio_id)
    flash('Guia oculto. Consulte Ajuda → Estúdios se precisar rever os passos.', 'info')
    return redirect(url_for('studios.owner_dashboard', studio_id=studio_id))


@studios_bp.route('/<studio_id>/painel')
@login_required
def owner_dashboard(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    rooms = list_rooms(studio_id, active_only=False)
    pending = list_bookings_for_studio(studio_id, status=BOOKING_PENDENTE)
    plano_ui = studio_plano_badge_ui(uid)
    room_limit = None if plano_ui.get('premium') else LIMITES_ESTUDIO_BASICO['sala']
    from security import external_url_for
    from studio_onboarding import get_studio_onboarding_progress
    from studio_growth import studio_metrics, studio_is_verified
    return render_template(
        'studios/owner/dashboard.html',
        studio=studio,
        rooms=rooms,
        pending=pending,
        can_add_room=check_studio_room_limit(uid),
        room_limit=room_limit,
        studio_plano_ui=plano_ui,
        booking_public_url=external_url_for('studios.booking_landing', studio_id=studio_id),
        studio_onboarding=get_studio_onboarding_progress(studio),
        studio_metrics=studio_metrics(studio),
        studio_verified=studio_is_verified(studio),
        bem_vindo=request.args.get('bem_vindo') in ('1', 'true', 'yes'),
    )


STUDIO_EXPENSE_CATEGORIES = (
    ('aluguel', 'Aluguel'),
    ('energia', 'Energia'),
    ('manutencao', 'Manutenção'),
    ('equipamento', 'Equipamento'),
    ('salarios', 'Salários'),
    ('outros', 'Outros'),
)


def _parse_finance_period() -> tuple[int, int]:
    from studio_finance import default_finance_period

    y, m, _, _ = default_finance_period()
    try:
        y = int(request.args.get('ano') or request.form.get('ano') or y)
        m = int(request.args.get('mes') or request.form.get('mes') or m)
    except (TypeError, ValueError):
        pass
    if m < 1:
        m = 1
    if m > 12:
        m = 12
    if y < 2000:
        y = 2000
    if y > 2100:
        y = 2100
    return y, m


def _resolve_studio_finance_user(studio_id: str):
    """Sessão do dono ou token curto para captura PDF server-side."""
    from db import get_studio, is_superadmin

    pdfgen = request.args.get('pdfgen', '').lower() in ('1', 'true', 'yes')
    if pdfgen:
        from security import verify_studio_finance_pdf_token

        uid = verify_studio_finance_pdf_token(request.args.get('pdf_token', ''), studio_id)
        if not uid:
            return None, None
        studio = get_studio(studio_id)
        if not studio:
            return None, None
        if studio.get('owner_user_id') != uid and not is_superadmin(uid):
            return None, None
        return studio, uid
    return _require_studio_owner(studio_id)


def _load_finance_report(studio_id: str, year: int, month: int):
    from studio_finance import build_studio_finance_report, month_bounds
    from models_studio_finance import list_studio_bookings_for_finance, list_studio_expenses

    studio = get_studio(studio_id)
    if not studio:
        return None
    from_date, to_date = month_bounds(year, month)
    bookings = list_studio_bookings_for_finance(
        studio_id, from_date=from_date, to_date=to_date,
    )
    expenses = list_studio_expenses(
        studio_id, from_date=from_date, to_date=to_date,
    )
    report = build_studio_finance_report(
        studio=studio,
        bookings=bookings,
        expenses=expenses,
        year=year,
        month=month,
    )
    return studio, report, from_date, to_date


def _finance_redirect(studio_id: str) -> str:
    y, m = _parse_finance_period()
    return redirect(url_for('studios.owner_finance', studio_id=studio_id, ano=y, mes=m))


@studios_bp.route('/<studio_id>/financeiro')
@login_required
def owner_finance(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    year, month = _parse_finance_period()
    loaded = _load_finance_report(studio_id, year, month)
    if not loaded:
        flash('Estúdio não encontrado.', 'danger')
        return redirect(url_for('studios.search'))
    studio, report, from_date, to_date = loaded
    return render_template(
        'studios/owner/finance.html',
        studio=studio,
        report=report,
        expense_categories=STUDIO_EXPENSE_CATEGORIES,
        from_date=from_date,
        to_date=to_date,
    )


@studios_bp.route('/<studio_id>/financeiro/imprimir')
def owner_finance_print(studio_id):
    studio, uid = _resolve_studio_finance_user(studio_id)
    if not studio:
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.path))
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    year, month = _parse_finance_period()
    loaded = _load_finance_report(studio_id, year, month)
    if not loaded:
        flash('Estúdio não encontrado.', 'danger')
        return redirect(url_for('studios.search'))
    studio, report, from_date, to_date = loaded
    from config import app_now_str
    from studio_finance_pdf import period_label

    pdfgen = request.args.get('pdfgen', '').lower() in ('1', 'true', 'yes')
    expense_labels = dict(STUDIO_EXPENSE_CATEGORIES)
    return render_template(
        'studios/owner/finance_print.html',
        studio=studio,
        report=report,
        from_date=from_date,
        to_date=to_date,
        period_label=period_label(year, month),
        generated_at=app_now_str()[:16].replace('T', ' '),
        expense_labels=expense_labels,
        pdfgen=pdfgen,
    )


@studios_bp.route('/<studio_id>/financeiro/exportar-pdf')
@login_required
def owner_finance_export_pdf(studio_id):
    from io import BytesIO

    from studio_finance_pdf import build_finance_pdf_download_name, generate_studio_finance_pdf_bytes

    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    year, month = _parse_finance_period()
    try:
        pdf_bytes = generate_studio_finance_pdf_bytes(
            studio_id, uid, year=year, month=month,
        )
    except Exception as exc:
        current_app.logger.exception('PDF financeiro do estúdio falhou: %s', exc)
        flash('Não foi possível gerar o PDF agora. Tente imprimir pelo navegador.', 'danger')
        return redirect(url_for('studios.owner_finance_print', studio_id=studio_id, ano=year, mes=month))
    filename = build_finance_pdf_download_name(studio['nome'], year, month)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )


@studios_bp.route('/<studio_id>/financeiro/precos', methods=['GET', 'POST'])
@login_required
def owner_finance_prices(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    rooms = list_rooms(studio_id, active_only=False)
    year, month = _parse_finance_period()

    if request.method == 'POST':
        from studio_schemas import parse_finance_prices_form

        studio_preco, room_prices = parse_finance_prices_form(
            request.form, [r['id'] for r in rooms],
        )
        update_studio(studio_id, preco_hora=studio_preco)
        for room in rooms:
            rid = room['id']
            if rid in room_prices:
                update_room(rid, preco_hora=room_prices[rid])
        flash('Preços por hora salvos.', 'success')
        return redirect(url_for(
            'studios.owner_finance', studio_id=studio_id, ano=year, mes=month,
        ))

    return render_template(
        'studios/owner/finance_prices.html',
        studio=studio,
        rooms=rooms,
        finance_year=year,
        finance_month=month,
    )


@studios_bp.route('/<studio_id>/financeiro/reserva/<booking_id>', methods=['POST'])
@login_required
def save_booking_finance(studio_id, booking_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        abort(404)
    booking = get_booking_enriched(booking_id)
    if not booking or (booking.get('studio') or {}).get('id') != studio_id:
        flash('Reserva não encontrada.', 'danger')
        return _finance_redirect(studio_id)
    from studio_finance import parse_money_field
    from models_studio_finance import update_booking_finance

    raw_valor = request.form.get('valor_cobrado', '').strip()
    clear_valor = 'clear_valor' in request.form
    valor = parse_money_field(raw_valor) if raw_valor and not clear_valor else None
    paid_raw = request.form.get('pago')
    paid = True if paid_raw == '1' else False if paid_raw == '0' else None
    notes = (request.form.get('finance_notes') or '').strip()[:500]

    update_booking_finance(
        booking_id,
        valor_cobrado=valor,
        clear_valor=clear_valor or (not raw_valor and not clear_valor and 'valor_cobrado' in request.form),
        paid=paid,
        finance_notes=notes,
    )
    flash('Reserva atualizada.', 'success')
    return _finance_redirect(studio_id)


@studios_bp.route('/<studio_id>/financeiro/despesa', methods=['POST'])
@login_required
def add_studio_expense(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        abort(404)
    from studio_finance import parse_money_field
    from models_studio_finance import create_studio_expense

    data = (request.form.get('data') or '').strip()[:10]
    descricao = (request.form.get('descricao') or '').strip()
    valor = parse_money_field(request.form.get('valor'))
    categoria = (request.form.get('categoria') or 'outros').strip()[:40]
    if not data or not descricao or valor is None or valor <= 0:
        flash('Preencha data, descrição e valor da despesa.', 'danger')
        return _finance_redirect(studio_id)
    create_studio_expense(
        studio_id,
        data=data,
        descricao=descricao,
        valor=valor,
        categoria=categoria,
        created_by_user_id=uid,
    )
    flash('Despesa registrada.', 'success')
    return _finance_redirect(studio_id)


@studios_bp.route('/<studio_id>/financeiro/despesa/<expense_id>/excluir', methods=['POST'])
@login_required
def delete_studio_expense_route(studio_id, expense_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        abort(404)
    from models_studio_finance import delete_studio_expense

    if delete_studio_expense(expense_id, studio_id):
        flash('Despesa removida.', 'success')
    else:
        flash('Despesa não encontrada.', 'danger')
    return _finance_redirect(studio_id)


@studios_bp.route('/<studio_id>/editar', methods=['GET', 'POST'])
@login_required
def edit_studio(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    if request.method == 'POST':
        data = parse_studio_form(request.form)
        if not data:
            flash('Preencha nome e cidade.', 'danger')
        else:
            update_studio(studio_id, **data)
            flash('Estúdio atualizado.', 'success')
            return redirect(url_for('studios.owner_dashboard', studio_id=studio_id))
    photos = list_studio_photos(studio_id)
    return _render_studio_form(studio)


@studios_bp.route('/<studio_id>/calendario')
@login_required
def owner_calendar(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    bookings = list_studio_calendar_bookings(studio_id)
    events_calendar = calendar_events_from_bookings(
        bookings,
        url_builder=lambda bid: url_for('studios.owner_dashboard', studio_id=studio_id),
    )
    rooms = list_rooms(studio_id, active_only=False)
    return render_template(
        'studios/owner/calendar.html',
        studio=studio,
        rooms=rooms,
        events_calendar=events_calendar,
    )


# ── Salas ─────────────────────────────────────────────────────────────────

@studios_bp.route('/<studio_id>/salas')
@login_required
def owner_rooms(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    rooms = list_rooms(studio_id, active_only=False)
    plano_ui = studio_plano_badge_ui(uid)
    room_limit = None if plano_ui.get('premium') else LIMITES_ESTUDIO_BASICO['sala']
    booking_counts = {r['id']: count_bookings_for_room(r['id']) for r in rooms}
    return render_template(
        'studios/owner/rooms.html',
        studio=studio,
        rooms=rooms,
        booking_counts=booking_counts,
        can_add_room=check_studio_room_limit(uid),
        room_limit=room_limit,
        studio_plano_ui=plano_ui,
    )


@studios_bp.route('/<studio_id>/salas/nova', methods=['GET', 'POST'])
@login_required
def new_room(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    if not check_studio_room_limit(uid):
        return resposta_limite_estudio()
    if request.method == 'POST':
        data = parse_room_form(request.form)
        if not data:
            flash('Informe o nome da sala.', 'danger')
        else:
            room_id = create_room(studio_id, **data)
            flash('Sala criada.', 'success')
            return redirect(url_for('studios.room_availability', studio_id=studio_id, room_id=room_id))
    return render_template(
        'studios/owner/room_form.html',
        studio=studio,
        room=None,
        rooms_back_url=url_for('studios.owner_rooms', studio_id=studio_id),
    )


@studios_bp.route('/<studio_id>/salas/<room_id>/editar', methods=['GET', 'POST'])
@login_required
def edit_room(studio_id, room_id):
    studio, room, uid = _require_room_in_studio(studio_id, room_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    if request.method == 'POST':
        data = parse_room_form(request.form)
        if not data:
            flash('Informe o nome da sala.', 'danger')
        else:
            update_room(room_id, **data)
            flash('Sala atualizada.', 'success')
            return redirect(url_for('studios.owner_rooms', studio_id=studio_id))
    photos = list_room_photos(room_id)
    return render_template(
        'studios/owner/room_form.html',
        studio=studio,
        room=room,
        photos=photos,
        rooms_back_url=url_for('studios.owner_rooms', studio_id=studio_id),
    )


@studios_bp.route('/<studio_id>/salas/<room_id>/toggle-ativa', methods=['POST'])
@login_required
def toggle_room_active(studio_id, room_id):
    studio, room, uid = _require_room_in_studio(studio_id, room_id)
    if not studio or not room:
        abort(404)
    new_state = 0 if room.get('ativa') else 1
    update_room(room_id, ativa=new_state)
    flash(
        'Sala reativada.' if new_state else 'Sala desativada — não aparece para novas reservas.',
        'success',
    )
    return redirect(url_for('studios.owner_rooms', studio_id=studio_id))


@studios_bp.route('/<studio_id>/salas/<room_id>/excluir', methods=['POST'])
@login_required
def remove_room(studio_id, room_id):
    studio, room, uid = _require_room_in_studio(studio_id, room_id)
    if not studio or not room:
        abort(404)
    n_bookings = count_bookings_for_room(room_id)
    if n_bookings and not request.form.get('confirm_delete'):
        flash(
            f'Esta sala tem {n_bookings} reserva(s) no histórico. '
            'Confirme a exclusão para remover tudo.',
            'warning',
        )
        return redirect(url_for('studios.owner_rooms', studio_id=studio_id))
    for photo in list_room_photos(room_id):
        delete_room_photo_file(room_id, photo.get('filename') or '')
    if delete_room(room_id):
        flash('Sala excluída.', 'success')
    else:
        flash('Não foi possível excluir a sala.', 'danger')
    return redirect(url_for('studios.owner_rooms', studio_id=studio_id))


@studios_bp.route('/<studio_id>/salas/<room_id>/disponibilidade', methods=['GET', 'POST'])
@login_required
def room_availability(studio_id, room_id):
    studio, room, uid = _require_room_in_studio(studio_id, room_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    if request.method == 'POST':
        weekly = parse_weekly_availability_form(request.form)
        replace_weekly_availability(room_id, weekly)
        flash('Disponibilidade salva.', 'success')
        return redirect(url_for('studios.room_availability', studio_id=studio_id, room_id=room_id))
    availability = list_room_availability(room_id)
    weekly_by_dow = {int(a['dia_semana']): a for a in availability if a.get('dia_semana') is not None}
    return render_template(
        'studios/owner/availability.html',
        studio=studio,
        room=room,
        weekday_labels=WEEKDAY_LABELS,
        weekly_by_dow=weekly_by_dow,
    )


@studios_bp.route('/<studio_id>/salas/<room_id>/bloqueios', methods=['GET', 'POST'])
@login_required
def room_blocks(studio_id, room_id):
    studio, room, uid = _require_room_in_studio(studio_id, room_id)
    if not studio:
        flash('Sem acesso.', 'danger')
        return redirect(url_for('studios.search'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            delete_room_block(request.form.get('block_id', ''))
            flash('Bloqueio removido.', 'success')
        else:
            data = parse_block_form(request.form)
            if not data:
                flash('Preencha data e horários.', 'danger')
            else:
                add_room_block(room_id, **data)
                flash('Bloqueio adicionado.', 'success')
        return redirect(url_for('studios.room_blocks', studio_id=studio_id, room_id=room_id))
    blocks = list_room_blocks(room_id)
    return render_template(
        'studios/owner/blocks.html',
        studio=studio,
        room=room,
        blocks=blocks,
    )


# ── Fotos ─────────────────────────────────────────────────────────────────

@studios_bp.route('/<studio_id>/fotos', methods=['POST'])
@login_required
def upload_studio_photo(studio_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        abort(403)
    if count_studio_photos(studio_id) >= MAX_STUDIO_PHOTOS:
        flash(f'Máximo de {MAX_STUDIO_PHOTOS} fotos.', 'warning')
        return redirect(url_for('studios.edit_studio', studio_id=studio_id))
    f = request.files.get('foto')
    filename, err = save_studio_photo_upload(studio_id, f)
    if err:
        flash(err, 'danger')
    else:
        add_studio_photo(studio_id, filename, count_studio_photos(studio_id))
        flash('Foto enviada.', 'success')
    return redirect(url_for('studios.edit_studio', studio_id=studio_id))


@studios_bp.route('/<studio_id>/fotos/<photo_id>/excluir', methods=['POST'])
@login_required
def delete_studio_photo_route(studio_id, photo_id):
    studio, uid = _require_studio_owner(studio_id)
    if not studio:
        abort(403)
    row = delete_studio_photo(photo_id)
    if row:
        delete_studio_photo_file(studio_id, row['filename'])
    return redirect(url_for('studios.edit_studio', studio_id=studio_id))


@studios_bp.route('/<studio_id>/fotos/arquivo/<filename>')
@login_required
def serve_studio_photo(studio_id, filename):
    path = studio_photo_path(studio_id, filename)
    if not path:
        abort(404)
    return send_file(path, mimetype=photo_mimetype(filename))


@studios_bp.route('/<studio_id>/salas/<room_id>/fotos', methods=['POST'])
@login_required
def upload_room_photo(studio_id, room_id):
    studio, room, uid = _require_room_in_studio(studio_id, room_id)
    if not studio:
        abort(403)
    if count_room_photos(room_id) >= MAX_ROOM_PHOTOS:
        flash(f'Máximo de {MAX_ROOM_PHOTOS} fotos por sala.', 'warning')
        return redirect(url_for('studios.edit_room', studio_id=studio_id, room_id=room_id))
    f = request.files.get('foto')
    filename, err = save_room_photo_upload(room_id, f)
    if err:
        flash(err, 'danger')
    else:
        add_room_photo(room_id, filename, count_room_photos(room_id))
        flash('Foto enviada.', 'success')
    return redirect(url_for('studios.edit_room', studio_id=studio_id, room_id=room_id))


@studios_bp.route('/salas/fotos/arquivo/<room_id>/<filename>')
@login_required
def serve_room_photo(room_id, filename):
    path = room_photo_path(room_id, filename)
    if not path:
        abort(404)
    return send_file(path, mimetype=photo_mimetype(filename))


# ── API slots ─────────────────────────────────────────────────────────────

@studios_bp.route('/api/salas/<room_id>/slots')
@login_required
def api_room_slots(room_id):
    date_iso = (request.args.get('data') or '').strip()
    if not date_iso:
        return jsonify({'ok': False, 'error': 'Informe data=YYYY-MM-DD'}), 400
    room, studio = get_room_with_studio(room_id)
    if not room or not studio or not studio.get('ativo'):
        return jsonify({'ok': False, 'error': 'Sala não encontrada'}), 404
    slots = _slots_for_room_date(room_id, date_iso)
    return jsonify({'ok': True, 'slots': available_slots_to_api(slots)})


@studios_bp.route('/<studio_id>/salas/<room_id>/horarios')
@login_required
def room_slots_page(studio_id, room_id):
    return api_room_slots(room_id)


# ── Reserva (banda) ───────────────────────────────────────────────────────

@studios_bp.route('/<studio_id>/salas/<room_id>/reservar', methods=['GET', 'POST'])
@login_required
def book_room(studio_id, room_id):
    studio = get_studio(studio_id)
    room = get_room(room_id)
    if not studio or not room or not studio.get('ativo') or not room.get('ativa'):
        flash('Sala não disponível.', 'danger')
        return redirect(url_for('studios.search'))
    user_bands = [b for b in get_user_bands(_user_id()) if is_band_member(b['id'], _user_id())]
    if request.method == 'POST':
        data = parse_booking_form(request.form)
        if not data:
            flash('Preencha banda, data e horário.', 'danger')
        elif not is_band_member(data['band_id'], _user_id()):
            flash('Você não é membro dessa banda.', 'danger')
        else:
            target = parse_booking_date(data['data'])
            if not target:
                flash('Data inválida.', 'danger')
            else:
                avail, bookings, blocks = _scheduling_context(room_id, target)
                ok, msg = validate_booking_request(
                    availability_rows=avail,
                    bookings=bookings,
                    blocks=blocks,
                    target=target,
                    start=data['hora_inicio'],
                    end=data['hora_fim'],
                )
                if not ok:
                    flash(msg, 'danger')
                else:
                    booking_id = create_booking(
                        room_id,
                        data['band_id'],
                        _user_id(),
                        data=data['data'],
                        hora_inicio=data['hora_inicio'],
                        hora_fim=data['hora_fim'],
                        observacao=data.get('observacao'),
                    )
                    booking = get_booking(booking_id)
                    band = get_band(data['band_id'])
                    sn.booking_requested(booking, studio, room, band)
                    flash('Solicitação enviada! Aguarde a confirmação do estúdio.', 'success')
                    return redirect(url_for('studios.detail', studio_id=studio_id))
    selected_date = request.args.get('data', '')
    slots = _slots_for_room_date(room_id, selected_date) if selected_date else []
    return render_template(
        'studios/book.html',
        studio=studio,
        room=room,
        user_bands=user_bands,
        selected_date=selected_date,
        slots=slots,
        full_address=studio_full_address(studio),
    )


# ── Ações de agendamento ──────────────────────────────────────────────────

@studios_bp.route('/agendamentos/<booking_id>/confirmar', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    booking = get_booking_enriched(booking_id)
    if not booking:
        flash('Agendamento não encontrado.', 'danger')
        return redirect(url_for('studios.search'))
    studio = booking.get('studio')
    room = booking.get('room')
    if not studio or studio.get('owner_user_id') != _user_id():
        flash('Sem permissão.', 'danger')
        return redirect(url_for('studios.search'))
    if booking.get('status') != BOOKING_PENDENTE:
        flash('Este agendamento já foi respondido.', 'warning')
        return redirect(url_for('studios.owner_dashboard', studio_id=studio['id']))
    target = parse_booking_date(booking['data'])
    avail, bookings, blocks = _scheduling_context(room['id'], target)
    ok, msg = validate_booking_request(
        availability_rows=avail,
        bookings=bookings,
        blocks=blocks,
        target=target,
        start=booking['hora_inicio'],
        end=booking['hora_fim'],
        exclude_booking_id=booking_id,
    )
    if not ok:
        flash(msg, 'danger')
        update_booking_status(booking_id, BOOKING_RECUSADO)
        return redirect(url_for('studios.owner_dashboard', studio_id=studio['id']))
    starts_at, ends_at = booking_datetime_range(
        booking['data'], booking['hora_inicio'], booking['hora_fim'],
    )
    setlist_id = request.form.get('setlist_id')
    setlist_id_int = int(setlist_id) if setlist_id and str(setlist_id).isdigit() else None
    title = f'Ensaio — {studio["nome"]} / {room["nome"]}'
    event_id = create_band_event(
        booking['band_id'],
        title=title,
        event_type=EVENT_ENSAIO,
        starts_at=starts_at,
        ends_at=ends_at,
        location=studio_full_address(studio),
        notes=booking.get('observacao'),
        setlist_id=setlist_id_int,
        created_by=_user_id(),
        studio_booking_id=booking_id,
    )
    update_booking_status(booking_id, BOOKING_CONFIRMADO, band_event_id=event_id)
    from product_funnel import log_funnel_step
    log_funnel_step(studio.get('owner_user_id'), 'estudio_reserva_confirmada', meta={'booking_id': booking_id})
    booking['band_event_id'] = event_id
    band = get_band(booking['band_id'])
    sn.booking_confirmed(booking, studio, room, band)
    flash('Agendamento confirmado e adicionado à agenda da banda.', 'success')
    return redirect(url_for('studios.owner_dashboard', studio_id=studio['id']))


@studios_bp.route('/agendamentos/<booking_id>/recusar', methods=['POST'])
@login_required
def reject_booking(booking_id):
    booking = get_booking_enriched(booking_id)
    if not booking:
        flash('Agendamento não encontrado.', 'danger')
        return redirect(url_for('studios.search'))
    studio = booking.get('studio')
    room = booking.get('room')
    if not studio or studio.get('owner_user_id') != _user_id():
        flash('Sem permissão.', 'danger')
        return redirect(url_for('studios.search'))
    if booking.get('status') != BOOKING_PENDENTE:
        flash('Este agendamento já foi respondido.', 'warning')
    else:
        update_booking_status(booking_id, BOOKING_RECUSADO)
        sn.booking_rejected(booking, studio, room)
        flash('Agendamento recusado.', 'info')
    return redirect(url_for('studios.owner_dashboard', studio_id=studio['id']))


@studios_bp.route('/agendamentos/<booking_id>/cancelar', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = get_booking_enriched(booking_id)
    if not booking:
        flash('Agendamento não encontrado.', 'danger')
        return redirect(url_for('studios.search'))
    studio = booking.get('studio')
    room = booking.get('room')
    uid = _user_id()
    is_owner = studio and studio.get('owner_user_id') == uid
    is_band = is_band_member(booking['band_id'], uid)
    if not is_owner and not is_band:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('studios.search'))
    status = booking.get('status')
    if status == BOOKING_CANCELADO:
        flash('Já cancelado.', 'info')
    elif status == BOOKING_CONFIRMADO:
        if booking.get('band_event_id'):
            delete_band_event(booking['band_event_id'])
        update_booking_status(booking_id, BOOKING_CANCELADO)
        band = get_band(booking['band_id'])
        sn.booking_cancelled(booking, studio, room, band, by_user_id=uid)
        flash('Agendamento cancelado.', 'success')
    elif status == BOOKING_PENDENTE:
        update_booking_status(booking_id, BOOKING_CANCELADO)
        flash('Solicitação cancelada.', 'success')
    else:
        flash('Não é possível cancelar este agendamento.', 'warning')
    if is_owner and studio:
        return redirect(url_for('studios.owner_dashboard', studio_id=studio['id']))
    return redirect(url_for('studios.my_bookings'))


@studios_bp.route('/minhas-reservas')
@login_required
def my_bookings():
    bands = get_user_bands(_user_id())
    all_bookings = []
    for b in bands:
        all_bookings.extend(list_bookings_for_band(b['id']))
    all_bookings.sort(key=lambda x: (x.get('data', ''), x.get('hora_inicio', '')), reverse=True)
    return render_template('studios/my_bookings.html', bookings=all_bookings)
