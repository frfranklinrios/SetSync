"""Estúdios de ensaio — cadastro, salas, disponibilidade e agendamentos."""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from database import IS_POSTGRES
from db import get_db
from studio_scheduling import (
    BOOKING_CANCELADO,
    BOOKING_CONFIRMADO,
    BOOKING_PENDENTE,
    BOOKING_RECUSADO,
)
from config import app_now_naive, app_now_str

PLANO_ESTUDIO_BASICO = 'estudio_basico'
PLANO_ESTUDIO_PREMIUM = 'estudio_premium'


def _row_dict(row) -> dict | None:
    return dict(row) if row else None


def _rows(rows) -> list[dict]:
    return [dict(r) for r in rows]


# ── Assinatura estúdio (beta) ─────────────────────────────────────────────

def get_studio_subscription(user_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studio_subscriptions WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    db.close()
    return _row_dict(row)


def get_or_create_studio_subscription(user_id: str) -> dict:
    existing = get_studio_subscription(user_id)
    if existing:
        return existing
    sub_id = str(uuid.uuid4())
    now = app_now_str()  # was strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO studio_subscriptions (id, user_id, plano, status, created_at)
           VALUES (?, ?, ?, 'ativa', ?)''',
        (sub_id, user_id, PLANO_ESTUDIO_BASICO, now),
    )
    db.commit()
    db.close()
    return {
        'id': sub_id,
        'user_id': user_id,
        'plano': PLANO_ESTUDIO_BASICO,
        'status': 'ativa',
        'created_at': now,
    }


def get_studio_subscription_by_mp_id(mp_id: str) -> dict | None:
    if not mp_id:
        return None
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM studio_subscriptions
           WHERE mp_subscription_id = ? OR mp_preapproval_id = ?''',
        (mp_id, mp_id),
    )
    row = c.fetchone()
    db.close()
    return _row_dict(row)


def update_studio_subscription(user_id: str, **kwargs) -> None:
    allowed = {
        'plano', 'status', 'mp_preapproval_id', 'mp_subscription_id', 'data_proxima_cobranca',
        'trial_inicio', 'trial_fim', 'trial_usado',
    }
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return
    get_or_create_studio_subscription(user_id)
    sets = ', '.join(f'{k} = ?' for k in fields)
    vals = list(fields.values()) + [user_id]
    db = get_db()
    c = db.cursor()
    c.execute(f'UPDATE studio_subscriptions SET {sets} WHERE user_id = ?', vals)
    db.commit()
    db.close()


def update_studio_subscription_trial(
    user_id: str,
    *,
    trial_inicio: str | None = None,
    trial_fim: str | None = None,
    trial_usado: int | None = None,
) -> None:
    fields = {}
    if trial_inicio is not None:
        fields['trial_inicio'] = trial_inicio
    if trial_fim is not None:
        fields['trial_fim'] = trial_fim
    if trial_usado is not None:
        fields['trial_usado'] = trial_usado
    if fields:
        update_studio_subscription(user_id, **fields)


def count_rooms_for_owner(owner_user_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT COUNT(*) AS n FROM studio_rooms r
           JOIN studios s ON s.id = r.studio_id
           WHERE s.owner_user_id = ? AND r.ativa = 1''',
        (owner_user_id,),
    )
    row = c.fetchone()
    db.close()
    return int(row['n'] if row else 0)


# ── Estúdios ──────────────────────────────────────────────────────────────

def create_studio(
    owner_user_id: str,
    *,
    nome: str,
    cidade: str,
    descricao: str | None = None,
    bairro: str | None = None,
    endereco: str | None = None,
    endereco_lat: float | None = None,
    endereco_lng: float | None = None,
    endereco_place_id: str | None = None,
    telefone: str | None = None,
    whatsapp: str | None = None,
    preco_hora: float | None = None,
) -> str:
    existing_count = len(list_studios_by_owner(owner_user_id))
    studio_id = str(uuid.uuid4())
    get_or_create_studio_subscription(owner_user_id)
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO studios
           (id, owner_user_id, nome, descricao, cidade, bairro, endereco,
            endereco_lat, endereco_lng, endereco_place_id,
            telefone, whatsapp, preco_hora, ativo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''',
        (
            studio_id, owner_user_id, nome, descricao, cidade, bairro, endereco,
            endereco_lat, endereco_lng, endereco_place_id,
            telefone, whatsapp, preco_hora,
        ),
    )
    db.commit()
    db.close()
    if existing_count == 0:
        from monetizacao import iniciar_trial_estudio
        iniciar_trial_estudio(owner_user_id)
    from studio_onboarding_emails import registrar_onboarding_estudio
    from product_funnel import log_funnel_step
    registrar_onboarding_estudio(owner_user_id, studio_id)
    log_funnel_step(owner_user_id, 'estudio_cadastrado')
    return studio_id


