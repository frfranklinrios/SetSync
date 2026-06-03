"""Armazenamento e exibição do logo da banda (impressão e UI)."""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

from db import DB_PATH

ALLOWED_EXTENSIONS = frozenset({'.png', '.jpg', '.jpeg', '.webp'})
ALLOWED_MIMES = frozenset({
    'image/png',
    'image/jpeg',
    'image/webp',
})
MAX_LOGO_BYTES = 2 * 1024 * 1024


def logo_dir() -> Path:
    base = Path(DB_PATH).resolve().parent
    d = base / 'band_logos'
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ext_from_filename(name: str) -> str | None:
    ext = Path(name or '').suffix.lower()
    return ext if ext in ALLOWED_EXTENSIONS else None


def _ext_from_mime(mime: str) -> str | None:
    mapping = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/webp': '.webp',
    }
    return mapping.get((mime or '').split(';')[0].strip().lower())


def _detect_image_ext(data: bytes) -> str | None:
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return '.png'
    if data[:3] == b'\xff\xd8\xff':
        return '.jpg'
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return '.webp'
    return None


def logo_path(band_id: str, filename: str) -> Path | None:
    if not band_id or not filename:
        return None
    if not filename.startswith(f'{band_id}.'):
        return None
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    path = logo_dir() / filename
    if not path.is_file() or path.resolve().parent != logo_dir().resolve():
        return None
    return path


def delete_band_logo_files(band_id: str) -> None:
    if not band_id:
        return
    for path in logo_dir().glob(f'{band_id}.*'):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def save_band_logo_upload(band_id: str, file_storage) -> tuple[str | None, str | None]:
    """
    Salva upload do logo. Retorna (filename, erro).
    filename = '{band_id}.png' etc.
    """
    if not file_storage or not getattr(file_storage, 'filename', None):
        return None, 'Selecione uma imagem.'
    raw_name = file_storage.filename or ''
    ext = _ext_from_filename(raw_name)
    data = file_storage.read()
    if not data:
        return None, 'Arquivo vazio.'
    if len(data) > MAX_LOGO_BYTES:
        return None, 'Imagem muito grande (máx. 2 MB).'
    detected = _detect_image_ext(data)
    if not detected:
        return None, 'Use PNG, JPG ou WebP.'
    mime = (getattr(file_storage, 'mimetype', None) or '').lower()
    if mime and mime not in ALLOWED_MIMES:
        mime_ext = _ext_from_mime(mime)
        if mime_ext and mime_ext != detected:
            return None, 'Formato de imagem inválido.'
    ext = detected
    delete_band_logo_files(band_id)
    filename = f'{band_id}{ext}'
    dest = logo_dir() / filename
    dest.write_bytes(data)
    return filename, None


def band_logo_data_uri(band: dict | None) -> str | None:
    """Data URI para impressão/PDF (sem depender de cookie na requisição)."""
    if not band:
        return None
    filename = (band.get('logo_filename') or '').strip()
    if not filename:
        return None
    path = logo_path(band['id'], filename)
    if not path:
        return None
    mime = mimetypes.guess_type(path.name)[0] or 'image/png'
    b64 = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{b64}'


def band_has_logo(band: dict | None) -> bool:
    if not band:
        return False
    filename = (band.get('logo_filename') or '').strip()
    if not filename:
        return False
    return logo_path(band['id'], filename) is not None
