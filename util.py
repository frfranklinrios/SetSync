
from pychord import Chord
import re
import html as html_lib


def _to_br_note(note):
    if not note:
        return note
    # Mantem a alteracao original (# ou b) e apenas normaliza glifos unicode.
    return str(note).replace('♯', '#').replace('♭', 'b')


def to_brazilian_chord_notation(chord_str):
    """Padroniza um acorde para notação brasileira.

    Regras aplicadas:
    - mantem a alteracao original da nota (#/b), sem forcar enarmonizacao
    - majX / MX / XM -> X+ (ex.: Cmaj7, CM7, C7M -> C7+)
    - dim / dim7 -> ° / °7
    - min -> m
    - m7 permanece m7 (nao confundir M maiúsculo com m de menor)
    """
    if not chord_str:
        return chord_str

    s = str(chord_str).strip()
    m = re.match(r'^([A-G](?:#|b)?)(.*?)(?:/([A-G](?:#|b)?))?$', s)
    if not m:
        return s

    root, quality, bass = m.group(1), (m.group(2) or ''), m.group(3)
    root = _to_br_note(root)
    if bass:
        bass = _to_br_note(bass)

    q = quality
    # Ordem importa: dim7 antes de qualquer regra que possa casar "m7" dentro de "dim7"
    q = re.sub(r'(?i)dim7', '°7', q)
    q = re.sub(r'(?i)dim', '°', q)
    q = re.sub(r'(?i)maj(\d+)', r'\1+', q)
    q = re.sub(r'(\d+)M(?!\w)', r'\1+', q)       # 7M, 9M (BR)
    q = re.sub(r'(?<![a-zA-Z])M(\d+)', r'\1+', q)  # M7 maiúsculo — NÃO casa m7 de menor
    q = re.sub(r'(?i)min', 'm', q)

    out = root + q
    if bass:
        out += '/' + bass
    return out


def format_text_chords_br(text):
    """Padroniza todos os acordes encontrados em um texto."""
    if text is None:
        return ''

    def _fmt(match):
        return to_brazilian_chord_notation(match.group(1))

    return re.sub(_CHORD_REGEX_WB, _fmt, str(text))

def _normalize_chord_for_pychord(chord_str):
    """Converte notação brasileira para algo que o pychord entenda.

    Conversões:
      - º / °  →  dim
      - X7+    →  Xmaj7  (notação BR comum: "+" após 7 significa maj7)
      - 7M / M7 já são aceitos pelo pychord
      - "+" / "-" remanescentes são removidos (pychord não os entende)
    """
    s = re.sub(r'[°º]', 'dim', chord_str)
    # Captura base (com m opcional) + dígito + '+' → base + 'maj' + dígito
    # Ex.: "C7+" → "Cmaj7";  "Cm7+" → "Cmmaj7" (pychord não suporta, fallback abaixo)
    s = re.sub(
        r'^([A-G][#b]?)(\d{1,2})\+',
        r'\1maj\2',
        s
    )
    # Remove +/- restantes que o pychord não entende (ex.: "B7-")
    s = re.sub(r'[+\-](?=[\d]|$|/)', '', s)
    return s


def split_chord_progression(symbol):
    """Divide uma sequência de acordes em partes (ex.: 'Bmaj7 -> F#7')."""
    if not symbol:
        return []
    parts = re.split(r'\s*(?:→|->|⇒|~|,)\s*', symbol.strip())
    return [p for p in parts if p]


def clean_chord_symbol(symbol):
    """Remove wrappers visuais para tentar parsear o acorde corretamente."""
    if not symbol:
        return ''
    s = symbol.strip()
    if s.startswith('[') and s.endswith(']') and len(s) >= 2:
        s = s[1:-1].strip()
    s = s.strip('()[]{} ')
    return s


