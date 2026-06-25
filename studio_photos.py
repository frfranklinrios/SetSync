"""Upload e exibição de fotos — estúdios e salas."""

from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path

from band_logos import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIMES,
    MAX_LOGO_BYTES,
    _detect_image_ext,
    _ext_from_filename,
    _ext_from_mime,
)
from db import DB_PATH

MAX_STUDIO_PHOTOS = 8
MAX_ROOM_PHOTOS = 4


def _base_data_dir() -> Path:
    return Path(DB_PATH).resolve().parent


def studio_photos_dir(studio_id: str) -> Path:
    d = _base_data_dir() / 'studio_photos' / studio_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def room_photos_dir(room_id: str) -> Path:
    d = _base_data_dir() / 'studio_room_photos' / room_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _save_upload(file_storage, dest_dir: Path, prefix: str) -> tuple[str | None, str | None]:
    if not file_storage or not getattr(file_storage, 'filename', None):
        return None, 'Selecione uma imagem.'
    ext = _ext_from_filename(file_storage.filename or '')
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
    filename = f'{prefix}_{uuid.uuid4().hex[:12]}{ext}'
    dest = dest_dir / filename
    dest.write_bytes(data)
    return filename, None


def save_studio_photo_upload(studio_id: str, file_storage) -> tuple[str | None, str | None]:
    return _save_upload(file_storage, studio_photos_dir(studio_id), 'st')


def save_room_photo_upload(room_id: str, file_storage) -> tuple[str | None, str | None]:
    return _save_upload(file_storage, room_photos_dir(room_id), 'rm')


def studio_photo_path(studio_id: str, filename: str) -> Path | None:
    if not studio_id or not filename or '..' in filename or '/' in filename:
        return None
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    path = studio_photos_dir(studio_id) / filename
    if not path.is_file():
        return None
    return path


def room_photo_path(room_id: str, filename: str) -> Path | None:
    if not room_id or not filename or '..' in filename or '/' in filename:
        return None
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    path = room_photos_dir(room_id) / filename
    if not path.is_file():
        return None
    return path


def delete_studio_photo_file(studio_id: str, filename: str) -> None:
    path = studio_photo_path(studio_id, filename)
    if path:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def delete_room_photo_file(room_id: str, filename: str) -> None:
    path = room_photo_path(room_id, filename)
    if path:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def photo_mimetype(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or 'image/jpeg'