def get_studio(studio_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studios WHERE id = ?', (studio_id,))
    row = c.fetchone()
    db.close()
    return _row_dict(row)


def update_studio(studio_id: str, **fields) -> None:
    allowed = {
        'nome', 'descricao', 'cidade', 'bairro', 'endereco',
        'endereco_lat', 'endereco_lng', 'endereco_place_id',
        'telefone', 'whatsapp', 'preco_hora', 'ativo', 'onboarding_dismissed',
    }
    parts, vals = [], []
    for key, val in fields.items():
        if key in allowed:
            parts.append(f'{key} = ?')
            vals.append(val)
    if not parts:
        return
    vals.append(studio_id)
    db = get_db()
    c = db.cursor()
    c.execute(f'UPDATE studios SET {", ".join(parts)} WHERE id = ?', vals)
    db.commit()
    db.close()


def studio_profile_complete(studio: dict) -> bool:
    if not (studio.get('descricao') or '').strip():
        return False
    has_location = bool((studio.get('endereco') or '').strip()) or studio.get('endereco_lat') is not None
    has_contact = bool((studio.get('telefone') or '').strip()) or bool((studio.get('whatsapp') or '').strip())
    return has_location and has_contact


def studio_onboarding_dismissed(studio_id: str) -> bool:
    studio = get_studio(studio_id)
    return bool(studio and studio.get('onboarding_dismissed'))


def dismiss_studio_onboarding(studio_id: str) -> None:
    update_studio(studio_id, onboarding_dismissed=1)


def list_studios_by_owner(owner_user_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM studios WHERE owner_user_id = ? ORDER BY nome',
        (owner_user_id,),
    )
    rows = _rows(c.fetchall())
    db.close()
    return rows


def is_studio_primary_user(user_id: str) -> bool:
    """Dono de estúdio sem participação em nenhuma banda — home é o painel do estúdio."""
    from db import get_user_bands

    if not list_studios_by_owner(user_id):
        return False
    return len(get_user_bands(user_id)) == 0


def studio_primary_home_endpoint(user_id: str) -> tuple[str, dict] | None:
    """(endpoint Flask, kwargs) da home para conta estúdio, ou None."""
    if not is_studio_primary_user(user_id):
        return None
    studios = list_studios_by_owner(user_id)
    if len(studios) == 1:
        return 'studios.owner_dashboard', {'studio_id': studios[0]['id']}
    return 'studios.search', {}


def enrich_studios_for_dashboard(owner_user_id: str) -> list[dict]:
    out = []
    for s in list_studios_by_owner(owner_user_id):
        row = dict(s)
        row['pending_count'] = len(
            list_bookings_for_studio(s['id'], status=BOOKING_PENDENTE),
        )
        row['rooms_count'] = len(list_rooms(s['id'], active_only=False))
        out.append(row)
    return out


def list_all_studios() -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studios ORDER BY cidade, nome')
    rows = _rows(c.fetchall())
    db.close()
    return rows


def enrich_studios_for_admin(studios: list[dict]) -> list[dict]:
    from db import get_user
    from monetizacao import studio_plano_badge_ui

    out = []
    for s in studios:
        row = dict(s)
        owner = get_user(s.get('owner_user_id'))
        row['owner'] = owner or {}
        row['rooms_count'] = len(list_rooms(s['id'], active_only=False))
        row['pending_count'] = len(
            list_bookings_for_studio(s['id'], status=BOOKING_PENDENTE),
        )
        row['plano_ui'] = studio_plano_badge_ui(s['owner_user_id']) if s.get('owner_user_id') else None
        out.append(row)
    return out


def search_studios(*, cidade: str | None = None, bairro: str | None = None) -> list[dict]:
    db = get_db()
    c = db.cursor()
    sql = 'SELECT * FROM studios WHERE ativo = 1'
    params: list = []
    if cidade:
        sql += ' AND LOWER(cidade) LIKE ?'
        params.append(f'%{cidade.strip().lower()}%')
    if bairro:
        sql += ' AND LOWER(bairro) LIKE ?'
        params.append(f'%{bairro.strip().lower()}%')
    sql += ' ORDER BY cidade, bairro, nome'
    c.execute(sql, params)
    rows = _rows(c.fetchall())
    db.close()
    return rows


def studio_full_address(studio: dict | None) -> str:
    if not studio:
        return ''
    parts = [
        studio.get('endereco') or '',
        studio.get('bairro') or '',
        studio.get('cidade') or '',
    ]
    return ' — '.join(p for p in parts if p)


# ── Fotos (metadados) ─────────────────────────────────────────────────────

def add_studio_photo(studio_id: str, filename: str, sort_order: int = 0) -> str:
    photo_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        'INSERT INTO studio_photos (id, studio_id, filename, sort_order) VALUES (?, ?, ?, ?)',
        (photo_id, studio_id, filename, sort_order),
    )
    db.commit()
    db.close()
    return photo_id