def chord_components_info(symbol):
    """Retorna informações de componentes de um acorde para renderização de diagrama."""
    s = clean_chord_symbol(symbol)
    if not s:
        return None

    normalized = _normalize_chord_for_pychord(s)
    try:
        chord = Chord(normalized)
        notes = chord.components()
        if not isinstance(notes, list) or not notes:
            return None
        return {
            'input': symbol,
            'display': s,
            'normalized': normalized,
            'notes': notes,
        }
    except Exception:
        return None


_CHROMATIC_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
_CHROMATIC_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']


def _split_chord_root_quality(chord_str):
    m = re.match(r'^([A-G](?:#|b)?)(.*?)(?:/([A-G](?:#|b)?))?$', (chord_str or '').strip())
    if not m:
        return None
    return m.group(1), (m.group(2) or ''), m.group(3)


def _note_semitone_index(note):
    n = _to_br_note(note or '')
    if n in _CHROMATIC_SHARP:
        return _CHROMATIC_SHARP.index(n)
    if n in _CHROMATIC_FLAT:
        return _CHROMATIC_FLAT.index(n)
    return None


def _spell_semitone(semitone, prefer_flats=False):
    return _CHROMATIC_FLAT[semitone % 12] if prefer_flats else _CHROMATIC_SHARP[semitone % 12]


def _respell_chord_roots(transposed, original):
    """Mantém o estilo de bemóis/sustenidos do acorde original após transpor."""
    orig = _split_chord_root_quality(original)
    new = _split_chord_root_quality(transposed)
    if not orig or not new:
        return transposed

    orig_root, _, orig_bass = orig
    new_root, quality, new_bass = new

    prefer_flats = ('b' in orig_root and '#' not in orig_root)
    prefer_sharps = ('#' in orig_root and 'b' not in orig_root)
    if prefer_flats or prefer_sharps:
        idx = _note_semitone_index(new_root)
        if idx is not None:
            new_root = _spell_semitone(idx, prefer_flats=prefer_flats)

    if new_bass and orig_bass:
        prefer_flats_b = ('b' in orig_bass and '#' not in orig_bass)
        prefer_sharps_b = ('#' in orig_bass and 'b' not in orig_bass)
        if prefer_flats_b or prefer_sharps_b:
            idx_b = _note_semitone_index(new_bass)
            if idx_b is not None:
                new_bass = _spell_semitone(idx_b, prefer_flats=prefer_flats_b)

    out = new_root + quality
    if new_bass:
        out += '/' + new_bass
    return out


def pychord_transpose_chord(chord_str, semitones):
    """Transpõe um acorde usando pychord (mais robusto para acordes complexos)."""
    normalized = _normalize_chord_for_pychord(chord_str)
    try:
        chord = Chord(normalized)
        chord.transpose(semitones)
        new_str = str(chord)
        # Preserva a notação "+" original se existia
        if chord_str.endswith('+') and not new_str.endswith('+'):
            # Re-aplica o "+" se a entrada original usava (mantém estilo BR)
            new_str = re.sub(r'maj(\d+)$', r'\1+', new_str)
        new_str = _respell_chord_roots(new_str, chord_str)
        return to_brazilian_chord_notation(new_str)
    except Exception:
        return to_brazilian_chord_notation(chord_str)


# Componentes que podem aparecer em qualquer ordem após a nota base de um acorde:
#   - qualidade: maj7, maj, min, m7b5, m7, m, M7, M, dim7, dim, aug, sus2, sus4, sus, add9, add
#   - número/extensão: 7, 9, 11, 13, 6, 5, 4, 2
#   - alteração brasileira: + (= maj), - (= menor/dim em algumas notações), ° / º (dim)
#   - tensões alteradas: b5, #5, b9, #9, #11, b13, etc.
_CHORD_PART = (
    r'(?:maj7|maj|min|m7b5|m7|M7|m|M|dim7|dim|aug|sus2|sus4|sus|add9|add'
    r'|7|9|11|13|6|5|4|2'
    r'|[+\-°º]'
    r'|[b#]\d{1,2})'
)
# Nota raiz: quando há # ou b logo após a letra, consome junto (evita casar só "F" em "F#")
_CHORD_ROOT = r'(?:[A-G]#|[A-G]b|[A-G](?![#b]))'
_CHORD_BASS = r'(?:/(?:[A-G]#|[A-G]b|[A-G](?![#b])))?'
# Compat: alias usado em outros pontos
_CHORD_HEAD = _CHORD_ROOT

