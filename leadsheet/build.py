"""Montagem e validação do payload LeadSheet (formulário do editor)."""

from __future__ import annotations

from datetime import datetime, timezone

LOCAL_SOURCE_URL = "file://local/audio"
DEFAULT_AUDIO_FILE_NAME = "audio.mp3"


def _to_float(value: str | None):
    value = (value or "").strip().replace(",", ".")
    return float(value) if value else None


def _to_int(value: str | None):
    value = (value or "").strip()
    return int(value) if value else None


def parse_sections(raw: str) -> list[dict]:
    sections = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            raise ValueError(f"Seção inválida: '{line}'. Use nome|inicio|fim")
        sections.append(
            {
                "name": parts[0],
                "start_seconds": float(parts[1].replace(",", ".")),
                "end_seconds": float(parts[2].replace(",", ".")),
            }
        )
    return sections


def parse_events(raw: str) -> list[dict]:
    events = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            raise ValueError(f"Evento inválido: '{line}'. Use tempo|tipo|valor")
        if parts[1] not in {"chord", "lyric", "marker"}:
            raise ValueError(f"Tipo de evento inválido: '{parts[1]}'")
        events.append(
            {
                "time_seconds": float(parts[0].replace(",", ".")),
                "type": parts[1],
                "value": parts[2],
            }
        )
    return events


def _audio_file_name(data: dict) -> str:
    name = (data.get("file_name") or "").strip()
    return name or DEFAULT_AUDIO_FILE_NAME


def _audio_duration(data: dict, events: list[dict]) -> float:
    duration = _to_float(data.get("duration"))
    if duration and duration > 0:
        return duration
    if events:
        return max(float(event["time_seconds"]) for event in events) + 1.0
    return 1.0


def _build_sections(data: dict, events: list[dict]) -> list[dict]:
    raw = (data.get("sections") or "").strip()
    if raw:
        return parse_sections(raw)
    end = _audio_duration(data, events)
    return [{"name": "Música", "start_seconds": 0.0, "end_seconds": end}]


def _build_events(data: dict) -> list[dict]:
    raw = (data.get("events") or "").strip()
    if not raw:
        raise ValueError(
            "Monte o lead sheet no editor (insira compassos e acordes) ou use Analisar MP3."
        )
    return parse_events(raw)


def build_payload(data: dict) -> dict:
    events = _build_events(data)
    duration = _audio_duration(data, events)
    payload = {
        "source": {"platform": "youtube", "url": LOCAL_SOURCE_URL},
        "audio": {
            "file_name": _audio_file_name(data),
            "duration_seconds": duration,
        },
        "song": {"title": (data.get("song_title") or "").strip()},
        "sections": _build_sections(data, events),
        "events": events,
        "metadata": {
            "generated_by": "setsync-leadsheet-editor",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    sample_rate = _to_int(data.get("sample_rate"))
    if sample_rate is not None:
        payload["audio"]["sample_rate"] = sample_rate

    artist = (data.get("artist") or "").strip()
    if artist:
        payload["song"]["artist"] = artist

    tempo_bpm = _to_float(data.get("tempo_bpm"))
    if tempo_bpm is not None:
        payload["song"]["tempo_bpm"] = tempo_bpm

    time_signature = (data.get("time_signature") or "").strip()
    if time_signature:
        payload["song"]["time_signature"] = time_signature

    song_key = (data.get("song_key") or "").strip()
    if song_key:
        payload["song"]["key"] = song_key

    if payload["song"].get("time_signature") == "4/4":
        bpm = payload["song"].get("tempo_bpm")
        if bpm and bpm > 0:
            beat_duration = 60.0 / bpm
            pulse_map_44 = []
            for event in payload["events"]:
                if event.get("type") != "chord":
                    continue
                t = float(event["time_seconds"])
                absolute_beat = int(round(t / beat_duration))
                beat = (absolute_beat % 4) + 1
                bar = (absolute_beat // 4) + 1
                pulse_map_44.append(
                    {
                        "time_seconds": round(t, 2),
                        "chord": event.get("value", ""),
                        "bar": bar,
                        "beat": beat,
                    }
                )
            payload["metadata"]["pulse_map_4_4"] = pulse_map_44

    if not payload["song"]["title"]:
        raise ValueError("Informe o título da música.")
    return payload
