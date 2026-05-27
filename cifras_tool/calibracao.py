from __future__ import annotations

import re

from cifras_tool.compasso import CompassoInfo, compasso_padrao
from cifras_tool.formatter import (
    CompassoGrade,
    HarmonicPart,
    build_grade,
    detect_tonality,
    split_harmonic_parts_compassos,
)

ACORDE_ENTRE_COLCHETES = re.compile(r"\[([^\]]+)\]")

# Acorde real (exclui Intro, Primeira Parte, etc.)
PADRAO_ACORDE_VALIDO = re.compile(
    r"^[A-G][#b]?"
    r"(?:maj7?|min|m7b5|m7|M7?|m|dim7?|dim|aug|sus[24]?|add\d*|º|°|\+|\d+)*"
    r"(?:/[A-G][#b]?)?$",
    re.IGNORECASE,
)

ROTULOS_SECAO = re.compile(
    r"^(intro|final|refr[aã]o|verso|ponte|solo|interl[uú]dio|primeira\s+parte|"
    r"segunda\s+parte|terceira\s+parte|ponte|passagem|outro|tab)",
    re.IGNORECASE,
)

ENARMONICOS = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "Cb": "B",
    "Fb": "E",
}


def eh_acorde_valido(token: str) -> bool:
    token = (token or "").strip()
    if not token or " " in token or len(token) > 14:
        return False
    if ROTULOS_SECAO.match(token):
        return False
    if not re.match(r"^[A-G]", token, re.IGNORECASE):
        return False
    return bool(PADRAO_ACORDE_VALIDO.match(token))


def extrair_acordes_referencia(cifra: str) -> list[str]:
    acordes: list[str] = []
    for bruto in ACORDE_ENTRE_COLCHETES.findall(cifra):
        if eh_acorde_valido(bruto):
            acordes.append(limpar_acorde_referencia(bruto))
    return acordes


def limpar_acorde_referencia(acorde: str) -> str:
    acorde = acorde.strip()
    if "/" in acorde:
        acorde = acorde.split("/")[0]
    acorde = acorde.replace("º", "dim").replace("°", "dim")
    raiz = re.match(r"^(C#|D#|F#|G#|A#|Db|Eb|Gb|Ab|Bb|C|D|E|F|G|A|B)", acorde)
    if raiz:
        nota = ENARMONICOS.get(raiz.group(1), raiz.group(1))
        sufixo = acorde[len(raiz.group(1)) :]
        return f"{nota}{sufixo}"
    return acorde


def _compasso_por_acorde(acorde: str, beats_per_bar: int) -> list[str]:
    """Um acorde por compasso; demais tempos do compasso ficam como %."""
    return [acorde] + ["%"] * (beats_per_bar - 1)


def compassos_com_secoes_da_cifra(
    cifra: str, compasso: CompassoInfo
) -> list[CompassoGrade]:
    """
    Um compasso por acorde; rótulos de seção (Intro, Primeira Parte…) ficam
    separados, não dentro dos compassos.
    """
    bpb = compasso.beats_per_bar
    saida: list[CompassoGrade] = []
    secao_pendente: str | None = None

    for bruto in ACORDE_ENTRE_COLCHETES.findall(cifra):
        token = bruto.strip()
        if not token:
            continue
        if eh_acorde_valido(token):
            acorde = limpar_acorde_referencia(token)
            barra = _compasso_por_acorde(acorde, bpb)
            if (
                saida
                and not secao_pendente
                and tuple(saida[-1].acordes) == tuple(barra)
            ):
                continue
            saida.append(CompassoGrade(acordes=barra, secao=secao_pendente))
            secao_pendente = None
        else:
            secao_pendente = token

    return saida


def grade_compacta_da_cifra(
    referencia: list[str], compasso: CompassoInfo | None = None
) -> str:
    """Progressão da cifra: um compasso por acorde."""
    if not referencia:
        return ""
    info = compasso or compasso_padrao()
    compassos = [
        CompassoGrade(acordes=_compasso_por_acorde(a, info.beats_per_bar))
        for a in referencia
    ]
    parte = HarmonicPart(name="Progressão (cifra)", compassos=compassos)
    return build_grade([parte], compasso=info)


def montar_grade_da_cifra(
    cifra: str,
    referencia: list[str],
    total_beats: int,
    compasso: CompassoInfo | None = None,
) -> tuple[str, str, list[str], list[HarmonicPart]]:
    """
    Grade a partir da cifra: um compasso por acorde, com % nos tempos repetidos.
    total_beats é usado só em estatísticas (resumo); não estica a progressão.
    """
    if not referencia:
        return "", "Desconhecida", [], []

    info = compasso or compasso_padrao()
    compassos = compassos_com_secoes_da_cifra(cifra, info)
    partes = split_harmonic_parts_compassos(compassos, window_bars=4)
    grade = build_grade(partes, compasso=info)
    tonalidade = tonalidade_da_referencia(referencia)
    acordes = [c.acordes[0] for c in compassos]
    return grade, tonalidade, acordes, partes


def tonalidade_da_referencia(referencia: list[str]) -> str:
    if not referencia:
        return "Desconhecida"
    tom = detect_tonality(referencia)
    return tom.replace(" (estimada)", " (cifra)")


def resolver_tonalidade(tom_site: str, referencia: list[str]) -> tuple[str, str]:
    """
    Prioriza o tom do site; senão estima pelos acordes da cifra.
    Retorna (tom para exibição, tom estimado ou vazio).
    """
    tom_site = (tom_site or "").strip()
    estimada = tonalidade_da_referencia(referencia) if referencia else "Desconhecida"
    if tom_site:
        return tom_site, estimada
    return estimada, estimada


def resumo_processamento(
    acordes_referencia: list[str],
    acordes_no_tempo: list[str],
    beats_audio: int,
    compasso: CompassoInfo | None = None,
) -> dict:
    info = compasso or compasso_padrao()
    bpb = max(info.beats_per_bar, 1)
    return {
        "acordes_cifra": acordes_referencia,
        "acordes_unicos": list(dict.fromkeys(acordes_referencia)),
        "total_acordes_cifra": len(acordes_referencia),
        "beats_audio": beats_audio,
        "compasso": info.formula,
        "beats_por_compasso": info.beats_per_bar,
        "unidade_compasso": info.beat_unit,
        "downbeat_offset": info.downbeat_offset,
        "confianca_compasso": info.confidence,
        "compassos_audio": beats_audio // bpb,
        "beats_grade": len(acordes_no_tempo),
        "compassos_grade": len(acordes_no_tempo),
    }
