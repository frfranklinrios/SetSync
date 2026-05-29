import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models_setlist import (
    create_setlist, get_band_setlists, get_setlist, delete_setlist,
    add_cifra_to_setlist, remove_cifra_from_setlist, reorder_setlist, get_setlist_cifras,
    set_setlist_vocalist, set_setlist_cifra_vocalist,
)
from db import get_band, is_band_admin, is_band_member, get_band_cifras
from blueprints.auth import login_required

setlists_bp = Blueprint('setlists', __name__, url_prefix='/setlists')


def _require_setlist_access(setlist, user_id):
    """Retorna (ok, band) — verifica existência e membership."""
    if not setlist:
        return False, None
    band = get_band(setlist['band_id'])
    if not band or not is_band_member(setlist['band_id'], user_id):
        return False, band
    return True, band


# Modo tocar: exibe músicas em duas colunas com paginação
@setlists_bp.route('/<setlist_id>/tocar')
@login_required
def tocar(setlist_id):
    from blueprints.cifras import enrich_cifra_for_tocar, render_play_mode
    user_id = session['user_id']
    setlist = get_setlist(setlist_id)
    ok, band = _require_setlist_access(setlist, user_id)
    if not ok:
        flash('Setlist não encontrada' if not setlist else 'Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    all_cifras = [
        enrich_cifra_for_tocar(dict(c), setlist_id=setlist_id)
        for c in get_setlist_cifras(setlist_id)
    ]
    start_id = request.args.get('start')
    start_idx = 0
    if start_id:
        for i, c in enumerate(all_cifras):
            if str(c['id']) == str(start_id):
                start_idx = i
                break
    return render_play_mode(setlist, band, all_cifras, start_idx=start_idx, is_virtual=False)

# Ordenar músicas da setlist via AJAX (drag-and-drop inline)
@setlists_bp.route('/<setlist_id>/reorder', methods=['POST'])
@login_required
def reorder_ajax(setlist_id):
    setlist = get_setlist(setlist_id)
    if not setlist:
        return jsonify({'error': 'Setlist não encontrada'}), 404
    user_id = session['user_id']
    if not is_band_member(setlist['band_id'], user_id):
        return jsonify({'error': 'Sem permissão'}), 403
    data = request.get_json(silent=True) or {}
    ordered_ids = data.get('cifra_ids') or []
    if not ordered_ids:
        return jsonify({'error': 'IDs não fornecidos'}), 400
    reorder_setlist(setlist_id, ordered_ids)
    return jsonify({'success': True, 'count': len(ordered_ids)})
