#!/usr/bin/env python3
"""Converte tombatossals/chords-db para SetSync REAL_SHAPES (violao/ukulele)."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

SUFFIX_TO_KEY = {
    'major': '',
    'minor': 'm',
    'dim': 'dim',
    'dim7': 'dim7',
    'm7b5': 'm7b5',
    'aug': 'aug',
    'sus2': 'sus2',
    'sus4': 'sus4',
    '7sus4': '7sus4',
    'major7': 'maj7',
    'm7': 'm7',
    '7': '7',
    '6': '6',
    'm6': 'm6',
    '9': '9',
    'm9': 'm9',
    'maj9': 'maj9',
    'add9': 'add9',
    '11': '11',
    'm11': 'm11',
    '13': '13',
    'm13': 'm13',
    'maj13': 'maj13',
    'alt': 'alt',
    '5': '5',
}

INSTRUMENT_DIRS = {
    'guitar': 'violao',
    'ukulele': 'ukulele',
}


def parse_frets(s: str) -> list:
    out = []
    for ch in s:
        if ch.lower() == 'x':
            out.append('x')
        elif ch.isdigit():
            out.append(int(ch))
        elif ch.lower() in 'abcdef':
            out.append(10 + ord(ch.lower()) - ord('a'))
        else:
            out.append('x')
    return out


def parse_fingers(s: str | None, n: int) -> list | None:
    if not s:
        return None
    out = []
    for ch in s:
        if ch == '0':
            out.append(0)
        elif ch.isdigit():
            out.append(int(ch))
        elif ch.lower() == 't':
            out.append(1)
        else:
            out.append(0)
    while len(out) < n:
        out.append(0)
    return out[:n]


def chord_symbol(key: str, suffix: str) -> str:
    q = SUFFIX_TO_KEY.get(suffix, suffix)
    return f'{key}{q}' if q else key


def load_chord_file(path: Path) -> dict | None:
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'export\s+default\s+', '', text.strip()).rstrip(';')
    # JS object → JSON (chaves e strings com aspas simples)
    text = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', text)
    text = text.replace("'", '"')
    text = re.sub(r',\s*([}\]])', r'\1', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def build_bank(repo: Path, instrument: str, max_positions: int = 3) -> dict:
    base = repo / 'src' / 'db' / instrument / 'chords'
    if not base.is_dir():
        return {}
    bank: dict[str, list] = {}
    for key_dir in sorted(base.iterdir()):
        if not key_dir.is_dir():
            continue
        for js_file in sorted(key_dir.glob('*.js')):
            data = load_chord_file(js_file)
            if not data:
                continue
            sym = chord_symbol(data.get('key', key_dir.name), data.get('suffix', ''))
            positions = []
            for pos in (data.get('positions') or [])[:max_positions]:
                frets_s = pos.get('frets', '')
                if not frets_s:
                    continue
                frets = parse_frets(frets_s)
                fingers = parse_fingers(pos.get('fingers'), len(frets))
                capo = pos.get('capo')
                barre = pos.get('barres')
                label = 'Padrão'
                if capo and barre:
                    label = f'{barre}ª casa (pestana)'
                elif barre:
                    label = f'{barre}ª casa'
                elif frets.count(0) >= 2:
                    label = 'Abertura'
                positions.append({
                    'label': label,
                    'frets': frets,
                    'fingers': fingers,
                    'source': 'chords-db',
                })
            if positions:
                bank.setdefault(sym, []).extend(positions)
    return bank


def js_escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace("'", "\\'")


def emit_shape(pos: dict) -> str:
    frets = json.dumps(pos['frets'])
    fingers = json.dumps(pos['fingers']) if pos.get('fingers') else 'null'
    return (
        f"P('{js_escape(pos['label'])}', {frets}, {fingers}, '{js_escape(pos.get('source', 'chords-db'))}')"
    )


def main() -> None:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/chords-db')
    out = Path(__file__).resolve().parent.parent / 'static' / 'js' / 'chord-diagram' / 'chords-db-shapes.js'
    if not repo.is_dir():
        print(f'Repositório não encontrado: {repo}', file=sys.stderr)
        sys.exit(1)

    lines = [
        '/** Posições importadas de tombatossals/chords-db — gerado por scripts/build_chords_db_shapes.py */',
        '(function (global) {',
        '  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});',
        '  function P(label, frets, fingers, source) {',
        "    return { label: label, frets: frets, fingers: fingers || null, source: source || 'chords-db' };",
        '  }',
        '  CD.CHORDS_DB_SHAPES = {',
    ]

    for inst_dir, inst_key in INSTRUMENT_DIRS.items():
        bank = build_bank(repo, inst_dir)
        lines.append(f'    {inst_key}: {{')
        for sym in sorted(bank.keys()):
            shapes = bank[sym]
            joined = ',\n      '.join(emit_shape(p) for p in shapes)
            lines.append(f"      '{sym}': [\n      {joined}\n      ],")
        lines.append('    },')

    lines.extend([
        '  };',
        '})(typeof window !== "undefined" ? window : globalThis);',
        '',
    ])
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Gerado {out} ({out.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
