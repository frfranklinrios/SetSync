"""Fechamento de cachê por evento — divide entre confirmados na escalação."""

from __future__ import annotations

from typing import Any


def _money(v: Any) -> float:
    try:
        return max(0.0, float(v or 0))
    except (TypeError, ValueError):
        return 0.0


def compute_event_fee_split(
    event: dict,
    assignments: list[dict],
    band_members: list[dict],
    *,
    name_for_user,
) -> dict:
    """Calcula valor líquido e divisão igual entre confirmados."""
    total = _money(event.get('fee_total'))
    transport = _money(event.get('fee_transport_discount'))
    equipment = _money(event.get('fee_equipment_discount'))
    net = max(0.0, total - transport - equipment)

    payees: list[dict] = []
    if assignments:
        for a in assignments:
            if (a.get('response_status') or 'pending') != 'accepted':
                continue
            uid = a.get('user_id')
            if not uid:
                continue
            payees.append({
                'user_id': uid,
                'name': name_for_user(a),
                'role_label': a.get('role_label') or '',
            })
    else:
        for m in band_members:
            uid = m.get('user_id')
            if not uid:
                continue
            payees.append({
                'user_id': uid,
                'name': name_for_user(m),
                'role_label': m.get('role') or '',
            })

    count = len(payees)
    if count == 0:
        return {
            'total': total,
            'transport_discount': transport,
            'equipment_discount': equipment,
            'net': net,
            'share': 0.0,
            'payees': [],
            'warning': 'Nenhum integrante confirmado para dividir o cachê.',
        }

    share = round(net / count, 2)
    remainder = round(net - share * count, 2)
    splits = []
    for i, p in enumerate(payees):
        amount = share + (remainder if i == 0 else 0.0)
        splits.append({**p, 'amount': round(amount, 2)})

    return {
        'total': total,
        'transport_discount': transport,
        'equipment_discount': equipment,
        'net': net,
        'share': share,
        'payees': splits,
        'warning': None,
    }