# Para uso em match exato (token completo)
CHORD_TOKEN_RE = re.compile(
    r'^' + _CHORD_ROOT + r'(?:' + _CHORD_PART + r')*' + _CHORD_BASS + r'$'
)
# Para uso em substituição inline dentro de uma linha
CHORD_INLINE_RE = re.compile(
    r'(' + _CHORD_ROOT + r'(?:' + _CHORD_PART + r')*' + _CHORD_BASS + r')'
)
# Texto livre: \b falha após "#" (ex.: "F#" vira "F" + "#" solto)
_CHORD_REGEX_WB = (
    r'(?<![A-Za-z])(' + _CHORD_ROOT + r'(?:' + _CHORD_PART + r')*' + _CHORD_BASS + r')(?![A-Za-z0-9])'
)


def pychord_highlight_chords(text):
    """Destaca acordes usando pychord para validação. Suporta º/° como diminuto."""
    not_recognized = set()

    def highlight(match):
        chord_str = match.group(1)
        normalized = _normalize_chord_for_pychord(chord_str)
        try:
            _ = Chord(normalized)
            return f'<span class="chord">{chord_str}</span>'
        except Exception:
            not_recognized.add(chord_str)
            return chord_str

    result = re.sub(_CHORD_REGEX_WB, highlight, text)
    if not_recognized:
        print("Acordes não reconhecidos pelo pychord:", not_recognized)
    return result

def pychord_transpose_text(text, semitones):
    """Transpõe todos os acordes de um texto usando pychord. Suporta º/° como diminuto."""
    if semitones == 0:
        return text or ''
    if text is None:
        return ''
    stripped = text.strip()
    # Token isolado (grade harmônica: "F#", "G#m", "%", etc.)
    if stripped == '%':
        return '%'
    if CHORD_TOKEN_RE.match(stripped):
        return pychord_transpose_chord(stripped, semitones)

    def transp(match):
        return pychord_transpose_chord(match.group(1), semitones)

    return re.sub(_CHORD_REGEX_WB, transp, text)


# Notas em ordem cromática
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Mapa de aliases (bemol -> sustenido equivalente e vice-versa)
NOTE_ALIASES = {
    'B#': 'C', 'E#': 'F', 'Cb': 'B', 'Fb': 'E',
    'C♯': 'C#', 'D♯': 'D#', 'E♯': 'F', 'F♯': 'F#',
    'G♯': 'G#', 'A♯': 'A#', 'B♯': 'C',
    'D♭': 'Db', 'E♭': 'Eb', 'F♭': 'E', 'G♭': 'Gb',
    'A♭': 'Ab', 'B♭': 'Bb', 'C♭': 'B',
}

def normalize_note(note):
    """Normaliza notação de notas (ex: Db, ♭, ♯)"""
    if note in NOTE_ALIASES:
        note = NOTE_ALIASES[note]
    return note

def find_notes_in_text(text):
    """Encontra todas as notas/acordes no texto"""
    # Padrão: nota [#/♯/b/♭] [acordes modificadores como m, maj7, etc]
    pattern = r'\b([A-G][#♯b♭]?)(?:m|maj|min|dim|aug|sus|add|m7|maj7|7|9|11|13)?\b'
    matches = re.finditer(pattern, text)
    return [(m.group(1), m.start(), m.end()) for m in matches]

def get_note_index(note):
    """Retorna o índice da nota na escala cromática"""
    note = normalize_note(note)
    if note in NOTES:
        return NOTES.index(note)
    elif note in NOTES_FLAT:
        return NOTES_FLAT.index(note)
    return None

