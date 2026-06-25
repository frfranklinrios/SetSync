import functools
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from blueprints.auth import login_required
from db import (
    is_superadmin,
    get_all_bands,
    get_all_cifras,
    get_all_users,
    get_user,
    get_band,
    get_band_members,
    get_band_cifras,
    get_latest_admin_whatsapp_invites,
    list_studio_prospects,
    list_testimonials,
    get_testimonial,
    create_testimonial,
    update_testimonial,
    delete_testimonial,
    set_band_contact_whatsapp,
    set_user_superadmin,
    is_superadmin_env_only,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def superadmin_required(f):
    @functools.wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not is_superadmin(session.get('user_id')):
            flash(
                'Acesso restrito a administradores (configure SETSYNC_SUPERADMIN_* no .env '
                'ou peça promoção no banco).',
                'danger',
            )
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return wrapped


@admin_bp.route('/')
@superadmin_required
def index():
    from models_studio import enrich_studios_for_admin, list_all_studios

    bands = get_all_bands()
    cifras = get_all_cifras()
    users = get_all_users()
    studios = enrich_studios_for_admin(list_all_studios())

    for band in bands:
        owner = get_user(band['owner_id'])
        band['owner'] = owner or {}
        band['members_count'] = len(get_band_members(band['id']))
        band['cifras_count'] = len(get_band_cifras(band['id']))

    for u in users:
        u['is_superadmin_db'] = bool(u.get('is_superadmin'))
        u['is_superadmin_env'] = is_superadmin_env_only(u['id'])
        u['is_env_admin'] = is_superadmin(u['id'])

    env_users = os.getenv('SETSYNC_SUPERADMIN_USERNAMES', '').strip()
    env_emails = os.getenv('SETSYNC_SUPERADMIN_EMAILS', '').strip()

    from product_funnel import funnel_counts
    from whatsapp_service import is_configured as whatsapp_configured

    funnel_stats = funnel_counts()
    invite_log = get_latest_admin_whatsapp_invites()
    studio_prospects = list_studio_prospects()

    return render_template(
        'admin/index.html',
        bands=bands,
        cifras=cifras,
        users=users,
        studios=studios,
        studio_prospects=studio_prospects,
        env_users=env_users,
        env_emails=env_emails,
        funnel_stats=funnel_stats,
        invite_log=invite_log,
        whatsapp_configured=whatsapp_configured(),
        stats={
            'bands': len(bands),
            'cifras': len(cifras),
            'users': len(users),
            'studios': len(studios),
        },
    )


@admin_bp.route('/depoimentos')
@superadmin_required
def depoimentos():
    return render_template(
        'admin/depoimentos.html',
        testimonials=list_testimonials(active_only=False),
    )


@admin_bp.route('/depoimentos/criar', methods=['GET', 'POST'])
@superadmin_required
def depoimentos_criar():
    if request.method == 'POST':
        data = {
            'nome': request.form.get('nome', '').strip(),
            'cidade': request.form.get('cidade', '').strip(),
            'descricao': request.form.get('descricao', '').strip(),
            'texto': request.form.get('texto', '').strip(),
            'foto_url': request.form.get('foto_url', '').strip(),
            'ativo': request.form.get('ativo') == '1',
            'ordem': int(request.form.get('ordem') or 0),
        }
        if not data['nome'] or not data['texto']:
            flash('Nome e texto são obrigatórios.', 'danger')
        else:
            create_testimonial(data)
            flash('Depoimento criado.', 'success')
            return redirect(url_for('admin.depoimentos'))
    return render_template('admin/depoimento_form.html', testimonial=None)


@admin_bp.route('/depoimentos/<int:testimonial_id>/editar', methods=['GET', 'POST'])
@superadmin_required
def depoimentos_editar(testimonial_id: int):
    t = get_testimonial(testimonial_id)
    if not t:
        flash('Depoimento não encontrado.', 'danger')
        return redirect(url_for('admin.depoimentos'))
    if request.method == 'POST':
        data = {
            'nome': request.form.get('nome', '').strip(),
            'cidade': request.form.get('cidade', '').strip(),
            'descricao': request.form.get('descricao', '').strip(),
            'texto': request.form.get('texto', '').strip(),
            'foto_url': request.form.get('foto_url', '').strip(),
            'ativo': request.form.get('ativo') == '1',
            'ordem': int(request.form.get('ordem') or 0),
        }
        update_testimonial(testimonial_id, data)
        flash('Depoimento atualizado.', 'success')
        return redirect(url_for('admin.depoimentos'))
    return render_template('admin/depoimento_form.html', testimonial=t)


@admin_bp.route('/depoimentos/<int:testimonial_id>/excluir', methods=['POST'])
@superadmin_required
def depoimentos_excluir(testimonial_id: int):
    delete_testimonial(testimonial_id)
    flash('Depoimento removido.', 'success')
    return redirect(url_for('admin.depoimentos'))


@admin_bp.route('/convite-whatsapp', methods=['POST'])
@superadmin_required
def convite_whatsapp():
    target_type = (request.form.get('target_type') or '').strip().lower()
    target_id = (request.form.get('target_id') or '').strip()
    phone = (request.form.get('phone') or '').strip()
    action = (request.form.get('action') or 'send').strip()

    if target_type == 'studio_prospect':
        from admin_outreach import send_studio_prospect_invite

        if action == 'resend' and target_id:
            from admin_outreach import send_admin_whatsapp_invite
            from db import get_studio_prospect

            prospect = get_studio_prospect(target_id)
            if not prospect:
                flash('Prospect não encontrado.', 'danger')
                return redirect(url_for('admin.index') + '#tab-convites')
            result = send_admin_whatsapp_invite(
                target_type='studio_prospect',
                target_id=target_id,
                phone=prospect.get('phone') or phone,
                sent_by_user_id=session['user_id'],
                save_phone=False,
            )
        else:
            result = send_studio_prospect_invite(
                phone=phone,
                nome=(request.form.get('studio_nome') or '').strip(),
                cidade=(request.form.get('studio_cidade') or '').strip(),
                sent_by_user_id=session['user_id'],
                notes=(request.form.get('notes') or '').strip(),
            )
        if result.get('ok'):
            flash('Convite de cadastro enviado por WhatsApp.', 'success')
        else:
            flash(result.get('error') or 'Não foi possível enviar.', 'danger')
        return redirect(url_for('admin.index') + '#tab-convites')

    if target_type not in ('band',) or not target_id:
        flash('Selecione uma banda válida.', 'danger')
        return redirect(url_for('admin.index') + '#tab-convites')

    if action == 'save_only':
        from whatsapp_service import normalize_whatsapp_phone

        normalized = normalize_whatsapp_phone(phone) if phone else None
        if phone and not normalized:
            flash('Número de WhatsApp inválido.', 'danger')
            return redirect(url_for('admin.index') + '#tab-bands')

        if not get_band(target_id):
            flash('Banda não encontrada.', 'danger')
            return redirect(url_for('admin.index') + '#tab-bands')
        set_band_contact_whatsapp(target_id, normalized)
        flash('WhatsApp da banda salvo.', 'success')
        return redirect(url_for('admin.index') + '#tab-bands')

    from admin_outreach import send_admin_whatsapp_invite

    result = send_admin_whatsapp_invite(
        target_type=target_type,
        target_id=target_id,
        phone=phone,
        sent_by_user_id=session['user_id'],
        save_phone=True,
    )
    if result.get('ok'):
        flash('Convite enviado por WhatsApp.', 'success')
    else:
        flash(result.get('error') or 'Não foi possível enviar.', 'danger')
    tab = (request.form.get('return_tab') or '').strip() or 'bands'
    return redirect(url_for('admin.index') + f'#tab-{tab}')


@admin_bp.route('/usuarios/<user_id>/superadmin', methods=['POST'])
@superadmin_required
def toggle_superadmin(user_id: str):
    enabled = request.form.get('enabled') == '1'
    if set_user_superadmin(user_id, enabled):
        flash('Privilégio de superadmin do app atualizado.', 'success')
    else:
        flash('Usuário não encontrado.', 'danger')
    return redirect(url_for('admin.index') + '#tab-users')
