import sys
import os
import json
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from blueprints.auth import login_required
from db import (get_band, get_cifra, get_band_cifras, create_cifra, update_cifra,
                delete_cifra, is_band_member, is_band_admin)
from util import (transpose_text, get_available_tones, pychord_transpose_text,
                  pychord_highlight_chords, highlight_chords_html,
                  split_chord_progression, chord_components_info,
                  to_brazilian_chord_notation, format_text_chords_br,
                  get_transposition_options, key_at_transpose, get_absolute_key_list,
                  build_transpose_map, parse_tom_root)

cifras_bp = Blueprint('cifras', __name__, url_prefix='/cifras')


def _parse_extra_fields(form):
    """Extrai e valida cifra_json, grade_json, bpm e duracao_seg do FormData.
    Retorna (cifra_json, grade_json, bpm, duracao_seg).
    Em caso de JSON inválido, faz flash de erro e retorna False no campo inválido.
    """
    cifra_json_raw = form.get('cifra_json', '').strip()
    grade_json_raw = form.get('grade_json', '').strip()
    bpm_raw = form.get('bpm', '').strip()
    duracao_seg_raw = form.get('duracao_seg', '').strip()

    cifra_json = None
    if cifra_json_raw:
        try:
            json.loads(cifra_json_raw)
            cifra_json = cifra_json_raw
        except ValueError:
            flash('JSON da cifra inválido — verifique o formato', 'danger')
            return False, None, None, None

    grade_json = None
    if grade_json_raw:
        try:
            json.loads(grade_json_raw)
            grade_json = grade_json_raw
        except ValueError:
            flash('JSON da grade inválido — verifique o formato', 'danger')
            return None, False, None, None

    bpm = float(bpm_raw) if bpm_raw else None
    duracao_seg = int(float(duracao_seg_raw)) if duracao_seg_raw else None

    return cifra_json, grade_json, bpm, duracao_seg


def _group_cifra_data(data):
    """Agrupa entradas do cifra_json pelo campo 'group' para exibir acorde acima da sílaba.
    Entradas sem campo 'group' (formato setsync_cifra.json) ficam em um único grupo."""
    if not data:
        return []
    if 'group' not in data[0]:
        return [data]
    groups = []
    current_g = None
    current_items = []
    for item in data:
        g = item.get('group', 0)
        if g != current_g:
            if current_items:
                groups.append(current_items)
            current_g = g
            current_items = [item]
        else:
            current_items.append(item)
    if current_items:
        groups.append(current_items)
    return groups


def _parse_conteudo_to_cifra_data(conteudo):
    """Parse simples do conteudo textual para estrutura cifra_json-like.

    Focado em preservar espacos no formato com colchetes, incluindo texto
    antes do primeiro acorde na linha.
    """
    text = (conteudo or '').replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    result = []
    seq = 0
    group = 0

    for line in lines:
        if not line.strip():
            group += 1
            continue

        if '[' in line and ']' in line:
            re_br = re.compile(r'\[([^\]]+)\]([^\[]*)')
            last = 0
            matched = False
            for m in re_br.finditer(line):
                matched = True
                if m.start() > last:
                    prefixo = line[last:m.start()]
                    if prefixo:
                        result.append({
                            'segundo': seq,
                            'texto_letra': prefixo,
                            'acorde': '',
                            'group': group,
                        })
                        seq += 1

                result.append({
                    'segundo': seq,
                    'texto_letra': (m.group(2) or ''),
                    'acorde': (m.group(1) or '').strip(),
                    'group': group,
                })
                seq += 1
                last = m.end()

            if matched and last < len(line):
                sufixo = line[last:]
                if sufixo:
                    result.append({
                        'segundo': seq,
                        'texto_letra': sufixo,
                        'acorde': '',
                        'group': group,
                    })
                    seq += 1

            if matched:
                group += 1
                continue

        # Fallback para linha sem colchetes: conserva como letra pura
        result.append({
            'segundo': seq,
            'texto_letra': line,
            'acorde': '',
            'group': group,
        })
        seq += 1
        group += 1

    return result


def _space_count(cifra_data):
    if not cifra_data:
        return 0
    total = 0
    for item in cifra_data:
        total += str(item.get('texto_letra') or '').count(' ')
    return total


def _load_best_structured_cifra(cifra, semitones=0):
    """Carrega cifra estruturada preferindo conteudo quando detecta JSON legado colado."""
    parsed = None
    raw_structured = cifra.get('cifra_json')
    if raw_structured:
        try:
            parsed = json.loads(raw_structured)
        except (ValueError, TypeError):
            parsed = None

    fallback = _parse_conteudo_to_cifra_data(cifra.get('conteudo') or '')

    use_fallback = parsed is None
    if parsed is not None and fallback:
        parsed_spaces = _space_count(parsed)
        fallback_spaces = _space_count(fallback)
        # Heuristica para detectar legado onde espacos foram "colados".
        if fallback_spaces >= parsed_spaces + 3:
            use_fallback = True

    data = fallback if use_fallback else parsed
    if not data:
        return []

    if semitones:
        for item in data:
            if item.get('acorde'):
                item['acorde'] = pychord_transpose_text(item['acorde'], semitones)

    for item in data:
        if item.get('acorde'):
            item['acorde'] = to_brazilian_chord_notation(item['acorde'])

    return data


def _transpose_grade_data(grade_list, semitones=0):
    """Transpõe acordes da grade harmônica, preservando '%' (repeat)."""
    result = []
    for comp in grade_list:
        comp = dict(comp)
        acordes = []
        for token in comp.get('acordes', []):
            if token == '%':
                acordes.append('%')
            elif semitones:
                acordes.append(pychord_transpose_text(token, semitones))
            else:
                acordes.append(to_brazilian_chord_notation(token))
        comp['acordes'] = acordes
        result.append(comp)
    return result