def transpose_note(note, semitones):
    """Transpõe uma nota por um número de semitons"""
    note = normalize_note(note)
    idx = get_note_index(note)
    if idx is None:
        return note
    
    new_idx = (idx + semitones) % 12
    return NOTES[new_idx]

def extract_chord(text, start_pos):
    """Extrai um acorde completo a partir de uma posição"""
    # Padrão: nota + modificadores (m, maj7, etc)
    pattern = r'[A-G][#♯b♭]?(?:m|maj|min|dim|aug|sus|add|m7|maj7|7|9|11|13)?'
    match = re.match(pattern, text[start_pos:])
    if match:
        return match.group(0)
    return None

def transpose_text(text, semitones):
    """Transpõe todos os acordes em um texto"""
    if semitones == 0:
        return text
    
    result = list(text)
    
    # Encontrar todos os acordes
    pattern = r'\b([A-G][#♯b♭]?)(?:(m|maj|min|dim|aug|sus|add|m7|maj7|7|9|11|13))?\b'
    
    for match in re.finditer(pattern, text):
        base_note = match.group(1)
        modifier = match.group(2) or ''
        
        new_note = transpose_note(base_note, semitones)
        new_chord = new_note + modifier
        old_chord = match.group(0)
        
        # Substituir no resultado
        start = match.start()
        end = match.end()
        for i in range(start, end):
            result[i] = ''
        result[start] = new_chord
    
    return ''.join(result)

def get_available_tones():
    """Retorna os tons disponíveis para transposição (legado — preferir get_transposition_options)."""
    return {
        -12: 'Oitava Baixa',
        -11: 'A',
        -10: 'A#/Bb',
        -9: 'B',
        -8: 'C',
        -7: 'C#/Db',
        -6: 'D',
        -5: 'D#/Eb',
        -4: 'E',
        -3: 'F',
        -2: 'F#/Gb',
        -1: 'G',
        0: 'Original',
        1: 'G#/Ab',
        2: 'A',
        3: 'A#/Bb',
        4: 'B',
        5: 'C',
        6: 'C#/Db',
        7: 'D',
        8: 'D#/Eb',
        9: 'E',
        10: 'F',
        11: 'F#/Gb',
        12: 'G (Oitava Alta)',
    }


def parse_tom_root(tom_original):
    """Extrai a nota raiz do tom cadastrado (ex.: Bmaj7 -> B, F#m -> F#)."""
    s = (tom_original or 'C').strip()
    if not s:
        return 'C'
    m = re.match(r'^([A-G])(#|b)?', s, re.I)
    if not m:
        return 'C'
    return _to_br_note(m.group(1).upper() + (m.group(2) or ''))


def normalize_tom_label(tom_original):
    """Normaliza rótulos de tom para notação de cifra (C, F#, Am...)."""
    s = (tom_original or '').strip()
    if not s:
        return 'C'

    m = re.match(r'^([A-G](?:#|b)?)\s+(maior|menor)(?:\s*\(.*\))?$', s, re.IGNORECASE)
    if m:
        nota = _to_br_note(m.group(1))
        modo = m.group(2).lower()
        return f'{nota}m' if modo == 'menor' else nota

    # Remove sufixos de origem como "(cifra)" ou "(estimada)" mantendo a notação do acorde.
    s = re.sub(r'\s*\((?:cifra|estimada)\)\s*$', '', s, flags=re.IGNORECASE).strip()
    return s or 'C'


def semitones_between_keys(from_tom, to_key):
    """Semitons para ir do tom original até a tonalidade alvo."""
    a = _note_semitone_index(parse_tom_root(from_tom))
    b = _note_semitone_index(parse_tom_root(to_key))
    if a is None or b is None:
        return 0
    diff = b - a
    if diff > 6:
        diff -= 12
    elif diff < -6:
        diff += 12
    return diff


def key_at_transpose(tom_original, semitones):
    """Nome da tonalidade resultante após transpor (bemóis: Bb, Eb… — alinha com acordes na tela)."""
    root = parse_tom_root(tom_original)
    idx = _note_semitone_index(root)
    if idx is None:
        return root
    return _spell_semitone(idx + semitones, prefer_flats=True)


