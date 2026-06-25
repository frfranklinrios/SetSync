"""Hub em memória para eventos SSE por banda (single-process)."""

from __future__ import annotations

import json
import queue
import threading
from typing import Any

_lock = threading.Lock()
_subscribers: dict[str, list[queue.Queue[str]]] = {}


def subscribe(band_id: str) -> queue.Queue[str]:
    q: queue.Queue[str] = queue.Queue(maxsize=64)
    with _lock:
        _subscribers.setdefault(str(band_id), []).append(q)
    return q


def unsubscribe(band_id: str, q: queue.Queue[str]) -> None:
    with _lock:
        subs = _subscribers.get(str(band_id), [])
        if q in subs:
            subs.remove(q)
        if not subs:
            _subscribers.pop(str(band_id), None)


def publish(band_id: str, event: str, data: dict[str, Any] | None = None) -> None:
    payload = json.dumps({'event': event, 'data': data or {}}, ensure_ascii=False)
    with _lock:
        subs = list(_subscribers.get(str(band_id), []))
    for q in subs:
        try:
            q.put_nowait(payload)
        except queue.Full:
            pass
