"""Progresso de onboarding e ativação pós-cadastro."""

from __future__ import annotations

from db import (
    count_band_cifras,
    count_band_setlists,
    get_owned_bands,
    get_user_bands,
    user_agenda_event_used,
    user_onboarding_checklist_dismissed,
    user_play_mode_used,
)
from flask import url_for


def get_onboarding_progress(user_id: str) -> dict | None:
    """Checklist de ativação para o dashboard. None se oculto ou concluído."""
    if user_onboarding_checklist_dismissed(user_id):
        return None

    owned = get_owned_bands(user_id)
    member_bands = get_owned_bands(user_id) or get_user_bands(user_id)
    bands = owned or member_bands

    has_band = bool(bands)
    total_cifras = sum(count_band_cifras(b['id']) for b in bands) if bands else 0
    total_setlists = sum(count_band_setlists(b['id']) for b in bands) if bands else 0

    first_band_id = bands[0]['id'] if bands else None
    first_cifra_id = None
    if first_band_id and total_cifras:
        from db import get_band_cifras

        rows = get_band_cifras(first_band_id)
        if rows:
            first_cifra_id = rows[0]['id']

    steps = [
        {
            'id': 'band',
            'label': 'Criar sua primeira banda',
            'done': has_band,
            'url': url_for('bands.view', band_id=first_band_id) if has_band else url_for('bands.create'),
        },
        {
            'id': 'cifra',
            'label': 'Adicionar ou importar uma música',
            'done': total_cifras > 0,
            'url': (
                url_for('cifras.add', band_id=first_band_id)
                if first_band_id
                else url_for('bands.create')
            ),
        },
        {
            'id': 'setlist',
            'label': 'Montar uma setlist',
            'done': total_setlists > 0,
            'url': (
                url_for('setlists.create', band_id=first_band_id)
                if first_band_id
                else url_for('bands.create')
            ),
        },
        {
            'id': 'tocar',
            'label': 'Testar o Modo Tocar',
            'done': user_play_mode_used(user_id),
            'url': (
                url_for('cifras.tocar_band', band_id=first_band_id, start=first_cifra_id)
                if first_band_id and first_cifra_id
                else (
                    url_for('cifras.tocar_band', band_id=first_band_id)
                    if first_band_id and total_cifras
                    else (url_for('cifras.add', band_id=first_band_id) if first_band_id else url_for('bands.create'))
                )
            ),
        },
        {
            'id': 'agenda',
            'label': 'Criar um evento na agenda',
            'done': user_agenda_event_used(user_id),
            'url': (
                url_for('agenda.create', band_id=first_band_id)
                if first_band_id
                else url_for('bands.create')
            ),
        },
    ]

    done_count = sum(1 for s in steps if s['done'])
    if done_count == len(steps):
        return None

    return {
        'steps': steps,
        'done_count': done_count,
        'total': len(steps),
        'percent': round(100 * done_count / len(steps)) if steps else 0,
        'complete': False,
        'activated': has_band and total_cifras > 0,
    }
