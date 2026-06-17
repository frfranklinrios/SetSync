#!/usr/bin/env python3
"""Extrai CD.REAL_SHAPES de real-shapes.js para JSON (uso no servidor)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'static/js/chord-diagram/real-shapes.js'
OUT = ROOT / 'chord_diagram/data/real_shapes.json'

P_CALL = re.compile(
    r"P\(\s*'([^']*)'\s*,\s*\[([^\]]+)\]\s*(?:,\s*\[([^\]]+)\])?\s*\)",
)


def _parse_frets_blob(blob: str) -> list:
    out = []
    for p in blob.split(','):
        p = p.strip().strip("'\"")
        if p == 'x':
            out.append('x')
        else:
            out.append(int(p))
    return out


def _parse_fingers_blob(blob: str | None) -> list[int] | None:
    if not blob:
        return None
    return [int(x.strip()) for x in blob.split(',') if x.strip().lstrip('-').isdigit()]


def _extract_positions(chunk: str) -> list[dict]:
    out = []
    for m in P_CALL.finditer(chunk):
        out.append({
            'label': m.group(1),
            'frets': _parse_frets_blob(m.group(2)),
            'fingers': _parse_fingers_blob(m.group(3)),
            'source': 'Cifra clássica',
        })
    return out


def main() -> int:
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
        m_inst = re.match(r'\s+(violao|cavaco|ukulele):\s*\{', line)
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

        m_inline = re.match(r"\s+('?[\w#]+'?):\s*\[(.*)\],?\s*$", line)
        if m_inline and inst and 'P(' in line:
            flush_chord()
            chord = m_inline.group(1).strip("'")
            positions = _extract_positions(m_inline.group(2))
            if positions:
                bank[inst][chord] = positions
            continue

        m_open = re.match(r"\s+('?[\w#]+'?):\s*\[", line)
        if m_open and inst:
            flush_chord()
            pending_chord = m_open.group(1).strip("'")
            rest = line[m_open.end():]
            pending_chunk = [rest]
            if '],' in line or line.rstrip().endswith('],'):
                flush_chord()
            continue

        if pending_chord is not None:
            pending_chunk.append(line)
            if '],' in line:
                flush_chord()

    flush_chord()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
    total = sum(len(v) for i in bank.values() for v in i.values())
    print(f'Gerado {OUT} — {total} posições em {len(bank)} instrumentos')
    return 0


if __name__ == '__main__':
    sys.exit(main())
