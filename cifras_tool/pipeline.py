from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from cifras_tool.chord_model import ChordRecognizer
from cifras_tool.compasso import CompassoInfo, alinhar_pulsos_ao_compasso, detectar_compasso
from cifras_tool.formatter import (
    build_cifra,
    build_grade,
    detect_tonality,
    refine_progression,
    split_harmonic_parts,
)


@dataclass
class AnalysisResult:
    cifra: str
    grade: str
    tonality: str
    chords_by_beat: list[str]
    compasso: CompassoInfo


class AudioPipeline:
    def __init__(self) -> None:
        self.chord_model = ChordRecognizer()

    def run(self, wav_path: Path) -> AnalysisResult:
        y, sr = librosa.load(str(wav_path), sr=22050, mono=True)
        y = librosa.util.normalize(y)

        sf.write(str(wav_path), y, sr)

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr).T
        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        if len(beat_frames) == 0:
            beat_frames = np.arange(0, len(y), sr // 2)
            beat_frames = np.clip(beat_frames, 0, chroma.shape[0] - 1)

        beat_frames = np.clip(beat_frames.astype(int), 0, chroma.shape[0] - 1)
        chroma_beats = chroma[beat_frames]

        frame_preds = self.chord_model.predict(chroma_beats)
        chords_by_beat = [p.chord for p in frame_preds]
        chords_by_beat = refine_progression(chords_by_beat)

        compasso = detectar_compasso(y, sr, beat_frames)
        chords_alinhados = alinhar_pulsos_ao_compasso(chords_by_beat, compasso)
        bpb = compasso.beats_per_bar

        parts = split_harmonic_parts(
            chords_alinhados, beats_per_bar=bpb, window_bars=8
        )
        return AnalysisResult(
            cifra=build_cifra(chords_alinhados, beats_per_bar=bpb),
            grade=build_grade(parts, compasso=compasso),
            tonality=detect_tonality(chords_by_beat),
            chords_by_beat=chords_by_beat,
            compasso=compasso,
        )
