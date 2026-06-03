from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

NOTA_TOM = re.compile(
    r"^(C#|D#|F#|G#|A#|Db|Eb|Gb|Ab|Bb|C|D|E|F|G|A|B)$",
    re.IGNORECASE,
)


def normalizar_nota_tom(nota: str) -> str:
    nota = nota.strip()
    if not nota:
        return ""
    mapa = {
        "db": "Db",
        "eb": "Eb",
        "gb": "Gb",
        "ab": "Ab",
        "bb": "Bb",
        "cb": "Cb",
        "fb": "Fb",
    }
    if len(nota) == 2 and nota[1] in "#b":
        base = nota[0].upper() + nota[1].lower()
        return mapa.get(base.lower(), base)
    return nota[0].upper() + (nota[1:] if len(nota) > 1 else "")


def extrair_tom_do_html(soup: BeautifulSoup) -> str:
    """Tom exibido no site (ex.: Cifra Club #cifra_tom)."""
    seletores = [
        "#cifra_tom a",
        "#cifra_tom",
        ".js-key",
        "[data-key]",
    ]
    for seletor in seletores:
        elemento = soup.select_one(seletor)
        if not elemento:
            continue
        texto = elemento.get("data-key") or elemento.get_text(" ", strip=True)
        texto = re.sub(r"(?i)^tom\s*:\s*", "", texto).strip()
        match = NOTA_TOM.match(texto)
        if match:
            return normalizar_nota_tom(match.group(0))
        # "tom: G" em um único nó
        match = re.search(
            r"(?i)tom\s*:\s*(C#|D#|F#|G#|A#|Db|Eb|Gb|Ab|Bb|C|D|E|F|G|A|B)",
            texto,
        )
        if match:
            return normalizar_nota_tom(match.group(1))
    return ""


_TAG_SPAN_CHORD = re.compile(
    r'<span\s+data-chord="([^"]+)"[^>]*>[\s\S]*?</span>',
    re.IGNORECASE,
)
_TAG_B = re.compile(r"<b>([^<]*)</b>", re.IGNORECASE)
_TAG_I = re.compile(r"<i>([\s\S]*?)</i>", re.IGNORECASE)
_TAG_QUALQUER = re.compile(r"<[^>]+>", re.IGNORECASE)
_MARCADOR_SECAO = re.compile(r"\[[^\]]+\]")


VIDEO_ID_YOUTUBE = re.compile(r"^[A-Za-z0-9_-]{11}$")
PADRAO_URL_YOUTUBE = re.compile(
    r"(?:v=|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})"
)


def normalizar_url_youtube(url: str) -> str:
    """Aceita watch, youtu.be, embed ou só o ID de 11 caracteres."""
    url = url.strip()
    if not url:
        raise ValueError("URL do YouTube vazia.")

    if VIDEO_ID_YOUTUBE.match(url):
        return f"https://www.youtube.com/watch?v={url}"

    if not url.startswith(("http://", "https://")):
        url = f"https://{url.lstrip('/')}"

    match = PADRAO_URL_YOUTUBE.search(url)
    if not match:
        raise ValueError(
            "URL do YouTube inválida. Use watch?v=..., youtu.be/... ou o ID do vídeo."
        )
    return f"https://www.youtube.com/watch?v={match.group(1)}"


def normalizar_url(url: str) -> str:
    url = url.strip()
    url = re.sub(r"^https?://www\.https?://", "https://", url, flags=re.IGNORECASE)
    if not url.startswith(("http://", "https://")):
        url = f"https://{url.lstrip('/')}"
    parsed = urlparse(url)
    if not parsed.netloc or "." not in parsed.netloc:
        raise ValueError(f"URL inválida: {url}")
    return url


def detectar_fonte(url: str) -> str:
    parsed = urlparse(normalizar_url(url))
    host = parsed.netloc.lower().replace("www.", "")
    if "cifraclub.com.br" in host:
        return "cifraclub"
    if "cifras.com.br" in host:
        return "cifras.com.br"
    raise ValueError(
        "Fonte não suportada. Use URL do cifras.com.br ou cifraclub.com.br"
    )


def html_para_layout(linha_html: str) -> str:
    """Remove tags HTML preservando espaços; acordes ficam no lugar (colunas)."""
    s = (linha_html or "").replace("&nbsp;", " ").replace("&#160;", " ")
    partes: list[str] = []
    pos = 0
    while pos < len(s):
        m = _TAG_SPAN_CHORD.match(s, pos)
        if m:
            partes.append(m.group(1).strip())
            pos = m.end()
            continue
        m = _TAG_B.match(s, pos)
        if m:
            partes.append(m.group(1).strip())
            pos = m.end()
            continue
        m = _TAG_I.match(s, pos)
        if m:
            partes.append(m.group(1))
            pos = m.end()
            continue
        m = _TAG_QUALQUER.match(s, pos)
        if m:
            pos = m.end()
            continue
        partes.append(s[pos])
        pos += 1
    return "".join(partes)


