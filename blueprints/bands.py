import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from blueprints.auth import login_required
from db import (create_band, get_band, get_user_bands, get_owned_bands, get_all_bands,
                update_band, delete_band, get_band_members, add_band_member, remove_band_member,
                is_band_member, is_band_admin, is_superadmin, can_delete_band,
                can_edit_band_settings, get_user)

bands_bp = Blueprint('bands', __name__, url_prefix='/bands')

@bands_bp.route('/')
@login_required
def list_bands():
    user_id = session['user_id']
    owned = get_owned_bands(user_id)
    member_of = get_user_bands(user_id)
    all_bands = get_all_bands() if is_superadmin(user_id) else None
    return render_template(
        'bands/list.html',
        owned=owned,
        member_of=member_of,
        all_bands=all_bands,
        is_superadmin=is_superadmin(user_id),
    )

@bands_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Nome da banda é obrigatório', 'danger')
            return render_template('bands/create.html')
        
        band_id = create_band(name, description, user_id)
        flash(f'Banda "{name}" criada com sucesso!', 'success')
        return redirect(url_for('bands.view', band_id=band_id))
    
    return render_template('bands/create.html')

@bands_bp.route('/<band_id>')
@login_required
def view(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band:
        flash('Banda não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    
    if not is_band_member(band_id, user_id):
        flash('Você não tem acesso a essa banda', 'danger')
        return redirect(url_for('dashboard'))
    
    from db import get_band_cifras
    from models_setlist import get_band_setlists, get_setlist_cifras
    members = get_band_members(band_id)
    cifras = get_band_cifras(band_id)
    setlists_raw = get_band_setlists(band_id)
    setlists = []
    for s in setlists_raw:
        s = dict(s)
        s['cifras_count'] = len(get_setlist_cifras(s['id']))
        setlists.append(s)
    owner = get_user(band['owner_id'])
    admin = is_band_admin(band_id, user_id)
    from blueprints.cifras import vocalist_label_for_band
    vocalist_name = vocalist_label_for_band(band_id)

    return render_template('bands/view.html', band=band, members=members,
                           cifras=cifras, setlists=setlists,
                           owner=owner, vocalist_name=vocalist_name,
                           is_admin=admin,
                           is_superadmin=is_superadmin(user_id))

@bands_bp.route('/<band_id>/settings', methods=['GET', 'POST'])
@login_required
def settings(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not can_edit_band_settings(band_id, user_id):
        flash('Sem permissão para editar configurações desta banda', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))
    
    if request.method == 'POST':
        from db import get_user_by_username
        name = request.form.get('name', '').strip() or band['name']
        description = request.form.get('description', '').strip()
        vocalist_name = request.form.get('vocalist_name', '').strip()
        link_account = request.form.get('vocalist_link_account') == '1'
        vocalist_user_id = request.form.get('vocalist_user_id', '').strip()
        vocalist_username = request.form.get('vocalist_username', '').strip()

        if link_account:
            if vocalist_username and not vocalist_user_id:
                u = get_user_by_username(vocalist_username)
                if not u:
                    flash(f'Usuário "{vocalist_username}" não encontrado no SetSync.', 'danger')
                    return redirect(url_for('bands.settings', band_id=band_id))
                vocalist_user_id = u['id']
            if vocalist_user_id:
                u = get_user(vocalist_user_id)
                if not u:
                    flash('Conta selecionada não existe.', 'danger')
                    return redirect(url_for('bands.settings', band_id=band_id))
                if not vocalist_name:
                    vocalist_name = (u.get('display_name') or '').strip() or u.get('username') or ''
        else:
            vocalist_user_id = ''

        if not vocalist_name and not vocalist_user_id:
            vocalist_name = ''
            vocalist_user_id = ''

        update_band(
            band_id, name, description,
            vocalist_user_id=vocalist_user_id,
            vocalist_name=vocalist_name,
        )
        flash('Configurações atualizadas', 'success')
        return redirect(url_for('bands.view', band_id=band_id))

    band_members = get_band_members(band_id)
    linked_vocalist_username = None
    if band.get('vocalist_user_id'):
        u = get_user(band['vocalist_user_id'])
        if u:
            linked_vocalist_username = u.get('username')
    return render_template(
        'bands/settings.html',
        band=band,
        band_members=band_members,
        linked_vocalist_username=linked_vocalist_username,
    )

@bands_bp.route('/<band_id>/members')
@login_required
def members(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_admin(band_id, user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))
    
    band_members = get_band_members(band_id)
    return render_template('bands/members.html', band=band, band_members=band_members)

@bands_bp.route('/<band_id>/invite', methods=['POST'])
@login_required
def invite(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_admin(band_id, user_id):
        return jsonify({'error': 'Sem permissão'}), 403
    
    email = request.form.get('email', '').strip()
    
    # Buscar usuário por email
    db = __import__('db').get_db()
    c = db.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    db.close()
    
    if not row:
        flash('Usuário não encontrado', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))
    
    invited_user_id = row['id']
    
    if is_band_member(band_id, invited_user_id):
        flash('Usuário já é membro', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))
    
    add_band_member(band_id, invited_user_id)
    user = get_user(invited_user_id)
    flash(f'{user["username"]} adicionado à banda', 'success')
    return redirect(url_for('bands.members', band_id=band_id))

@bands_bp.route('/<band_id>/remove-member/<user_id_to_remove>', methods=['POST'])
@login_required
def remove_member(band_id, user_id_to_remove):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_admin(band_id, user_id):
        return jsonify({'error': 'Sem permissão'}), 403
    
    if band['owner_id'] == user_id_to_remove:
        flash('Não pode remover o dono', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))
    
    remove_band_member(band_id, user_id_to_remove)
    user = get_user(user_id_to_remove)
    flash(f'{user["username"]} removido da banda', 'success')
    return redirect(url_for('bands.members', band_id=band_id))


@bands_bp.route('/<band_id>/delete', methods=['POST'])
@login_required
def delete(band_id):
    user_id = session['user_id']
    band = get_band(band_id)

    if not band or not can_delete_band(band_id, user_id):
        flash('Sem permissão para excluir esta banda', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))

    name = band['name']
    delete_band(band_id)
    flash(f'Banda "{name}" excluída com sucesso.', 'success')
    return redirect(url_for('bands.list_bands'))
