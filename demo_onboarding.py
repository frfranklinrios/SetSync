"""Conteúdo demo pós-cadastro — aha moment em < 60s (coleção + Modo Tocar)."""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

_DEMO_META = json.dumps({'is_demo': True, 'source': 'onboarding'}, ensure_ascii=False)


def demo_songs() -> list[dict]:
    """3–4 músicas curtas (gospel conhecido) para o primeiro Modo Tocar."""
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
[E]Com cordas de [B]amor [C#m]me [A]atraiu
{end_of_chorus}""",
        },
    ]


def user_has_demo_library(user_id: str) -> bool:
    from db import get_user_personal_cifras

    for c in get_user_personal_cifras(user_id):
        raw = c.get('referencia_json') or ''
        if isinstance(raw, dict):
            if raw.get('is_demo'):
                return True
            continue
        try:
            meta = json.loads(raw) if raw else {}
        except (TypeError, ValueError):
            meta = {}
        if meta.get('is_demo'):
            return True
        if (c.get('titulo') or '') in {s['titulo'] for s in demo_songs()}:
            return True
    return False


def seed_demo_library_for_user(user_id: str) -> list[str]:
    """
    Popula a coleção pessoal com cifras demo (idempotente).
    Retorna IDs criados (vazio se já havia demo ou cifras).
    """
    if not user_id:
        return []
    from db import count_user_personal_cifras, create_personal_cifra

    # Se já tem qualquer cifra pessoal, não sobrescreve o repertório real
    if count_user_personal_cifras(user_id) > 0:
        return []
    if user_has_demo_library(user_id):
        return []

    created: list[str] = []
    try:
        for song in demo_songs():
            cid = create_personal_cifra(
                user_id,
                song['titulo'],
                song['artista'],
                song['tom'],
                song['conteudo'],
                bpm=song.get('bpm'),
                referencia_json=_DEMO_META,
            )
            if cid:
                created.append(str(cid))
    except Exception:
        logger.exception('Falha ao seedar biblioteca demo user=%s', user_id)
    return created


def maybe_start_trial_on_value(user_id: str, *, reason: str = 'play_mode') -> str | None:
    """
    Inicia trial Pro na 1ª banda do usuário no momento de valor
    (Modo Tocar ou 1º setlist real) — não no create da banda.
    Retorna banda_id se iniciou.
    """
    if not user_id:
        return None
    from db import get_owned_bands
    from monetizacao import iniciar_trial_banda
    from product_funnel import log_funnel_step

    owned = get_owned_bands(user_id)
    if not owned:
        return None
    for band in owned:
        band_id = band['id']
        if iniciar_trial_banda(band_id):
            try:
                from google_ads import mark_funnel_event

                mark_funnel_event('trial_iniciado')
            except Exception:
                pass
            log_funnel_step(
                user_id,
                'trial_iniciado',
                meta={'source': reason, 'banda_id': band_id},
            )
            return band_id
    return None