def extrair_acordes_layout(layout: str) -> list[tuple[int, str]]:
    """Acordes com índice de coluna no layout visual da linha."""
    from util import _is_chord_token, clean_chord_symbol

    tokens = [(m.start(), m.group(0)) for m in re.finditer(r"\S+", layout or "")]
    tem_letra = any(
        not _is_chord_token(clean_chord_symbol(t)) and not _MARCADOR_SECAO.match(t)
        for _, t in tokens
    )

    posicoes: list[tuple[int, str]] = []
    for pos, bruto in tokens:
        if bruto.startswith("[") and bruto.endswith("]"):
            continue
        token = clean_chord_symbol(bruto)
        if not _is_chord_token(token):
            continue
        if re.match(r"^[A-G][#b]?$", token) and tem_letra:
            continue
        posicoes.append((pos, token))
    return posicoes


def _snap_inicio_palavra(letra: str, pos: int) -> int:
    pos = min(max(0, pos), len(letra))
    if pos >= len(letra) or letra[pos].isspace():
        return pos
    while pos > 0 and not letra[pos - 1].isspace():
        pos -= 1
    return pos


def analisar_linha_html(linha_html: str) -> dict:
    layout = html_para_layout(linha_html)
    acordes = extrair_acordes_layout(layout)
    resto = layout
    for pos, acorde in sorted(acordes, key=lambda x: x[0], reverse=True):
        resto = resto[:pos] + (" " * len(acorde)) + resto[pos + len(acorde) :]
    lyric = re.sub(r"\s+", " ", resto).strip()
    return {
        "layout": layout,
        "acordes": acordes,
        "lyric_text": lyric,
        "tem_acordes": bool(acordes),
        "somente_acordes": bool(acordes) and not lyric,
        "somente_letra": not acordes and bool(lyric),
    }


def mesclar_acordes_inline(
    acordes: list[tuple[int, str]],
    letra: str,
    largura_layout: int | None = None,
    deslocamento: int = 0,
) -> str:
    """Insere [acordes] na letra; escala colunas se a linha de acordes for bem mais larga."""
    letra = (letra or "").rstrip()
    tamanho = len(letra)
    ref = largura_layout if largura_layout and largura_layout > 0 else tamanho

    if ref < tamanho * 0.6 and acordes:
        prefixo = " ".join(f"[{a}]" for _, a in sorted(acordes, key=lambda x: x[0])) + " "
        return prefixo + letra

    resultado = letra
    escala = ref > tamanho * 1.12 and tamanho > 0

    for posicao, acorde in sorted(acordes, key=lambda item: item[0], reverse=True):
        p = round(posicao * tamanho / ref) if escala else posicao
        if deslocamento:
            p = p - deslocamento
        p = _snap_inicio_palavra(letra, min(max(0, p), tamanho))
        resultado = resultado[:p] + f"[{acorde}]" + resultado[p:]

    return resultado


def formatar_linha_acordes_brackets(layout: str, acordes: list[tuple[int, str]]) -> str:
    linha = layout
    for posicao, acorde in sorted(acordes, key=lambda item: item[0], reverse=True):
        linha = linha[:posicao] + f"[{acorde}]" + linha[posicao + len(acorde) :]
    return re.sub(r" +", " ", linha).strip()


def parse_linha_html(linha_html: str) -> tuple[list[tuple[int, str]], str, bool]:
    """Compat: retorna acordes (coluna, nome), texto e flag."""
    info = analisar_linha_html(linha_html)
    return info["acordes"], info["lyric_text"] or info["layout"].rstrip(), info["tem_acordes"]


def _texto_bloco_tablatura(conteudo_html: str) -> str:
    """Extrai texto legível de um bloco <span class="tablatura">…</span>."""
    texto = re.sub(r'<span\s+class=["\']cnt["\'][^>]*>', '', conteudo_html, flags=re.I)
    texto = re.sub(r'</span>', '', texto, flags=re.I)
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = texto.replace('&nbsp;', ' ').replace('&#160;', ' ')
    linhas = [ln.rstrip() for ln in texto.splitlines()]
    return '\n'.join(ln for ln in linhas if ln.strip())


