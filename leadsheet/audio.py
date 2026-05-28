"""Análise de áudio para estimativa inicial de LeadSheet."""

from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def _chord_templates() -> tuple[list[str], np.ndarray]:
    major = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0], dtype=float)
    minor = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], dtype=float)
    labels: list[str] = []
    templates: list[np.ndarray] = []
    notes = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    for i, note in enumerate(notes):
        labels.append(note)
        labels.append(f"{note}m")
        templates.append(np.roll(major, i))
        templates.append(np.roll(minor, i))
    return labels, np.array(templates)


CHORD_LABELS, CHORD_TEMPLATES = _chord_templates()


def analyze_audio_for_leadsheet(audio_path: Path) -> dict:
    y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
    if y.size == 0:
        raise ValueError("Arquivo de áudio vazio.")

    tempo_raw, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    tempo = float(np.atleast_1d(tempo_raw)[0]) if np.size(tempo_raw) else 0.0

    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=512)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)
    duration_seconds = float(librosa.get_duration(y=y, sr=sr))

    if beat_frames.size == 0:
        raise ValueError("Não foi possível detectar batidas no áudio.")

    events = []
    pulse_map_44 = []
    max_events = 128

    for i, frame in enumerate(beat_frames[:max_events]):
        vec = chroma[:, frame].astype(float)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        scores = CHORD_TEMPLATES @ vec
        chord = CHORD_LABELS[int(np.argmax(scores))]
        timestamp = float(beat_times[i])
        beat_44 = (i % 4) + 1
        bar_44 = (i // 4) + 1
        events.append(
            {
                "time_seconds": round(timestamp, 2),
                "type": "chord",
                "value": chord,
                "beat_44": beat_44,
                "bar_44": bar_44,
            }
        )
        pulse_map_44.append(
            {
                "time_seconds": round(timestamp, 2),
                "chord": chord,
                "bar": bar_44,
                "beat": beat_44,
            }
        )

    return {
        "tempo_bpm": round(tempo, 2),
        "sample_rate": int(sr),
        "duration_seconds": round(duration_seconds, 2),
        "events": events,
        "pulse_map_44": pulse_map_44,
    }
