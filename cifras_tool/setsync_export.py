from __future__ import annotations

import re
from typing import Any

from cifras_tool.formatter import HarmonicPart

ACORDE_INLINE = re.compile(r"\[([^\]]+)\]([^\[]*)")


def cifra_inline_para_setsync(conteudo: str) -> list[dict[str, Any]]:
    """
    Formato SetSync (setsync_cifra.json):
    [{ "segundo", "texto_letra", "acorde", "group" }, ...]
    """
    from util import (
        _is_tab_header,
        _is_tab_line,
        _is_tab_meta_line,
        is_bracket_chord_name,
    )

    texto = (conteudo or "").replace("\r\n", "\n").replace("\r", "\n")
    linhas = texto.split("\n")
    resultado: list[dict[str, Any]] = []
    seq = 0
    group = 0
    i = 0

    while i < len(linhas):
        linha = linhas[i]
        if not linha.strip():
            group += 1
            i += 1
            continue

        stripped = linha.strip()
        if _is_tab_line(stripped) or _is_tab_header(stripped) or _is_tab_meta_line(stripped):
            while i < len(linhas):
                tab_linha = linhas[i]
                tab_stripped = tab_linha.strip()
                if not (
                    tab_stripped
                    and (
                        _is_tab_line(tab_stripped)
                        or _is_tab_header(tab_stripped)
                        or _is_tab_meta_line(tab_stripped)
                    )
                ):
                    break
                resultado.append(
                    {
                        "segundo": seq,
                        "texto_letra": tab_linha.rstrip(),
                        "acorde": "",
                        "group": group,
                    }
                )
                seq += 1
                i += 1
            group += 1
            continue

        if "[" in linha and "]" in linha:
            ultimo = 0
            encontrou = False
            for match in ACORDE_INLINE.finditer(linha):
                encontrou = True
                if match.start() > ultimo:
                    prefixo = linha[ultimo : match.start()]
                    if prefixo:
                        resultado.append(
                            {
                                "segundo": seq,
                                "texto_letra": prefixo,
                                "acorde": "",
                                "group": group,
                            }
                        )
                        seq += 1
                token = (match.group(1) or "").strip()
                texto_apos = match.group(2) or ""
                if is_bracket_chord_name(token):
                    resultado.append(
                        {
                            "segundo": seq,
                            "texto_letra": texto_apos,
                            "acorde": token,
                            "group": group,
                        }
                    )
                else:
                    label = token
                    extra = texto_apos.strip()
                    resultado.append(
                        {
                            "segundo": seq,
                            "texto_letra": f"[{label}]" + (extra if extra else ""),
                            "acorde": "",
                            "group": group,
                            "section": label,
                        }
                    )
                seq += 1
                ultimo = match.end()

            if encontrou and ultimo < len(linha):
                sufixo = linha[ultimo:]
                if sufixo:
                    resultado.append(
                        {
                            "segundo": seq,
                            "texto_letra": sufixo,
                            "acorde": "",
                            "group": group,
                        }
                    )
                    seq += 1

            if encontrou:
                group += 1
                i += 1
                continue

        resultado.append(
            {
                "segundo": seq,
                "texto_letra": linha,
                "acorde": "",
                "group": group,
            }
        )
        seq += 1
        group += 1
        i += 1

    return resultado


def partes_para_grade_ui(partes: list[HarmonicPart]) -> list[dict[str, Any]]:
    """Estrutura para renderizar a grade no frontend."""
    return [
        {
            "nome": parte.name,
            "compassos": [
                {
                    "secao": compasso.secao,
                    "acordes": list(compasso.acordes),
                }
                for compasso in parte.compassos
            ],
        }
        for parte in partes
    ]


def partes_para_setsync_grade(partes: list[HarmonicPart]) -> list[dict[str, Any]]:
    """
    Formato SetSync (setsync_grade.json):
    [{ "compasso", "acordes", "parte"? }, ...]
    """
    saida: list[dict[str, Any]] = []
    numero = 1

    for parte in partes:
        rotulo = ""
        if parte.name.lower().startswith("parte "):
            rotulo = parte.name[6:].strip().upper()
        elif parte.name:
            rotulo = parte.name.strip().upper()

        for compasso in parte.compassos:
            acordes = [str(a).strip() or "%" for a in compasso.acordes]
            if not acordes:
                continue
            item: dict[str, Any] = {"compasso": numero, "acordes": acordes}
            if rotulo and rotulo not in ("PROGRESSÃO (CIFRA)", "PROGRESSAO (CIFRA)"):
                item["parte"] = rotulo
            if compasso.secao:
                item["secao"] = compasso.secao
            saida.append(item)
            numero += 1

    return saida


def montar_pacote_setsync(
    *,
    titulo: str,
    artista: str,
    tom_original: str,
    conteudo: str,
    partes_grade: list[HarmonicPart],
    bpm: float | None = None,
    duracao_seg: int | None = None,
    url_cifra: str = "",
    url_youtube: str = "",
) -> dict[str, Any]:
    """Pacote completo para upload no formulário do SetSync."""
    cifra_json = cifra_inline_para_setsync(conteudo)
    grade_json = partes_para_setsync_grade(partes_grade)

    return {
        "titulo": titulo,
        "artista": artista,
        "tom_original": tom_original,
        "conteudo": conteudo,
        "cifra_json": cifra_json,
        "grade_json": grade_json,
        "bpm": bpm,
        "duracao_seg": duracao_seg,
        "url_cifra": url_cifra,
        "url_youtube": url_youtube,
    }