def extrair_tablaturas_do_html(html: str) -> str:
    """Substitui blocos de tablatura HTML por texto plano antes do parse de acordes."""
    padrao = re.compile(
        r'<span\s+class=["\']tablatura["\'][^>]*>(.*?)</span>',
        re.DOTALL | re.IGNORECASE,
    )

    def _substituir(match: re.Match) -> str:
        bloco = _texto_bloco_tablatura(match.group(1))
        return f'\n{bloco}\n' if bloco else ''

    return padrao.sub(_substituir, html)


def looks_like_cifraclub_colagem(texto: str) -> bool:
    """Detecta colagem em texto plano (linhas de acordes alinhadas com espaços)."""
    from chordpro import is_chordpro_document

    if not (texto or "").strip():
        return False
    if is_chordpro_document(texto):
        return False
    linhas_somente_acorde = 0
    for ln in texto.splitlines():
        if not ln.strip():
            continue
        if analisar_linha_html(ln)["somente_acordes"]:
            linhas_somente_acorde += 1
    return linhas_somente_acorde >= 2


def normalizar_colagem_cifraclub(texto: str) -> str:
    """Converte colagem Cifra Club (HTML ou texto) para acordes inline [X]letra."""
    if not looks_like_cifraclub_colagem(texto):
        return texto
    return converter_html_para_inline(texto)


def converter_html_para_inline(html: str) -> str:
    """Converte HTML colado do Cifra Club (ou similar) para texto inline SetSync."""
    html_bruto = extrair_tablaturas_do_html(html or "")
    html_bruto = re.sub(r"<br\s*/?>", "\n", html_bruto, flags=re.IGNORECASE)
    linhas_html = re.split(r"\r\n?|\n", html_bruto)
    saida: list[str] = []
    indice = 0
    total = len(linhas_html)

    while indice < total:
        if not linhas_html[indice].strip():
            indice += 1
            continue

        atual = analisar_linha_html(linhas_html[indice])

        # Letra → linha só de acordes → letra (padrão comum no Cifra Club)
        if (
            atual["somente_letra"]
            and indice + 2 < total
        ):
            meio = analisar_linha_html(linhas_html[indice + 1])
            prox = analisar_linha_html(linhas_html[indice + 2])
            if meio["somente_acordes"] and prox["somente_letra"]:
                saida.append(atual["lyric_text"])
                letra2 = prox["lyric_text"] or html_para_layout(linhas_html[indice + 2]).strip()
                desloc = max(0, len(atual["lyric_text"]) - len(letra2))
                saida.append(
                    mesclar_acordes_inline(
                        meio["acordes"],
                        letra2,
                        len(meio["layout"]),
                        desloc,
                    )
                )
                indice += 3
                continue

        if atual["somente_acordes"]:
            if indice + 1 < total:
                prox = analisar_linha_html(linhas_html[indice + 1])
                if prox["somente_letra"]:
                    letra = prox["lyric_text"] or html_para_layout(linhas_html[indice + 1]).strip()
                    saida.append(
                        mesclar_acordes_inline(
                            atual["acordes"],
                            letra,
                            len(atual["layout"]),
                        )
                    )
                    indice += 2
                    continue
            saida.append(formatar_linha_acordes_brackets(atual["layout"], atual["acordes"]))
            indice += 1
            continue

        if atual["somente_letra"]:
            saida.append(atual["lyric_text"])
            indice += 1
            continue

        if atual["tem_acordes"]:
            letra = atual["lyric_text"]
            if letra and _MARCADOR_SECAO.fullmatch(letra.strip()):
                saida.append(
                    formatar_linha_acordes_brackets(atual["layout"], atual["acordes"])
                )
            elif letra:
                saida.append(
                    mesclar_acordes_inline(
                        atual["acordes"], letra, len(atual["layout"])
                    )
                )
            else:
                saida.append(formatar_linha_acordes_brackets(atual["layout"], atual["acordes"]))
            indice += 1
            continue

        texto = html_para_layout(linhas_html[indice]).strip()
        if texto:
            saida.append(texto)
        indice += 1

    return "\n".join(saida)


def converter_pre_para_inline(pre_element) -> str:
    return converter_html_para_inline(pre_element.decode_contents())


def primeiro_texto(soup: BeautifulSoup, seletores: list[str]) -> str:
    for seletor in seletores:
        elemento = soup.select_one(seletor)
        if elemento:
            valor = elemento.get_text(" ", strip=True)
            if valor:
                return valor
    return ""


def extrair_pre_cifra(soup: BeautifulSoup, seletores: list[str]) -> str:
    for seletor in seletores:
        elemento = soup.select_one(seletor)
        if elemento:
            return converter_pre_para_inline(elemento)
    return ""
