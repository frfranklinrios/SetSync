import functools
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, redirect, url_for, flash, session
from blueprints.auth import login_required
from db import (
    is_superadmin,
    get_all_bands,
    get_all_cifras,
    get_all_users,
    get_user,
    get_band_members,
    get_band_cifras,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def superadmin_required(f):
    @functools.wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not is_superadmin(session.get('user_id')):
            flash('Acesso restrito a administradores (configure SETSYNC_SUPERADMIN_* no .env).', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return wrapped


@admin_bp.route('/')
@superadmin_required
def index():
    bands = get_all_bands()
    cifras = get_all_cifras()
    users = get_all_users()

    for band in bands:
        owner = get_user(band['owner_id'])
        band['owner'] = owner or {}
        band['members_count'] = len(get_band_members(band['id']))
        band['cifras_count'] = len(get_band_cifras(band['id']))

    for u in users:
        u['is_env_admin'] = is_superadmin(u['id'])

    env_users = os.getenv('SETSYNC_SUPERADMIN_USERNAMES', '').strip()
    env_emails = os.getenv('SETSYNC_SUPERADMIN_EMAILS', '').strip()

    return render_template(
        'admin/index.html',
        bands=bands,
        cifras=cifras,
        users=users,
        env_users=env_users,
        env_emails=env_emails,
        stats={
            'bands': len(bands),
            'cifras': len(cifras),
            'users': len(users),
        },
    )
