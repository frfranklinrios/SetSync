"""Conversão entre LeadSheet (JSON) e grade harmônica legada (lista plana)."""

from __future__ import annotations

import json
from typing import Any

LOCAL_SOURCE_URL = "file://local/audio"


def is_leadsheet_document(data: Any) -> bool:
    return isinstance(data, dict) and "events" in data and "sections" in data


def _beats_per_bar(time_signature: str) -> int:
    sig = (time_signature or "4/4").strip()
    try:
        beats = int(sig.split("/")[0])
        return beats if beats > 0 else 4
    except (ValueError, IndexError):
        return 4


def grade_flat_to_leadsheet(
    grade_list: list[dict],
    *,
    title: str = "",
    artist: str = "",
    bpm: float | None = None,
    time_signature: str = "4/4",
    song_key: str = "",
    file_name: str = "audio.mp3",
    duration_seconds: float | None = None,
) -> dict:
    """Converte lista plana legada em documento LeadSheet."""
    beats = _beats_per_bar(time_signature)
    bpm_val = float(bpm) if bpm and bpm > 0 else 120.0
    beat_dur = 60.0 / bpm_val

    events: list[dict] = []
    max_time = 0.0
    bar_index = 0

    for item in grade_list or []:
        if not isinstance(item, dict):
            continue
        compasso = item.get("compasso")
        if compasso is not None:
            try:
                bar_index = max(0, int(compasso) - 1)
            except (TypeError, ValueError):
                pass

        t_start = bar_index * beats * beat_dur
        secao = (item.get("secao") or "").strip()
        if secao:
            events.append(
                {"time_seconds": round(t_start, 2), "type": "marker", "value": secao}
            )

        acordes = item.get("acordes") or ["%"]
        if not isinstance(acordes, list):
            acordes = ["%"]
        for beat_i, chord in enumerate(acordes):
            chord = str(chord or "").strip() or "%"
            if chord != "%":
                t = t_start + beat_i * beat_dur
                events.append(
                    {
                        "time_seconds": round(t, 2),
                        "type": "chord",
                        "value": chord,
                    }
                )
                max_time = max(max_time, t)

        bar_index += 1
        max_time = max(max_time, t_start + beats * beat_dur)

    duration = duration_seconds if duration_seconds and duration_seconds > 0 else max_time + beat_dur
    sections = [{"name": "Música", "start_seconds": 0.0, "end_seconds": round(duration, 2)}]

    payload: dict = {
        "source": {"platform": "youtube", "url": LOCAL_SOURCE_URL},
        "audio": {"file_name": file_name, "duration_seconds": round(duration, 2)},
        "song": {"title": title or "Sem título", "time_signature": time_signature},
        "sections": sections,
        "events": sorted(events, key=lambda e: e["time_seconds"]),
        "metadata": {"generated_by": "setsync-grade-migration"},
    }
    if artist:
        payload["song"]["artist"] = artist
    if bpm_val:
        payload["song"]["tempo_bpm"] = round(bpm_val, 2)
    if song_key:
        payload["song"]["key"] = song_key
    return payload


def leadsheet_to_grade_flat(leadsheet: dict) -> list[dict]:
    """Converte LeadSheet para lista plana usada pelo renderer legado."""
    song = leadsheet.get("song") or {}
    bpm = float(song.get("tempo_bpm") or 120)
    beats = _beats_per_bar(song.get("time_signature") or "4/4")
    beat_dur = 60.0 / bpm if bpm > 0 else 0.5

    events = sorted(leadsheet.get("events") or [], key=lambda e: float(e.get("time_seconds", 0)))
    bar_chords: dict[int, list[str]] = {}
    bar_secao: dict[int, str] = {}
    bar_lyric: dict[int, str] = {}
    max_bar = -1

    for evt in events:
        if not isinstance(evt, dict):
            continue
        t = float(evt.get("time_seconds", 0))
        abs_beat = int(round(t / beat_dur))
        bar = abs_beat // beats
        beat = abs_beat % beats
        max_bar = max(max_bar, bar)
        etype = evt.get("type")
        value = str(evt.get("value") or "").strip()
        if etype == "marker" and value:
            bar_secao[bar] = value
        elif etype == "lyric" and value:
            bar_lyric[bar] = value
        elif etype == "chord" and value:
            if bar not in bar_chords:
                bar_chords[bar] = ["%"] * beats
            if beat < len(bar_chords[bar]):
                bar_chords[bar][beat] = value

    out: list[dict] = []
    for bar in range(max_bar + 1):
        if bar not in bar_chords and bar not in bar_secao:
            continue
        acordes = bar_chords.get(bar, ["%"] * beats)
        item: dict = {"compasso": bar + 1, "acordes": acordes}
        secao = bar_secao.get(bar)
        if secao:
            item["secao"] = secao
            lyric = bar_lyric.get(bar)
            if lyric:
                item["secao"] = f"{secao} - {lyric}"
        out.append(item)
    return out


def resolve_leadsheet_document(cifra: dict) -> dict | None:
    """Obtém documento LeadSheet a partir da cifra (novo ou legado)."""
    raw_ls = cifra.get("leadsheet_json")
    if raw_ls:
        try:
            data = json.loads(raw_ls) if isinstance(raw_ls, str) else raw_ls
            if is_leadsheet_document(data):
                return data
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

    raw_grade = cifra.get("grade_json")
    if not raw_grade:
        return None
    try:
        parsed = json.loads(raw_grade) if isinstance(raw_grade, str) else raw_grade
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

    if is_leadsheet_document(parsed):
        return parsed
    if isinstance(parsed, list) and parsed:
        return grade_flat_to_leadsheet(
            parsed,
            title=cifra.get("titulo") or "",
            artist=cifra.get("artista") or "",
            bpm=cifra.get("bpm"),
            song_key=cifra.get("tom_original") or "",
        )
    return None


def resolve_to_grade_flat(cifra: dict) -> list[dict] | None:
    doc = resolve_leadsheet_document(cifra)
    if not doc:
        return None
    return leadsheet_to_grade_flat(doc)