def get_absolute_key_list():
    """Lista das 12 tonalidades para seleção absoluta (setlists)."""
    return list(_CHROMATIC_FLAT)


def get_transposition_options(tom_original):
    """Opções de transposição {semitones: label} relativas ao tom_original da música."""
    root = parse_tom_root(tom_original)
    chromatic = _CHROMATIC_FLAT

    options = {}
    for key in chromatic:
        semi = semitones_between_keys(root, key)
        if semi == 0:
            options[semi] = f'{key} (Original)'
        else:
            options[semi] = key
    return dict(sorted(options.items(), key=lambda x: x[0]))


def build_transpose_map(tom_original):
    """Mapa { tonalidade: semitons } para uso no modo tocar (por música)."""
    root = parse_tom_root(tom_original)
    return {key: semitones_between_keys(root, key) for key in get_absolute_key_list()}


def _is_chord_token(token):
    """Verifica se um token isolado é um acorde válido"""
    t = token.strip('()[]{} ')
    t = re.sub(r'[°º]', 'dim', t)
    return bool(CHORD_TOKEN_RE.match(t))


def _is_chord_line(line):
    """Retorna True se a linha for predominantemente acordes"""
    if _is_tab_line(line) or _is_tab_header(line) or _is_tab_meta_line(line):
        return False
    tokens = [t for t in line.split() if t.strip('()[]{} ')]
    if not tokens:
        return False
    chord_count = sum(1 for t in tokens if _is_chord_token(t))
    return chord_count >= max(1, len(tokens) * 0.7)


_TAB_LINE_RE = re.compile(
    r'^[EBGDAe]\s*\|',
    re.IGNORECASE,
)
_TAB_HEADER_RE = re.compile(
    r'^(?:\[(?:Tab|TAB)[^\]]*\]|(?:Tab|TABlatura)\b)',
    re.IGNORECASE,
)
_TAB_META_RE = re.compile(
    r'^(?:Parte\s+\d+\s+de\s+\d+|Riff\b)',
    re.IGNORECASE,
)
_TAB_ARTIFACT_RE = re.compile(
    r'span\s+class\s*=|</?span|spa\[|/span>',
    re.IGNORECASE,
)


def _is_tab_line(line: str) -> bool:
    return bool(_TAB_LINE_RE.match((line or '').strip()))


def _is_tab_header(line: str) -> bool:
    s = (line or '').strip()
    if _TAB_HEADER_RE.match(s):
        return True
    if s.startswith('[Tab') or s.startswith('[TAB'):
        return True
    return False


def _is_tab_meta_line(line: str) -> bool:
    s = (line or '').strip()
    if not s:
        return False
    if _TAB_META_RE.match(s):
        return True
    if _TAB_ARTIFACT_RE.search(s) and 'Parte' in s:
        return True
    return False


def sanitize_tab_html_artifacts(text: str) -> str:
    """Remove resíduos HTML de tablaturas importadas (ex.: Cifra Club)."""
    if not text:
        return ''
    cleaned = []
    for raw in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        line = raw
        line = re.sub(r'^span class="tablatura">?\s*', '', line, flags=re.I)
        line = re.sub(r'^span class="cnt">?\s*', '', line, flags=re.I)
        line = re.sub(r'spa\[([^\]]+)\]n class="cnt">', '', line, flags=re.I)
        line = re.sub(r'/span>\s*/span>\s*$', '', line, flags=re.I)
        line = re.sub(r'</?span[^>]*>', '', line, flags=re.I)
        line = re.sub(r'^spa\s*$', '', line, flags=re.I)
        cleaned.append(line.rstrip())
    return '\n'.join(cleaned)


def content_has_tablatura(text: str) -> bool:
    """Indica se o texto contém tablatura (linhas E| B|… ou seções Tab)."""
    text = sanitize_tab_html_artifacts(text or '')
    for line in text.split('\n'):
        s = line.strip()
        if not s:
            continue
        if _is_tab_line(s) or _is_tab_header(s):
            return True
    return False


