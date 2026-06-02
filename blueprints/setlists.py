import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
from models_setlist import (
    create_setlist, get_band_setlists, get_setlist, delete_setlist,
    add_cifra_to_setlist, remove_cifra_from_setlist, reorder_setlist, get_setlist_cifras,
    set_setlist_vocalist, set_setlist_cifra_vocalist,
)
from db import get_band, is_band_admin, is_band_member, get_band_cifras, get_cifra
from blueprints.auth import login_required
import band_notifications as bn

setlists_bp = Blueprint('setlists', __name__, url_prefix='/setlists')


def _resolve_print_user_id(setlist_id: str) -> str | None:
    """Sessão normal ou token assinado de curta duração (PDF server-side)."""
    pdfgen = request.args.get('pdfgen', '').lower() in ('1', 'true', 'yes')
    if pdfgen:
        from security import verify_pdf_access_token
        uid = verify_pdf_access_token(request.args.get('pdf_token', ''), setlist_id)
        if uid:
            return uid
    return session.get('user_id')


def _require_setlist_access(setlist, user_id):
    """Retorna (ok, band) — verifica existência e membership."""
    if not setlist:
        return False, None
    band = get_band(setlist['band_id'])
    if not band or not is_band_member(setlist['band_id'], user_id):
        return False, band
    return True, band


def _prepare_setlist_print_data(setlist_id, user_id):
    """Monta setlist, band e sheets para impressão/PDF. Retorna None se sem acesso ou vazia."""
    from datetime import datetime
    from db import get_band_vocalists, get_band_vocalist
    from blueprints.cifras import (
        prepare_cifra_sheet,
        cifra_display_key,
        cifra_transpose_semitones,
        vocalist_entry_display_name,
    )

    setlist = get_setlist(setlist_id)
    ok, band = _require_setlist_access(setlist, user_id)
    if not ok:
        return None

    cifras_raw = get_setlist_cifras(setlist_id)
    if not cifras_raw:
        return {'empty': True, 'setlist': setlist, 'band': band}

    vocalists = get_band_vocalists(band['id'])
    default_vid = vocalists[0]['id'] if vocalists else None
    sheets = []
    for i, c in enumerate(cifras_raw, start=1):
        vid = c.get('setlist_vocalist_id') or default_vid
        semi = cifra_transpose_semitones(c, vocalist_id=vid)
        sheet = prepare_cifra_sheet(c, semi)
        v = get_band_vocalist(vid) if vid else None
        vname = vocalist_entry_display_name(v) if v else ''
        sheet['index'] = i
        sheet['cifra_id'] = c['id']
        sheet['vocalist_name'] = vname
        sheet['display_key'] = (
            cifra_display_key(c, vocalist_id=vid) if c.get('tom_original') else sheet['display_key']
        )
        sheets.append(sheet)

    two_cols = request.args.get('cols', '1') == '2'
    palco_compact = len(sheets) > 10 or request.args.get('compact', '') == '1'

    return {
        'empty': False,
        'setlist': setlist,
        'band': band,
        'sheets': sheets,
        'printed_at': datetime.now(),
        'two_cols': two_cols,
        'palco_compact': palco_compact,
    }


@setlists_bp.route('/<setlist_id>/imprimir')
def imprimir(setlist_id):
    """Página para imprimir todas as músicas da setlist (tom por cantor da linha)."""
    user_id = _resolve_print_user_id(setlist_id)
    if not user_id:
        return redirect(url_for('auth.login'))
    data = _prepare_setlist_print_data(setlist_id, user_id)
    if data is None:
        flash('Setlist não encontrada' if not get_setlist(setlist_id) else 'Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    if data.get('empty'):
        flash('Setlist vazia — adicione músicas antes de imprimir.', 'warning')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))

    autoprint = request.args.get('print', '').lower() in ('1', 'true', 'yes')
    pdfgen = request.args.get('pdfgen', '').lower() in ('1', 'true', 'yes')

    return render_template(
        'setlists/print.html',
        autoprint=autoprint,
        pdfgen=pdfgen,
        **{k: v for k, v in data.items() if k != 'empty'},
    )


