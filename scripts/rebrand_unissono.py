#!/usr/bin/env python3
"""Substitui marca visível SetSync → Uníssono (preserva identificadores técnicos)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'data',
    'static/screenshots', 'chord_diagram/data', '.claude', '.cursor',
}

SKIP_FILES = {
    'scripts/rebrand_unissono.py',
    'uv.lock',
    '.env',
    'docker-compose.prod.yml',
    'docker-compose.postgres.yml',
}

# Não alterar: globals JS, formatos, domínio, env vars, paths internos
SKIP_LINE_RE = re.compile(
    r'SetSyncCifra|setSetSyncTheme|setsync-theme|setsync_cifra|setsync_grade|'
    r'setsync\.com\.br|SETSYNC_|setsync_export|logoSetSync|setsync-mail|'
    r'setsync-web|setsync-api|palco-logo-setsync|@setsync\.com|'
    r'setsync\.dados\.tec|postgresql://setsync|SetSync/cifras_tool|'
    r'window\.SetSync|SetSyncChordPro|SetSyncGradeVisual|SetSyncCifraClubPaste|'
    r'setsync-theme\.css|setsync_cifra\.json|setsync_grade\.json',
    re.I,
)

EXTS = {'.html', '.py', '.md', '.webmanifest', '.js', '.css', '.json', '.txt', '.yml'}

# Ordem importa: frases compostas antes do catch-all
REPLACEMENTS: list[tuple[str, str]] = [
    ('SetSync Cifras e Setlists', 'Uníssono — Cifras e Setlists'),
    ('SetSync para Igrejas', 'Uníssono para Igrejas'),
    ('SetSync para Estúdios', 'Uníssono para Estúdios'),
    ('SetSync para igrejas', 'Uníssono para igrejas'),
    ('SetSync para estúdios', 'Uníssono para estúdios'),
    ('Bem-vindo ao SetSync', 'Bem-vindo ao Uníssono'),
    ('Ajuda SetSync', 'Ajuda Uníssono'),
    ('Guia do SetSync', 'Guia do Uníssono'),
    ('Cifra → SetSync', 'Cifra → Uníssono'),
    ('Cifra -> SetSync', 'Cifra → Uníssono'),
    ('Gerado pelo SetSync', 'Gerado pelo Uníssono'),
    ('Relatório gerado pelo SetSync', 'Relatório gerado pelo Uníssono'),
    ('marca SetSync', 'marca Uníssono'),
    ('padrão SetSync', 'padrão Uníssono'),
    ('estilo SetSync', 'estilo Uníssono'),
    ('formato do SetSync', 'formato do Uníssono'),
    ('formato SetSync', 'formato Uníssono'),
    ('equipe SetSync', 'equipe Uníssono'),
    ('suporte SetSync', 'suporte Uníssono'),
    ('no SetSync', 'no Uníssono'),
    ('ao SetSync', 'ao Uníssono'),
    ('do SetSync', 'do Uníssono'),
    ('pelo SetSync', 'pelo Uníssono'),
    ('O SetSync', 'O Uníssono'),
    ('o SetSync', 'o Uníssono'),
    ('SetSync <', 'Uníssono <'),
    ('SetSync —', 'Uníssono —'),
    ('SetSync -', 'Uníssono —'),
    ('- SetSync', '— Uníssono'),
    ('· SetSync', '· Uníssono'),
    ('SetSync!', 'Uníssono!'),
    ('SetSync.', 'Uníssono.'),
    ('SetSync?', 'Uníssono?'),
    ('SetSync:', 'Uníssono:'),
    ('SetSync,', 'Uníssono,'),
    ('SetSync</', 'Uníssono</'),
    ('SetSync"', 'Uníssono"'),
    ("SetSync'", "Uníssono'"),
    ('>SetSync<', '>Uníssono<'),
    ('SetSync ', 'Uníssono '),
    ('SetSync\n', 'Uníssono\n'),
    ('SetSync\t', 'Uníssono\t'),
    ('SetSync`', 'Uníssono`'),
    ('SetSync)', 'Uníssono)'),
    ('(SetSync', '(Uníssono'),
    ('SetSync*', 'Uníssono*'),
    ('SetSync/', 'Uníssono/'),
]


def should_skip_file(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in SKIP_FILES:
        return True
    for part in path.parts:
        if part in SKIP_DIRS or (part.startswith('.') and part not in ('.', '..')):
            return True
    if rel.startswith('static/js/'):
        return True
    if rel.startswith('cifras_tool/') and rel != 'cifras_tool/api_cifras_client.py':
        return True
    if rel.startswith('chordsheet/') and 'test' not in rel:
        return True
    return False


def transform_line(line: str) -> str:
    if SKIP_LINE_RE.search(line):
        return line
    out = line
    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    # catch-all final (linha sem identificadores técnicos)
    if 'SetSync' in out and not SKIP_LINE_RE.search(out):
        out = out.replace('SetSync', 'Uníssono')
    return out


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path.suffix not in EXTS:
            continue
        if should_skip_file(path):
            continue
        text = path.read_text(encoding='utf-8')
        lines = text.splitlines(keepends=True)
        new_lines = [transform_line(ln) for ln in lines]
        new_text = ''.join(new_lines)
        if new_text != text:
            path.write_text(new_text, encoding='utf-8')
            changed += 1
            print(path.relative_to(ROOT))
    print(f'\n{changed} arquivo(s) atualizado(s).')


if __name__ == '__main__':
    main()
