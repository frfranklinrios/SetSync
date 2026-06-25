import sys
import os
import copy
import json
import re
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from leadsheet.audio import ALLOWED_AUDIO_EXTENSIONS, analyze_audio_for_leadsheet
from leadsheet.build import build_payload
from leadsheet.converter import (
    is_leadsheet_document,
    leadsheet_to_grade_flat,
    resolve_leadsheet_document,
    resolve_to_grade_flat,
)
from blueprints.auth import login_required
from db import (get_band, get_cifra, get_band_cifras, count_band_cifras, create_cifra, update_cifra,
                delete_cifra, is_band_member, is_band_admin, is_band_editor,
                set_cifra_transpose_semitones, get_band_vocalists, get_band_vocalist,
                get_cifra_vocalist_transpose, get_cifra_transpose_by_vocalists,
                band_vocalist_belongs_to_band, vocalists_summary_label,
                vocalist_entry_display_name, update_cifra_referencia,
                restore_cifra_from_referencia,
                get_cifra_user_draft, upsert_cifra_user_draft, delete_cifra_user_draft,
                publish_cifra_user_draft)
import band_notifications as bn

def _notify_band_realtime(band_id, event: str, **data) -> None:
    try:
        from blueprints.realtime import notify_band
        notify_band(str(band_id), event, dict(data))
    except Exception:
        pass

from util import (transpose_text, get_available_tones, pychord_transpose_text,
                  pychord_highlight_chords, highlight_chords_html,
                  split_chord_progression, chord_components_info,
                  to_brazilian_chord_notation, format_text_chords_br,
                  get_transposition_options, key_at_transpose, get_absolute_key_list,
                  build_transpose_map, parse_tom_root, normalize_transpose_semitones,
                  normalize_tom_label,
                  sanitize_tab_html_artifacts, content_has_tablatura,
                  highlight_chords_play_html, render_grouped_cifra_html,
                  _is_tab_line, _is_tab_header, _is_tab_meta_line, _TAB_ARTIFACT_RE)
from config import app_now_naive, app_now_str

cifras_bp = Blueprint('cifras', __name__, url_prefix='/cifras')

PLAY_TARGET_KEY_SESSION = 'play_target_key'
VOCALIST_SESSION_PREFIX = 'band_vocalist:'


def _vocalist_session_key(band_id: str) -> str:
    return f'{VOCALIST_SESSION_PREFIX}{band_id}'


def get_active_vocalist_id(
    band_id: str,
    vocalist_id: str | None = None,
    setlist_id=None,
) -> str | None:
    """Cantor ativo: parâmetro, setlist, sessão ou primeiro da lista."""
    if not band_id:
        return None
    vocalists = get_band_vocalists(band_id)
    if not vocalists:
        return None
    ids = {v['id'] for v in vocalists}

    def _store(vid: str) -> str:
        session[_vocalist_session_key(band_id)] = vid
        session.modified = True
        return vid

    if vocalist_id and vocalist_id in ids:
        return _store(vocalist_id)
    q = request.args.get('vocalist', '').strip() if request else ''
    if q and q in ids:
        return _store(q)
    if setlist_id:
        from models_setlist import get_setlist
        sl = get_setlist(setlist_id)
        if sl:
            sv = sl.get('vocalist_id')
            if sv and sv in ids:
                return sv
    stored = session.get(_vocalist_session_key(band_id))
    if stored and stored in ids:
        return stored
    return vocalists[0]['id']


def active_vocalist_label(
    band_id: str,
    vocalist_id: str | None = None,
    setlist_id=None,
) -> str | None:
    vid = get_active_vocalist_id(band_id, vocalist_id, setlist_id=setlist_id)
    if not vid:
        return None
    v = get_band_vocalist(vid)
    name = vocalist_entry_display_name(v) if v else None
    return name or None


def vocalist_label_for_band(band_id: str) -> str | None:
    return vocalists_summary_label(band_id)


def cifra_transpose_semitones(cifra, vocalist_id: str | None = None) -> int:
    """Semitons de transposição do cantor ativo ou legado na cifra."""
    if not cifra:
        return 0
    band_id = cifra.get('band_id')
    cid = cifra.get('id')
    if band_id and cid:
        vid = get_active_vocalist_id(band_id, vocalist_id)
        if vid:
            return get_cifra_vocalist_transpose(cid, vid)
    try:
        return int(cifra.get('transpose_semitones') or 0)
    except (TypeError, ValueError):
        return 0


def get_stored_transpose_semitones(cifra_id, vocalist_id: str | None = None):
    cifra = get_cifra(cifra_id)
    return cifra_transpose_semitones(cifra, vocalist_id) if cifra else 0


def cifra_display_key(cifra, vocalist_id: str | None = None, setlist_id=None):
    """Tom para exibir em listas: transposição do cantor ou cadastro."""
    if not cifra:
        return ''
    tom = (cifra.get('tom_original') or '').strip()
    if vocalist_id is None and setlist_id:
        vocalist_id = get_active_vocalist_id(cifra.get('band_id'), setlist_id=setlist_id)
    semi = normalize_transpose_semitones(cifra_transpose_semitones(cifra, vocalist_id))
    if semi:
        return key_at_transpose(tom, semi)
    return normalize_tom_label(tom)


def resolve_cifra_transpose(cifra_id, tom_original):
    """Transposição: ?transpose= grava para o cantor ativo; senão lê do banco."""
    cifra = get_cifra(cifra_id)
    band_id = cifra.get('band_id') if cifra else None
    vid = get_active_vocalist_id(band_id) if band_id else None
    if 'transpose' in request.args:
        semitones = normalize_transpose_semitones(request.args.get('transpose', 0, type=int))
        set_cifra_transpose_semitones(cifra_id, semitones, vocalist_id=vid)
    else:
        semitones = normalize_transpose_semitones(
            cifra_transpose_semitones(cifra, vid) if cifra else 0
        )

    if semitones:
        session[PLAY_TARGET_KEY_SESSION] = key_at_transpose(tom_original, semitones)
    elif 'transpose' in request.args:
        session.pop(PLAY_TARGET_KEY_SESSION, None)
    session.modified = True
    return semitones


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
            flash('JSON do chord sheet inválido — verifique o formato', 'danger')
            return None, False, None, None

    bpm = float(bpm_raw) if bpm_raw else None
    duracao_seg = int(float(duracao_seg_raw)) if duracao_seg_raw else None

    return cifra_json, grade_json, bpm, duracao_seg


def _parse_streaming_urls(form):
    apple = (form.get('apple_music_url') or '').strip()
    if apple and not apple.startswith(('http://', 'https://')):
        flash('URL do Apple Music inválida — use link completo (https://…)', 'danger')
        return False
    return apple or None


def _finalize_referencia_json(form, *, titulo, artista, tom_original):
    """Normaliza snapshot da biblioteca enviado pelo formulário (import api-cifras)."""
    raw = (form.get('referencia_json') or '').strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        flash('Referência da biblioteca inválida — importe a cifra novamente.', 'warning')
        return None
    if not isinstance(data, dict):
        return None

    from cifra_referencia import build_referencia_snapshot

    ref_titulo = (data.get('titulo') or titulo or '').strip()
    ref_artista = (data.get('artista') or artista or '').strip()
    ref_tom = (data.get('tom_original') or tom_original or 'C').strip()
    cifra_json_raw = data.get('cifra_json')
    if isinstance(cifra_json_raw, (list, dict)):
        cifra_json_raw = json.dumps(cifra_json_raw, ensure_ascii=False)

    conteudo_ref, cifra_json_ref = _prepare_conteudo_for_save(
        data.get('conteudo') or '',
        titulo=ref_titulo,
        artista=ref_artista,
        tom_original=ref_tom,
        cifra_json_raw=cifra_json_raw,
    )
    grade_json = data.get('grade_json')
    if isinstance(grade_json, (list, dict)):
        grade_json = json.dumps(grade_json, ensure_ascii=False)

    meta = data.get('meta') if isinstance(data.get('meta'), dict) else {}
    source = (data.get('source') or 'api-cifras').strip() or 'api-cifras'
    return build_referencia_snapshot(
        source=source,
        titulo=ref_titulo,
        artista=ref_artista,
        tom_original=ref_tom,
        conteudo=conteudo_ref,
        cifra_json=cifra_json_ref,
        grade_json=grade_json,
        meta=meta,
    )


