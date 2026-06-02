from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from cifras_tool.compasso import CompassoInfo


@dataclass
class CompassoGrade:
    """Um compasso na grade; secao é rótulo da cifra (Intro, Refrão…), não acorde."""

    acordes: list[str]
    secao: str | None = None


@dataclass
class HarmonicPart:
    name: str
    compassos: list[CompassoGrade]

    @property
    def bars(self) -> list[list[str]]:
        return [c.acordes for c in self.compassos]


def build_cifra(chords_by_beat: Sequence[str], beats_per_bar: int = 4) -> str:
    if not chords_by_beat:
        return ""

    bars = _to_bars(chords_by_beat, beats_per_bar=beats_per_bar)
    return " | ".join(" ".join(bar) for bar in bars)


def build_grade(
    parts: Sequence[HarmonicPart],
    compasso: CompassoInfo | None = None,
) -> str:
    from cifras_tool.compasso import compasso_padrao, linha_marcadores_compasso

    info = compasso or compasso_padrao()
    sections: list[str] = [
        "Lead sheet",
        f"Compasso: {info.formula}",
        linha_marcadores_compasso(info.beats_per_bar),
    ]
    bpb = info.beats_per_bar
    for part in parts:
        sections.append("")
        sections.append(part.name)
        bloco_atual: list[str] = []

        for compasso in part.compassos:
            if compasso.secao:
                if bloco_atual:
                    sections.append(_linha_compassos(bloco_atual))
                    bloco_atual = []
                sections.append(f"  ▸ {compasso.secao}")
            bloco_atual.append(_formatar_compasso_numerado(compasso.acordes, bpb))

        if bloco_atual:
            sections.append(_linha_compassos(bloco_atual))

    return "\n".join(sections[1:] if sections and sections[0] == "" else sections)


def _linha_compassos(barras_formatadas: list[str]) -> str:
    return " | ".join(barras_formatadas)


def _formatar_compasso_numerado(bar: Sequence[str], beats_per_bar: int) -> str:
    """Um compasso: acordes alinhados aos pulsos (1..N)."""
    simbolos = _bar_with_repetition_symbols(bar)
    tokens = simbolos.split()
    while len(tokens) < beats_per_bar:
        tokens.append("%")
    tokens = tokens[:beats_per_bar]
    largura = max(4, max(len(t) for t in tokens))
    return " ".join(f"{tok:>{largura}}" for tok in tokens)


def detect_tonality(chords_by_beat: Sequence[str]) -> str:
    if not chords_by_beat:
        return "Desconhecida"
    key_root, mode = _estimate_key(chords_by_beat)
    if key_root == "N":
        return "Desconhecida"
    sufix = "maior" if mode == "major" else "menor"
    return f"{key_root} {sufix} (estimada)"


def normalize_chords_to_tonality(chords_by_beat: Sequence[str]) -> list[str]:
    if not chords_by_beat:
        return []
    normalized: list[str] = []
    for chord in chords_by_beat:
        if chord == "N":
            normalized.append(normalized[-1] if normalized else "C")
        else:
            normalized.append(chord)
    normalized = _median_smooth_labels(normalized, window=3)
    return _enforce_harmonic_context(normalized)


def refine_progression(chords_by_beat: Sequence[str]) -> list[str]:
    if not chords_by_beat:
        return []
    step1 = normalize_chords_to_tonality(chords_by_beat)
    step2 = _median_smooth_labels(step1, window=3)
    return _enforce_harmonic_context(step2)


def split_harmonic_parts(
    chords_by_beat: Sequence[str], beats_per_bar: int = 4, window_bars: int = 8
) -> list[HarmonicPart]:
    """
    Heuristica inicial:
    - converte em compassos
    - agrupa janelas de 4 compassos por assinatura textual da progressao
    - assinatura repetida reaproveita nome de parte (A, B, C...)
    """
    bars = _to_bars(chords_by_beat, beats_per_bar=beats_per_bar)
    compassos = [CompassoGrade(acordes=b) for b in bars]
    return split_harmonic_parts_compassos(compassos, window_bars=window_bars)


def split_harmonic_parts_bars(
    bars: list[list[str]], window_bars: int = 4
) -> list[HarmonicPart]:
    """Agrupa compassos já formados em partes A, B, C..."""
    compassos = [CompassoGrade(acordes=b) for b in bars]
    return split_harmonic_parts_compassos(compassos, window_bars=window_bars)


