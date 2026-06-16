from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True)
class CompassoInfo:
    """Fórmula de compasso e alinhamento de pulsos para agrupar a grade."""

    beats_per_bar: int
    beat_unit: int
    formula: str
    downbeat_offset: int
    confidence: float

    @property
    def pulsos_por_compasso(self) -> int:
        return self.beats_per_bar


def compasso_padrao() -> CompassoInfo:
    return CompassoInfo(
        beats_per_bar=4,
        beat_unit=4,
        formula="4/4",
        downbeat_offset=0,
        confidence=0.0,
    )


def parsear_compasso(texto: str) -> CompassoInfo:
    """Aceita '4/4', '3/4', '2/4', '6/8'."""
    texto = texto.strip().replace(" ", "")
    match = re.match(r"^(\d+)\s*/\s*(\d+)$", texto)
    if not match:
        raise ValueError(
            f"Compasso inválido: {texto!r}. Use formato como 4/4, 3/4 ou 6/8."
        )
    numerador = int(match.group(1))
    denominador = int(match.group(2))
    if denominador not in (4, 8):
        raise ValueError("Denominador suportado: 4 ou 8 (ex.: 4/4, 6/8).")
    if numerador < 1 or numerador > 12:
        raise ValueError("Numerador deve estar entre 1 e 12.")

    beats_per_bar = numerador
    formula = _formula_de_pulsos(numerador, denominador) or f"{numerador}/{denominador}"

    # 6/8: grade harmônica costuma usar 2 tempos fortes por compasso
    if numerador == 6 and denominador == 8:
        beats_per_bar = 2
        formula = "6/8"

    return CompassoInfo(
        beats_per_bar=beats_per_bar,
        beat_unit=denominador,
        formula=formula,
        downbeat_offset=0,
        confidence=1.0,
    )


def _formula_de_pulsos(numerador: int, denominador: int) -> str:
    if numerador == 6 and denominador == 8:
        return "6/8"
    if denominador == 4:
        return f"{numerador}/4"
    return f"{numerador}/{denominador}"


def detectar_compasso(
    y: np.ndarray,
    sr: int,
    beat_frames: np.ndarray,
) -> CompassoInfo:
    """
    Estima compasso a partir da ênfase rítmica nos pulsos (downbeats mais fortes).
    Testa 2/4, 3/4, 4/4 e 6/8 (2 pulsos fortes por compasso).
    """
    import librosa
    import numpy as np

    if len(beat_frames) < 8:
        return compasso_padrao()

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    frames = np.clip(beat_frames.astype(int), 0, len(onset_env) - 1)
    strengths = onset_env[frames].astype(float)
    peak = float(np.max(strengths)) or 1.0
    strengths = strengths / peak

    candidatos: list[tuple[float, int, int, int, str]] = []

    for beats_per_bar, beat_unit, formula in (
        (2, 4, "2/4"),
        (3, 4, "3/4"),
        (4, 4, "4/4"),
        (2, 8, "6/8"),
    ):
        for offset in range(beats_per_bar):
            score = _pontuar_compasso(strengths, beats_per_bar, offset)
            if formula == "6/8" and not _sugere_composto(y, sr):
                score *= 0.85
            candidatos.append((score, beats_per_bar, beat_unit, offset, formula))

    melhor = max(candidatos, key=lambda item: item[0])
    score, beats_per_bar, beat_unit, offset, formula = melhor

    confianca = 0.0
    if candidatos:
        scores = sorted(c[0] for c in candidatos)
        if len(scores) > 1 and scores[-1] > 0:
            confianca = float(np.clip((scores[-1] - scores[-2]) / scores[-1], 0, 1))

    return CompassoInfo(
        beats_per_bar=beats_per_bar,
        beat_unit=beat_unit,
        formula=formula,
        downbeat_offset=offset,
        confidence=round(confianca, 3),
    )


def _pontuar_compasso(
    strengths: np.ndarray, beats_per_bar: int, offset: int
) -> float:
    import numpy as np

    downbeats: list[float] = []
    outros: list[float] = []
    for indice, valor in enumerate(strengths):
        if (indice - offset) % beats_per_bar == 0:
            downbeats.append(float(valor))
        else:
            outros.append(float(valor))
    if not downbeats or not outros:
        return 0.0
    return float(np.mean(downbeats) - np.mean(outros))


def _sugere_composto(y: np.ndarray, sr: int) -> bool:
    """Heurística leve para 6/8: subdivisão ternária mais clara que binária."""
    try:
        import librosa
        import numpy as np

        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        ac = librosa.autocorrelate(onset_env, max_size=3 * sr // 512)
        if len(ac) < 12:
            return False
        picos = []
        for lag in (3, 4, 6, 8):
            if lag < len(ac):
                picos.append((lag, float(ac[lag])))
        if len(picos) < 2:
            return False
        ternario = next((v for lag, v in picos if lag == 3), 0.0)
        binario = next((v for lag, v in picos if lag == 4), 0.0)
        return ternario > binario * 1.08
    except Exception:
        return False


def alinhar_pulsos_ao_compasso(
    pulsos: list[str], compasso: CompassoInfo
) -> list[str]:
    """Rotaciona a lista para o primeiro pulso coincidir com o downbeat."""
    if not pulsos or compasso.downbeat_offset == 0:
        return pulsos
    offset = compasso.downbeat_offset % max(compasso.beats_per_bar, 1)
    if offset == 0:
        return pulsos
    return pulsos[offset:] + pulsos[:offset]


def linha_marcadores_compasso(beats_per_bar: int) -> str:
    """Linha de referência numérica para escrever a grade 'em cima' do compasso."""
    celulas = [str(n + 1).center(4) for n in range(beats_per_bar)]
    return "Pulsos:   " + " | ".join(celulas)