# Adicionar música à setlist
@setlists_bp.route('/<setlist_id>/add', methods=['GET', 'POST'])
@login_required
def add_cifra(setlist_id):
    from db import get_band_cifras
    user_id = session['user_id']
    setlist = get_setlist(setlist_id)
    ok, band = _require_setlist_access(setlist, user_id)
    if not ok:
        flash('Setlist não encontrada' if not setlist else 'Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        cifra_id = request.form.get('cifra_id')
        if cifra_id:
            add_cifra_to_setlist(setlist_id, cifra_id)
            flash('Música adicionada!', 'success')
            return redirect(url_for('setlists.view', setlist_id=setlist_id))
    # Listar cifras da banda que não estão na setlist
    todas = get_band_cifras(band['id'])
    atuais = [c['id'] for c in get_setlist_cifras(setlist_id)]
    disponiveis = [c for c in todas if c['id'] not in atuais]
    return render_template('setlists/add_cifra.html', setlist=setlist, band=band, cifras=disponiveis)

# Remover música da setlist
@setlists_bp.route('/<setlist_id>/remove/<cifra_id>', methods=['POST'])
@login_required
def remove_cifra(setlist_id, cifra_id):
    user_id = session['user_id']
    setlist = get_setlist(setlist_id)
    ok, _ = _require_setlist_access(setlist, user_id)
    if not ok:
        flash('Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    remove_cifra_from_setlist(setlist_id, cifra_id)
    flash('Música removida da setlist.', 'success')
    return redirect(url_for('setlists.view', setlist_id=setlist_id))

# Deletar setlist
@setlists_bp.route('/<setlist_id>/delete', methods=['POST'])
@login_required
def delete(setlist_id):
    user_id = session['user_id']
    setlist = get_setlist(setlist_id)
    if not setlist:
        flash('Setlist não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    if not is_band_admin(setlist['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))
    band_id = setlist['band_id']
    delete_setlist(setlist_id)
    flash('Setlist excluída.', 'success')
    return redirect(url_for('setlists.list_setlists', band_id=band_id))

@setlists_bp.route('/band/<band_id>')
@login_required
def list_setlists(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    from db import is_band_member
    if not band or not is_band_member(band_id, user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('bands.view', band_id=band_id))
    setlists = []
    for s in get_band_setlists(band_id):
        s = dict(s)
        s['cifras_count'] = len(get_setlist_cifras(s['id']))
        setlists.append(s)
    return render_template('setlists/list.html', band=band, setlists=setlists)

@setlists_bp.route('/create/<band_id>', methods=['GET', 'POST'])
@login_required
def create(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    if not band or not is_band_admin(band_id, user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('bands.view', band_id=band_id))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Nome obrigatório', 'danger')
            return render_template('setlists/create.html', band=band)
        setlist_id = create_setlist(band_id, name, description)
        flash('Setlist criada!', 'success')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))
    return render_template('setlists/create.html', band=band)

@setlists_bp.route('/<setlist_id>/cifra/<cifra_id>/vocalist', methods=['POST'])
@login_required
def set_cifra_vocalist(setlist_id, cifra_id):
    """Cantor(a) desta música na setlist."""
    from db import band_vocalist_belongs_to_band, get_band_vocalist, get_cifra
    from blueprints.cifras import cifra_display_key, vocalist_entry_display_name
    setlist = get_setlist(setlist_id)
    ok, band = _require_setlist_access(setlist, session['user_id'])
    if not ok:
        return jsonify({'ok': False, 'error': 'Sem acesso'}), 403
    data = request.get_json(silent=True) or {}
    vid = (data.get('vocalist_id') or '').strip()
    if vid and not band_vocalist_belongs_to_band(vid, band['id']):
        return jsonify({'ok': False, 'error': 'Cantor inválido'}), 400
    set_setlist_cifra_vocalist(setlist_id, cifra_id, vid or None)
    cifra = get_cifra(cifra_id)
    v = get_band_vocalist(vid) if vid else None
    vname = vocalist_entry_display_name(v) if v else ''
    display_key = cifra_display_key(cifra, vocalist_id=vid) if cifra else ''
    return jsonify({'ok': True, 'vocalist_id': vid, 'vocalist_name': vname, 'display_key': display_key})


@setlists_bp.route('/<setlist_id>/vocalist', methods=['POST'])
@login_required
def set_vocalist(setlist_id):
    """Define cantor(a) padrão desta setlist."""
    from db import band_vocalist_belongs_to_band
    setlist = get_setlist(setlist_id)
    ok, band = _require_setlist_access(setlist, session['user_id'])
    if not ok:
        return jsonify({'ok': False, 'error': 'Sem acesso'}), 403
    data = request.get_json(silent=True) or {}
    vid = (data.get('vocalist_id') or request.form.get('vocalist_id') or '').strip()
    if vid and not band_vocalist_belongs_to_band(vid, band['id']):
        return jsonify({'ok': False, 'error': 'Cantor inválido'}), 400
    set_setlist_vocalist(setlist_id, vid or None)
    from blueprints.cifras import active_vocalist_label
    return jsonify({
        'ok': True,
        'vocalist_id': vid or None,
        'vocalist_name': active_vocalist_label(band['id'], setlist_id=setlist_id),
    })


@setlists_bp.route('/<setlist_id>')
@login_required
def view(setlist_id):
    user_id = session['user_id']
    setlist = get_setlist(setlist_id)
    ok, band = _require_setlist_access(setlist, user_id)
    if not ok:
        flash('Setlist não encontrada' if not setlist else 'Sem permissão', 'danger')
        return redirect(url_for('dashboard'))

    from db import get_band_vocalists, get_band_vocalist
    from blueprints.cifras import cifra_display_key, vocalist_entry_display_name

    cifras_raw = get_setlist_cifras(setlist_id)
    vocalists = get_band_vocalists(band['id'])
    default_vid = vocalists[0]['id'] if vocalists else None
    cifras = []
    for c in cifras_raw:
        row = dict(c)
        vid = row.get('setlist_vocalist_id') or default_vid
        row['row_vocalist_id'] = vid
        v = get_band_vocalist(vid) if vid else None
        row['row_vocalist_name'] = vocalist_entry_display_name(v) if v else ''
        row['row_display_key'] = cifra_display_key(c, vocalist_id=vid) if c.get('tom_original') else ''
        cifras.append(row)

    return render_template(
        'setlists/view.html',
        setlist=setlist,
        band=band,
        cifras=cifras,
        vocalists=vocalists,
    )