def split_harmonic_parts_compassos(
    compassos: list[CompassoGrade], window_bars: int = 4
) -> list[HarmonicPart]:
    """Agrupa compassos em partes A, B, C… (ignora rótulos de seção na assinatura)."""
    if not compassos:
        return []

    windows: list[list[CompassoGrade]] = []
    signatures: list[str] = []
    idx = 0
    while idx < len(compassos):
        chunk = compassos[idx : idx + window_bars]
        windows.append(chunk)
        signatures.append(_window_signature([c.acordes for c in chunk]))
        idx += window_bars

    clusters: list[dict] = []
    for i, sig in enumerate(signatures):
        assigned = False
        for cluster in clusters:
            if _signature_distance(sig, cluster["signature"]) <= 0.75:
                cluster["indexes"].append(i)
                assigned = True
                break
        if not assigned:
            clusters.append({"signature": sig, "indexes": [i]})

    part_names = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cluster_to_part: dict[int, str] = {}
    for idx_cluster in range(len(clusters)):
        if idx_cluster < len(part_names):
            cluster_to_part[idx_cluster] = f"Parte {part_names[idx_cluster]}"
        else:
            cluster_to_part[idx_cluster] = f"Parte {idx_cluster + 1}"

    parts: list[HarmonicPart] = []
    for i, chunk in enumerate(windows):
        best_cluster = 0
        best_distance = float("inf")
        for c_idx, cluster in enumerate(clusters):
            d = _signature_distance(signatures[i], cluster["signature"])
            if d < best_distance:
                best_distance = d
                best_cluster = c_idx
        part_name = cluster_to_part[best_cluster]

        if parts and parts[-1].name == part_name:
            parts[-1].compassos.extend(chunk)
        else:
            parts.append(HarmonicPart(name=part_name, compassos=list(chunk)))
    return parts


def _to_bars(chords_by_beat: Sequence[str], beats_per_bar: int = 4) -> list[list[str]]:
    bars: list[list[str]] = []
    current: list[str] = []
    for chord in chords_by_beat:
        current.append(chord)
        if len(current) == beats_per_bar:
            bars.append(current)
            current = []
    if current:
        current.extend([current[-1]] * (beats_per_bar - len(current)))
        bars.append(current)
    return bars


def _bar_with_repetition_symbols(bar: Sequence[str]) -> str:
    out: list[str] = []
    last = None
    for chord in bar:
        if last is not None and chord == last:
            out.append("%")
        else:
            out.append(chord)
            last = chord
    return " ".join(out)


def _window_signature(chunk: Sequence[Sequence[str]]) -> str:
    # Usa apenas o primeiro acorde forte por compasso para reduzir ruido.
    bar_roots: list[str] = []
    for bar in chunk:
        normalized = [c for c in bar if c != "N"]
        if not normalized:
            bar_roots.append("N")
            continue
        bar_roots.append(Counter(normalized).most_common(1)[0][0])
    return "|".join(bar_roots)


def _signature_distance(a: str, b: str) -> float:
    a_items = a.split("|")
    b_items = b.split("|")
    max_len = max(len(a_items), len(b_items))
    if max_len == 0:
        return 0.0
    mismatch = 0
    for idx in range(max_len):
        av = a_items[idx] if idx < len(a_items) else "N"
        bv = b_items[idx] if idx < len(b_items) else "N"
        if av != bv:
            mismatch += 1
    return mismatch / max_len


NOTE_TO_INDEX = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}
INDEX_TO_NOTE = {v: k for k, v in NOTE_TO_INDEX.items()}


def _estimate_key(chords_by_beat: Sequence[str]) -> tuple[str, str]:
    roots = [_parse_chord(ch)[0] for ch in chords_by_beat if ch and ch != "N"]
    if not roots:
        return "N", "major"
    root_counts = Counter(roots)

    best_root = "N"
    best_mode = "major"
    best_score = -1
    for root in NOTE_TO_INDEX:
        major_set = {_parse_chord(ch)[0] for ch in _diatonic_chords(root, "major")}
        minor_set = {_parse_chord(ch)[0] for ch in _diatonic_chords(root, "minor")}
        major_score = sum(c for r, c in root_counts.items() if r in major_set)
        minor_score = sum(c for r, c in root_counts.items() if r in minor_set)
        if major_score > best_score:
            best_score = major_score
            best_root = root
            best_mode = "major"
        if minor_score > best_score:
            best_score = minor_score
            best_root = root
            best_mode = "minor"
    return best_root, best_mode


