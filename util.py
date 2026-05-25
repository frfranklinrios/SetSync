
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
    - majX / MX -> X+ (ex.: Cmaj7 -> C7+)
    - dim / dim7 -> ° / °7
    - min -> m
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
    q = re.sub(r'(?i)maj(\d+)', r'\1+', q)
    q = re.sub(r'(?i)M(\d+)', r'\1+', q)
    q = re.sub(r'(?i)dim7', '°7', q)
    q = re.sub(r'(?i)dim', '°', q)
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
_CHORD_HEAD = r'[A-G][#b]?'
_CHORD_BASS = r'(?:/[A-G][#b]?)?'

# Para uso em match exato (token completo)
CHORD_TOKEN_RE = re.compile(
    r'^' + _CHORD_HEAD + r'(?:' + _CHORD_PART + r')*' + _CHORD_BASS + r'$'
)
# Para uso em substituição inline dentro de uma linha
CHORD_INLINE_RE = re.compile(
    r'(' + _CHORD_HEAD + r'(?:' + _CHORD_PART + r')*' + _CHORD_BASS + r')'
)
# Versão com word boundary para uso em texto livre
_CHORD_REGEX_WB = (
    r'\b(' + _CHORD_HEAD + r'(?:' + _CHORD_PART + r')*' + _CHORD_BASS + r')\b'
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
    """Retorna os tons disponíveis para transposição"""
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


def _is_chord_token(token):
    """Verifica se um token isolado é um acorde válido"""
    t = token.strip('()[]{} ')
    t = re.sub(r'[°º]', 'dim', t)
    return bool(CHORD_TOKEN_RE.match(t))


def _is_chord_line(line):
    """Retorna True se a linha for predominantemente acordes"""
    tokens = [t for t in line.split() if t.strip('()[]{} ')]
    if not tokens:
        return False
    chord_count = sum(1 for t in tokens if _is_chord_token(t))
    return chord_count >= max(1, len(tokens) * 0.7)


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
    lines = text.split('\n')
    result = []

    for line in lines:
        if not line.strip():
            result.append('')
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

        # Linha só de acordes
        elif _is_chord_line(line):
            escaped = html_lib.escape(line)
            highlighted = CHORD_INLINE_RE.sub(
                r'<span class="chord">\1</span>',
                escaped
            )
            result.append(f'<span class="cifra-chords">{highlighted}</span>')

        # Linha de letra
        else:
            result.append(f'<span class="cifra-lyric">{html_lib.escape(line)}</span>')

    return '\n'.join(result)
