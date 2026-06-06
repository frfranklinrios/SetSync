import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, abort
from blueprints.auth import login_required
from db import (create_band, get_band, get_user_bands, get_owned_bands, get_all_bands,
                update_band, delete_band, get_band_members, add_band_member, remove_band_member,
                is_band_member, is_band_admin, is_superadmin, can_delete_band,
                can_edit_band_settings, set_band_logo_filename, get_user,
                enrich_bands_for_display, user_display_name)
from band_invites import make_band_invite_token
from security import external_url_for
import band_notifications as bn

bands_bp = Blueprint('bands', __name__, url_prefix='/bands')

@bands_bp.route('/')
@login_required
def list_bands():
    user_id = session['user_id']
    owned = enrich_bands_for_display(get_owned_bands(user_id))
    member_of = enrich_bands_for_display(get_user_bands(user_id))
    all_bands = (
        enrich_bands_for_display(get_all_bands())
        if is_superadmin(user_id) else None
    )
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

        from monetizacao import check_limite, resposta_limite_plano, LIMITES_GRATIS
        if not check_limite({'id': '', 'owner_id': user_id}, 'banda'):
            resp = resposta_limite_plano('bandas', LIMITES_GRATIS['banda'])
            if resp:
                return resp
        
        band_id = create_band(name, description, user_id)
        from monetizacao import iniciar_trial_banda
        if iniciar_trial_banda(band_id):
            flash(
                'Trial Pro de 14 dias ativado nesta banda — sem cartão. '
                'Aproveite recursos ilimitados!',
                'info',
            )
        import admin_notifications as an
        an.band_created(band_id, user_id)
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
    from models_setlist import get_band_setlists, count_setlist_cifras_by_ids
    members = get_band_members(band_id)
    cifras = get_band_cifras(band_id)
    setlists_raw = get_band_setlists(band_id)
    sl_ids = [s['id'] for s in setlists_raw]
    sl_counts = count_setlist_cifras_by_ids(sl_ids)
    setlists = []
    for s in setlists_raw:
        s = dict(s)
        s['cifras_count'] = sl_counts.get(int(s['id']), 0)
        setlists.append(s)
    owner = get_user(band['owner_id'])
    admin = is_band_admin(band_id, user_id)
    from blueprints.cifras import vocalist_label_for_band
    vocalist_name = vocalist_label_for_band(band_id)

    from band_logos import band_has_logo
    return render_template(
        'bands/view.html',
        band=band,
        members=members,
        cifras=cifras,
        setlists=setlists,
        owner=owner,
        vocalist_name=vocalist_name,
        is_admin=admin,
        is_superadmin=is_superadmin(user_id),
        band_has_logo=band_has_logo(band),
        band_logo_url=url_for('bands.band_logo', band_id=band_id) if band_has_logo(band) else None,
    )

@bands_bp.route('/<band_id>/logo')
@login_required
def band_logo(band_id):
    """Serve o logo da banda (membros autenticados)."""
    band = get_band(band_id)
    user_id = session['user_id']
    if not band or not is_band_member(band_id, user_id):
        abort(404)
    filename = (band.get('logo_filename') or '').strip()
    if not filename:
        abort(404)
    from band_logos import logo_path
    path = logo_path(band_id, filename)
    if not path:
        abort(404)
    return send_file(path, max_age=3600)


