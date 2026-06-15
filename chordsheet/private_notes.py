"""Notas privadas no chord sheet (visíveis só ao autor)."""

from __future__ import annotations

import re
from typing import Any

PRIVATE_LINE = re.compile(r"^!\s+(.+)$")


def split_private_notes(source: str) -> tuple[str, list[dict[str, Any]]]:
    """Remove linhas `! …` do texto compartilhado e devolve posição + texto."""
    shared: list[str] = []
    notes: list[dict[str, Any]] = []
    for raw_line in (source or "").splitlines():
        stripped = raw_line.strip()
        m = PRIVATE_LINE.match(stripped)
        if m:
            notes.append({"line": len(shared), "text": m.group(1).strip()})
        else:
            shared.append(raw_line)
    return "\n".join(shared), notes


def merge_private_notes(
    source: str,
    notes: list[dict[str, Any]] | None,
) -> str:
    """Reinsere notas privadas do usuário no texto-fonte do editor."""
    if not notes:
        return source or ""
    lines = (source or "").splitlines()
    for note in sorted(notes, key=lambda n: int(n.get("line", 0)), reverse=True):
        at = max(0, min(int(note.get("line", 0)), len(lines)))
        text = str(note.get("text", "")).strip()
        if text:
            lines.insert(at, f"! {text}")
    return "\n".join(lines)


def private_notes_for_user(
    payload: dict[str, Any] | None,
    user_id: str | None,
) -> list[dict[str, Any]]:
    if not payload or not user_id:
        return []
    raw = (payload.get("private_notes") or {}).get(str(user_id))
    return list(raw) if isinstance(raw, list) else []


def apply_private_notes_to_payload(
    data: dict[str, Any],
    user_id: str | None,
) -> dict[str, Any]:
    """Mescla notas privadas do usuário no `source` (editor / render)."""
    out = dict(data)
    notes = private_notes_for_user(out, user_id)
    out["source"] = merge_private_notes(out.get("source") or "", notes)
    return out


def extract_and_store_private_notes(
    data: dict[str, Any],
    user_id: str,
) -> dict[str, Any]:
    """Separa `! …` do source e atualiza `private_notes[user_id]`."""
    out = dict(data)
    shared, notes = split_private_notes(out.get("source") or "")
    out["source"] = shared
    pn = dict(out.get("private_notes") or {})
    pn[str(user_id)] = notes
    out["private_notes"] = pn
    return out