def list_studio_photos(studio_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM studio_photos WHERE studio_id = ? ORDER BY sort_order, id',
        (studio_id,),
    )
    rows = _rows(c.fetchall())
    db.close()
    return rows


def delete_studio_photo(photo_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studio_photos WHERE id = ?', (photo_id,))
    row = c.fetchone()
    if row:
        c.execute('DELETE FROM studio_photos WHERE id = ?', (photo_id,))
        db.commit()
    db.close()
    return _row_dict(row)


def count_studio_photos(studio_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM studio_photos WHERE studio_id = ?', (studio_id,))
    row = c.fetchone()
    db.close()
    return int(row['n'] if row else 0)


def add_room_photo(room_id: str, filename: str, sort_order: int = 0) -> str:
    photo_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        'INSERT INTO studio_room_photos (id, room_id, filename, sort_order) VALUES (?, ?, ?, ?)',
        (photo_id, room_id, filename, sort_order),
    )
    db.commit()
    db.close()
    return photo_id


def list_room_photos(room_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT * FROM studio_room_photos WHERE room_id = ? ORDER BY sort_order, id',
        (room_id,),
    )
    rows = _rows(c.fetchall())
    db.close()
    return rows


def delete_room_photo(photo_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studio_room_photos WHERE id = ?', (photo_id,))
    row = c.fetchone()
    if row:
        c.execute('DELETE FROM studio_room_photos WHERE id = ?', (photo_id,))
        db.commit()
    db.close()
    return _row_dict(row)


def count_room_photos(room_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM studio_room_photos WHERE room_id = ?', (room_id,))
    row = c.fetchone()
    db.close()
    return int(row['n'] if row else 0)


# ── Salas ─────────────────────────────────────────────────────────────────

def create_room(
    studio_id: str,
    *,
    nome: str,
    capacidade_pessoas: int | None = None,
    equipamentos: list | None = None,
) -> str:
    room_id = str(uuid.uuid4())
    equip_json = json.dumps(equipamentos or [], ensure_ascii=False)
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO studio_rooms
           (id, studio_id, nome, capacidade_pessoas, equipamentos_json, ativa)
           VALUES (?, ?, ?, ?, ?, 1)''',
        (room_id, studio_id, nome, capacidade_pessoas, equip_json),
    )
    db.commit()
    db.close()
    return room_id


def get_room(room_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studio_rooms WHERE id = ?', (room_id,))
    row = c.fetchone()
    db.close()
    room = _row_dict(row)
    if room and room.get('equipamentos_json'):
        try:
            room['equipamentos'] = json.loads(room['equipamentos_json'])
        except (json.JSONDecodeError, TypeError):
            room['equipamentos'] = []
    elif room:
        room['equipamentos'] = []
    return room


def list_rooms(studio_id: str, *, active_only: bool = True) -> list[dict]:
    db = get_db()
    c = db.cursor()
    sql = 'SELECT * FROM studio_rooms WHERE studio_id = ?'
    if active_only:
        sql += ' AND ativa = 1'
    sql += ' ORDER BY nome'
    c.execute(sql, (studio_id,))
    rows = _rows(c.fetchall())
    db.close()
    for room in rows:
        try:
            room['equipamentos'] = json.loads(room.get('equipamentos_json') or '[]')
        except (json.JSONDecodeError, TypeError):
            room['equipamentos'] = []
    return rows


def update_room(room_id: str, **fields) -> None:
    allowed = {'nome', 'capacidade_pessoas', 'ativa'}
    parts, vals = [], []
    for key, val in fields.items():
        if key in allowed:
            parts.append(f'{key} = ?')
            vals.append(val)
    if 'equipamentos' in fields:
        parts.append('equipamentos_json = ?')
        vals.append(json.dumps(fields['equipamentos'] or [], ensure_ascii=False))
    if not parts:
        return
    vals.append(room_id)
    db = get_db()
    c = db.cursor()
    c.execute(f'UPDATE studio_rooms SET {", ".join(parts)} WHERE id = ?', vals)
    db.commit()
    db.close()


def get_room_with_studio(room_id: str) -> tuple[dict | None, dict | None]:
    room = get_room(room_id)
    if not room:
        return None, None
    studio = get_studio(room['studio_id'])
    return room, studio


# ── Disponibilidade ───────────────────────────────────────────────────────

def clear_room_availability(room_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM studio_room_availability WHERE room_id = ?', (room_id,))
    db.commit()
    db.close()


def add_room_availability(
    room_id: str,
    *,
    hora_inicio: str,
    hora_fim: str,
    dia_semana: int | None = None,
    data_especifica: str | None = None,
    recorrente: bool = True,
) -> str:
    avail_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO studio_room_availability
           (id, room_id, dia_semana, data_especifica, hora_inicio, hora_fim, recorrente)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            avail_id, room_id, dia_semana, data_especifica,
            hora_inicio[:5], hora_fim[:5], 1 if recorrente else 0,
        ),
    )
    db.commit()
    db.close()
    return avail_id


def list_room_availability(room_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM studio_room_availability WHERE room_id = ?
           ORDER BY COALESCE(dia_semana, 99), data_especifica, hora_inicio''',
        (room_id,),
    )
    rows = _rows(c.fetchall())
    db.close()
    return rows


def replace_weekly_availability(room_id: str, weekly_slots: list[dict]) -> None:
    """weekly_slots: [{dia_semana, hora_inicio, hora_fim}, ...]"""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''DELETE FROM studio_room_availability
           WHERE room_id = ? AND data_especifica IS NULL''',
        (room_id,),
    )
    for slot in weekly_slots:
        c.execute(
            '''INSERT INTO studio_room_availability
               (id, room_id, dia_semana, data_especifica, hora_inicio, hora_fim, recorrente)
               VALUES (?, ?, ?, NULL, ?, ?, 1)''',
            (
                str(uuid.uuid4()), room_id, int(slot['dia_semana']),
                slot['hora_inicio'][:5], slot['hora_fim'][:5],
            ),
        )
    db.commit()
    db.close()


# ── Bloqueios ─────────────────────────────────────────────────────────────

def add_room_block(
    room_id: str,
    *,
    data: str,
    hora_inicio: str,
    hora_fim: str,
    motivo: str | None = None,
) -> str:
    block_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO studio_room_blocks (id, room_id, data, hora_inicio, hora_fim, motivo)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (block_id, room_id, data[:10], hora_inicio[:5], hora_fim[:5], motivo),
    )
    db.commit()
    db.close()
    return block_id


def list_room_blocks(room_id: str, *, from_date: str | None = None) -> list[dict]:
    db = get_db()
    c = db.cursor()
    if from_date:
        c.execute(
            '''SELECT * FROM studio_room_blocks
               WHERE room_id = ? AND data >= ? ORDER BY data, hora_inicio''',
            (room_id, from_date[:10]),
        )
    else:
        c.execute(
            'SELECT * FROM studio_room_blocks WHERE room_id = ? ORDER BY data, hora_inicio',
            (room_id,),
        )
    rows = _rows(c.fetchall())
    db.close()
    return rows


def delete_room_block(block_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM studio_room_blocks WHERE id = ?', (block_id,))
    db.commit()
    db.close()


# ── Agendamentos ──────────────────────────────────────────────────────────

def create_booking(
    room_id: str,
    band_id: str,
    requested_by_user_id: str,
    *,
    data: str,
    hora_inicio: str,
    hora_fim: str,
    observacao: str | None = None,
) -> str:
    booking_id = str(uuid.uuid4())
    now = app_now_str()  # was strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO studio_bookings
           (id, room_id, band_id, requested_by_user_id, data, hora_inicio, hora_fim,
            status, observacao, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            booking_id, room_id, band_id, requested_by_user_id,
            data[:10], hora_inicio[:5], hora_fim[:5],
            BOOKING_PENDENTE, observacao, now,
        ),
    )
    db.commit()
    db.close()
    return booking_id


def get_booking(booking_id: str) -> dict | None:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM studio_bookings WHERE id = ?', (booking_id,))
    row = c.fetchone()
    db.close()
    return _row_dict(row)


def get_booking_enriched(booking_id: str) -> dict | None:
    booking = get_booking(booking_id)
    if not booking:
        return None
    room, studio = get_room_with_studio(booking['room_id'])
    booking['room'] = room
    booking['studio'] = studio
    return booking


def list_bookings_for_room(
    room_id: str,
    *,
    from_date: str | None = None,
    statuses: tuple[str, ...] | None = None,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    sql = 'SELECT * FROM studio_bookings WHERE room_id = ?'
    params: list = [room_id]
    if from_date:
        sql += ' AND data >= ?'
        params.append(from_date[:10])
    if statuses:
        placeholders = ','.join('?' * len(statuses))
        sql += f' AND status IN ({placeholders})'
        params.extend(statuses)
    sql += ' ORDER BY data, hora_inicio'
    c.execute(sql, params)
    rows = _rows(c.fetchall())
    db.close()
    return rows


def list_bookings_for_studio(
    studio_id: str,
    *,
    status: str | None = None,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    sql = '''
        SELECT b.*, r.nome AS room_nome, s.nome AS studio_nome, bd.name AS band_name
        FROM studio_bookings b
        JOIN studio_rooms r ON r.id = b.room_id
        JOIN studios s ON s.id = r.studio_id
        LEFT JOIN bands bd ON bd.id = b.band_id
        WHERE r.studio_id = ?
    '''
    params: list = [studio_id]
    if status:
        sql += ' AND b.status = ?'
        params.append(status)
    sql += ' ORDER BY b.created_at DESC'
    c.execute(sql, params)
    rows = _rows(c.fetchall())
    db.close()
    return rows


def list_bookings_for_band(band_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT b.*, r.nome AS room_nome, s.nome AS studio_nome, s.cidade, s.bairro
           FROM studio_bookings b
           JOIN studio_rooms r ON r.id = b.room_id
           JOIN studios s ON s.id = r.studio_id
           WHERE b.band_id = ?
           ORDER BY b.data DESC, b.hora_inicio DESC''',
        (band_id,),
    )
    rows = _rows(c.fetchall())
    db.close()
    return rows


def update_booking_status(
    booking_id: str,
    status: str,
    *,
    band_event_id: str | None = None,
) -> None:
    now = app_now_str()  # was strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    if band_event_id is not None:
        c.execute(
            '''UPDATE studio_bookings
               SET status = ?, band_event_id = ?, responded_at = ?
               WHERE id = ?''',
            (status, band_event_id, now, booking_id),
        )
    else:
        c.execute(
            'UPDATE studio_bookings SET status = ?, responded_at = ? WHERE id = ?',
            (status, now, booking_id),
        )
    db.commit()
    db.close()


def set_booking_band_event(booking_id: str, band_event_id: str | None) -> None:
    db = get_db()
    c = db.cursor()
    c.execute(
        'UPDATE studio_bookings SET band_event_id = ? WHERE id = ?',
        (band_event_id, booking_id),
    )
    db.commit()
    db.close()


def list_studio_calendar_bookings(studio_id: str, *, from_date: str | None = None) -> list[dict]:
    db = get_db()
    c = db.cursor()
    sql = '''
        SELECT b.*, r.nome AS room_nome
        FROM studio_bookings b
        JOIN studio_rooms r ON r.id = b.room_id
        WHERE r.studio_id = ? AND b.status IN (?, ?)
    '''
    params: list = [studio_id, BOOKING_PENDENTE, BOOKING_CONFIRMADO]
    if from_date:
        sql += ' AND b.data >= ?'
        params.append(from_date[:10])
    sql += ' ORDER BY b.data, b.hora_inicio'
    c.execute(sql, params)
    rows = _rows(c.fetchall())
    db.close()
    return rows