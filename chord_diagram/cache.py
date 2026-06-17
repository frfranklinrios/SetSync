"""Cache de voicings — memória local com Redis opcional."""

from __future__ import annotations

import json
import os
import time
from typing import Any

_MEMORY: dict[str, tuple[float, Any]] = {}
_DEFAULT_TTL = int(os.getenv('MUSIC_API_CACHE_TTL', '3600'))
_REDIS = None
_REDIS_TRIED = False


def _redis_client():
    global _REDIS, _REDIS_TRIED
    if _REDIS_TRIED:
        return _REDIS
    _REDIS_TRIED = True
    url = (os.getenv('REDIS_URL') or os.getenv('MUSIC_API_REDIS_URL') or '').strip()
    if not url:
        return None
    try:
        import redis
        _REDIS = redis.from_url(url, decode_responses=True)
        _REDIS.ping()
    except Exception:
        _REDIS = None
    return _REDIS


def get_cached(key: str) -> Any | None:
    r = _redis_client()
    if r:
        try:
            raw = r.get(f'music_api:{key}')
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    item = _MEMORY.get(key)
    if not item:
        return None
    expires, value = item
    if time.time() > expires:
        _MEMORY.pop(key, None)
        return None
    return value


def set_cached(key: str, value: Any, ttl: int | None = None) -> None:
    ttl = ttl if ttl is not None else _DEFAULT_TTL
    r = _redis_client()
    if r:
        try:
            r.setex(f'music_api:{key}', ttl, json.dumps(value, ensure_ascii=False))
            return
        except Exception:
            pass
    _MEMORY[key] = (time.time() + ttl, value)


def cache_stats() -> dict:
    return {
        'memory_entries': len(_MEMORY),
        'redis': _redis_client() is not None,
    }