@bands_bp.route('/<band_id>/settings', methods=['GET', 'POST'])
@login_required
def settings(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not can_edit_band_settings(band_id, user_id):
        flash('Sem permissão para editar configurações desta banda', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))
    
    if request.method == 'POST':
        from db import (
            get_user_by_username, add_band_vocalists_from_text,
            delete_band_vocalist, get_band_vocalists, band_vocalist_belongs_to_band,
        )
        action = request.form.get('action', 'save_band')

        if action == 'save_band':
            name = request.form.get('name', '').strip() or band['name']
            description = request.form.get('description', '').strip()
            update_band(band_id, name, description)
            bn.band_updated(band_id, user_id)
            flash('Configurações atualizadas', 'success')

        elif action == 'add_vocalist':
            raw = request.form.get('vocalist_names', '').strip()
            if not raw:
                flash('Informe o nome de cantora/cantor.', 'danger')
            else:
                user_id = None
                if request.form.get('vocalist_link_account') == '1':
                    user_id = request.form.get('vocalist_user_id', '').strip()
                    username = request.form.get('vocalist_username', '').strip()
                    if username and not user_id:
                        u = get_user_by_username(username)
                        if not u:
                            flash(f'Usuário "{username}" não encontrado.', 'danger')
                            return redirect(url_for('bands.settings', band_id=band_id))
                        user_id = u['id']
                    if user_id and not get_user(user_id):
                        flash('Conta não encontrada.', 'danger')
                        return redirect(url_for('bands.settings', band_id=band_id))
                try:
                    add_band_vocalists_from_text(band_id, raw, user_id or None)
                    bn.vocalist_added(band_id, session['user_id'], raw)
                    flash('Cantoras/cantores adicionados.', 'success')
                except ValueError as e:
                    flash(str(e), 'danger')

        elif action == 'upload_logo':
            from band_logos import save_band_logo_upload
            logo_file = request.files.get('logo')
            filename, err = save_band_logo_upload(band_id, logo_file)
            if err:
                flash(err, 'danger')
            else:
                set_band_logo_filename(band_id, filename)
                bn.band_updated(band_id, user_id)
                flash('Logo da banda atualizado.', 'success')

        elif action == 'remove_logo':
            from band_logos import delete_band_logo_files
            delete_band_logo_files(band_id)
            set_band_logo_filename(band_id, None)
            bn.band_updated(band_id, user_id)
            flash('Logo removido.', 'success')

        elif action == 'delete_vocalist':
            vid = request.form.get('vocalist_id', '').strip()
            if vid and band_vocalist_belongs_to_band(vid, band_id):
                from db import get_band_vocalist, vocalist_entry_display_name
                v = get_band_vocalist(vid)
                vname = vocalist_entry_display_name(v) if v else 'Cantor(a)'
                delete_band_vocalist(vid)
                bn.vocalist_removed(band_id, session['user_id'], vname)
                flash('Cantora/cantor removido.', 'success')
            else:
                flash('Cantora/cantor não encontrado.', 'danger')

        return redirect(url_for('bands.settings', band_id=band_id))

    from db import get_band_vocalists
    band_members = get_band_members(band_id)
    vocalists = get_band_vocalists(band_id)
    from band_logos import band_has_logo
    return render_template(
        'bands/settings.html',
        band=band,
        band_members=band_members,
        vocalists=vocalists,
        band_has_logo=band_has_logo(band),
        band_logo_url=url_for('bands.band_logo', band_id=band_id) if band_has_logo(band) else None,
    )

@bands_bp.route('/<band_id>/members')
@login_required
def members(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_admin(band_id, user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))
    
    from db import get_band_vocalists
    band_members = get_band_members(band_id)
    vocalist_user_ids = {
        v['user_id'] for v in get_band_vocalists(band_id) if v.get('user_id')
    }
    token = make_band_invite_token(band_id)
    invite_url = external_url_for('auth.convite', token=token)
    return render_template(
        'bands/members.html',
        band=band,
        band_members=band_members,
        vocalist_user_ids=vocalist_user_ids,
        invite_url=invite_url,
    )

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
        flash('Se o e-mail estiver cadastrado, o usuário será adicionado à banda.', 'info')
        return redirect(url_for('bands.members', band_id=band_id))
    
    invited_user_id = row['id']
    
    if is_band_member(band_id, invited_user_id):
        flash('Usuário já é membro', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))

    from monetizacao import check_limite, resposta_limite_plano, LIMITES_GRATIS
    if not check_limite(band, 'integrante'):
        resp = resposta_limite_plano('integrantes', LIMITES_GRATIS['integrante'])
        if resp:
            return resp
    
    add_band_member(band_id, invited_user_id)
    user = get_user(invited_user_id)
    bn.member_added_by_admin(band_id, user_id, invited_user_id)
    flash(f'{user_display_name(user)} adicionado à banda', 'success')
    return redirect(url_for('bands.members', band_id=band_id))

@bands_bp.route('/<band_id>/remove-member/<user_id_to_remove>', methods=['POST'])
@login_required
def remove_member(band_id, user_id_to_remove):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_admin(band_id, user_id):
        return jsonify({'error': 'Sem permissão'}), 403
    
    if band['owner_id'] == user_id_to_remove:
        flash('Não é possível remover a pessoa titular da banda', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))
    
    remove_band_member(band_id, user_id_to_remove)
    user = get_user(user_id_to_remove)
    bn.member_removed(band_id, user_id, user_id_to_remove)
    flash(f'{user_display_name(user)} removido da banda', 'success')
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
    import admin_notifications as an
    an.band_deleted(band_id, user_id, name)
    flash(f'Banda "{name}" excluída com sucesso.', 'success')
    return redirect(url_for('bands.list_bands'))