def _highlight_tab_line_html(line: str) -> str:
    """Destaca cordas e números/técnicas em uma linha de tablatura."""
    s = line.rstrip()
    m = re.match(r'^([EBGDAe])(\s*\|)(.*)$', s, re.I)
    if not m:
        return f'<span class="cifra-tab-line">{html_lib.escape(s)}</span>'

    string_name = m.group(1).upper()
    pipe = m.group(2)
    rest = html_lib.escape(m.group(3))
    rest = re.sub(
        r'(\d+|x|X|/|\\|~|h|p|b)',
        r'<span class="tab-tech">\1</span>',
        rest,
    )
    return (
        f'<span class="cifra-tab-line">'
        f'<span class="tab-string">{string_name}{html_lib.escape(pipe)}</span>'
        f'{rest}'
        f'</span>'
    )


def _render_tab_block(lines: list[str]) -> str:
    parts = ['<div class="cifra-tab-block">']
    for line in lines:
        if not line.strip():
            continue
        s = line.strip()
        if _is_tab_header(s):
            parts.append(f'<span class="cifra-tab-title">{html_lib.escape(s)}</span>')
        elif _is_tab_meta_line(s):
            parts.append(f'<span class="cifra-tab-meta">{html_lib.escape(s)}</span>')
        elif _is_tab_line(s):
            parts.append(_highlight_tab_line_html(s))
        else:
            parts.append(f'<span class="cifra-tab-meta">{html_lib.escape(s)}</span>')
    parts.append('</div>')
    return ''.join(parts)


def highlight_chords_html(text):
    """
    Converte texto de cifra em HTML com acordes destacados.
    - Linhas de acorde puro: fundo sutil + cada acorde em <span class="chord">
    - Linhas com [Acorde] inline: destaca os colchetes
    - Linhas de letra: texto normal
    Seguro contra XSS: o conteúdo do usuário é escapado antes de qualquer markup.
    """
    if text is None:
        text = ''
    text = sanitize_tab_html_artifacts(text)
    lines = text.split('\n')
    result = []
    i = 0

    from chordpro import parse_chordpro_directive, SECTION_DIRECTIVES

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            result.append('')
            i += 1
            continue

        directive = parse_chordpro_directive(line.strip())
        if directive:
            name, value = directive
            if name == 'comment':
                label = html_lib.escape(value or '—')
                result.append(f'<span class="cifra-section">{label}</span>')
            elif name in SECTION_DIRECTIVES:
                label = html_lib.escape(value or SECTION_DIRECTIVES[name].title())
                result.append(f'<span class="cifra-section">{label}</span>')
            elif name not in ('title', 't', 'artist', 'subtitle', 'st', 'key', 'capo', 'tempo', 'time'):
                if not name.startswith('end_of'):
                    result.append(
                        f'<span class="cifra-directive">{html_lib.escape(line.strip())}</span>'
                    )
            i += 1
            continue

        if _is_tab_header(line) or _is_tab_line(line) or (
            _is_tab_meta_line(line) and i + 1 < len(lines) and _is_tab_line(lines[i + 1])
        ):
            block = []
            while i < len(lines):
                cur = lines[i]
                if not cur.strip():
                    if block:
                        i += 1
                        break
                    i += 1
                    continue
                if block and not (
                    _is_tab_header(cur) or _is_tab_line(cur) or _is_tab_meta_line(cur)
                ):
                    break
                block.append(cur)
                i += 1
            result.append(_render_tab_block(block))
            continue

        # Formato inline [Am] palavra [G] palavra
        if re.search(r'\[[A-G][^\]]{0,10}\]', line):
            escaped = html_lib.escape(line)
            highlighted = re.sub(
                r'\[([A-G][^\]]{0,10})\]',
                r'<span class="chord">[\1]</span>',
                escaped
            )
            result.append(f'<span class="cifra-lyric">{highlighted}</span>')
            i += 1
            continue

        # Linha só de acordes
        if _is_chord_line(line):
            escaped = html_lib.escape(line)
            highlighted = CHORD_INLINE_RE.sub(
                r'<span class="chord">\1</span>',
                escaped
            )
            result.append(f'<span class="cifra-chords">{highlighted}</span>')
            i += 1
            continue

        # Linha de letra
        result.append(f'<span class="cifra-lyric">{html_lib.escape(line)}</span>')
        i += 1

    return '\n'.join(result)


