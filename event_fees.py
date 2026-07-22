"""Fechamento de cachê — divisão igual OU liquidação de fim de noite.

Fluxo de liquidação (FinTech ao vivo):
  1. Casa paga um valor bruto ao líder
  2. Subtrai despesas da noite (combustível, pedágio, alimentação…)
  3. Paga taxa fixa a sidemen / substitutos / convidados
  4. Divide o restante entre os fundadores
"""

from __future__ import annotations

from typing import Any


def _money(v: Any) -> float:
    try:
        return max(0.0, float(v or 0))
    except (TypeError, ValueError):
        return 0.0


def _round2(v: float) -> float:
    return round(float(v), 2)


def compute_event_fee_split(
    event: dict,
    assignments: list[dict],
    band_members: list[dict],
    *,
    name_for_user,
    guests: list[dict] | None = None,
    event_expenses: list[dict] | None = None,
    fee_lines: list[dict] | None = None,
) -> dict:
    """Calcula divisão do cachê — usa liquidação de noite quando há dados extras."""
    if fee_lines or event_expenses or guests or _has_sideman_config(band_members):
        return compute_night_settlement(
            event,
            assignments,
            band_members,
            guests=guests or [],
            event_expenses=event_expenses or [],
            fee_lines=fee_lines,
            name_for_user=name_for_user,
        )
    return _legacy_equal_split(event, assignments, band_members, name_for_user=name_for_user)


def _has_sideman_config(band_members: list[dict]) -> bool:
    for m in band_members:
        role = (m.get('settlement_role') or 'founder').strip().lower()
        if role == 'sideman' or _money(m.get('default_fixed_fee')) > 0:
            return True
    return False


def _legacy_equal_split(
    event: dict,
    assignments: list[dict],
    band_members: list[dict],
    *,
    name_for_user,
) -> dict:
    """Divisão igual entre confirmados (comportamento histórico)."""
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
                'guest_id': None,
                'name': name_for_user(a),
                'role_label': a.get('role_label') or '',
                'kind': 'share',
            })
    else:
        for m in band_members:
            uid = m.get('user_id')
            if not uid:
                continue
            payees.append({
                'user_id': uid,
                'guest_id': None,
                'name': name_for_user(m),
                'role_label': m.get('role') or '',
                'kind': 'share',
            })

    count = len(payees)
    if count == 0:
        return {
            'mode': 'equal',
            'total': total,
            'transport_discount': transport,
            'equipment_discount': equipment,
            'night_expenses': 0.0,
            'fixed_total': 0.0,
            'expenses_detail': [],
            'net': net,
            'pool': net,
            'share': 0.0,
            'payees': [],
            'fixed_payees': [],
            'founder_payees': [],
            'warning': 'Nenhum integrante confirmado para dividir o cachê.',
        }

    share = _round2(net / count)
    remainder = _round2(net - share * count)
    splits = []
    for i, p in enumerate(payees):
        amount = share + (remainder if i == 0 else 0.0)
        splits.append({**p, 'amount': _round2(amount)})

    return {
        'mode': 'equal',
        'total': total,
        'transport_discount': transport,
        'equipment_discount': equipment,
        'night_expenses': 0.0,
        'fixed_total': 0.0,
        'expenses_detail': [],
        'net': net,
        'pool': net,
        'share': share,
        'payees': splits,
        'fixed_payees': [],
        'founder_payees': splits,
        'warning': None,
    }