def _referencia_context(cifra: dict | None) -> dict:
    from cifra_referencia import parse_referencia, referencia_diverged, referencia_label

    ref = parse_referencia(cifra)
    return {
        'cifra_referencia': ref,
        'cifra_referencia_label': referencia_label(cifra),
        'cifra_referencia_diverged': referencia_diverged(cifra) if ref else False,
    }


def _group_cifra_data(data):
    """Agrupa entradas do cifra_json pelo campo 'group' para exibir acorde acima da sílaba.
    Entradas sem campo 'group' (formato setsync_cifra.json) ficam em um único grupo."""
    if not data:
        return []
    if 'group' not in data[0]:
        groups = [data]
    else:
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
    return _normalize_grouped_sections(groups)


def _is_stored_comment_item(item: dict) -> bool:
    from chordpro import is_comment_line

    raw = (item.get('texto_letra') or '').strip()
    if (item.get('acorde') or '').strip():
        return False
    if is_comment_line(raw):
        return True
    if raw.lower().startswith('{comment'):
        return True
    return False


def _normalize_grouped_sections(groups):
    """Remove itens {comment: ...} da exibição (dados legados no cifra_json)."""
    if not groups:
        return groups

    flat: list[dict] = []
    for group in groups:
        for item in group:
            if _is_stored_comment_item(item):
                continue
            flat.append(dict(item))

    if not flat:
        return []

    if 'group' not in flat[0]:
        return [flat]

    rebuilt: list[list[dict]] = []
    current_g = None
    bucket: list[dict] = []
    for item in flat:
        g = item.get('group', 0)
        if g != current_g:
            if bucket:
                rebuilt.append(bucket)
            current_g = g
            bucket = [item]
        else:
            bucket.append(item)
    if bucket:
        rebuilt.append(bucket)
    return rebuilt


def _parse_conteudo_to_cifra_data(conteudo):
    """Parse ChordPro ou colchetes [Am] → estrutura cifra_json."""
    from chordpro import parse_conteudo_to_cifra_data
    return parse_conteudo_to_cifra_data(conteudo)


def _cifra_for_display(cifra: dict) -> dict:
    """Remove {comment: ...} do texto exibido no editor/visualização."""
    from chordpro import strip_comment_lines_from_text

    out = dict(cifra)
    raw = (out.get('conteudo') or '').strip()
    if raw:
        out['conteudo'] = strip_comment_lines_from_text(raw)
    return out


def _prepare_conteudo_for_save(conteudo, *, titulo, artista, tom_original, cifra_json_raw=None):
    """Converte para ChordPro no disco e alinha cifra_json ao corpo salvo."""
    from chordpro import conteudo_to_chordpro, cifra_json_from_conteudo

    from chordpro import strip_comment_lines_from_text

    conteudo_limpo = strip_comment_lines_from_text(conteudo or '')
    chordpro_body = conteudo_to_chordpro(
        conteudo_limpo,
        titulo=titulo or '',
        artista=artista or '',
        key=(tom_original or '').strip(),
    )
    parsed = cifra_json_from_conteudo(chordpro_body)
    cifra_json = json.dumps(parsed, ensure_ascii=False) if parsed else cifra_json_raw
    return chordpro_body, cifra_json


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

    from util import normalize_tom_label, transpose_chord_display

    tom_orig = normalize_tom_label(cifra.get('tom_original') or '')
    for item in data:
        if item.get('acorde'):
            item['acorde'] = transpose_chord_display(
                item['acorde'], semitones, tom_orig or 'C',
            )

    return data


def _transpose_grade_data(grade_list, semitones=0, tom_origem=None):
    """Transpõe acordes da grade harmônica, preservando '%' (repeat)."""
    from util import normalize_tom_label, transpose_chord_display

    tom = normalize_tom_label(tom_origem or 'C')
    result = []
    for comp in grade_list:
        comp = dict(comp)
        acordes = []
        for token in comp.get('acordes', []):
            if token == '%':
                acordes.append('%')
            else:
                acordes.append(transpose_chord_display(token, semitones, tom))
        comp['acordes'] = acordes
        result.append(comp)
    return result


def _load_display_grade_data(cifra, semitones=0):
    """LeadSheet (ou grade legada) convertida para exibição no modo tocar/visualização."""
    flat = resolve_to_grade_flat(cifra)
    if not flat:
        return None
    return _transpose_grade_data(flat, semitones, cifra.get('tom_original'))


def _transpose_leadsheet(doc: dict, semitones: int, tom_fallback: str | None = None) -> dict:
    """Transpõe acordes do documento LeadSheet."""
    if not semitones:
        return doc
    out = copy.deepcopy(doc)
    from util import normalize_tom_label, transpose_chord_display

    song = out.setdefault('song', {})
    tom_origem = normalize_tom_label(
        (song.get('key') or '').strip() or tom_fallback or 'C'
    )
    for evt in out.get('events') or []:
        if isinstance(evt, dict) and evt.get('type') == 'chord' and evt.get('value'):
            evt['value'] = transpose_chord_display(str(evt['value']), semitones, tom_origem)
    if song.get('key'):
        song['key'] = key_at_transpose(tom_origem, semitones)
    return out


def _load_display_leadsheet(cifra, semitones=0):
    """Documento LeadSheet para o modo tocar (com transposição opcional)."""
    doc = resolve_leadsheet_document(cifra)
    if not doc:
        return None
    if semitones:
        return _transpose_leadsheet(doc, semitones, cifra.get('tom_original'))
    return doc


def _lyrics_at_semitones(cifra, semitones=0):
    """Letra sem acordes, transposta conforme semitones."""
    from setlist_public import clean_lyrics_for_public, conteudo_to_lyrics_plain

    data = _load_best_structured_cifra(cifra, semitones)
    if data:
        blocks: list[str] = []
        for group in _group_cifra_data(data):
            parts = [str(item.get('texto_letra') or '') for item in group if item.get('texto_letra')]
            line = ''.join(parts).strip()
            if line:
                blocks.append(line)
        if blocks:
            return clean_lyrics_for_public('\n\n'.join(blocks))

    raw = sanitize_tab_html_artifacts(cifra.get('conteudo') or '')
    if semitones:
        raw = pychord_transpose_text(raw, semitones, cifra.get('tom_original'))
    raw = format_text_chords_br(raw, key_at_transpose(cifra.get('tom_original'), semitones))
    return conteudo_to_lyrics_plain(raw)


def _grade_flat_to_print_html(grade_list):
    """HTML simples da grade para impressão quando não há cifra linha a linha."""
    if not grade_list:
        return ''
    from markupsafe import escape

    parts = []
    bloco = []

    def flush_bloco():
        if not bloco:
            return
        bars = []
        for comp in bloco:
            cells = []
            for token in comp.get('acordes') or []:
                if token == '%':
                    cells.append('%')
                elif token:
                    cells.append(escape(str(token).strip()))
            if cells:
                bars.append(' · '.join(cells))
        if bars:
            parts.append(
                '<p class="setlist-print-grade-line">' + ' &nbsp;|&nbsp; '.join(bars) + '</p>'
            )
        bloco.clear()

    for comp in grade_list:
        comp = dict(comp)
        if comp.get('secao'):
            flush_bloco()
            parts.append(
                '<p class="setlist-print-grade-sec"><strong>'
                + escape(str(comp['secao']))
                + '</strong></p>'
            )
        bloco.append(comp)
    flush_bloco()
    return ''.join(parts)