@setlists_bp.route('/<setlist_id>/exportar-pdf')
@login_required
def exportar_pdf(setlist_id):
    """PDF via WeasyPrint (feature premium)."""
    from monetizacao import pode_exportar_pdf, resposta_plano_necessario
    from setlist_weasyprint import html_to_pdf_bytes, render_setlist_pdf_html

    data = _prepare_setlist_print_data(setlist_id, session['user_id'])
    if data is None:
        flash('Setlist não encontrada ou sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    if data.get('empty'):
        flash('Setlist vazia', 'warning')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))
    if not pode_exportar_pdf(data['band']['id']):
        return resposta_plano_necessario()

    try:
        html = render_setlist_pdf_html(current_app, data)
        pdf_bytes = html_to_pdf_bytes(html)
    except Exception as exc:
        current_app.logger.exception('Erro ao gerar PDF: %s', exc)
        flash('Não foi possível gerar o PDF. Verifique se o WeasyPrint está instalado.', 'danger')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))

    from setlist_pdf import build_pdf_download_name
    filename = build_pdf_download_name(data['setlist']['name'], data['band']['name'])
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )


@setlists_bp.route('/<setlist_id>/pdf')
@login_required
def download_pdf(setlist_id):
    """Gera e baixa PDF formatado (Chromium)."""
    from monetizacao import pode_exportar_pdf, resposta_plano_necessario

    data = _prepare_setlist_print_data(setlist_id, session['user_id'])
    if data is None:
        flash('Setlist não encontrada' if not get_setlist(setlist_id) else 'Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    if data.get('empty'):
        flash('Setlist vazia — adicione músicas antes de gerar o PDF.', 'warning')
        return redirect(url_for('setlists.view', setlist_id=setlist_id))
    if not pode_exportar_pdf(data['band']['id']):
        return resposta_plano_necessario()

    from setlist_pdf import build_pdf_download_name, render_url_to_pdf
    from security import make_pdf_access_token
    import os

    try:
        cols = request.args.get('cols', '1')
        user_id = session['user_id']
        token = make_pdf_access_token(setlist_id, user_id)
        internal = (os.getenv('SETSYNC_INTERNAL_URL') or 'http://127.0.0.1:5000').rstrip('/')
        pdf_url = (
            f'{internal}/setlists/{setlist_id}/imprimir'
            f'?cols={cols}&pdfgen=1&pdf_token={token}'
        )
        pdf_bytes = render_url_to_pdf(pdf_url)
    except Exception as exc:
        flash(f'Não foi possível gerar o PDF: {exc}', 'danger')
        return redirect(url_for('setlists.imprimir', setlist_id=setlist_id))

    filename = build_pdf_download_name(data['setlist']['name'], data['band']['name'])
    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )


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
            cifra = get_cifra(cifra_id)
            song = (cifra or {}).get('titulo') or 'Música'
            bn.setlist_song_added(
                band['id'], user_id, setlist_id, setlist['name'], song,
            )
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
    cifra = get_cifra(cifra_id)
    song = (cifra or {}).get('titulo') or 'Música'
    remove_cifra_from_setlist(setlist_id, cifra_id)
    bn.setlist_song_removed(
        setlist['band_id'], user_id, setlist_id, setlist['name'], song,
    )
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
    setlist_name = setlist['name']
    delete_setlist(setlist_id)
    bn.setlist_deleted(band_id, user_id, setlist_name)
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
        from monetizacao import check_limite, resposta_limite_plano
        if not check_limite(band, 'setlist'):
            resp = resposta_limite_plano()
            if resp:
                return resp
        setlist_id = create_setlist(band_id, name, description)
        bn.setlist_created(band_id, user_id, setlist_id, name)
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
        return jsonify({'ok': False, 'error': 'Cantora/cantor inválido'}), 400
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
        return jsonify({'ok': False, 'error': 'Cantora/cantor inválido'}), 400
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
