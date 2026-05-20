import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models_setlist import (
    create_setlist, get_band_setlists, get_setlist, delete_setlist,
    add_cifra_to_setlist, remove_cifra_from_setlist, reorder_setlist, get_setlist_cifras
)
from db import get_band, is_band_admin, get_band_cifras
from blueprints.auth import login_required

setlists_bp = Blueprint('setlists', __name__, url_prefix='/setlists')

# Modo tocar: exibe músicas em duas colunas com paginação
@setlists_bp.route('/<setlist_id>/tocar')
@login_required
def tocar(setlist_id):
    setlist = get_setlist(setlist_id)
    if not setlist:
        flash('Setlist não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    band = get_band(setlist['band_id'])
    all_cifras = get_setlist_cifras(setlist_id)
    return render_template('setlists/tocar.html', setlist=setlist, band=band, all_cifras=all_cifras)

# Ordenar músicas da setlist
@setlists_bp.route('/<setlist_id>/ordenar', methods=['GET', 'POST'])
@login_required
def ordenar(setlist_id):
    setlist = get_setlist(setlist_id)
    cifras = get_setlist_cifras(setlist_id)
    if request.method == 'POST':
        ordered_ids = request.form.getlist('cifra_ids')
        reorder_setlist(setlist_id, ordered_ids)
        flash('Ordem salva!', 'success')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))
    return render_template('setlists/ordenar.html', setlist=setlist, cifras=cifras)
# Adicionar música à setlist
@setlists_bp.route('/<setlist_id>/add', methods=['GET', 'POST'])
@login_required
def add_cifra(setlist_id):
    from db import get_band_cifras
    setlist = get_setlist(setlist_id)
    band = get_band(setlist['band_id'])
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
    remove_cifra_from_setlist(setlist_id, cifra_id)
    flash('Música removida da setlist.', 'success')
    return redirect(url_for('setlists.view', setlist_id=setlist_id))

# Deletar setlist
@setlists_bp.route('/<setlist_id>/delete', methods=['POST'])
@login_required
def delete(setlist_id):
    setlist = get_setlist(setlist_id)
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
    setlists = get_band_setlists(band_id)
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

@setlists_bp.route('/<setlist_id>')
@login_required
def view(setlist_id):
    setlist = get_setlist(setlist_id)
    if not setlist:
        flash('Setlist não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    band = get_band(setlist['band_id'])
    cifras = get_setlist_cifras(setlist_id)
    return render_template('setlists/view.html', setlist=setlist, band=band, cifras=cifras)

# Adicionar/remover cifras, ordenar, deletar setlist etc. podem ser implementados em seguida.
