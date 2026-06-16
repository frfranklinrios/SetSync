"""Convites de banda — aceitar ou recusar entrada."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, flash, redirect, render_template, session, url_for

import band_notifications as bn
from band_member_invites import (
    accept_band_member_invite,
    decline_band_member_invite,
    inviter_display_name,
    list_pending_invites_for_user,
)
from blueprints.auth import login_required
from monetizacao import LIMITES_GRATIS, resposta_limite_plano

convites_bp = Blueprint('convites', __name__, url_prefix='/convites')


@convites_bp.route('/')
@login_required
def index():
    invites = list_pending_invites_for_user(session['user_id'])
    return render_template(
        'convites/index.html',
        invites=invites,
        inviter_display_name=inviter_display_name,
    )


@convites_bp.route('/<invite_id>/aceitar', methods=['POST'])
@login_required
def aceitar(invite_id):
    user_id = session['user_id']
    ok, code = accept_band_member_invite(invite_id, user_id)
    if not ok:
        if code == 'limit':
            resp = resposta_limite_plano('integrantes', LIMITES_GRATIS['integrante'])
            if resp:
                return resp
        flash('Convite inválido ou já respondido.', 'warning')
        return redirect(url_for('convites.index'))

    from band_member_invites import get_band_member_invite

    inv = get_band_member_invite(invite_id)
    if inv:
        bn.member_accepted_invite(inv['band_id'], inv.get('invited_by'), user_id)
        flash(f'Você entrou na banda {inv["band_name"]}!', 'success')
        return redirect(url_for('bands.view', band_id=inv['band_id']))

    flash('Convite aceito.', 'success')
    return redirect(url_for('dashboard'))


@convites_bp.route('/<invite_id>/recusar', methods=['POST'])
@login_required
def recusar(invite_id):
    user_id = session['user_id']
    from band_member_invites import get_band_member_invite

    inv = get_band_member_invite(invite_id)
    if inv and decline_band_member_invite(invite_id, user_id):
        bn.band_invite_declined(inv['band_id'], inv.get('invited_by'), user_id)
        flash('Convite recusado.', 'info')
    else:
        flash('Convite inválido ou já respondido.', 'warning')
    return redirect(url_for('convites.index'))