def compute_night_settlement(
    event: dict,
    assignments: list[dict],
    band_members: list[dict],
    *,
    guests: list[dict],
    event_expenses: list[dict],
    fee_lines: list[dict] | None,
    name_for_user,
) -> dict:
    """Liquidação: bruto − despesas − taxas fixas → split entre fundadores."""
    total = _money(event.get('fee_total'))
    transport = _money(event.get('fee_transport_discount'))
    equipment = _money(event.get('fee_equipment_discount'))
    expenses_detail = [
        {
            'id': e.get('id'),
            'descricao': e.get('descricao') or 'Despesa',
            'valor': _round2(_money(e.get('valor'))),
            'categoria': e.get('categoria') or 'outros',
        }
        for e in (event_expenses or [])
        if _money(e.get('valor')) > 0
    ]
    night_expenses = _round2(sum(e['valor'] for e in expenses_detail))

    # Snapshot já fechado
    if fee_lines:
        fixed_payees = []
        founder_payees = []
        for line in fee_lines:
            item = {
                'user_id': line.get('user_id'),
                'guest_id': line.get('guest_id'),
                'name': line.get('display_name') or '—',
                'role_label': line.get('kind') or '',
                'kind': line.get('kind') or 'share',
                'amount': _round2(_money(line.get('amount'))),
            }
            if item['kind'] == 'fixed':
                fixed_payees.append(item)
            else:
                founder_payees.append(item)
        fixed_total = _round2(sum(p['amount'] for p in fixed_payees))
        pool = _round2(sum(p['amount'] for p in founder_payees))
        net = _round2(max(0.0, total - transport - equipment - night_expenses))
        return {
            'mode': 'night',
            'total': total,
            'transport_discount': transport,
            'equipment_discount': equipment,
            'night_expenses': night_expenses,
            'fixed_total': fixed_total,
            'expenses_detail': expenses_detail,
            'net': net,
            'pool': pool,
            'share': founder_payees[0]['amount'] if len(founder_payees) == 1 else (
                _round2(pool / len(founder_payees)) if founder_payees else 0.0
            ),
            'payees': fixed_payees + founder_payees,
            'fixed_payees': fixed_payees,
            'founder_payees': founder_payees,
            'warning': None if (fixed_payees or founder_payees) else (
                'Ninguém na liquidação deste show.'
            ),
            'from_snapshot': True,
        }

    members_by_id = {str(m.get('user_id')): m for m in band_members if m.get('user_id')}
    accepted_ids: set[str] = set()
    if assignments:
        for a in assignments:
            if (a.get('response_status') or 'pending') == 'accepted' and a.get('user_id'):
                accepted_ids.add(str(a['user_id']))
    else:
        accepted_ids = set(members_by_id.keys())

    fixed_payees: list[dict] = []
    founder_candidates: list[dict] = []

    for uid in sorted(accepted_ids):
        m = members_by_id.get(uid) or {}
        # Prefer assignment row for display name
        a_row = next((a for a in assignments if str(a.get('user_id')) == uid), None)
        name = name_for_user(a_row or m)
        role = (m.get('settlement_role') or 'founder').strip().lower()
        default_fee = _money(m.get('default_fixed_fee'))
        if role == 'sideman' or default_fee > 0:
            fixed_payees.append({
                'user_id': uid,
                'guest_id': None,
                'name': name,
                'role_label': 'Sideman / taxa fixa',
                'kind': 'fixed',
                'amount': _round2(default_fee),
            })
        else:
            founder_candidates.append({
                'user_id': uid,
                'guest_id': None,
                'name': name,
                'role_label': a_row.get('role_label') if a_row else (m.get('role') or 'Fundador'),
                'kind': 'share',
            })

    for g in guests or []:
        fee = _money(g.get('fixed_fee'))
        if fee <= 0:
            continue
        fixed_payees.append({
            'user_id': None,
            'guest_id': g.get('id'),
            'name': g.get('name') or 'Convidado',
            'role_label': g.get('role_label') or 'Convidado',
            'kind': 'fixed',
            'amount': _round2(fee),
        })

    # Se ninguém marcado como fundador mas há confirmados sem taxa, todos dividem
    if not founder_candidates and not fixed_payees and accepted_ids:
        for uid in sorted(accepted_ids):
            m = members_by_id.get(uid) or {}
            a_row = next((a for a in assignments if str(a.get('user_id')) == uid), None)
            founder_candidates.append({
                'user_id': uid,
                'guest_id': None,
                'name': name_for_user(a_row or m),
                'role_label': (a_row or {}).get('role_label') or m.get('role') or '',
                'kind': 'share',
            })

    fixed_total = _round2(sum(p['amount'] for p in fixed_payees))
    net = _round2(max(0.0, total - transport - equipment - night_expenses))
    pool = _round2(max(0.0, net - fixed_total))

    founder_payees: list[dict] = []
    count = len(founder_candidates)
    if count:
        share = _round2(pool / count)
        remainder = _round2(pool - share * count)
        for i, p in enumerate(founder_candidates):
            amount = share + (remainder if i == 0 else 0.0)
            founder_payees.append({**p, 'amount': _round2(amount)})
        share_out = share
    else:
        share_out = 0.0

    warning = None
    if total > 0 and not fixed_payees and not founder_payees:
        warning = 'Ninguém na liquidação — confirme a escala ou marque fundadores/sidemen.'
    elif pool < 0.01 and fixed_total > net and total > 0:
        warning = 'Taxas fixas superam o líquido após despesas — revise os valores.'

    return {
        'mode': 'night',
        'total': total,
        'transport_discount': transport,
        'equipment_discount': equipment,
        'night_expenses': night_expenses,
        'fixed_total': fixed_total,
        'expenses_detail': expenses_detail,
        'net': net,
        'pool': pool,
        'share': share_out,
        'payees': fixed_payees + founder_payees,
        'fixed_payees': fixed_payees,
        'founder_payees': founder_payees,
        'warning': warning,
        'from_snapshot': False,
    }
