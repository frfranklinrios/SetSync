"""Regras de disponibilidade e conflito de horários — estúdios de ensaio."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

BOOKING_PENDENTE = 'pendente'
BOOKING_CONFIRMADO = 'confirmado'
BOOKING_CANCELADO = 'cancelado'
BOOKING_RECUSADO = 'recusado'
BOOKING_ACTIVE_STATUSES = (BOOKING_PENDENTE, BOOKING_CONFIRMADO)


def parse_time_hhmm(value: str) -> time | None:
    if not value:
        return None
    value = str(value).strip()[:5]
    try:
        parts = value.split(':')
        if len(parts) != 2:
            return None
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return time(h, m)
    except (ValueError, TypeError):
        return None
    return None


def time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def minutes_to_hhmm(minutes: int) -> str:
    minutes = max(0, min(24 * 60 - 1, minutes))
    return f'{minutes // 60:02d}:{minutes % 60:02d}'


def intervals_overlap(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    """Intervalos [inicio, fim) — adjacentes não conflitam."""
    ta0, ta1 = parse_time_hhmm(a_start), parse_time_hhmm(a_end)
    tb0, tb1 = parse_time_hhmm(b_start), parse_time_hhmm(b_end)
    if not all((ta0, ta1, tb0, tb1)):
        return True
    ma0, ma1 = time_to_minutes(ta0), time_to_minutes(ta1)
    mb0, mb1 = time_to_minutes(tb0), time_to_minutes(tb1)
    if ma1 <= ma0 or mb1 <= mb0:
        return True
    return ma0 < mb1 and mb0 < ma1


def _date_weekday(d: date) -> int:
    return d.weekday()


def _availability_windows_for_date(
    availability_rows: list[dict],
    target: date,
) -> list[tuple[str, str]]:
    iso = target.isoformat()
    weekday = _date_weekday(target)
    windows: list[tuple[str, str]] = []
    for row in availability_rows:
        spec = (row.get('data_especifica') or '').strip()
        dow = row.get('dia_semana')
        if spec:
            if spec != iso:
                continue
        elif dow is not None:
            if int(dow) != weekday:
                continue
        else:
            continue
        hi, hf = row.get('hora_inicio'), row.get('hora_fim')
        if hi and hf and parse_time_hhmm(hi) and parse_time_hhmm(hf):
            windows.append((hi[:5], hf[:5]))
    return windows


def slot_within_windows(start: str, end: str, windows: list[tuple[str, str]]) -> bool:
    ts, te = parse_time_hhmm(start), parse_time_hhmm(end)
    if not ts or not te or time_to_minutes(te) <= time_to_minutes(ts):
        return False
    ms, me = time_to_minutes(ts), time_to_minutes(te)
    for w0, w1 in windows:
        wt0, wt1 = parse_time_hhmm(w0), parse_time_hhmm(w1)
        if not wt0 or not wt1:
            continue
        if ms >= time_to_minutes(wt0) and me <= time_to_minutes(wt1):
            return True
    return False


def slot_within_availability(
    availability_rows: list[dict],
    target: date,
    start: str,
    end: str,
) -> bool:
    windows = _availability_windows_for_date(availability_rows, target)
    if not windows:
        return False
    return slot_within_windows(start, end, windows)


def list_conflicts(
    *,
    bookings: list[dict],
    blocks: list[dict],
    date_iso: str,
    start: str,
    end: str,
    exclude_booking_id: str | None = None,
    count_pending: bool = False,
) -> list[dict]:
    conflicts: list[dict] = []
    for b in bookings:
        if b.get('data') != date_iso:
            continue
        if exclude_booking_id and str(b.get('id')) == str(exclude_booking_id):
            continue
        status = b.get('status') or ''
        if status == BOOKING_CONFIRMADO or (count_pending and status == BOOKING_PENDENTE):
            if intervals_overlap(start, end, b.get('hora_inicio', ''), b.get('hora_fim', '')):
                conflicts.append({'type': 'booking', 'id': b.get('id'), 'status': status})
    for bl in blocks:
        if bl.get('data') != date_iso:
            continue
        if intervals_overlap(start, end, bl.get('hora_inicio', ''), bl.get('hora_fim', '')):
            conflicts.append({'type': 'block', 'id': bl.get('id'), 'motivo': bl.get('motivo')})
    return conflicts


def _merge_minutes_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    ranges = sorted(ranges)
    merged = [ranges[0]]
    for start, end in ranges[1:]:
        last_s, last_e = merged[-1]
        if start <= last_e:
            merged[-1] = (last_s, max(last_e, end))
        else:
            merged.append((start, end))
    return merged


def get_available_slots(
    *,
    availability_rows: list[dict],
    bookings: list[dict],
    blocks: list[dict],
    target: date,
    slot_minutes: int = 60,
) -> list[dict[str, str]]:
    windows = _availability_windows_for_date(availability_rows, target)
    if not windows:
        return []
    iso = target.isoformat()
    free_ranges: list[tuple[int, int]] = []
    for w0, w1 in windows:
        t0, t1 = parse_time_hhmm(w0), parse_time_hhmm(w1)
        if t0 and t1 and time_to_minutes(t1) > time_to_minutes(t0):
            free_ranges.append((time_to_minutes(t0), time_to_minutes(t1)))
    free_ranges = _merge_minutes_ranges(free_ranges)

    occupied: list[tuple[int, int]] = []
    for b in bookings:
        if b.get('data') != iso or b.get('status') != BOOKING_CONFIRMADO:
            continue
        t0, t1 = parse_time_hhmm(b.get('hora_inicio', '')), parse_time_hhmm(b.get('hora_fim', ''))
        if t0 and t1:
            occupied.append((time_to_minutes(t0), time_to_minutes(t1)))
    for bl in blocks:
        if bl.get('data') != iso:
            continue
        t0, t1 = parse_time_hhmm(bl.get('hora_inicio', '')), parse_time_hhmm(bl.get('hora_fim', ''))
        if t0 and t1:
            occupied.append((time_to_minutes(t0), time_to_minutes(t1)))
    occupied = _merge_minutes_ranges(occupied)

    slots: list[dict[str, str]] = []
    for range_start, range_end in free_ranges:
        cursor = range_start
        while cursor + slot_minutes <= range_end:
            slot_end = cursor + slot_minutes
            blocked = False
            for o0, o1 in occupied:
                if cursor < o1 and o0 < slot_end:
                    blocked = True
                    break
            if not blocked:
                slots.append({
                    'inicio': minutes_to_hhmm(cursor),
                    'fim': minutes_to_hhmm(slot_end),
                })
            cursor += slot_minutes
    return slots


def validate_booking_request(
    *,
    availability_rows: list[dict],
    bookings: list[dict],
    blocks: list[dict],
    target: date,
    start: str,
    end: str,
    exclude_booking_id: str | None = None,
) -> tuple[bool, str]:
    if not slot_within_availability(availability_rows, target, start, end):
        return False, 'Horário fora da disponibilidade do estúdio.'
    iso = target.isoformat()
    conflicts = list_conflicts(
        bookings=bookings,
        blocks=blocks,
        date_iso=iso,
        start=start,
        end=end,
        exclude_booking_id=exclude_booking_id,
    )
    if conflicts:
        return False, 'Horário indisponível (conflito com reserva ou bloqueio).'
    return True, ''


def booking_datetime_range(data_iso: str, start: str, end: str) -> tuple[str, str]:
    """Retorna starts_at/ends_at para band_events."""
    d = (data_iso or '')[:10]
    return f'{d} {start[:5]}:00', f'{d} {end[:5]}:00'


def parse_booking_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip()[:10], '%Y-%m-%d').date()
    except ValueError:
        return None
