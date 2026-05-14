import re
import html as html_lib

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

# Regex de acorde completo (base + modificadores + baixo opcional)
_CHORD_MOD = r'(?:maj7|maj|min|m7b5|m7|m|dim7|dim|aug|sus2|sus4|sus|add9|add|7|9|11|13|6|5|4|2)?'
_CHORD_BASS = r'(?:/[A-G][#b]?)?'
CHORD_INLINE_RE = re.compile(
    r'([A-G][#b]?' + _CHORD_MOD + _CHORD_BASS + r')'
)
CHORD_TOKEN_RE = re.compile(
    r'^[A-G][#b]?' + _CHORD_MOD + _CHORD_BASS + r'$'
)

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
    return bool(CHORD_TOKEN_RE.match(token.strip('()[]{} ')))


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
    cifra = "Am - E - Am\nC - G - C\n[Am] Verso 1\n[E7] Refrão"
    print("Original:")
    print(cifra)
    print("\nTransposto +2 semitons (A para B):")
    print(transpose_text(cifra, 2))
    print("\nTransposto -3 semitons:")
    print(transpose_text(cifra, -3))
