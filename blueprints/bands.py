import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, abort
from blueprints.auth import login_required
from db import (create_band, get_band, get_user_bands, get_owned_bands, get_all_bands,
                update_band, delete_band, get_band_members, add_band_member, remove_band_member,
                is_band_member, is_band_admin, is_band_editor, is_superadmin, can_delete_band,
                can_edit_band_settings, set_band_logo_filename, get_user,
                update_band_member_role, get_band_member_role,
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
        from db import get_owned_bands
        from monetizacao import iniciar_trial_banda
        from google_ads import mark_funnel_event

        if len(get_owned_bands(user_id)) == 1:
            mark_funnel_event('primeira_banda')
        if iniciar_trial_banda(band_id):
            mark_funnel_event('trial_iniciado')
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
    can_edit = is_band_editor(band_id, user_id)
    from blueprints.cifras import vocalist_label_for_band
    vocalist_name = vocalist_label_for_band(band_id)

    from band_logos import band_has_logo
    from datetime import datetime
    from models_agenda import get_band_events, get_events_scale_summaries

    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    all_events = get_band_events(band_id)
    scale_summaries = get_events_scale_summaries([e['id'] for e in all_events])
    for e in all_events:
        summary = scale_summaries.get(e['id'], {})
        e['scale_count'] = summary.get('count', 0)
        e['scale_preview'] = summary.get('preview', '')

    events_upcoming = [e for e in all_events if str(e.get('starts_at') or '') >= now]
    events_past = [e for e in all_events if str(e.get('starts_at') or '') < now]
    events_past.reverse()

    events_calendar = [
        {
            'id': e['id'],
            'title': e.get('title') or '',
            'event_type': e.get('event_type') or 'ensaio',
            'starts_at': str(e.get('starts_at') or '')[:19],
            'location': e.get('location') or '',
            'scale_preview': e.get('scale_preview') or '',
            'url': url_for('agenda.view', event_id=e['id']),
        }
        for e in all_events
    ]

    return render_template(
        'bands/view.html',
        band=band,
        members=members,
        cifras=cifras,
        setlists=setlists,
        events_upcoming=events_upcoming,
        events_past=events_past,
        events_calendar=events_calendar,
        owner=owner,
        vocalist_name=vocalist_name,
        is_admin=admin,
        is_member=True,
        can_edit=can_edit,
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
    from band_member_invites import list_pending_invites_for_band

    return render_template(
        'bands/members.html',
        band=band,
        band_members=band_members,
        vocalist_user_ids=vocalist_user_ids,
        invite_url=invite_url,
        pending_invites=list_pending_invites_for_band(band_id),
        is_owner=(band['owner_id'] == user_id),
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
        flash('Se o e-mail estiver cadastrado, a pessoa receberá um convite para aceitar.', 'info')
        return redirect(url_for('bands.members', band_id=band_id))
    
    invited_user_id = row['id']
    
    if is_band_member(band_id, invited_user_id):
        flash('Usuário já é membro', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))

    from band_member_invites import create_band_member_invite

    result = create_band_member_invite(band_id, invited_user_id, user_id)
    if result == 'already_pending':
        flash('Já existe um convite pendente para este usuário.', 'info')
        return redirect(url_for('bands.members', band_id=band_id))
    if result == 'already_member':
        flash('Usuário já é membro', 'danger')
        return redirect(url_for('bands.members', band_id=band_id))

    user = get_user(invited_user_id)
    bn.band_invite_sent(band_id, user_id, invited_user_id)
    flash(f'Convite enviado para {user_display_name(user)}. A pessoa precisa aceitar para entrar na banda.', 'success')
    return redirect(url_for('bands.members', band_id=band_id))

@bands_bp.route('/<band_id>/invite/cancel/<invite_id>', methods=['POST'])
@login_required
def cancel_invite(band_id, invite_id):
    user_id = session['user_id']
    band = get_band(band_id)
    if not band or not is_band_admin(band_id, user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('bands.members', band_id=band_id) if band else url_for('dashboard'))

    from band_member_invites import cancel_band_member_invite

    if cancel_band_member_invite(invite_id, band_id):
        flash('Convite cancelado.', 'info')
    else:
        flash('Convite não encontrado.', 'warning')
    return redirect(url_for('bands.members', band_id=band_id))


@bands_bp.route('/<band_id>/members/<member_id>/role', methods=['POST'])
@login_required
def set_member_role(band_id, member_id):
    user_id = session['user_id']
    band = get_band(band_id)

    if not band or not is_band_admin(band_id, user_id):
        flash('Só administradores da banda podem alterar papéis de membros.', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))

    if member_id == band['owner_id']:
        flash('O titular da banda não pode ter o papel alterado.', 'warning')
        return redirect(url_for('bands.members', band_id=band_id))

    current_role = get_band_member_role(band_id, member_id)
    if current_role == 'admin' and band['owner_id'] != user_id:
        flash('Só o titular pode alterar o papel de administradores.', 'warning')
        return redirect(url_for('bands.members', band_id=band_id))

    role = (request.form.get('role') or 'member').strip().lower()
    if role not in ('member', 'editor', 'admin'):
        role = 'member'
    if role == 'admin' and band['owner_id'] != user_id:
        flash('Só o titular da banda pode promover administradores.', 'warning')
        return redirect(url_for('bands.members', band_id=band_id))

    if update_band_member_role(band_id, member_id, role):
        target = get_user(member_id)
        labels = {
            'admin': 'administrador da banda',
            'editor': 'editor',
            'member': 'membro',
        }
        flash(
            f'{user_display_name(target)} agora é {labels.get(role, role)} em {band["name"]}.',
            'success',
        )
    else:
        flash('Não foi possível atualizar o papel do membro.', 'danger')
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


@bands_bp.route('/<band_id>/equipe', methods=['GET', 'POST'])
@login_required
def equipe(band_id):
    """Funções, formações salvas e lista de reserva por função."""
    user_id = session['user_id']
    band = get_band(band_id)
    if not band or not can_edit_band_settings(band_id, user_id):
        flash('Sem permissão para gerenciar a equipe desta banda.', 'danger')
        return redirect(url_for('bands.view', band_id=band_id) if band else url_for('dashboard'))

    from models_band_team import (
        add_band_role,
        create_lineup,
        delete_band_role,
        delete_lineup,
        ensure_default_band_roles,
        get_lineup,
        get_lineup_members,
        list_band_lineups,
        list_band_roles,
        list_role_substitutes,
        set_role_substitutes,
        update_lineup,
    )

    ensure_default_band_roles(band_id)
    band_members = get_band_members(band_id)
    roles = list_band_roles(band_id)
    lineups = list_band_lineups(band_id)
    substitutes = list_role_substitutes(band_id)

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'add_role':
            label = (request.form.get('role_label') or '').strip()
            if add_band_role(band_id, label):
                flash(f'Função «{label}» adicionada.', 'success')
            else:
                flash('Função já existe ou nome inválido.', 'warning')

        elif action == 'delete_role':
            label = (request.form.get('role_label') or '').strip()
            if label:
                delete_band_role(band_id, label)
                flash('Função removida.', 'info')

        elif action == 'save_substitutes':
            role_label = (request.form.get('role_label') or '').strip()
            user_ids = request.form.getlist('substitute_ids')
            set_role_substitutes(band_id, role_label, user_ids)
            flash(f'Reservas para {role_label} atualizadas.', 'success')

        elif action == 'create_lineup':
            name = (request.form.get('lineup_name') or '').strip()
            if not name:
                flash('Informe o nome da formação.', 'warning')
            else:
                members = []
                for uid in request.form.getlist('lineup_member_ids'):
                    role = (request.form.get(f'lineup_role_{uid}') or '').strip() or None
                    members.append({'user_id': uid, 'role_label': role})
                create_lineup(band_id, name, members)
                flash(f'Formação «{name}» criada.', 'success')

        elif action == 'delete_lineup':
            lineup_id = (request.form.get('lineup_id') or '').strip()
            lu = get_lineup(lineup_id) if lineup_id else None
            if lu and lu.get('band_id') == band_id:
                delete_lineup(lineup_id)
                flash('Formação removida.', 'info')

        elif action == 'update_lineup':
            lineup_id = (request.form.get('lineup_id') or '').strip()
            lu = get_lineup(lineup_id) if lineup_id else None
            if not lu or lu.get('band_id') != band_id:
                flash('Formação inválida.', 'danger')
            else:
                name = (request.form.get('lineup_name') or '').strip() or lu['name']
                members = []
                for uid in request.form.getlist('lineup_member_ids'):
                    role = (request.form.get(f'lineup_role_{uid}') or '').strip() or None
                    members.append({'user_id': uid, 'role_label': role})
                update_lineup(lineup_id, name, members)
                flash('Formação atualizada.', 'success')

        return redirect(url_for('bands.equipe', band_id=band_id))

    lineup_details = {}
    for lu in lineups:
        lineup_details[lu['id']] = get_lineup_members(lu['id'])

    subs_by_role: dict[str, list[str]] = {}
    for s in substitutes:
        subs_by_role.setdefault(s['role_label'], []).append(s['user_id'])

    return render_template(
        'bands/equipe.html',
        band=band,
        band_members=band_members,
        roles=roles,
        lineups=lineups,
        lineup_details=lineup_details,
        substitutes_by_role=subs_by_role,
        user_display_name=user_display_name,
    )


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
