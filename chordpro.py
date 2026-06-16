"""Conversão e parsing de cifras no formato ChordPro (.cho / .pro)."""
from __future__ import annotations

import re
from typing import Any

from util import (
    _TAB_ARTIFACT_RE,
    _is_chord_line,
    _is_tab_header,
    _is_tab_line,
    _is_tab_meta_line,
    format_text_chords_br,
    is_bracket_chord_name,
    to_brazilian_chord_notation,
)

CHORDPRO_DIRECTIVE_RE = re.compile(
    r'^\{\s*([^}:]+?)(?:\s*:\s*(.*?))?\s*\}\s*$',
    re.IGNORECASE,
)
CHORD_INLINE_BRACKET_RE = re.compile(r'\[([^\]]+)\]([^\[]*)')
META_DIRECTIVES = frozenset({
    'title', 't', 'artist', 'subtitle', 'st', 'key', 'capo', 'tempo', 'time',
})
SECTION_DIRECTIVES = {
    'start_of_chorus': 'chorus',
    'soc': 'chorus',
    'start_of_verse': 'verse',
    'sov': 'verse',
    'start_of_bridge': 'bridge',
    'sob': 'bridge',
    'start_of_intro': 'intro',
    'start_of_tab': 'tab',
    'start_of_outro': 'outro',
}


def parse_chordpro_directive(line: str) -> tuple[str, str] | None:
    m = CHORDPRO_DIRECTIVE_RE.match((line or '').strip())
    if not m:
        return None
    return m.group(1).strip().lower(), (m.group(2) or '').strip()


_COMMENT_LOOSE_RE = re.compile(
    r'^\{\s*comment\s*:\s*(.*?)(?:\})?\s*$',
    re.IGNORECASE,
)


def is_comment_line(line: str) -> bool:
    """True se a linha for diretiva {comment: ...} (não exibir nem salvar)."""
    return parse_comment_line(line) is not None


def strip_comment_lines_from_text(text: str) -> str:
    """Remove linhas {comment: ...} do corpo da cifra."""
    if not text:
        return text
    out: list[str] = []
    for raw in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if is_comment_line(raw.strip()):
            continue
        out.append(raw)
    return '\n'.join(out)


# Compat: nome antigo usado em prepare_cifra_sheet
normalize_comment_lines_in_text = strip_comment_lines_from_text


def parse_comment_line(line: str) -> str | None:
    """
    Extrai rótulo de {comment: ...} (formato estrito ou colagem com `}` faltando).
    Retorna None se a linha não for comentário ChordPro.
    """
    stripped = (line or '').strip()
    if not stripped:
        return None
    directive = parse_chordpro_directive(stripped)
    if directive and directive[0] == 'comment':
        return directive[1]
    if re.fullmatch(r'\{\s*comment\s*\}', stripped, re.IGNORECASE):
        return ''
    m = _COMMENT_LOOSE_RE.match(stripped)
    if m:
        return m.group(1).strip()
    return None


def is_chordpro_document(text: str) -> bool:
    if not text:
        return False
    hits = 0
    for raw in text.split('\n')[:40]:
        d = parse_chordpro_directive(raw)
        if not d:
            continue
        name = d[0]
        if name in META_DIRECTIVES or name in SECTION_DIRECTIVES or name == 'comment':
            hits += 1
    return hits >= 1


def _format_chord_token(chord: str) -> str:
    return to_brazilian_chord_notation((chord or '').strip())


def _is_section_label(text: str) -> bool:
    s = (text or '').strip()
    if not s or '[' in s or ']' in s:
        return False
    if _is_tab_line(s) or _is_tab_header(s):
        return False
    if len(s) > 48 or s.count(' ') > 6:
        return False
    if re.search(r'\d{3,}', s):
        return False
    # Frases de letra (ex.: «Depois que eu ganhar dinheiro») não são rótulo de seção
    if re.search(r'[a-zà-ú]', s):
        return False
    return True


