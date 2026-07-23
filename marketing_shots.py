"""Screenshots de marketing — packs BR/gospel e URL diária."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from config import app_now_naive

# Slot 0–6: troca visual a cada dia da semana
NUM_SLOTS = 7

PACK_BR = 'br'
PACK_GOSPEL = 'gospel'
PACK_ESTUDIO = 'estudio'

# Nomes canônicos usados nos templates (arquivo final do dia)
SHOT_MODO_TOCAR = 'modo-tocar-mobile'
SHOT_SETLIST = 'setlist-desktop'
SHOT_FINANCE_BAND = 'financeiro-banda-desktop'
SHOT_FINANCE_ME = 'meu-financeiro-desktop'
SHOT_ESTUDIO_PAINEL = 'estudio-painel-mobile'
SHOT_ESTUDIO_FINANCE = 'estudio-financeiro-desktop'

_STATIC_DIR = Path(__file__).resolve().parent / 'static' / 'screenshots'


def screenshots_live_dir() -> Path:
    """Pasta persistente (volume ./data/screenshots)."""
    raw = os.getenv('SETSYNC_SCREENSHOTS_DIR') or ''
    if raw:
        return Path(raw)
    data = os.getenv('MAIL_DATA_DIR') or os.getenv('SETSYNC_DATA_DIR') or ''
    if data:
        # MAIL_DATA_DIR costuma ser /app/data/mail → sobe um nível
        base = Path(data)
        if base.name == 'mail':
            base = base.parent
        return base / 'screenshots'
    return Path(__file__).resolve().parent / 'data' / 'screenshots'


def slot_for_date(d: date | None = None) -> int:
    d = d or app_now_naive().date()
    return int(d.toordinal()) % NUM_SLOTS


def today_cache_bust() -> str:
    return app_now_naive().strftime('%Y%m%d')


def live_shot_file(pack: str, name: str, *, slot: int | None = None) -> Path:
    slot = slot_for_date() if slot is None else slot
    return screenshots_live_dir() / pack / f'slot-{slot}' / f'{name}.png'


def fallback_shot_file(name: str) -> Path | None:
    """Fallbacks estáticos (imagem baked na imagem Docker)."""
    aliases = {
        SHOT_MODO_TOCAR: 'modo-tocar-mobile.png',
        SHOT_SETLIST: 'setlist-desktop.png',
        SHOT_ESTUDIO_PAINEL: 'estudio-painel-mobile.png',
        SHOT_ESTUDIO_FINANCE: 'estudio-financeiro-desktop.png',
        SHOT_FINANCE_BAND: 'financeiro-banda-desktop.png',
        SHOT_FINANCE_ME: 'estudio-financeiro-desktop.png',
    }
    fname = aliases.get(name, f'{name}.png')
    path = _STATIC_DIR / fname
    return path if path.is_file() else None


def resolve_shot_path(pack: str, name: str, *, slot: int | None = None) -> Path | None:
    # 1) cópia estável do dia (current)
    current = screenshots_live_dir() / pack / 'current' / f'{name}.png'
    if current.is_file() and current.stat().st_size > 1000:
        return current
    # 2) slot do dia
    live = live_shot_file(pack, name, slot=slot)
    if live.is_file() and live.stat().st_size > 1000:
        return live
    # 3) qualquer slot do pack
    root = screenshots_live_dir() / pack
    if root.is_dir():
        for child in sorted(root.glob(f'slot-*/{name}.png'), reverse=True):
            if child.is_file() and child.stat().st_size > 1000:
                return child
    return fallback_shot_file(name)


def marketing_shot_url(pack: str, name: str) -> str:
    """URL pública com cache-bust diário."""
    from flask import url_for

    return url_for(
        'marketing_shots.serve',
        pack=pack,
        name=name,
        v=today_cache_bust(),
    )


def songs_br() -> list[dict]:
    """Repertório brasileiro para landing de bandas."""
    return [
        {
            'titulo': 'Evidências',
            'artista': 'Chitãozinho & Xororó',
            'tom': 'A',
            'bpm': 92,
            'conteudo': """{title: Evidências}
{artist: Chitãozinho & Xororó}
{key: A}
{tempo: 92}