def enrich_cifra_for_tocar(cifra):
    """Prepara cifra para o modo tocar com dados estruturados corretos."""
    c = dict(cifra)
    structured = _load_best_structured_cifra(c, 0)
    c['cifra_structured'] = structured if structured else None
    c['tom_root'] = parse_tom_root(c.get('tom_original'))
    c['transpose_map'] = build_transpose_map(c.get('tom_original'))
    return c


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

    transpositions = get_transposition_options(cifra['tom_original'])
    current_transpose = request.args.get('transpose', 0, type=int)
    display_key = key_at_transpose(cifra['tom_original'], current_transpose)

    conteudo = cifra['conteudo'] or ''
    # Transpor usando pychord se possível
    if current_transpose != 0:
        conteudo = pychord_transpose_text(conteudo, current_transpose)
    conteudo = format_text_chords_br(conteudo)

    # Parsear cifra_json e grade_json
    cifra_data = _load_best_structured_cifra(cifra, current_transpose)

    grade_data = None
    if cifra.get('grade_json'):
        try:
            raw_g = json.loads(cifra['grade_json'])
            grade_data = _transpose_grade_data(raw_g, current_transpose)
        except (ValueError, TypeError):
            pass

    grouped_cifra = _group_cifra_data(cifra_data) if cifra_data else None
    setlist = get_band_cifras(cifra['band_id'])
    cifra_index = next((i for i, c in enumerate(setlist) if c['id'] == cifra_id), 0)
    prev_cifra = setlist[cifra_index - 1] if cifra_index > 0 else None
    next_cifra = setlist[cifra_index + 1] if cifra_index < len(setlist) - 1 else None

    return render_template('cifras/view.html',
                           cifra=cifra,
                           band=band,
                           conteudo=conteudo,
                           cifra_data=cifra_data,
                           grade_data=grade_data,
                           grouped_cifra=grouped_cifra,
                           transpositions=transpositions,
                           current_transpose=current_transpose,
                           display_key=display_key,
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

    all_cifras = [enrich_cifra_for_tocar(c) for c in get_band_cifras(band_id)]
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
        key_options=get_absolute_key_list(),
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
        if not titulo or not artista:
            flash('Preencha título e artista', 'danger')
            return render_template('cifras/add.html', band=band)

        cifra_json, grade_json, bpm, duracao_seg = _parse_extra_fields(request.form)
        if cifra_json is False or grade_json is False:
            return render_template('cifras/add.html', band=band)

        cifra_id = create_cifra(titulo, artista, tom_original, conteudo or '',
                                band_id, cifra_json, grade_json, bpm, duracao_seg)
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
        if not titulo or not artista:
            flash('Preencha título e artista', 'danger')
            return render_template('cifras/edit.html', cifra=cifra, band=band)

        cifra_json_new, grade_json_new, bpm, duracao_seg = _parse_extra_fields(request.form)
        if cifra_json_new is False or grade_json_new is False:
            return render_template('cifras/edit.html', cifra=cifra, band=band)

        # Mantém valores existentes se nada novo foi enviado
        cifra_json = cifra_json_new if cifra_json_new is not None else cifra.get('cifra_json')
        grade_json = grade_json_new if grade_json_new is not None else cifra.get('grade_json')
        if bpm is None:
            bpm = cifra.get('bpm')
        if duracao_seg is None:
            duracao_seg = cifra.get('duracao_seg')

        update_cifra(cifra_id, titulo, artista, tom_original, conteudo,
                     cifra_json, grade_json, bpm, duracao_seg)
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
    """API para obter cifra transposta via AJAX.

    Suporta:
    - ?html=1 para HTML destacado (conteudo)
    - ?structured=1 para retornar cifra_json transposta
    - ?grade=1 para retornar grade_json transposta
    """
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)

    if not cifra or not is_band_member(cifra['band_id'], user_id):
        return jsonify({'error': 'Sem acesso'}), 403

    semitones = request.args.get('semitones', 0, type=int)
    want_html = request.args.get('html', '0') == '1'
    want_structured = request.args.get('structured', '0') == '1'
    want_grade = request.args.get('grade', '0') == '1'

    raw = cifra['conteudo'] or ''
    transposed = pychord_transpose_text(raw, semitones) if semitones else raw
    transposed = format_text_chords_br(transposed)

    payload = {
        'tom_original': cifra['tom_original'],
        'semitones': semitones,
        'display_key': key_at_transpose(cifra['tom_original'], semitones),
    }
    if want_html:
        payload['html'] = highlight_chords_html(transposed)
    else:
        payload['conteudo'] = transposed

    if want_structured:
        structured_data = _load_best_structured_cifra(cifra, semitones)
        payload['cifra_data'] = structured_data

    if want_grade:
        grade_data = []
        raw_grade = cifra.get('grade_json')
        if raw_grade:
            try:
                parsed_grade = json.loads(raw_grade)
                grade_data = _transpose_grade_data(parsed_grade, semitones)
            except (ValueError, TypeError):
                grade_data = []
        payload['grade_data'] = grade_data

    return jsonify(payload)


@cifras_bp.route('/chord-info', methods=['GET'])
@login_required
def chord_info():
    """Retorna notas/componentes de um acorde (ou progressão) para diagramas."""
    symbol = request.args.get('symbol', '').strip()
    if not symbol:
        return jsonify({'error': 'Acorde não informado'}), 400

    chunks = split_chord_progression(symbol)
    if not chunks:
        chunks = [symbol]

    result = []
    for chunk in chunks:
        info = chord_components_info(chunk)
        if info:
            info['display'] = to_brazilian_chord_notation(info.get('display', chunk))
            result.append(info)

    return jsonify({'chords': result})