def _merge_group_to_line(items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in items:
        chord = _format_chord_token(item.get('acorde') or '')
        lyric = str(item.get('texto_letra') or '')
        if chord:
            parts.append(f'[{chord}]{lyric}')
        else:
            parts.append(lyric)
    return format_text_chords_br(''.join(parts))


def _group_items_by_field(data: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    if not data:
        return []
    if 'group' not in data[0]:
        return [data]
    groups: list[list[dict[str, Any]]] = []
    current_g = None
    bucket: list[dict[str, Any]] = []
    for item in data:
        g = item.get('group')
        if current_g is None:
            current_g = g
        if g != current_g and bucket:
            groups.append(bucket)
            bucket = []
            current_g = g
        bucket.append(item)
    if bucket:
        groups.append(bucket)
    return groups


def parse_conteudo_to_cifra_data(conteudo: str) -> list[dict[str, Any]]:
    """
    Interpreta texto (ChordPro, colchetes ou duas linhas) → lista cifra_json.
    """
    from cifras_tool.scraper.comum import normalizar_colagem_cifraclub

    text = (conteudo or '').replace('\r\n', '\n').replace('\r', '\n')
    text = normalizar_colagem_cifraclub(text)
    lines = text.split('\n')
    result: list[dict[str, Any]] = []
    seq = 0
    group = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            group += 1
            i += 1
            continue

        if is_comment_line(stripped):
            i += 1
            continue

        directive = parse_chordpro_directive(stripped)
        if directive:
            name, value = directive
            if name in META_DIRECTIVES:
                i += 1
                continue
            if name == 'comment':
                i += 1
                continue
            if name in SECTION_DIRECTIVES:
                label = value or SECTION_DIRECTIVES[name].title()
                result.append({
                    'segundo': seq,
                    'texto_letra': label,
                    'acorde': '',
                    'group': group,
                    'section': label,
                })
                seq += 1
                group += 1
            if name.startswith('end_of'):
                group += 1
            i += 1
            continue

        if _is_tab_line(stripped) or _is_tab_header(stripped) or _is_tab_meta_line(stripped):
            while i < len(lines):
                tab_line = lines[i]
                tab_stripped = tab_line.strip()
                if not (
                    tab_stripped
                    and (
                        _is_tab_line(tab_stripped)
                        or _is_tab_header(tab_stripped)
                        or _is_tab_meta_line(tab_stripped)
                    )
                ):
                    break
                result.append({
                    'segundo': seq,
                    'texto_letra': tab_line.rstrip(),
                    'acorde': '',
                    'group': group,
                })
                seq += 1
                i += 1
            group += 1
            continue

        if re.fullmatch(r'spa', stripped, flags=re.I):
            group += 1
            i += 1
            continue

        if _TAB_ARTIFACT_RE.search(stripped) and '[' not in stripped:
            group += 1
            i += 1
            continue

        if '[' in line and ']' in line:
            last = 0
            matched = False
            for m in CHORD_INLINE_BRACKET_RE.finditer(line):
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
                token = m.group(1).strip()
                texto_apos = m.group(2) or ''
                if is_bracket_chord_name(token):
                    result.append({
                        'segundo': seq,
                        'texto_letra': texto_apos,
                        'acorde': _format_chord_token(token),
                        'group': group,
                    })
                else:
                    label = token
                    extra = texto_apos.strip()
                    result.append({
                        'segundo': seq,
                        'texto_letra': f'[{label}]' + (extra if extra else ''),
                        'acorde': '',
                        'group': group,
                        'section': label,
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
                i += 1
                continue

        next_line = lines[i + 1] if i + 1 < len(lines) else None
        if (
            next_line is not None
            and _is_chord_line(stripped)
            and not _is_chord_line(next_line.strip())
            and next_line.strip()
        ):
            chord_re = re.compile(r'\S+')
            chords = [(m.group(0), m.start()) for m in chord_re.finditer(line)]
            lyric = next_line
            for j, (chord, pos) in enumerate(chords):
                end = chords[j + 1][1] if j + 1 < len(chords) else len(lyric)
                texto = lyric[pos:end]
                result.append({
                    'segundo': seq,
                    'texto_letra': texto,
                    'acorde': _format_chord_token(chord),
                    'group': group,
                })
                seq += 1
            group += 1
            i += 2
            continue

        if is_comment_line(stripped):
            i += 1
            continue
        result.append({
            'segundo': seq,
            'texto_letra': line,
            'acorde': '',
            'group': group,
        })
        seq += 1
        group += 1
        i += 1

    return result


def _escape_directive_value(value: str) -> str:
    return (value or '').replace('\n', ' ').strip()


def _directive(name: str, value: str) -> str:
    val = _escape_directive_value(value)
    if val:
        return f'{{{name}: {val}}}'
    return f'{{{name}}}'


def _group_to_chordpro_lines(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return []
    has_chord = any((it.get('acorde') or '').strip() for it in items)
    merged = _merge_group_to_line(items)
    if not has_chord and _is_section_label(merged):
        return []
    if merged.strip():
        return [merged.rstrip()]
    return []


def conteudo_to_chordpro(
    conteudo: str,
    *,
    titulo: str = '',
    artista: str = '',
    key: str = '',
    preserve_existing_sections: bool = True,
) -> str:
    """
    Normaliza o corpo da cifra para ChordPro com metadados no topo.
    """
    text = (conteudo or '').replace('\r\n', '\n').replace('\r', '\n').strip()
    body_lines: list[str] = []
    preserved_meta: list[str] = []

    if is_chordpro_document(text):
        for raw in text.split('\n'):
            d = parse_chordpro_directive(raw.strip())
            if d and d[0] in META_DIRECTIVES:
                preserved_meta.append(raw.strip())
            else:
                body_lines.append(raw)
        text = '\n'.join(body_lines).strip()

    data = parse_conteudo_to_cifra_data(text)
    groups = _group_items_by_field(data)

    out: list[str] = []
    titulo = _escape_directive_value(titulo)
    artista = _escape_directive_value(artista)
    key = _escape_directive_value(key)

    if titulo:
        out.append(_directive('title', titulo))
    if artista:
        out.append(_directive('artist', artista))
    if key:
        out.append(_directive('key', key))
    if out:
        out.append('')

    prev_was_blank = True
    for items in groups:
        section_lines = _group_to_chordpro_lines(items)
        if not section_lines:
            continue
        if not prev_was_blank and out and out[-1] != '':
            out.append('')
        for sl in section_lines:
            if is_comment_line(sl.strip()):
                continue
            out.append(sl)
        prev_was_blank = False

    while out and out[-1] == '':
        out.pop()
    return '\n'.join(out) + '\n' if out else ''


def cifra_json_from_conteudo(conteudo: str) -> list[dict[str, Any]]:
    """Gera estrutura cifra_json a partir do texto (ChordPro ou legado)."""
    return parse_conteudo_to_cifra_data(conteudo)
