#!/usr/bin/env python3
"""Gera JSON/JS de arpejos de baixo a partir de The Bass Guitar Resource Book (PDF).

Uso:
  python3 scripts/build_bass_arpeggios_from_pdf.py \\
    /tmp/The-Bass-Guitar-Resource-Book.pdf

Se o PDF não existir ou não for válido, usa o seed embutido (7 arpejos
harmonizados de Dó maior + tríades/sétimas básicas do livro).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chord_diagram.bass_arpeggio_bank import default_seed_bank
from chord_diagram.bass_arpeggio_pdf import extract_patterns_from_pdf, patterns_to_bank

OUT_JSON = ROOT / 'chord_diagram' / 'data' / 'bass_arpeggio_shapes.json'
OUT_JS = ROOT / 'static' / 'js' / 'chord-diagram' / 'bass-arpeggio-shapes.js'


def _merge_banks(seed: dict, extracted: dict) -> dict:
    merged = {
        'meta': extracted.get('meta') or seed.get('meta'),
        'patterns': dict(seed.get('patterns') or {}),
    }
    for sym, entries in (extracted.get('patterns') or {}).items():
        merged['patterns'].setdefault(sym, [])
        seen = {json.dumps(e.get('steps'), sort_keys=True) for e in merged['patterns'][sym]}
        for e in entries:
            key = json.dumps(e.get('steps'), sort_keys=True)
            if key not in seen:
                merged['patterns'][sym].append(e)
                seen.add(key)
    return merged


def write_js(bank: dict, path: Path) -> None:
    payload = json.dumps(bank, ensure_ascii=False, indent=2)
    path.write_text(
        '/** Arpejos de baixo — gerado por scripts/build_bass_arpeggios_from_pdf.py */\n'
        '(function (global) {\n'
        '  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});\n'
        f'  CD.BASS_ARPEGGIO_BANK = {payload};\n'
        '})(typeof window !== "undefined" ? window : globalThis);\n',
        encoding='utf-8',
    )


def main() -> int:
    ap = argparse.ArgumentParser(description='Gera JSON de arpejos de baixo a partir do PDF')
    ap.add_argument(
        'pdf',
        nargs='?',
        default='/tmp/The-Bass-Guitar-Resource-Book.pdf',
        help='Caminho do PDF (The Bass Guitar Resource Book)',
    )
    ap.add_argument('--source', default='The Bass Guitar Resource Book')
    args = ap.parse_args()

    seed = default_seed_bank()
    pdf_path = Path(args.pdf)

    bank = seed
    if pdf_path.is_file() and pdf_path.read_bytes()[:4] == b'%PDF':
        try:
            patterns = extract_patterns_from_pdf(pdf_path, source=args.source)
            if patterns:
                extracted = patterns_to_bank(patterns)
                bank = _merge_banks(seed, extracted)
                print(f'Extraídos {len(patterns)} padrões do PDF; mesclados com seed.')
            else:
                print('PDF sem diagramas reconhecidos; usando seed do livro.')
        except Exception as exc:
            print(f'Aviso: falha na extração ({exc}); usando seed.')
    else:
        print(f'PDF não encontrado ou inválido em {pdf_path}; gravando seed do livro.')

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
    write_js(bank, OUT_JS)
    n = sum(len(v) for v in bank.get('patterns', {}).values())
    print(f'OK: {n} entradas → {OUT_JSON}')
    print(f'OK: {OUT_JS}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