def prepare_cifra_sheet(cifra, semitones=0, viewer_user_id=None):
    """Monta cifra transposta para exibição/impressão (mesma lógica da página ver cifra)."""
    semi = int(semitones or 0)
    tom_orig = normalize_tom_label(cifra.get('tom_original') or '')
    display_key = key_at_transpose(tom_orig, semi) if semi else tom_orig

    from chordpro import strip_comment_lines_from_text

    conteudo = sanitize_tab_html_artifacts(cifra.get('conteudo') or '')
    conteudo = strip_comment_lines_from_text(conteudo)
    if semi:
        conteudo = pychord_transpose_text(conteudo, semi, tom_orig)
    conteudo = format_text_chords_br(conteudo, key_at_transpose(tom_orig, semi))

    cifra_data = _load_best_structured_cifra(cifra, semi)
    grouped_cifra = _group_cifra_data(cifra_data) if cifra_data else None
    has_tab = content_has_tablatura(conteudo)
    conteudo_html = None
    grade_html = None

    if has_tab:
        grouped_cifra = None
        conteudo_html = highlight_chords_play_html(conteudo)
    elif not grouped_cifra and (conteudo or '').strip():
        conteudo_html = highlight_chords_play_html(conteudo)
    elif not grouped_cifra and not conteudo_html:
        grade_data = _load_display_grade_data(cifra, semi)
        if grade_data:
            grade_html = _grade_flat_to_print_html(grade_data)

    lyrics_plain = _lyrics_at_semitones(cifra, semi)
    chordsheet_html = None
    from chordsheet_bridge import cifra_has_chordsheet, render_cifra_chordsheet_html

    if cifra_has_chordsheet(cifra):
        chordsheet_html = render_cifra_chordsheet_html(
            cifra, semitones=semi, display_key=display_key,
            viewer_user_id=viewer_user_id,
        )

    return {
        'titulo': cifra.get('titulo') or 'Sem título',
        'artista': (cifra.get('artista') or '').strip(),
        'display_key': display_key,
        'tom_original': tom_orig,
        'semitones': semi,
        'grouped_cifra': grouped_cifra,
        'conteudo_html': conteudo_html,
        'grade_html': grade_html,
        'lyrics_plain': lyrics_plain,
        'chordsheet_html': chordsheet_html,
        'has_content': bool(grouped_cifra or conteudo_html or grade_html),
        'has_lyrics': bool((lyrics_plain or '').strip()),
        'has_chordsheet': bool(chordsheet_html),
    }


def _persist_leadsheet(cifra_id, payload: dict, meta: dict | None = None) -> None:
    """Salva LeadSheet, metadados da cifra e mantém grade_json legada sincronizada."""
    cifra = get_cifra(cifra_id)
    if not cifra:
        return
    meta = meta or {}
    flat = leadsheet_to_grade_flat(payload)
    leadsheet_json = json.dumps(payload, ensure_ascii=False)
    grade_json = json.dumps(flat, ensure_ascii=False) if flat else None
    song = payload.get("song") or {}
    audio = payload.get("audio") or {}
    bpm = song.get("tempo_bpm")
    dur = audio.get("duration_seconds")
    duracao_seg = int(dur) if dur else cifra.get("duracao_seg")
    update_cifra(
        cifra_id,
        meta.get("titulo") or cifra["titulo"],
        meta.get("artista") or cifra["artista"],
        meta.get("tom_original") or cifra["tom_original"],
        cifra["conteudo"],
        cifra.get("cifra_json"),
        grade_json,
        leadsheet_json,
        bpm if bpm is not None else cifra.get("bpm"),
        duracao_seg,
    )


def _effective_cifra_for_versao(cifra, user_id, versao=None):
    """Retorna cifra oficial ou mesclada com rascunho pessoal (?versao=minha)."""
    from cifra_user_draft import draft_differs_from_band, merge_cifra_with_draft

    if versao != 'minha' or not user_id:
        return cifra
    draft = get_cifra_user_draft(cifra['id'], user_id)
    if draft and draft_differs_from_band(draft, cifra):
        return merge_cifra_with_draft(cifra, draft)
    return cifra


def _enrich_single_cifra_for_tocar(cifra, setlist_id=None):
    """Prepara uma cifra (fonte banda ou mesclada) para o modo tocar."""
    c = dict(cifra)
    band_id = c.get('band_id')
    active_vid = get_active_vocalist_id(band_id, setlist_id=setlist_id) if band_id else None
    c['tom_original'] = normalize_tom_label(c.get('tom_original') or '')
    raw = sanitize_tab_html_artifacts(c.get('conteudo') or '')
    has_tab = content_has_tablatura(raw)
    structured = _load_best_structured_cifra(c, 0)
    c['cifra_structured'] = structured if structured else None
    grouped = _group_cifra_data(structured) if structured else None
    if grouped:
        c['html'] = render_grouped_cifra_html(grouped)
    else:
        c['html'] = highlight_chords_play_html(raw)
    c['tom_root'] = parse_tom_root(c.get('tom_original'))
    c['transpose_map'] = build_transpose_map(c.get('tom_original'))
    if band_id:
        c['transpose_by_vocalist'] = {
            vid: normalize_transpose_semitones(semi)
            for vid, semi in get_cifra_transpose_by_vocalists(c['id'], band_id).items()
        }
    else:
        c['transpose_by_vocalist'] = {}
    c['transpose_semitones'] = normalize_transpose_semitones(cifra_transpose_semitones(c, active_vid))
    c['has_tablatura'] = has_tab
    c['lyrics_plain'] = _lyrics_at_semitones(c, c.get('transpose_semitones') or 0)
    doc = resolve_leadsheet_document(c)
    if doc:
        c['leadsheet_json'] = json.dumps(doc, ensure_ascii=False)
    flat = resolve_to_grade_flat(c)
    if flat:
        c['grade_json'] = json.dumps(flat, ensure_ascii=False)
    return c


def enrich_cifra_for_tocar(cifra, setlist_id=None, user_id=None):
    """Prepara cifra para o modo tocar; inclui campos da versão pessoal quando existir."""
    from cifra_user_draft import draft_differs_from_band, merge_cifra_with_draft

    result = _enrich_single_cifra_for_tocar(cifra, setlist_id=setlist_id)
    result['has_personal_draft'] = False

    if user_id:
        draft = get_cifra_user_draft(cifra['id'], user_id)
        if draft and draft_differs_from_band(draft, cifra):
            personal = _enrich_single_cifra_for_tocar(
                merge_cifra_with_draft(cifra, draft), setlist_id=setlist_id
            )
            result['has_personal_draft'] = True
            result['html_mine'] = personal['html']
            result['cifra_structured_mine'] = personal.get('cifra_structured')
            result['lyrics_plain_mine'] = personal.get('lyrics_plain')
            result['has_tablatura_mine'] = personal.get('has_tablatura')
            result['tom_original_mine'] = personal.get('tom_original')
            result['tom_root_mine'] = personal.get('tom_root')
            result['transpose_map_mine'] = personal.get('transpose_map')
            result['grade_s_mine'] = personal.get('grade_json')
            result['leadsheet_s_mine'] = personal.get('leadsheet_json')
            if personal.get('titulo') != result.get('titulo'):
                result['titulo_mine'] = personal.get('titulo')
            if personal.get('artista') != result.get('artista'):
                result['artista_mine'] = personal.get('artista')

    return result


