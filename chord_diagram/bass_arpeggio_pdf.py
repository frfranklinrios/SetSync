"""Extrai padrões de arpejo de PDFs com diagramas de braço (4 cordas).

Compatível com *The Bass Guitar Resource Book* (Dan Hawkins / Online Bass Courses)
e manuais similares (ex.: TalkingBass Arpeggio Reference Manual).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

# Braço no diagrama: corda G no topo → E embaixo (como no livro)
BASS_TUNING_TOP_DOWN = ('G', 'D', 'A', 'E')
STRING_OPEN_PC = {'E': 4, 'A': 9, 'D': 2, 'G': 7}

CHORD_SYMBOL_RE = re.compile(
    r'^(?:'
    r'C(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|D(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|E(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|F(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|G(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|A(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|B(?:maj7|maj|m7b5|m7|m|7|dim7|dim|aug|sus4|sus2|6)?'
    r'|C#,D#,F#,G#,A#'
    r')$',
    re.I,
)

TITLE_ALIASES = {
    'major triad': ('C', 'maj'),
    'minor triad': ('C', 'm'),
    'augmented triad': ('C', 'aug'),
    'diminished triad': ('C', 'dim'),
    'major 7': ('C', 'maj7'),
    'dominant 7': ('C', '7'),
    'minor 7': ('C', 'm7'),
    'minor(major 7)': ('C', 'mmaj7'),
    'major7#5': ('C', 'maj7#5'),
    'dominant 7#5': ('C', '7#5'),
    'minor7b5': ('C', 'm7b5'),
    'diminished 7th': ('C', 'dim7'),
    'c major 7': ('C', 'maj7'),
    'd minor 7': ('D', 'm7'),
    'e minor 7': ('E', 'm7'),
    'f major 7': ('F', 'maj7'),
    'g dominant 7': ('G', '7'),
    'a minor 7': ('A', 'm7'),
    'b minor 7 flat 5': ('B', 'm7b5'),
    'b minor 7 b5': ('B', 'm7b5'),
}


@dataclass
class ArpeggioStep:
    string: str
    fret: int
    finger: int | None = None
    interval: str = ''
    note: str = ''
    is_root: bool = False


@dataclass
class ArpeggioPattern:
    id: str
    label: str
    root: str
    quality: str
    symbols: list[str] = field(default_factory=list)
    intervals: list[str] = field(default_factory=list)
    steps: list[ArpeggioStep] = field(default_factory=list)
    source: str = ''
    pattern: str = 'root'
    base_fret: int = 0


def _is_red(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r > 150 and g < 120 and b < 120 and r > g + 40


def _is_dark_dot(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r < 90 and g < 90 and b < 90


def _cluster_centers(mask: np.ndarray, min_pixels: int = 40) -> list[tuple[int, int]]:
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    centers: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visited[y, x]:
                continue
            stack = [(x, y)]
            pts: list[tuple[int, int]] = []
            visited[y, x] = True
            while stack:
                cx, cy = stack.pop()
                pts.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((nx, ny))
            if len(pts) >= min_pixels:
                ax = sum(p[0] for p in pts) / len(pts)
                ay = sum(p[1] for p in pts) / len(pts)
                centers.append((int(ax), int(ay)))
    return centers


def _string_rows(h: int) -> list[int]:
    # 4 cordas igualmente espaçadas na faixa central do diagrama
    top, bottom = int(h * 0.18), int(h * 0.82)
    return [int(top + (bottom - top) * i / 3) for i in range(4)]


def _find_nut_x(img: np.ndarray) -> int:
    h, w = img.shape[:2]
    col_strength = []
    for x in range(int(w * 0.05), int(w * 0.25)):
        col = img[:, x, :].mean(axis=1)
        strength = (col < 40).sum()
        col_strength.append((strength, x))
    col_strength.sort(reverse=True)
    return col_strength[0][1] if col_strength else int(w * 0.08)


def parse_fretboard_image(
    img_path: str | Path,
    *,
    frets_visible: int = 8,
) -> list[dict]:
    """Detecta bolinhas no diagrama 4 cordas e retorna passos ordenados (grave → agudo)."""
    img = np.array(Image.open(img_path).convert('RGB'))
    h, w = img.shape[:2]
    nut_x = _find_nut_x(img)
    fret_w = (w - nut_x - 4) / frets_visible
    string_ys = _string_rows(h)

    red_mask = np.zeros((h, w), dtype=bool)
    dark_mask = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(w):
            rgb = tuple(int(v) for v in img[y, x])
            if _is_red(rgb):
                red_mask[y, x] = True
            elif _is_dark_dot(rgb):
                dark_mask[y, x] = True

    dots: list[tuple[int, int, bool]] = []
    for cx, cy in _cluster_centers(red_mask):
        dots.append((cx, cy, True))
    for cx, cy in _cluster_centers(dark_mask):
        if not any(abs(cx - ox) < 12 and abs(cy - oy) < 12 for ox, oy, _ in dots):
            dots.append((cx, cy, False))

    dots.sort(key=lambda d: (d[0], d[1]))

    steps: list[dict] = []
    for cx, cy, is_root in dots:
        string_idx = min(range(4), key=lambda i: abs(string_ys[i] - cy))
        fret = max(0, min(frets_visible, round((cx - nut_x - fret_w / 2) / fret_w)))
        string_name = BASS_TUNING_TOP_DOWN[string_idx]
        steps.append({
            'string': string_name,
            'fret': fret,
            'is_root': is_root,
        })
    return steps


def _note_at(string: str, fret: int, key: str = 'C') -> str:
    from chord_diagram.theory.pitch import pc_to_spelling

    oi = STRING_OPEN_PC.get(string)
    if oi is None:
        return ''
    pc = (oi + fret) % 12
    return pc_to_spelling(pc, key)


def enrich_steps(steps: list[dict], root: str, quality: str) -> list[ArpeggioStep]:
    from chord_diagram.theory.chord_parser import chord_theory_block

    theory = chord_theory_block(root + _quality_suffix(quality))
    notes = (theory or {}).get('notes') or []
    root_pc = None
    if notes:
        from chord_diagram.theory.pitch import note_to_pc
        root_pc = note_to_pc(notes[0])

    out: list[ArpeggioStep] = []
    for i, st in enumerate(steps):
        note = _note_at(st['string'], st['fret'], root)
        interval = ''
        if notes and root_pc is not None:
            from chord_diagram.theory.pitch import note_to_pc
            from chord_diagram.theory.intervals import interval_name
            ni = note_to_pc(note)
            if ni is not None:
                interval = interval_name((ni - root_pc) % 12)
        out.append(ArpeggioStep(
            string=st['string'],
            fret=st['fret'],
            interval=interval or str(i + 1),
            note=note,
            is_root=bool(st.get('is_root')),
        ))
    return out


def _quality_suffix(quality: str) -> str:
    q = quality.lower()
    if q in ('maj', 'major'):
        return ''
    if q == 'maj7':
        return 'maj7'
    if q == 'mmaj7':
        return 'maj7'  # placeholder; parser uses m separately
    return q


def _parse_title(text: str) -> tuple[str, str, str] | None:
    t = re.sub(r'\s+', ' ', text.strip().lower())
    if t in TITLE_ALIASES:
        root, q = TITLE_ALIASES[t]
        return root, q, text.strip()
    # "C Major 7" style
    m = re.match(r'^([a-g]#?)\s+(major\s*7|minor\s*7|dominant\s*7|major|minor)', t, re.I)
    if m:
        root = m.group(1)[0].upper() + m.group(1)[1:]
        kind = m.group(2).lower().replace(' ', '')
        qmap = {
            'major7': 'maj7', 'minor7': 'm7', 'dominant7': '7',
            'major': 'maj', 'minor': 'm',
        }
        return root, qmap.get(kind, kind), text.strip()
    m = re.match(r'^(major|minor|dominant|diminished|augmented)\s*(7|triad)?', t, re.I)
    if m:
        kind = (m.group(1) + (m.group(2) or '')).lower().replace(' ', '')
        qmap = {
            'majortriad': 'maj', 'minortriad': 'm', 'augmentedtriad': 'aug',
            'diminishedtriad': 'dim', 'major7': 'maj7', 'minor7': 'm7',
            'dominant7': '7', 'diminished7': 'dim7',
        }
        q = qmap.get(kind.replace(' ', ''), 'maj7')
        return 'C', q, text.strip()
    return None


def extract_patterns_from_pdf(
    pdf_path: str | Path,
    *,
    source: str = 'The Bass Guitar Resource Book',
) -> list[ArpeggioPattern]:
    import fitz

    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    if pdf_path.read_bytes()[:4] != b'%PDF':
        raise ValueError(f'Arquivo não é PDF válido: {pdf_path}')

    doc = fitz.open(str(pdf_path))
    patterns: list[ArpeggioPattern] = []
    seen: set[str] = set()

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # Diagramas pequenos (~306px) com bolinhas
        for img_i, img_info in enumerate(page.get_images()):
            xref = img_info[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.width > 400 or pix.height > 220:
                continue
            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            tmp = pdf_path.parent / f'_bass_diag_{page_idx}_{img_i}.png'
            pix.save(str(tmp))
            raw_steps = parse_fretboard_image(tmp)
            tmp.unlink(missing_ok=True)
            if len(raw_steps) < 3:
                continue

            title = _title_for_diagram(lines, img_i)
            if not title:
                continue
            parsed = _parse_title(title)
            if not parsed:
                continue
            root, quality, label = parsed
            pid = f'{root}_{quality}'
            if pid in seen:
                continue
            seen.add(pid)

            steps = enrich_steps(raw_steps, root, quality)
            nums = [s.fret for s in steps if s.fret > 0]
            base = max(0, min(nums) - 1) if nums else 0

            patterns.append(ArpeggioPattern(
                id=pid,
                label=label,
                root=root,
                quality=quality,
                symbols=[root + _quality_suffix(quality)],
                steps=steps,
                source=source,
                pattern='root',
                base_fret=base,
            ))

    doc.close()
    return patterns


def _title_for_diagram(lines: list[str], img_index: int) -> str | None:
    """Heurística: título imediatamente antes do diagrama na página."""
    candidates = []
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in (
            'triad', 'major 7', 'minor 7', 'dominant 7', 'diminished',
            'major 7', 'c major', 'd minor', 'e minor', 'f major',
            'g dominant', 'a minor', 'b minor',
        )):
            candidates.append(ln)
    if img_index < len(candidates):
        return candidates[img_index]
    return candidates[0] if len(candidates) == 1 else None


def patterns_to_bank(patterns: list[ArpeggioPattern]) -> dict:
    bank: dict = {
        'meta': {
            'source': patterns[0].source if patterns else 'The Bass Guitar Resource Book',
            'instrument': 'baixo4',
            'tuning': list(reversed(BASS_TUNING_TOP_DOWN)),  # E A D G
            'strings': 4,
        },
        'patterns': {},
    }
    for p in patterns:
        key = p.root + _quality_suffix(p.quality)
        entry = {
            'id': p.id,
            'label': p.label,
            'root': p.root,
            'quality': p.quality,
            'symbols': p.symbols,
            'pattern': p.pattern,
            'baseFret': p.base_fret,
            'source': p.source,
            'steps': [
                {
                    'string': s.string,
                    'fret': s.fret,
                    'finger': s.finger,
                    'interval': s.interval,
                    'note': s.note,
                    'isRoot': s.is_root,
                }
                for s in p.steps
            ],
        }
        bank['patterns'].setdefault(key, []).append(entry)
    return bank