{start_of_verse: Verso}
[A]Quando eu digo que deixei de [E]te amar
[F#m7]É porque eu te [D]amo
[A]Quando eu digo que não quero [E]mais você
[F#m7]É porque eu te [D]quero
{end_of_verse}

{start_of_chorus: Refrão}
[D]Eu tenho medo de te dar [A]liberdade
[E]Medo de você não me [F#m7]encontrar nunca mais
[D]Por isso eu finjo que [A]não te quero
[E]Finjo pra você [D]continuar [A]comigo
{end_of_chorus}""",
        },
        {
            'titulo': 'Tempo Perdido',
            'artista': 'Legião Urbana',
            'tom': 'G',
            'bpm': 98,
            'conteudo': """{title: Tempo Perdido}
{artist: Legião Urbana}
{key: G}
{tempo: 98}

{start_of_verse: Verso}
[G]Todos os [D]dias quando a[Em]cordeiro
[C]Não tenho mais [G]tempo [D]perdido
[G]Quero [D]você [Em]sempre perto
[C]Nada [G]melhor [D]do que [G]nós
{end_of_verse}""",
        },
        {
            'titulo': 'Anna Júlia',
            'artista': 'Los Hermanos',
            'tom': 'A',
            'bpm': 110,
            'conteudo': """{title: Anna Júlia}
{artist: Los Hermanos}
{key: A}
{tempo: 110}

{start_of_verse: Verso}
[A]Meu amor [E]inventei [F#m]pra te [D]ganhar
[A]Não sou [E]poeta [F#m]nem [D]inventei
[A]Só sei [E]que [F#m]te amo [D]demais
{end_of_verse}""",
        },
        {
            'titulo': 'Sutilmente',
            'artista': 'Skank',
            'tom': 'E',
            'bpm': 100,
            'conteudo': """{title: Sutilmente}
{artist: Skank}
{key: E}
{tempo: 100}

{start_of_verse: Verso}
[E]Eu [B]quero [C#m]você [A]assim
[E]Sutil[B]mente [C#m]bem [A]perto
{end_of_verse}""",
        },
        {
            'titulo': 'Do Seu Lado',
            'artista': 'Jota Quest',
            'tom': 'G',
            'bpm': 96,
            'conteudo': """{title: Do Seu Lado}
{artist: Jota Quest}
{key: G}
{tempo: 96}

{start_of_chorus: Refrão}
[G]Deixa eu [D]ficar do [Em]seu [C]lado
[G]Não diga [D]nada [Em]errado [C]
{end_of_chorus}""",
        },
        {
            'titulo': 'Eduardo e Mônica',
            'artista': 'Legião Urbana',
            'tom': 'A',
            'bpm': 120,
            'conteudo': """{title: Eduardo e Mônica}
{artist: Legião Urbana}
{key: A}
{tempo: 120}

{start_of_verse: Verso}
[A]Quem um dia [E]irá dizer
[F#m]Que existe [D]razão
[A]Pra tantas [E]coisas [D]boas
{end_of_verse}""",
        },
        {
            'titulo': 'Ai, Ai, Ai…',
            'artista': 'Vanessa da Mata',
            'tom': 'D',
            'bpm': 88,
            'conteudo': """{title: Ai, Ai, Ai…}
{artist: Vanessa da Mata}
{key: D}
{tempo: 88}

{start_of_verse: Verso}
[D]Ai ai [A]ai [Bm]que vontade
[G]De te [D]beijar [A]
{end_of_verse}""",
        },
        {
            'titulo': 'Exagerado',
            'artista': 'Cazuza',
            'tom': 'C',
            'bpm': 112,
            'conteudo': """{title: Exagerado}
{artist: Cazuza}
{key: C}
{tempo: 112}

{start_of_chorus: Refrão}
[C]Eu [G]sou [Am]exagerado
[F]É [C]tudo [G]ou [Am]nada [F]
{end_of_chorus}""",
        },
    ]


def songs_gospel() -> list[dict]:
    """Repertório gospel/louvor para landing de igrejas."""
    return [
        {
            'titulo': 'Porque Ele Vive',
            'artista': 'Harpa Cristã / Tradicional',
            'tom': 'G',
            'bpm': 76,
            'conteudo': """{title: Porque Ele Vive}
{artist: Harpa Cristã}
{key: G}
{tempo: 76}

{start_of_verse: Verso}
[G]Deus [D]enviou [Em]seu [C]filho amado
[G]Pra [D]me [Em]salvar e [C]perdoar
[G]Na [D]cruz [Em]morreu por [C]minhas culpas
[G]Mas [D]ressusci[G]tou
{end_of_verse}

{start_of_chorus: Refrão}
[G]Porque Ele [D]vive, [Em]posso crer no [C]amanhã
[G]Porque Ele [D]vive, [Em]temor não há [C]
[G]Eu sei [D]quem sou [Em]e [C]onde vou
[G]Porque Ele [D]vive em [G]mim
{end_of_chorus}""",
        },
        {
            'titulo': 'Deus de Promessas',
            'artista': 'Diante do Trono',
            'tom': 'A',
            'bpm': 72,
            'conteudo': """{title: Deus de Promessas}
{artist: Diante do Trono}
{key: A}
{tempo: 72}

{start_of_verse: Verso}
[A]Deus de [E]promessas, [F#m]teu nome é [D]fiel
[A]Teus [E]planos não [F#m]falham, [D]és Deus
{end_of_verse}

{start_of_chorus: Refrão}
[A]Eu [E]creio, [F#m]creio [D]
[A]Nas [E]promessas [F#m]de Deus [D]
{end_of_chorus}""",
        },
        {
            'titulo': 'Bondade de Deus',
            'artista': 'Isadora Pompeo',
            'tom': 'G',
            'bpm': 68,
            'conteudo': """{title: Bondade de Deus}
{artist: Isadora Pompeo}
{key: G}
{tempo: 68}

{start_of_chorus: Refrão}
[G]Tua [D]bondade me [Em]seguiu [C]
[G]Em todos os [D]dias da [Em]minha [C]vida
[G]Eu [D]cantarei [Em]do grande [C]amor
[G]Da [D]bondade de [G]Deus
{end_of_chorus}""",
        },
        {
            'titulo': 'Me Atraiu',
            'artista': 'Gabriela Rocha',
            'tom': 'E',
            'bpm': 70,
            'conteudo': """{title: Me Atraiu}
{artist: Gabriela Rocha}
{key: E}
{tempo: 70}

{start_of_verse: Verso}
[E]Como um [B]ímã Tu me [C#m]atraiu [A]
[E]Com cordas de [B]amor [C#m]me [A]trouxe
{end_of_verse}

{start_of_chorus: Refrão}
[E]Me [B]atraiu, [C#m]me [A]atraiu
[E]Ao Teu [B]coração [C#m]me [A]atraiu
{end_of_chorus}""",
        },
        {
            'titulo': 'Algo Novo',
            'artista': 'Grove Worship',
            'tom': 'D',
            'bpm': 74,
            'conteudo': """{title: Algo Novo}
{artist: Grove Worship}
{key: D}
{tempo: 74}

{start_of_chorus: Refrão}
[D]Faz [A]algo [Bm]novo em [G]mim
[D]Eu [A]quero [Bm]Te ver [G]agir
{end_of_chorus}""",
        },
        {
            'titulo': 'Tua Graça Me Basta',
            'artista': 'Davi Fernandes',
            'tom': 'C',
            'bpm': 66,
            'conteudo': """{title: Tua Graça Me Basta}
{artist: Davi Fernandes}
{key: C}
{tempo: 66}

{start_of_chorus: Refrão}
[C]Tua [G]graça [Am]me [F]basta
[C]O [G]Teu [Am]poder se [F]aperfeiçoa
[C]Na [G]minha [Am]fra[F]queza
{end_of_chorus}""",
        },
        {
            'titulo': 'Oceanos',
            'artista': 'Hillsong / Ana Paula Valadão',
            'tom': 'D',
            'bpm': 64,
            'conteudo': """{title: Oceanos}
{artist: Hillsong United}
{key: D}
{tempo: 64}

{start_of_verse: Verso}
[D]Tu [A]me chamas [Bm]para águas [G]mais profundas
[D]Onde [A]os meus pés [Bm]podem [G]falhar
{end_of_verse}

{start_of_chorus: Refrão}
[D]Espírito [A]guia-me [Bm]onde a minha [G]fé
[D]É sem [A]fronteiras [Bm] [G]
{end_of_chorus}""",
        },
        {
            'titulo': 'Lugar Secreto',
            'artista': 'Gabriela Rocha',
            'tom': 'G',
            'bpm': 62,
            'conteudo': """{title: Lugar Secreto}
{artist: Gabriela Rocha}
{key: G}
{tempo: 62}

{start_of_chorus: Refrão}
[G]No [D]lugar [Em]secreto [C]
[G]Quero [D]estar [Em] [C]
[G]Me [D]esconder em [Em]Ti [C]
{end_of_chorus}""",
        },
    ]


def rotate_songs(songs: list[dict], slot: int) -> list[dict]:
    """Gira a ordem do repertório conforme o dia (screenshot diferente)."""
    if not songs:
        return songs
    n = slot % len(songs)
    return songs[n:] + songs[:n]