def _leadsheet_meta_value(cifra, field: str) -> str:
    """Extrai campo de meta do LeadSheet/chordsheet embutido na cifra."""
    for key in ('leadsheet_json', 'grade_json'):
        raw = cifra.get(key)
        if not raw:
            continue
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            meta = data.get('meta')
            if isinstance(meta, dict):
                val = meta.get(field)
                if val not in (None, ''):
                    return str(val).strip()
    doc = resolve_leadsheet_document(cifra)
    if not doc:
        return ''
    meta = doc.get('meta') if isinstance(doc, dict) else None
    if not meta:
        return ''
    val = meta.get(field)
    return str(val).strip() if val not in (None, '') else ''


def _resolve_play_notes(cifra) -> str:
    """Notas de palco: setlist sobrescreve notas gerais da cifra."""
    sl = (cifra.get('setlist_play_notes') or '').strip()
    if sl:
        return sl
    return (cifra.get('play_notes') or '').strip()


def play_cifra_client_payload(cifra, setlist_id=None, is_virtual=False):
    """Monta dict serializável para o JSON do modo tocar."""
    sl_id = None if is_virtual else setlist_id
    payload = {
        'id': cifra['id'],
        'titulo': cifra.get('titulo'),
        'artista': cifra.get('artista'),
        'tom': cifra_display_key(cifra, setlist_id=sl_id),
        'tom_original': cifra.get('tom_original'),
        'tom_root': cifra.get('tom_root'),
        'transpose_semitones': cifra.get('transpose_semitones') or 0,
        'transpose_by_vocalist': cifra.get('transpose_by_vocalist') or {},
        'transpose_map': cifra.get('transpose_map'),
        'has_tablatura': bool(cifra.get('has_tablatura')),
        'html': cifra.get('html'),
        'cifra_structured': cifra.get('cifra_structured'),
        'lyrics_plain': cifra.get('lyrics_plain') or '',
        'bpm': cifra.get('bpm'),
        'capo': _leadsheet_meta_value(cifra, 'capo') or cifra.get('capo') or '',
        'time_signature': _leadsheet_meta_value(cifra, 'time_signature') or '4/4',
        'duracao_seg': cifra.get('duracao_seg'),
        'play_notes': _resolve_play_notes(cifra),
        'grade_s': cifra.get('grade_json'),
        'leadsheet_s': cifra.get('leadsheet_json'),
        'has_personal_draft': bool(cifra.get('has_personal_draft')),
    }
    if payload['has_personal_draft']:
        payload.update({
            'html_mine': cifra.get('html_mine'),
            'cifra_structured_mine': cifra.get('cifra_structured_mine'),
            'lyrics_plain_mine': cifra.get('lyrics_plain_mine') or '',
            'has_tablatura_mine': cifra.get('has_tablatura_mine'),
            'tom_original_mine': cifra.get('tom_original_mine'),
            'tom_root_mine': cifra.get('tom_root_mine'),
            'transpose_map_mine': cifra.get('transpose_map_mine'),
            'grade_s_mine': cifra.get('grade_s_mine'),
            'leadsheet_s_mine': cifra.get('leadsheet_s_mine'),
        })
        if cifra.get('titulo_mine'):
            payload['titulo_mine'] = cifra['titulo_mine']
        if cifra.get('artista_mine'):
            payload['artista_mine'] = cifra['artista_mine']
    return payload


def play_cifras_json_for_client(all_cifras, setlist_id=None, is_virtual=False):
    """JSON seguro para embutir em <script type=\"application/json\">."""
    items = [
        play_cifra_client_payload(c, setlist_id=setlist_id, is_virtual=is_virtual)
        for c in all_cifras
    ]
    return json.dumps(items, ensure_ascii=False).replace('</', '<\\/')


def play_cifras_json_b64_for_client(all_cifras, setlist_id=None, is_virtual=False):
    """JSON em base64 — evita quebra do HTML por conteúdo da cifra no embed."""
    import base64

    raw = play_cifras_json_for_client(all_cifras, setlist_id=setlist_id, is_virtual=is_virtual)
    return base64.b64encode(raw.encode('utf-8')).decode('ascii')


@cifras_bp.route('/band/<band_id>/offline-pack.json')
@login_required
def offline_pack(band_id):
    """Pacote JSON para armazenamento offline (IndexedDB) no dispositivo."""
    from datetime import datetime

    user_id = session['user_id']
    band = get_band(band_id)
    if not band or not is_band_member(band_id, user_id):
        return jsonify({'detail': 'Sem acesso.'}), 403

    cifras = get_band_cifras(band_id)
    enriched = [
        enrich_cifra_for_tocar(c, user_id=user_id)
        for c in cifras
    ]
    payload = {
        'band_id': str(band_id),
        'band_name': band.get('name') or '',
        'saved_at': app_now_naive().strftime('%Y-%m-%dT%H:%M:%S'),
        'cifras': [play_cifra_client_payload(c) for c in enriched],
    }
    return jsonify(payload)


@cifras_bp.route('/<cifra_id>/play-notes', methods=['POST'])
@login_required
def save_cifra_play_notes(cifra_id):
    """Salva notas de palco gerais da música (banda)."""
    from db import get_cifra, set_cifra_play_notes

    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    if not cifra:
        return jsonify({'ok': False, 'error': 'Cifra não encontrada'}), 404
    if not is_band_editor(cifra['band_id'], user_id):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    data = request.get_json(silent=True) or {}
    notes = (data.get('play_notes') or '').strip()
    set_cifra_play_notes(cifra_id, notes or None)
    return jsonify({'ok': True, 'play_notes': notes})