def highlight_chords_play_html(text):
    """HTML para modo tocar: TAB formatada + acordes acima da letra (sp-line)."""
    if text is None:
        text = ''
    text = sanitize_tab_html_artifacts(text)
    lines = text.split('\n')
    result = []
    i = 0
    re_br = re.compile(r'\[([^\]]+)\]([^\[]*)')

    from chordpro import parse_chordpro_directive, SECTION_DIRECTIVES

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            result.append('')
            i += 1
            continue

        directive = parse_chordpro_directive(line.strip())
        if directive:
            name, value = directive
            if name == 'comment':
                label = html_lib.escape(value or '—')
                result.append(f'<span class="cifra-section">{label}</span>')
            elif name in SECTION_DIRECTIVES:
                label = html_lib.escape(value or SECTION_DIRECTIVES[name].title())
                result.append(f'<span class="cifra-section">{label}</span>')
            elif name not in ('title', 't', 'artist', 'subtitle', 'st', 'key', 'capo', 'tempo', 'time'):
                if not name.startswith('end_of'):
                    result.append(
                        f'<span class="cifra-directive">{html_lib.escape(line.strip())}</span>'
                    )
            i += 1
            continue

        if _is_tab_header(line) or _is_tab_line(line) or (
            _is_tab_meta_line(line) and i + 1 < len(lines) and _is_tab_line(lines[i + 1])
        ):
            block = []
            while i < len(lines):
                cur = lines[i]
                if not cur.strip():
                    if block:
                        i += 1
                        break
                    i += 1
                    continue
                if block and not (
                    _is_tab_header(cur) or _is_tab_line(cur) or _is_tab_meta_line(cur)
                ):
                    break
                block.append(cur)
                i += 1
            result.append(_render_tab_block(block))
            continue

        if re.search(r'\[[A-G][^\]]{0,10}\]', line):
            parts = ['<div class="sp-line">']
            last = 0
            found = False
            for m in re_br.finditer(line):
                found = True
                # Preserva texto antes do primeiro acorde (ou entre matches)
                if m.start() > last:
                    prefix = line[last:m.start()]
                    if prefix:
                        parts.append(
                            '<span class="sp-item">'
                            '<span class="sp-chord"></span>'
                            f'<span class="sp-word">{html_lib.escape(prefix)}</span>'
                            '</span>'
                        )

                chord = html_lib.escape(m.group(1).strip())
                lyric = html_lib.escape(m.group(2) or '')
                parts.append(
                    '<span class="sp-item">'
                    f'<span class="sp-chord">{chord}</span>'
                    f'<span class="sp-word">{lyric}</span>'
                    '</span>'
                )
                last = m.end()

            # Sufixo sem acorde no fim da linha
            if found and last < len(line):
                suffix = line[last:]
                if suffix:
                    parts.append(
                        '<span class="sp-item">'
                        '<span class="sp-chord"></span>'
                        f'<span class="sp-word">{html_lib.escape(suffix)}</span>'
                        '</span>'
                    )

            parts.append('</div>')
            result.append(''.join(parts))
            i += 1
            continue

        if _is_chord_line(line):
            escaped = html_lib.escape(line)
            highlighted = CHORD_INLINE_RE.sub(
                r'<span class="chord">\1</span>',
                escaped,
            )
            result.append(f'<span class="cifra-chords">{highlighted}</span>')
            i += 1
            continue

        result.append(f'<span class="cifra-lyric">{html_lib.escape(line)}</span>')
        i += 1

    return '\n'.join(result)
