#!/usr/bin/env python3
"""Extrai CD.CHORDS_DB_SHAPES de chords-db-shapes.js para JSON (uso no servidor)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'static/js/chord-diagram/chords-db-shapes.js'
OUT = ROOT / 'chord_diagram/data/chords_db_shapes.json'

P_CALL = re.compile(
    r"P\(\s*'([^']*)'\s*,\s*\[([^\]]+)\]\s*(?:,\s*\[([^\]]+)\])?(?:,\s*'([^']*)')?(?:,\s*(\[[^\]]*\]))?\s*\)",
)


def _parse_barres_blob(blob: str | None) -> list[dict]:
    if not blob:
        return []
    try:
        raw = json.loads(blob)
    except json.JSONDecodeError:
        return []
    out = []
    for b in raw:
        if not isinstance(b, dict):
            continue
        out.append({
            'fret': b.get('fret'),
            'from': b.get('from'),
            'to': b.get('to'),
        })
    return out


def _parse_frets_blob(blob: str) -> list:
    out = []
    for p in blob.split(','):
        p = p.strip().strip("'\"")
        if p.lower() == 'x':
            out.append('x')
        else:
            out.append(int(p))
    return out


def _parse_fingers_blob(blob: str | None) -> list[int] | None:
    if not blob:
        return None
    out = []
    for x in blob.split(','):
        x = x.strip()
        if x.lstrip('-').isdigit():
            out.append(int(x))
    return out or None


def _extract_positions(chunk: str) -> list[dict]:
    out = []
    for m in P_CALL.finditer(chunk):
        out.append({
            'label': m.group(1),
            'frets': _parse_frets_blob(m.group(2)),
            'fingers': _parse_fingers_blob(m.group(3)),
            'source': m.group(4) or 'chords-db',
            'barres': _parse_barres_blob(m.group(5)),
        })
    return out


def main() -> int:
    if not JS.is_file():
        print(f'Arquivo não encontrado: {JS}', file=sys.stderr)
        return 1
    text = JS.read_text(encoding='utf-8')
    bank: dict = {}
    inst = None
    pending_chord = None
    pending_chunk: list[str] = []

    def flush_chord():
        nonlocal pending_chord, pending_chunk
        if inst and pending_chord is not None:
            chunk = '\n'.join(pending_chunk)
            positions = _extract_positions(chunk)
            if positions:
                bank.setdefault(inst, {})[pending_chord] = positions
        pending_chord = None
        pending_chunk = []

    for raw in text.splitlines():
        line = raw.rstrip()
        m_inst = re.match(r'\s+(violao|ukulele):\s*\{', line)
        if m_inst:
            flush_chord()
            inst = m_inst.group(1)
            bank.setdefault(inst, {})
            continue
        if re.match(r'\s+\},?\s*$', line) and pending_chord is None:
            if line.strip().startswith('}'):
                flush_chord()
                inst = None
            continue

        m_inline = re.match(r"\s+('?[#\w/]+'?):\s*\[(.*)\],?\s*$", line)
        if m_inline and inst and 'P(' in line:
            flush_chord()
            chord = m_inline.group(1).strip("'")
            positions = _extract_positions(m_inline.group(2))
            if positions:
                bank[inst][chord] = positions
            continue

        m_open = re.match(r"\s+('?[#\w/]+'?):\s*\[", line)
        if m_open and inst:
            flush_chord()
            pending_chord = m_open.group(1).strip("'")
            rest = line[m_open.end():]
            pending_chunk = [rest]
            if re.match(r'\s*\],?\s*$', line):
                flush_chord()
            continue

        if pending_chord is not None:
            pending_chunk.append(line)
            if re.match(r'\s*\],?\s*$', line):
                flush_chord()

    flush_chord()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
    total = sum(len(v) for i in bank.values() for v in i.values())
    print(f'Gerado {OUT} — {total} posições em {len(bank)} instrumentos')
    return 0


if __name__ == '__main__':
    sys.exit(main())