@cifras_bp.route('/band/<band_id>')
@login_required
def list_by_band(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_member(band_id, user_id):
        flash('Sem acesso a essa banda', 'danger')
        return redirect(url_for('dashboard'))
    
    cifras = get_band_cifras(band_id)
    return render_template(
        'cifras/list.html',
        band=band,
        cifras=cifras,
        is_member=True,
        can_edit=is_band_editor(band_id, user_id),
        is_admin=is_band_admin(band_id, user_id),
    )

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

    from cifra_user_draft import draft_differs_from_band, merge_cifra_with_draft

    draft = get_cifra_user_draft(cifra_id, user_id)
    viewing_personal = request.args.get('versao') == 'minha' and draft
    display_source = merge_cifra_with_draft(cifra, draft) if viewing_personal else cifra
    has_personal_draft = bool(draft and draft_differs_from_band(draft, cifra))

    transpositions = get_transposition_options(display_source['tom_original'])
    current_transpose = resolve_cifra_transpose(cifra_id, display_source['tom_original'])
    display_key = key_at_transpose(display_source['tom_original'], current_transpose)

    display_source = _cifra_for_display(display_source)
    conteudo = sanitize_tab_html_artifacts(display_source['conteudo'] or '')
    if current_transpose != 0:
        conteudo = pychord_transpose_text(conteudo, current_transpose, display_source['tom_original'])
    conteudo = format_text_chords_br(conteudo, key_at_transpose(display_source['tom_original'], current_transpose))

    cifra_data = _load_best_structured_cifra(display_source, current_transpose)
    grade_data = _load_display_grade_data(display_source, current_transpose)
    leadsheet_document = _load_display_leadsheet(display_source, current_transpose)

    grouped_cifra = _group_cifra_data(cifra_data) if cifra_data else None
    has_tab = content_has_tablatura(conteudo)
    conteudo_html = None
    if grouped_cifra:
        conteudo_html = render_grouped_cifra_html(grouped_cifra)
    elif (conteudo or '').strip():
        conteudo_html = highlight_chords_play_html(conteudo)
    setlist = get_band_cifras(cifra['band_id'])
    cifra_index = next((i for i, c in enumerate(setlist) if c['id'] == cifra_id), 0)
    prev_cifra = setlist[cifra_index - 1] if cifra_index > 0 else None
    next_cifra = setlist[cifra_index + 1] if cifra_index < len(setlist) - 1 else None

    vocalists = get_band_vocalists(band['id'])
    active_vocalist_id = get_active_vocalist_id(band['id'])
    active_vocalist = get_band_vocalist(active_vocalist_id) if active_vocalist_id else None
    vocalist_name = vocalist_entry_display_name(active_vocalist) if active_vocalist else None
    vocalist_linked = bool(active_vocalist and active_vocalist.get('user_id'))

    from chordsheet_bridge import cifra_has_chordsheet
    from setlist_public import lyrics_from_cifra

    active_tab = (request.args.get('tab') or 'cifra').strip().lower()
    if active_tab not in ('cifra', 'chordsheet', 'letra'):
        active_tab = 'cifra'

    return render_template('cifras/view.html',
                           cifra=display_source,
                           band=band,
                           conteudo=conteudo,
                           conteudo_html=conteudo_html,
                           cifra_data=cifra_data,
                           grade_data=grade_data,
                           leadsheet_document=leadsheet_document,
                           has_chordsheet=cifra_has_chordsheet(display_source) or bool(leadsheet_document),
                           grouped_cifra=grouped_cifra,
                           lyrics_plain=lyrics_from_cifra(display_source, vocalist_id=active_vocalist_id),
                           active_tab=active_tab,
                           transpositions=transpositions,
                           current_transpose=current_transpose,
                           display_key=display_key,
                           setlist=setlist,
                           cifra_index=cifra_index,
                           prev_cifra=prev_cifra,
                           next_cifra=next_cifra,
                           vocalists=vocalists,
                           active_vocalist_id=active_vocalist_id,
                           vocalist_name=vocalist_name,
                           vocalist_linked=vocalist_linked,
                           is_admin=is_band_admin(cifra['band_id'], user_id),
                           is_member=is_band_member(cifra['band_id'], user_id),
                           can_edit=is_band_editor(cifra['band_id'], user_id),
                           viewing_personal=viewing_personal,
                           has_personal_draft=has_personal_draft,
                           can_publish_draft=is_band_editor(cifra['band_id'], user_id),
                           **_referencia_context(cifra))

def render_play_mode(setlist, band, all_cifras, start_idx=0, is_virtual=False, exit_url=None, event_context=None):
    """Renderiza o modo tocar (mesmo layout para banda e setlist)."""
    from flask import request as _req

    user_id = session.get('user_id')
    vocalists = get_band_vocalists(band['id']) if band else []
    sl_id = None if is_virtual or not setlist else setlist.get('id')
    active_vocalist_id = get_active_vocalist_id(band['id'], setlist_id=sl_id) if band else None
    vocalist_name = active_vocalist_label(band['id'], setlist_id=sl_id) if band else None
    can_edit = bool(band and user_id and is_band_editor(band['id'], user_id))
    play_state_url = None
    offline_pack_url = None
    play_notes_url_tpl = None
    if band and band.get('id'):
        from flask import url_for as _url_for
        play_state_url = _url_for('realtime.set_play_state', band_id=band['id'])
        if setlist and not is_virtual and setlist.get('id'):
            offline_pack_url = _url_for('setlists.offline_pack', setlist_id=setlist['id'])
            play_notes_url_tpl = _url_for(
                'setlists.set_cifra_play_notes', setlist_id=setlist['id'], cifra_id='__ID__'
            )
        else:
            offline_pack_url = _url_for('cifras.offline_pack', band_id=band['id'])
            play_notes_url_tpl = _url_for('cifras.save_cifra_play_notes', cifra_id='__ID__')
    return render_template(
        'cifras/play_mode.html',
        setlist=setlist,
        band=band,
        all_cifras=all_cifras,
        play_cifras_json=play_cifras_json_b64_for_client(
            all_cifras,
            setlist_id=sl_id,
            is_virtual=is_virtual,
        ),
        start_idx=start_idx,
        is_virtual=is_virtual,
        exit_url=exit_url,
        vocalists=vocalists,
        active_vocalist_id=active_vocalist_id,
        vocalist_name=vocalist_name,
        can_edit=can_edit,
        play_target_key=session.get(PLAY_TARGET_KEY_SESSION) or '',
        start_versao=(_req.args.get('versao') or '').strip().lower(),
        event_context=event_context,
        play_state_url=play_state_url,
        offline_pack_url=offline_pack_url,
        play_notes_url_tpl=play_notes_url_tpl,
        user_id=user_id,
        auto_follow_leader=bool(event_context),
    )


@cifras_bp.route('/band/<band_id>/tocar')
@login_required
def tocar_band(band_id):
    """Modo tocar usando todas as cifras da banda como setlist virtual."""
    user_id = session['user_id']
    band = get_band(band_id)

    if not band or not is_band_member(band_id, user_id):
        flash('Sem acesso a essa banda', 'danger')
        return redirect(url_for('dashboard'))

    from db import mark_user_play_mode_used
    from product_funnel import log_funnel_step
    mark_user_play_mode_used(user_id)
    log_funnel_step(user_id, 'play_mode')

    all_cifras = [
        enrich_cifra_for_tocar(c, user_id=user_id) for c in get_band_cifras(band_id)
    ]
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
    return render_play_mode(
        virtual_setlist, band, all_cifras, start_idx=start_idx, is_virtual=True
    )


@cifras_bp.route('/band/<band_id>/add', methods=['GET', 'POST'])
@login_required
def add(band_id):
    user_id = session['user_id']
    band = get_band(band_id)
    
    if not band or not is_band_editor(band_id, user_id):
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

        from monetizacao import check_limite, resposta_limite_plano, LIMITES_GRATIS
        if not check_limite(band, 'musica'):
            resp = resposta_limite_plano('músicas', LIMITES_GRATIS['musica'])
            if resp:
                return resp

        cifras_antes = count_band_cifras(band_id)
        cifra_json, grade_json, bpm, duracao_seg = _parse_extra_fields(request.form)
        if cifra_json is False or grade_json is False:
            return render_template('cifras/add.html', band=band)

        conteudo, cifra_json = _prepare_conteudo_for_save(
            conteudo,
            titulo=titulo,
            artista=artista,
            tom_original=tom_original,
            cifra_json_raw=cifra_json,
        )

        referencia_json = _finalize_referencia_json(
            request.form,
            titulo=titulo,
            artista=artista,
            tom_original=tom_original,
        )

        cifra_id = create_cifra(titulo, artista, tom_original, conteudo or '',
                                band_id, cifra_json, grade_json, None, bpm, duracao_seg,
                                referencia_json=referencia_json)
        streaming = _parse_streaming_urls(request.form)
        if streaming is False:
            return render_template('cifras/add.html', band=band)
        from db import update_cifra_streaming
        update_cifra_streaming(cifra_id, streaming)
        if cifras_antes == 0:
            from google_ads import mark_funnel_event
            from product_funnel import log_funnel_step
            mark_funnel_event('primeira_cifra')
            log_funnel_step(user_id, 'primeira_cifra')
        bn.cifra_created(band_id, user_id, cifra_id, titulo)
        flash(f'Cifra "{titulo}" adicionada!', 'success')
        return redirect(url_for('cifras.view', cifra_id=cifra_id))

    return render_template('cifras/add.html', band=band)

def _edit_page_context(cifra, band, active_tab=None, user_id=None):
    from chordsheet.examples import EXAMPLES
    from chordsheet_bridge import load_editor_initial
    from setlist_public import lyrics_from_cifra
    from cifra_user_draft import draft_differs_from_band, merge_cifra_with_draft

    tab = (active_tab or request.args.get('tab') or 'cifra').strip().lower()
    if tab not in ('cifra', 'chordsheet', 'letra'):
        tab = 'cifra'
    draft = get_cifra_user_draft(cifra['id'], user_id) if user_id else None
    display_cifra = merge_cifra_with_draft(cifra, draft) if draft else cifra
    initial = load_editor_initial(display_cifra, user_id=user_id)
    examples_public = {
        key: {
            'title': ex.get('title', key),
            'meta': ex.get('meta') or {},
            'source': ex.get('source') or '',
        }
        for key, ex in EXAMPLES.items()
    }
    return {
        'cifra': _cifra_for_display(display_cifra),
        'band': band,
        'active_tab': tab,
        'lyrics_plain': lyrics_from_cifra(display_cifra),
        'chordsheet_initial': initial,
        'chordsheet_examples': examples_public,
        'has_personal_draft': bool(draft and draft_differs_from_band(draft, cifra)),
        'can_publish_draft': is_band_editor(band['id'], user_id) if user_id else False,
        **_referencia_context(cifra),
    }


@cifras_bp.route('/<cifra_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(cifra_id):
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    
    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    
    band = get_band(cifra['band_id'])
    
    if not is_band_editor(cifra['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip() or cifra['titulo']
        artista = request.form.get('artista', '').strip() or cifra['artista']
        tom_original = request.form.get('tom_original', cifra['tom_original']).strip()
        conteudo = request.form.get('conteudo', '').strip() or cifra['conteudo']
        if not titulo or not artista:
            flash('Preencha título e artista', 'danger')
            cifra['titulo'] = titulo
            cifra['artista'] = artista
            cifra['tom_original'] = tom_original
            cifra['conteudo'] = conteudo
            return render_template('cifras/edit.html', **_edit_page_context(cifra, band, user_id=user_id))

        cifra_json_new, grade_json_new, bpm, duracao_seg = _parse_extra_fields(request.form)
        if cifra_json_new is False or grade_json_new is False:
            return render_template('cifras/edit.html', **_edit_page_context(cifra, band, user_id=user_id))

        # Mantém valores existentes se nada novo foi enviado
        cifra_json = cifra_json_new if cifra_json_new is not None else cifra.get('cifra_json')
        grade_json = grade_json_new if grade_json_new is not None else cifra.get('grade_json')
        leadsheet_json = cifra.get('leadsheet_json')
        if grade_json_new:
            try:
                parsed_g = json.loads(grade_json_new)
                if is_leadsheet_document(parsed_g):
                    leadsheet_json = grade_json_new
                    flat = leadsheet_to_grade_flat(parsed_g)
                    grade_json = json.dumps(flat, ensure_ascii=False) if flat else grade_json_new
                    song = parsed_g.get('song') or {}
                    audio = parsed_g.get('audio') or {}
                    if song.get('tempo_bpm') is not None:
                        bpm = song['tempo_bpm']
                    if audio.get('duration_seconds') is not None:
                        duracao_seg = int(audio['duration_seconds'])
            except (TypeError, ValueError, json.JSONDecodeError):
                pass
        if bpm is None:
            bpm = cifra.get('bpm')
        if duracao_seg is None:
            duracao_seg = cifra.get('duracao_seg')

        conteudo, cifra_json = _prepare_conteudo_for_save(
            conteudo,
            titulo=titulo,
            artista=artista,
            tom_original=tom_original,
            cifra_json_raw=cifra_json,
        )

        update_cifra(cifra_id, titulo, artista, tom_original, conteudo,
                     cifra_json, grade_json, leadsheet_json, bpm, duracao_seg)

        streaming = _parse_streaming_urls(request.form)
        if streaming is False:
            return render_template('cifras/edit.html', **_edit_page_context(cifra, band, user_id=user_id))
        from db import update_cifra_streaming
        update_cifra_streaming(cifra_id, streaming)
        cifra['apple_music_url'] = streaming

        referencia_json = _finalize_referencia_json(
            request.form,
            titulo=titulo,
            artista=artista,
            tom_original=tom_original,
        )
        if referencia_json:
            update_cifra_referencia(cifra_id, referencia_json)

        bn.cifra_updated(cifra['band_id'], user_id, cifra_id, titulo)
        _notify_band_realtime(cifra['band_id'], 'cifra_updated', cifra_id=cifra_id, titulo=titulo)
        flash('Cifra atualizada!', 'success')
        return redirect(url_for('cifras.view', cifra_id=cifra_id))

    return render_template('cifras/edit.html', **_edit_page_context(cifra, band, user_id=user_id))


@cifras_bp.route('/<cifra_id>/restaurar-referencia', methods=['POST'])
@login_required
def restaurar_referencia(cifra_id):
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    if not is_band_editor(cifra['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('dashboard'))

    from cifra_referencia import parse_referencia
    if not parse_referencia(cifra):
        flash('Esta cifra não tem versão de referência salva.', 'warning')
        return redirect(url_for('cifras.edit', cifra_id=cifra_id))

    if not restore_cifra_from_referencia(cifra_id):
        flash('Não foi possível restaurar a cifra de referência.', 'danger')
        return redirect(url_for('cifras.edit', cifra_id=cifra_id))

    bn.cifra_updated(cifra['band_id'], user_id, cifra_id, cifra['titulo'])
    _notify_band_realtime(cifra['band_id'], 'cifra_updated', cifra_id=cifra_id, titulo=cifra['titulo'])
    flash('Cifra restaurada para a versão da biblioteca. As alterações da banda foram descartadas.', 'success')
    return redirect(url_for('cifras.edit', cifra_id=cifra_id, tab='cifra'))


@cifras_bp.route('/<cifra_id>/delete', methods=['POST'])
@login_required
def delete(cifra_id):
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    
    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    
    band = get_band(cifra['band_id'])
    
    if not is_band_editor(cifra['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('cifras.view', cifra_id=cifra_id))
    
    titulo = cifra['titulo']
    band_id = cifra['band_id']
    delete_cifra(cifra_id)
    bn.cifra_deleted(band_id, user_id, titulo)
    _notify_band_realtime(band_id, 'cifra_deleted', cifra_id=cifra_id, titulo=titulo)
    flash('Cifra deletada', 'success')
    return redirect(url_for('cifras.list_by_band', band_id=band_id))

@cifras_bp.route('/<cifra_id>/transpose', methods=['POST'])
@login_required
def save_transpose(cifra_id):
    """Salva transposição para o cantor(a) da banda (ou tom único se não houver cantor)."""
    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_member(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem acesso'}), 403
    data = request.get_json(silent=True) or {}
    semitones = normalize_transpose_semitones(int(data.get('semitones', 0)))
    band_id = cifra['band_id']
    vid = get_active_vocalist_id(band_id, data.get('vocalist_id'))
    set_cifra_transpose_semitones(cifra_id, semitones, vocalist_id=vid)
    tom = cifra.get('tom_original') or ''
    if semitones:
        session[PLAY_TARGET_KEY_SESSION] = key_at_transpose(tom, semitones)
    else:
        session.pop(PLAY_TARGET_KEY_SESSION, None)
    session.modified = True
    v = get_band_vocalist(vid) if vid else None
    vname = vocalist_entry_display_name(v) if v else None
    return jsonify({
        'ok': True,
        'semitones': semitones,
        'display_key': key_at_transpose(tom, semitones),
        'vocalist_id': vid,
        'vocalist_name': vname,
    })


@cifras_bp.route('/<cifra_id>/transpose', methods=['GET'])
@login_required
def get_transposed(cifra_id):
    """API para obter cifra transposta via AJAX.

    Suporta:
    - ?html=1 para HTML destacado (conteudo)
    - ?structured=1 para retornar cifra_json transposta
    - ?grade=1 para retornar grade_json transposta
    - ?lyrics=1 para letra sem acordes (transposta)
    """
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)

    if not cifra or not is_band_member(cifra['band_id'], user_id):
        return jsonify({'error': 'Sem acesso'}), 403

    cifra = _effective_cifra_for_versao(cifra, user_id, request.args.get('versao'))

    semitones = request.args.get('semitones', 0, type=int)
    want_html = request.args.get('html', '0') == '1'
    want_play = request.args.get('play', '0') == '1'
    want_structured = request.args.get('structured', '0') == '1'
    want_grade = request.args.get('grade', '0') == '1'
    want_lyrics = request.args.get('lyrics', '0') == '1'

    raw = sanitize_tab_html_artifacts(cifra['conteudo'] or '')
    transposed = pychord_transpose_text(raw, semitones, cifra['tom_original']) if semitones else raw
    transposed = format_text_chords_br(transposed, key_at_transpose(cifra['tom_original'], semitones))

    payload = {
        'tom_original': cifra['tom_original'],
        'semitones': semitones,
        'display_key': key_at_transpose(cifra['tom_original'], semitones),
    }
    if want_html:
        structured_data = _load_best_structured_cifra(cifra, semitones)
        grouped = _group_cifra_data(structured_data) if structured_data else None
        if grouped:
            payload['html'] = render_grouped_cifra_html(grouped)
        else:
            payload['html'] = highlight_chords_play_html(transposed)
    else:
        payload['conteudo'] = transposed

    if want_structured:
        structured_data = _load_best_structured_cifra(cifra, semitones)
        payload['cifra_data'] = structured_data

    if want_grade:
        payload['grade_data'] = _load_display_grade_data(cifra, semitones) or []
        leadsheet = _load_display_leadsheet(cifra, semitones)
        if leadsheet:
            payload['leadsheet'] = leadsheet

    if want_lyrics:
        payload['lyrics_plain'] = _lyrics_at_semitones(cifra, semitones)

    return jsonify(payload)


@cifras_bp.route('/<cifra_id>/chordsheet/render', methods=['GET'])
@login_required
def chordsheet_render(cifra_id):
    """Renderiza chord sheet (módulo chordsheet) em HTML para play mode e visualização."""
    from chordsheet_bridge import render_cifra_chordsheet_html

    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_member(cifra['band_id'], user_id):
        return jsonify({'ok': False, 'error': 'Sem acesso'}), 403

    cifra = _effective_cifra_for_versao(cifra, user_id, request.args.get('versao'))

    semitones = normalize_transpose_semitones(
        request.args.get('semitones', 0, type=int)
    )
    display_key = key_at_transpose(cifra['tom_original'], semitones)
    nashville = request.args.get('nashville', '').lower() in ('1', 'true', 'yes')
    html = render_cifra_chordsheet_html(
        cifra,
        semitones=semitones,
        display_key=display_key,
        viewer_user_id=user_id,
        nashville=nashville,
    )
    if not html:
        return jsonify({'ok': False, 'error': 'Grade harmônica indisponível'}), 404
    return jsonify({'ok': True, 'html': html, 'display_key': display_key})


@cifras_bp.route('/chord-info', methods=['GET'])
@login_required
def chord_info():
    """Retorna notas, posições e escalas para diagramas (API v1)."""
    from chord_diagram.api_service import fetch_progression_for_modal

    symbol = request.args.get('symbol', '').strip()
    instrument = request.args.get('instrument', 'violao')
    key_ctx = request.args.get('key')
    payload = fetch_progression_for_modal(symbol, instrument=instrument, key_context=key_ctx)
    if payload.get('error') and not payload.get('chords'):
        return jsonify(payload), 400
    return jsonify(payload)


# ── LeadSheet (substitui grade harmônica) ───────────────────────────────────


@cifras_bp.route('/<cifra_id>/leadsheet')
@login_required
def leadsheet_editor(cifra_id):
    """Redireciona para edição unificada na aba Chord Sheet."""
    user_id = session['user_id']
    cifra = get_cifra(cifra_id)
    if not cifra:
        flash('Cifra não encontrada', 'danger')
        return redirect(url_for('dashboard'))
    if not is_band_editor(cifra['band_id'], user_id):
        flash('Sem permissão', 'danger')
        return redirect(url_for('dashboard'))
    return redirect(url_for('cifras.edit', cifra_id=cifra_id, tab='chordsheet'))


@cifras_bp.route('/<cifra_id>/chordsheet/api/render', methods=['POST'])
@login_required
def chordsheet_api_render(cifra_id):
    from chordsheet.parser import parse_chart
    from chordsheet.render import render_chart_html
    from chordsheet_bridge import apply_chart_cifra_spelling
    from util import normalize_tom_label

    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_member(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem acesso'}), 403
    data = request.get_json(force=True) or {}
    try:
        meta = data.get('meta') or {}
        spell_key = normalize_tom_label(
            meta.get('key') or cifra.get('tom_original') or ''
        )
        chart = parse_chart(
            data.get('source', ''),
            meta=meta,
            prefs=data.get('prefs') or {},
        )
        if spell_key:
            apply_chart_cifra_spelling(chart, spell_key)
        html = render_chart_html(chart)
        return jsonify({'ok': True, 'html': html, 'bar_count': len(chart.bars)})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400


@cifras_bp.route('/<cifra_id>/chordsheet/api/transpose', methods=['POST'])
@login_required
def chordsheet_api_transpose(cifra_id):
    from dataclasses import asdict

    from chordsheet.parser import parse_chart
    from chordsheet.private_notes import merge_private_notes, split_private_notes
    from chordsheet.transpose import transpose_chart
    from chordsheet_bridge import apply_chart_cifra_spelling
    from util import key_at_transpose, normalize_tom_label, normalize_transpose_semitones

    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_editor(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    data = request.get_json(force=True) or {}
    semitones = normalize_transpose_semitones(int(data.get('semitones', 0)))
    try:
        meta = data.get('meta') or {}
        tom = normalize_tom_label(meta.get('key') or cifra.get('tom_original') or '')
        shared_source, private_notes = split_private_notes(data.get('source', ''))
        chart = parse_chart(
            shared_source,
            meta=meta,
            prefs=data.get('prefs') or {},
        )
        target_key = key_at_transpose(tom, semitones) if tom else ""
        transposed = transpose_chart(chart, semitones, source_key=tom or None)
        if target_key:
            apply_chart_cifra_spelling(transposed, target_key)
        return jsonify({
            'ok': True,
            'source': merge_private_notes(transposed.to_source(), private_notes),
            'meta': asdict(transposed.meta),
        })
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400


@cifras_bp.route('/<cifra_id>/chordsheet/api/save', methods=['POST'])
@login_required
def chordsheet_api_save(cifra_id):
    from chordsheet_bridge import persist_chordsheet_payload

    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_editor(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    data = request.get_json(force=True) or {}
    autosave = bool(data.get("autosave"))
    try:
        persist_chordsheet_payload(cifra_id, data, user_id=session["user_id"])
        if not autosave:
            titulo = (data.get("meta") or {}).get("title") or cifra.get("titulo") or "Cifra"
            bn.cifra_updated(cifra["band_id"], session["user_id"], cifra_id, titulo)
            _notify_band_realtime(cifra["band_id"], 'cifra_updated', cifra_id=cifra_id, titulo=titulo)
        cifra = get_cifra(cifra_id)
        return jsonify({
            "ok": True,
            "autosave": autosave,
            "saved_at": str(cifra.get("updated_at") or "") if cifra else "",
        })
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400


@cifras_bp.route('/<cifra_id>/chordsheet/api/extract-from-cifra', methods=['POST'])
@login_required
def chordsheet_api_extract_from_cifra(cifra_id):
    """Gera texto-fonte da grade harmônica a partir dos acordes da cifra."""
    from chordsheet_bridge import extract_chordsheet_from_cifra

    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_editor(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    data = request.get_json(force=True, silent=True) or {}
    ts = (data.get('time_signature') or '4/4').strip() or '4/4'
    source = extract_chordsheet_from_cifra(cifra, time_signature=ts)
    if not source:
        return jsonify({
            'ok': False,
            'error': 'Não encontramos acordes na cifra. Use [G]… na letra ou importe uma cifra primeiro.',
        }), 400
    return jsonify({
        'ok': True,
        'source': source,
        'meta': {
            'title': (cifra.get('titulo') or '').strip(),
            'artist': (cifra.get('artista') or '').strip(),
            'key': (cifra.get('tom_original') or '').strip(),
            'bpm': str(int(cifra['bpm'])) if cifra.get('bpm') else '',
            'time_signature': ts,
        },
    })


@cifras_bp.route('/<cifra_id>/leadsheet/api/gerar', methods=['POST'])
@login_required
def leadsheet_api_gerar(cifra_id):
    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_editor(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    try:
        data = request.form.to_dict()
        if not data.get('song_title'):
            data['song_title'] = cifra.get('titulo') or ''
        if not data.get('artist'):
            data['artist'] = cifra.get('artista') or ''
        if not data.get('song_key'):
            data['song_key'] = cifra.get('tom_original') or ''
        payload = build_payload(data)
        return jsonify({'ok': True, 'payload': payload})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400


@cifras_bp.route('/<cifra_id>/leadsheet/api/salvar', methods=['POST'])
@login_required
def leadsheet_api_salvar(cifra_id):
    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_editor(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    try:
        data = request.form.to_dict()
        if not data.get('song_title'):
            data['song_title'] = cifra.get('titulo') or ''
        if not data.get('artist'):
            data['artist'] = cifra.get('artista') or ''
        if not data.get('song_key'):
            data['song_key'] = cifra.get('tom_original') or ''
        payload = build_payload(data)
        meta = {
            'titulo': (data.get('song_title') or '').strip() or cifra.get('titulo'),
            'artista': (data.get('artist') or '').strip() or cifra.get('artista'),
            'tom_original': (data.get('song_key') or '').strip() or cifra.get('tom_original'),
        }
        _persist_leadsheet(cifra_id, payload, meta)
        titulo = meta.get('titulo') or cifra.get('titulo') or 'Cifra'
        bn.cifra_updated(cifra['band_id'], session['user_id'], cifra_id, titulo)
        _notify_band_realtime(cifra['band_id'], 'cifra_updated', cifra_id=cifra_id, titulo=titulo)
        return jsonify({
            'ok': True,
            'redirect': url_for('cifras.view', cifra_id=cifra_id),
        })
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400


@cifras_bp.route('/<cifra_id>/leadsheet/api/analisar-audio', methods=['POST'])
@login_required
def leadsheet_api_analisar(cifra_id):
    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_editor(cifra['band_id'], session['user_id']):
        return jsonify({'ok': False, 'error': 'Sem permissão'}), 403
    try:
        if 'audio_file' not in request.files:
            raise ValueError("Envie um arquivo de áudio.")
        file = request.files['audio_file']
        if not file or not file.filename:
            raise ValueError("Nenhum arquivo foi enviado.")
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError("Formato não suportado. Use: mp3, wav, m4a, flac ou ogg.")
        with tempfile.NamedTemporaryFile(prefix='ls_', suffix=ext, delete=False) as tmp:
            file.save(tmp.name)
            temp_path = Path(tmp.name)
        try:
            result = analyze_audio_for_leadsheet(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)
        return jsonify({'ok': True, 'analysis': result})
    except Exception as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400


def _draft_access(cifra_id: str, user_id: str):
    cifra = get_cifra(cifra_id)
    if not cifra or not is_band_member(cifra['band_id'], user_id):
        return None, None
    return cifra, cifra['band_id']


@cifras_bp.route('/<cifra_id>/api/rascunho', methods=['GET'])
@login_required
def api_get_rascunho(cifra_id):
    user_id = session['user_id']
    cifra, _ = _draft_access(cifra_id, user_id)
    if not cifra:
        return jsonify({'detail': 'Sem acesso.'}), 403
    draft = get_cifra_user_draft(cifra_id, user_id)
    from cifra_user_draft import draft_differs_from_band
    return jsonify({
        'draft': draft,
        'has_draft': bool(draft and draft_differs_from_band(draft, cifra)),
        'can_publish': is_band_editor(cifra['band_id'], user_id),
    })


@cifras_bp.route('/<cifra_id>/api/rascunho', methods=['PUT'])
@login_required
def api_save_rascunho(cifra_id):
    user_id = session['user_id']
    cifra, band_id = _draft_access(cifra_id, user_id)
    if not cifra:
        return jsonify({'detail': 'Sem acesso.'}), 403
    if not is_band_editor(band_id, user_id):
        return jsonify({'detail': 'Sem permissão para editar.'}), 403

    from cifra_user_draft import draft_payload_from_form, draft_differs_from_band

    data = request.get_json(silent=True) or {}
    fields = draft_payload_from_form(data)
    if not fields:
        return jsonify({'detail': 'Nada para salvar.'}), 400

    for key in ('titulo', 'artista', 'tom_original', 'conteudo'):
        if key not in fields or fields[key] in (None, ''):
            fields[key] = cifra.get(key)

    draft_id = upsert_cifra_user_draft(cifra_id, user_id, fields)
    draft = get_cifra_user_draft(cifra_id, user_id)
    return jsonify({
        'ok': True,
        'draft_id': draft_id,
        'has_draft': bool(draft and draft_differs_from_band(draft, cifra)),
    })


@cifras_bp.route('/<cifra_id>/api/rascunho/publicar', methods=['POST'])
@login_required
def api_publicar_rascunho(cifra_id):
    user_id = session['user_id']
    cifra, band_id = _draft_access(cifra_id, user_id)
    if not cifra:
        return jsonify({'detail': 'Sem acesso.'}), 403
    if not is_band_editor(band_id, user_id):
        return jsonify({'detail': 'Sem permissão para publicar na banda.'}), 403
    if not publish_cifra_user_draft(cifra_id, user_id):
        return jsonify({'detail': 'Rascunho não encontrado.'}), 404
    titulo = get_cifra(cifra_id).get('titulo') or 'Cifra'
    bn.cifra_updated(band_id, user_id, cifra_id, titulo)
    _notify_band_realtime(band_id, 'cifra_published', cifra_id=cifra_id, titulo=titulo)
    return jsonify({
        'ok': True,
        'redirect': url_for('cifras.view', cifra_id=cifra_id),
    })


@cifras_bp.route('/<cifra_id>/api/rascunho/descartar', methods=['POST'])
@login_required
def api_descartar_rascunho(cifra_id):
    user_id = session['user_id']
    cifra, _ = _draft_access(cifra_id, user_id)
    if not cifra:
        return jsonify({'detail': 'Sem acesso.'}), 403
    delete_cifra_user_draft(cifra_id, user_id)
    return jsonify({'ok': True})


@cifras_bp.route('/<cifra_id>/api/play-draw', methods=['GET'])
@login_required
def api_get_play_draw(cifra_id):
    user_id = session['user_id']
    cifra, _ = _draft_access(cifra_id, user_id)
    if not cifra:
        return jsonify({'detail': 'Sem acesso.'}), 403
    from db import get_cifra_play_drawing
    row = get_cifra_play_drawing(cifra_id, user_id)
    strokes = []
    if row and row.get('strokes_json'):
        try:
            strokes = json.loads(row['strokes_json'])
        except ValueError:
            strokes = []
    return jsonify({'strokes': strokes, 'updated_at': row.get('updated_at') if row else None})


@cifras_bp.route('/<cifra_id>/api/play-draw', methods=['PUT'])
@login_required
def api_save_play_draw(cifra_id):
    user_id = session['user_id']
    cifra, _ = _draft_access(cifra_id, user_id)
    if not cifra:
        return jsonify({'detail': 'Sem acesso.'}), 403
    data = request.get_json(silent=True) or {}
    strokes = data.get('strokes')
    if not isinstance(strokes, list):
        return jsonify({'detail': 'Campo strokes inválido.'}), 400
    from db import upsert_cifra_play_drawing
    upsert_cifra_play_drawing(cifra_id, user_id, json.dumps(strokes, ensure_ascii=False))
    return jsonify({'ok': True})