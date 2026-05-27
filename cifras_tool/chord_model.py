from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass
class ChordFrame:
    start_beat: int
    chord: str


class ChordRecognizer:
    def __init__(self) -> None:
        self.device = "cpu"
        self.note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.templates = self._build_templates()

    def predict(self, chroma_beats: np.ndarray) -> Sequence[ChordFrame]:
        if chroma_beats.size == 0:
            return []

        # Normaliza e suaviza para reduzir ruido de frame unico.
        smoothed = self._median_smooth_chroma(chroma_beats, kernel_size=5)

        raw_labels: list[str] = []
        emission_scores: list[dict[str, float]] = []
        for beat_vec in smoothed:
            label, scores = self._predict_single(beat_vec)
            raw_labels.append(label)
            emission_scores.append(scores)

        labels = self._viterbi_decode(emission_scores, stay_bonus=0.03)
        labels = self._smooth_labels(labels, window=5)
        frames: list[ChordFrame] = []
        for beat_idx, chord in enumerate(labels):
            frames.append(ChordFrame(start_beat=beat_idx, chord=chord))
        return frames

    def _build_templates(self) -> list[tuple[str, np.ndarray]]:
        templates: list[tuple[str, np.ndarray]] = []
        for root in range(12):
            root_name = self.note_names[root]
            templates.extend(
                [
                    (root_name, self._chord_template(root, [0, 4, 7])),        # major
                    (f"{root_name}m", self._chord_template(root, [0, 3, 7])),  # minor
                    (f"{root_name}7", self._chord_template(root, [0, 4, 7, 10])),  # dom7
                    (f"{root_name}m7", self._chord_template(root, [0, 3, 7, 10])),  # min7
                ]
            )
        return templates

    @staticmethod
    def _chord_template(root: int, intervals: list[int]) -> np.ndarray:
        tmpl = np.zeros(12, dtype=np.float32)
        for interval in intervals:
            tmpl[(root + interval) % 12] = 1.0
        return tmpl / np.linalg.norm(tmpl)

    @staticmethod
    def _median_smooth_chroma(chroma_beats: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        pad = kernel_size // 2
        padded = np.pad(chroma_beats, ((pad, pad), (0, 0)), mode="edge")
        out = np.zeros_like(chroma_beats)
        for idx in range(chroma_beats.shape[0]):
            out[idx] = np.median(padded[idx : idx + kernel_size], axis=0)
        norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-8
        return out / norms

    def _predict_single(self, beat_vec: np.ndarray) -> tuple[str, dict[str, float]]:
        vec = beat_vec.astype(np.float32)
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        best_label = "N"
        best_score = -1.0
        scores: dict[str, float] = {}
        for label, template in self.templates:
            score = float(np.dot(vec, template))
            scores[label] = score
            if score > best_score:
                best_score = score
                best_label = label
        return best_label, scores

    @staticmethod
    def _smooth_labels(labels: list[str], window: int = 5) -> list[str]:
        if not labels:
            return labels
        radius = window // 2
        out: list[str] = []
        for idx in range(len(labels)):
            left = max(0, idx - radius)
            right = min(len(labels), idx + radius + 1)
            chunk = labels[left:right]
            # desempata preservando acorde atual
            values, counts = np.unique(chunk, return_counts=True)
            best = values[int(np.argmax(counts))]
            if labels[idx] in values and counts[list(values).index(labels[idx])] == counts.max():
                best = labels[idx]
            out.append(str(best))
        return out

    @staticmethod
    def _viterbi_decode(
        emission_scores: list[dict[str, float]], stay_bonus: float = 0.08
    ) -> list[str]:
        if not emission_scores:
            return []
        states = list(emission_scores[0].keys())
        n_states = len(states)
        n_steps = len(emission_scores)

        score = np.full((n_steps, n_states), -1e9, dtype=np.float32)
        back = np.zeros((n_steps, n_states), dtype=np.int32)

        for s_idx, state in enumerate(states):
            score[0, s_idx] = emission_scores[0][state]

        for t in range(1, n_steps):
            for s_idx, state in enumerate(states):
                emit = emission_scores[t][state]
                best_prev = 0
                best_val = -1e9
                for p_idx, prev_state in enumerate(states):
                    transition = stay_bonus if prev_state == state else 0.0
                    val = score[t - 1, p_idx] + transition + emit
                    if val > best_val:
                        best_val = val
                        best_prev = p_idx
                score[t, s_idx] = best_val
                back[t, s_idx] = best_prev

        path = [int(np.argmax(score[-1]))]
        for t in range(n_steps - 1, 0, -1):
            path.append(int(back[t, path[-1]]))
        path.reverse()
        return [states[idx] for idx in path]