def _diatonic_chords(key_root: str, mode: str) -> list[str]:
    root = NOTE_TO_INDEX[key_root]
    if mode == "major":
        degrees = [0, 2, 4, 5, 7, 9, 11]
        qualities = ["", "m", "m", "", "", "m", "dim"]
    else:
        degrees = [0, 2, 3, 5, 7, 8, 10]
        qualities = ["m", "dim", "", "m", "m", "", ""]

    chords: list[str] = []
    for degree, q in zip(degrees, qualities):
        chord_root = INDEX_TO_NOTE[(root + degree) % 12]
        chords.append(f"{chord_root}{q}" if q != "dim" else f"{chord_root}m")
    # dominante secundario mais comum no pop/gospel
    fifth = INDEX_TO_NOTE[(root + 7) % 12]
    chords.append(f"{fifth}7")
    return chords


def _parse_chord(chord: str) -> tuple[str, str]:
    match = re.match(r"^(C#|D#|F#|G#|A#|C|D|E|F|G|A|B)(.*)$", chord)
    if not match:
        return "N", ""
    return match.group(1), match.group(2)


def _nearest_diatonic(chord: str, allowed: set[str]) -> str:
    root, quality = _parse_chord(chord)
    if root == "N":
        return next(iter(allowed))
    idx = NOTE_TO_INDEX[root]
    best = None
    best_dist = 99
    for candidate in sorted(allowed):
        c_root, c_q = _parse_chord(candidate)
        c_idx = NOTE_TO_INDEX.get(c_root, idx)
        dist = min((idx - c_idx) % 12, (c_idx - idx) % 12)
        if c_q == quality:
            dist -= 0.25
        if dist < best_dist:
            best_dist = dist
            best = candidate
    return best or chord


def _median_smooth_labels(labels: list[str], window: int = 5) -> list[str]:
    if not labels:
        return labels
    radius = window // 2
    out: list[str] = []
    for i in range(len(labels)):
        left = max(0, i - radius)
        right = min(len(labels), i + radius + 1)
        chunk = labels[left:right]
        out.append(Counter(chunk).most_common(1)[0][0])
    return out


def _enforce_harmonic_context(chords: Sequence[str]) -> list[str]:
    key_root, mode = _estimate_key(chords)
    if key_root == "N":
        return list(chords)

    allowed = set(_diatonic_chords(key_root, mode))
    # cadencias comuns em pop/gospel
    cadence_pairs = _cadence_pairs(key_root, mode)

    out = list(chords)
    counts = Counter(out)
    total = max(len(out), 1)

    for i, chord in enumerate(out):
        if chord in allowed:
            continue
        root, _ = _parse_chord(chord)
        freq = counts[chord] / total
        # acorde raro ou fora da area tonal => aproxima para diatonico mais proximo
        if root == "N" or freq < 0.015:
            out[i] = _nearest_diatonic(chord, allowed)

    # reforca pares de cadencia quando ha transicao vizinha parecida
    for i in range(len(out) - 1):
        curr = out[i]
        nxt = out[i + 1]
        if (curr, nxt) in cadence_pairs:
            continue
        curr_root, _ = _parse_chord(curr)
        nxt_root, _ = _parse_chord(nxt)
        for c1, c2 in cadence_pairs:
            r1, _ = _parse_chord(c1)
            r2, _ = _parse_chord(c2)
            if curr_root == r1 and nxt_root == r2:
                out[i] = c1
                out[i + 1] = c2
                break

    return out


def _cadence_pairs(key_root: str, mode: str) -> set[tuple[str, str]]:
    root_idx = NOTE_TO_INDEX[key_root]
    if mode == "major":
        ii = f"{INDEX_TO_NOTE[(root_idx + 2) % 12]}m"
        v = f"{INDEX_TO_NOTE[(root_idx + 7) % 12]}7"
        i = INDEX_TO_NOTE[root_idx]
        iv = INDEX_TO_NOTE[(root_idx + 5) % 12]
        vi = f"{INDEX_TO_NOTE[(root_idx + 9) % 12]}m"
    else:
        ii = f"{INDEX_TO_NOTE[(root_idx + 2) % 12]}m7"
        v = f"{INDEX_TO_NOTE[(root_idx + 7) % 12]}7"
        i = f"{INDEX_TO_NOTE[root_idx]}m"
        iv = f"{INDEX_TO_NOTE[(root_idx + 5) % 12]}m"
        vi = INDEX_TO_NOTE[(root_idx + 8) % 12]

    return {
        (ii, v),
        (v, i),
        (iv, v),
        (vi, iv),
    }
