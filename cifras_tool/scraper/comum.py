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


PADRAO_ACORDES_HTML = re.compile(
    r'<span\s+data-chord="([^"]+)"[^>]*>.*?</span>|'
    r"<b>([^<]+)</b>|"
    r"<i>(.*?)</i>|"
    r"([^<]+)",
    re.DOTALL,
)


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


def parse_linha_html(linha_html: str) -> tuple[list[tuple[int, str]], str, bool]:
    posicoes: list[tuple[int, str]] = []
    texto = ""
    tem_acordes = False

    for match in PADRAO_ACORDES_HTML.finditer(linha_html):
        if match.group(1):
            tem_acordes = True
            posicoes.append((len(texto), match.group(1)))
            texto += match.group(1)
        elif match.group(2):
            tem_acordes = True
            acorde = match.group(2).strip()
            posicoes.append((len(texto), acorde))
            texto += acorde
        elif match.group(3) is not None:
            texto += match.group(3)
        elif match.group(4):
            texto += match.group(4)

    return posicoes, texto.rstrip(), tem_acordes


def mesclar_acordes_inline(acordes: list[tuple[int, str]], letra: str) -> str:
    letra = letra.rstrip()
    tamanho = len(letra)
    resultado = letra

    for posicao, acorde in sorted(acordes, key=lambda item: item[0], reverse=True):
        posicao = min(posicao, tamanho)
        resultado = resultado[:posicao] + f"[{acorde}]" + resultado[posicao:]

    return resultado


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


def converter_html_para_inline(html: str) -> str:
    """Converte HTML colado do Cifra Club (ou similar) para texto inline SetSync."""
    html_bruto = extrair_tablaturas_do_html(html or "")
    linhas_html = re.split(r"\r\n?|\n", html_bruto)
    saida: list[str] = []
    indice = 0

    while indice < len(linhas_html):
        if not linhas_html[indice].strip():
            indice += 1
            continue

        acordes, texto, tem_acordes = parse_linha_html(linhas_html[indice])

        if tem_acordes:
            if indice + 1 < len(linhas_html):
                _, proxima_letra, proxima_tem_acordes = parse_linha_html(
                    linhas_html[indice + 1]
                )
                if not proxima_tem_acordes and proxima_letra.strip():
                    saida.append(mesclar_acordes_inline(acordes, proxima_letra))
                    indice += 2
                    continue

            linha = texto
            for posicao, acorde in sorted(acordes, key=lambda item: item[0], reverse=True):
                linha = linha[:posicao] + f"[{acorde}]" + linha[posicao + len(acorde) :]
            saida.append(linha.strip())
            indice += 1
            continue

        if texto.strip():
            saida.append(texto.strip())
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
