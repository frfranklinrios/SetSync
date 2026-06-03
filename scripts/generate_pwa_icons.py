#!/usr/bin/env python3
"""Gera ícones PWA com fundo alinhado ao manifest (sem caixa preta)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'static'
LOGO_PATH = STATIC / 'logoSetSync.png'
ICONS_DIR = STATIC / 'icons'

# Mesmo tom do manifest (splash Android/Chrome)
BG_RGBA = (15, 23, 42, 255)  # #0f172a


def _trim_logo(src: Image.Image) -> Image.Image:
    bbox = src.getbbox()
    if not bbox:
        return src
    return src.crop(bbox)


def _fit_logo(logo: Image.Image, max_side: int) -> Image.Image:
    w, h = logo.size
    scale = min(max_side / w, max_side / h, 1.0)
    if scale < 1.0:
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        return logo.resize((nw, nh), Image.Resampling.LANCZOS)
    return logo


def render_icon(size: int, *, maskable: bool = False) -> Image.Image:
    pad_ratio = 0.26 if maskable else 0.16
    pad = max(4, int(size * pad_ratio))
    max_side = size - 2 * pad

    canvas = Image.new('RGBA', (size, size), BG_RGBA)
    raw = Image.open(LOGO_PATH).convert('RGBA')
    logo = _fit_logo(_trim_logo(raw), max_side)
    x = (size - logo.width) // 2
    y = (size - logo.height) // 2
    canvas.paste(logo, (x, y), logo)
    return canvas


def main() -> None:
    if not LOGO_PATH.is_file():
        raise SystemExit(f'Logo não encontrado: {LOGO_PATH}')
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    targets = [
        ('favicon-32.png', 32, False),
        ('icon-192.png', 192, False),
        ('icon-512.png', 512, False),
        ('apple-touch-icon.png', 180, False),
        ('icon-192-maskable.png', 192, True),
        ('icon-512-maskable.png', 512, True),
    ]
    for name, size, maskable in targets:
        out = ICONS_DIR / name
        render_icon(size, maskable=maskable).save(out, format='PNG', optimize=True)
        print(f'wrote {out.relative_to(ROOT)} ({size}px, maskable={maskable})')


if __name__ == '__main__':
    main()
