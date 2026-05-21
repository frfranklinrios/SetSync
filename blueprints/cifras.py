import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from blueprints.auth import login_required
from db import (get_band, get_cifra, get_band_cifras, create_cifra, update_cifra,
                delete_cifra, is_band_member, is_band_admin)
from util import (transpose_text, get_available_tones, pychord_transpose_text,
                  pychord_highlight_chords, highlight_chords_html)

cifras_bp = Blueprint('cifras', __name__, url_prefix='/cifras')

@cifras_bp.route('/band/<band_id>')
@login_required
def list_by_band(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_member(band_id, user_id):
        flash('Sem acesso a essa banda', 'danger')
        return redirect(url_for('dashboard'))
    
    cifras = get_band_cifras(band_id)
    return render_template('cifras/list.html', band=band, cifras=cifras)

@cifras_bp.route('/<cifra_id>')
@login_required
def view(cifra_id):
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)

    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))

    band = get_band(cifra['band_id'])

    if not is_band_member(cifra['band_id'], user_id):
        flash('Sem acesso', 'danger')
        return redirect(url_for('dashboard'))

    transpositions = get_available_tones()
    current_transpose = request.args.get('transpose', 0, type=int)

    conteudo = cifra['conteudo'] or ''
    # Transpor usando pychord se possível
    if current_transpose != 0:
        conteudo = pychord_transpose_text(conteudo, current_transpose)
    # Destacar acordes válidos
    setlist = get_band_cifras(cifra['band_id'])
    cifra_index = next((i for i, c in enumerate(setlist) if c['id'] == cifra_id), 0)
    prev_cifra = setlist[cifra_index - 1] if cifra_index > 0 else None
    next_cifra = setlist[cifra_index + 1] if cifra_index < len(setlist) - 1 else None

    return render_template('cifras/view.html',
                           cifra=cifra,
                           band=band,
                           conteudo=conteudo,
                           transpositions=transpositions,
                           current_transpose=current_transpose,
                           setlist=setlist,
                           cifra_index=cifra_index,
                           prev_cifra=prev_cifra,
                           next_cifra=next_cifra,
                           is_admin=is_band_admin(cifra['band_id'], user_id),
                           is_member=is_band_member(cifra['band_id'], user_id))

@cifras_bp.route('/band/<band_id>/tocar')
@login_required
def tocar_band(band_id):
    """Modo tocar usando todas as cifras da banda como setlist virtual."""
    user_id = session['user_id']
    band = get_band(band_id)

    if not band or not is_band_member(band_id, user_id):
        flash('Sem acesso a essa banda', 'danger')
        return redirect(url_for('dashboard'))

    all_cifras = get_band_cifras(band_id)
    if not all_cifras:
        flash('Esta banda ainda não tem cifras.', 'warning')
        return redirect(url_for('bands.view', band_id=band_id))

    start_id = request.args.get('start')
    start_idx = 0
    if start_id:
        for i, c in enumerate(all_cifras):
            if str(c['id']) == str(start_id):
                start_idx = i
                break

    virtual_setlist = {
        'id': None,
        'band_id': band_id,
        'name': f'Cifras de {band["name"]}',
    }
    return render_template(
        'setlists/tocar.html',
        setlist=virtual_setlist,
        band=band,
        all_cifras=all_cifras,
        transpositions=get_available_tones(),
        start_idx=start_idx,
        is_virtual=True,
    )


@cifras_bp.route('/band/<band_id>/add', methods=['GET', 'POST'])
@login_required
def add(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_member(band_id, user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        artista = request.form.get('artista', '').strip()
        tom_original = request.form.get('tom_original', 'C').strip()
        conteudo = request.form.get('conteudo', '').strip()
        if not titulo or not artista or not conteudo:
            flash('Preencha todos os campos', 'danger')
            return render_template('cifras/add.html', band=band)
        if conteudo is None or conteudo == '':
            conteudo = '[Cifra sem conteúdo]'
        cifra_id = create_cifra(titulo, artista, tom_original, conteudo, band_id)
        flash(f'Cifra "{titulo}" adicionada!', 'success')
        return redirect(url_for('cifras.view', cifra_id=cifra_id))
    
    return render_template('cifras/add.html', band=band)

@cifras_bp.route('/<cifra_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(cifra_id):
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    
    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    
    band = get_band(cifra['band_id'])
    
    if not is_band_member(cifra['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip() or cifra['titulo']
        artista = request.form.get('artista', '').strip() or cifra['artista']
        tom_original = request.form.get('tom_original', cifra['tom_original']).strip()
        conteudo = request.form.get('conteudo', '').strip() or cifra['conteudo']
        if not titulo or not artista or not conteudo:
            flash('Preencha todos os campos', 'danger')
            return render_template('cifras/edit.html', cifra=cifra, band=band)
        if conteudo is None or conteudo == '':
            conteudo = '[Cifra sem conteúdo]'
        update_cifra(cifra_id, titulo, artista, tom_original, conteudo)
        flash('Cifra atualizada!', 'success')
        return redirect(url_for('cifras.view', cifra_id=cifra_id))
    
    return render_template('cifras/edit.html', cifra=cifra, band=band)

@cifras_bp.route('/<cifra_id>/delete', methods=['POST'])
@login_required
def delete(cifra_id):
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    
    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    
    band = get_band(cifra['band_id'])
    
    if not is_band_admin(cifra['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('cifras.view', cifra_id=cifra_id))
    
    delete_cifra(cifra_id)
    flash('Cifra deletada', 'success')
    return redirect(url_for('cifras.list_by_band', band_id=cifra['band_id']))

@cifras_bp.route('/<cifra_id>/transpose', methods=['GET'])
@login_required
def get_transposed(cifra_id):
    """API para obter cifra transposta via AJAX. Suporta ?html=1 para HTML destacado."""
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)

    if not cifra or not is_band_member(cifra['band_id'], user_id):
        return jsonify({'error': 'Sem acesso'}), 403

    semitones = request.args.get('semitones', 0, type=int)
    want_html = request.args.get('html', '0') == '1'

    raw = cifra['conteudo'] or ''
    transposed = pychord_transpose_text(raw, semitones) if semitones else raw

    payload = {
        'tom_original': cifra['tom_original'],
        'semitones': semitones,
    }
    if want_html:
        payload['html'] = highlight_chords_html(transposed)
    else:
        payload['conteudo'] = transposed
    return jsonify(payload)
