"""Assistente de ajuda — busca em FAQ, Ajuda e páginas do Guia."""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from seo_pages import faq_entries, list_seo_pages

_ROOT = Path(__file__).resolve().parent
_AJUDA_HTML = _ROOT / 'templates' / 'ajuda' / 'index.html'

_STOPWORDS = frozenset({
    'a', 'ao', 'aos', 'as', 'com', 'como', 'da', 'das', 'de', 'do', 'dos', 'e', 'em', 'eu',
    'isso', 'meu', 'minha', 'na', 'no', 'nos', 'o', 'os', 'ou', 'para', 'por', 'que', 'qual',
    'quais', 'quando', 'quero', 'se', 'ser', 'sim', 'sua', 'seu', 'um', 'uma', 'é', 'nao', 'não',
})


def _normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', text.lower()).strip()


def _tokenize(query: str) -> list[str]:
    norm = _normalize(query)
    tokens = [t for t in re.findall(r'[a-z0-9]+', norm) if len(t) > 2 and t not in _STOPWORDS]
    return tokens


def _strip_jinja(html: str) -> str:
    html = re.sub(r'\{%.*?%\}', '', html, flags=re.DOTALL)
    return re.sub(r'\{\{.*?\}\}', '', html, flags=re.DOTALL)


def _strip_html(html: str) -> str:
    return BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)


def _load_ajuda_sections() -> list[dict[str, Any]]:
    if not _AJUDA_HTML.is_file():
        return []
    raw = _strip_jinja(_AJUDA_HTML.read_text(encoding='utf-8'))
    soup = BeautifulSoup(raw, 'html.parser')
    entries: list[dict[str, Any]] = []
    for section in soup.select('section.help-section'):
        sid = section.get('id') or ''
        header = section.select_one('.card-header')
        title = header.get_text(' ', strip=True) if header else sid
        body = section.select_one('.card-body')
        text = body.get_text(' ', strip=True) if body else ''
        if len(text) < 40:
            continue
        entries.append({
            'id': f'ajuda-{sid}',
            'title': title,
            'text': text,
            'answer': None,
            'source': 'ajuda',
            'url_path': '/ajuda',
            'url_fragment': f'#{sid}' if sid else '',
        })
    return entries


def _load_guia_sections() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for page in list_seo_pages():
        parts = [
            page.get('phrase') or '',
            page.get('meta_description') or '',
            page.get('meta_title') or '',
        ]
        for sec in page.get('sections') or []:
            parts.append(sec.get('h2') or '')
            parts.append(_strip_html(sec.get('html') or ''))
        text = ' '.join(p for p in parts if p).strip()
        if len(text) < 40:
            continue
        entries.append({
            'id': f'guia-{page["slug"]}',
            'title': page.get('title') or (page.get('phrase') or '').capitalize(),
            'text': text,
            'answer': page.get('meta_description'),
            'source': 'guia',
            'url_path': f'/guia/{page["slug"]}',
            'url_fragment': '',
        })
    return entries


def _load_faq() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for i, item in enumerate(faq_entries()):
        q, a = item['q'], item['a']
        entries.append({
            'id': f'faq-{i}',
            'title': q,
            'text': f'{q} {a}',
            'answer': a,
            'source': 'faq',
            'url_path': '/ajuda',
            'url_fragment': '',
        })
    return entries


@lru_cache(maxsize=1)
def get_knowledge_base() -> tuple[dict[str, Any], ...]:
    items = _load_faq() + _load_ajuda_sections() + _load_guia_sections()
    return tuple(items)


def clear_knowledge_base_cache() -> None:
    """Invalida cache após alterar Ajuda, FAQ ou Guia."""
    get_knowledge_base.cache_clear()


def default_suggestions(limit: int = 6) -> list[str]:
    curated = [
        'Como usar o Modo Tocar no palco?',
        'Como sincronizar a banda no palco?',
        'Como configurar pedal Bluetooth no SetSync?',
        'Posso usar cifras offline no celular?',
        'Como reservar estúdio de ensaio?',
        'Como gerenciar o financeiro do estúdio?',
        'Como resgatar voucher Estúdio Premium?',
        'Qual a diferença entre Pro e Worship?',
        'Como montar setlist online para show ou ensaio?',
        'O que são notas de palco na setlist?',
    ]
    return curated[:limit]


def _score_entry(tokens: list[str], entry: dict[str, Any]) -> float:
    if not tokens:
        return 0.0
    title = _normalize(entry.get('title') or '')
    text = _normalize(entry.get('text') or '')
    score = 0.0
    joined = ' '.join(tokens)
    if joined and joined in text:
        score += 12.0
    for token in tokens:
        if token in title:
            score += 5.0
        if token in text:
            score += 1.0
    return score


def _excerpt(text: str, max_len: int = 420) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    last = max(cut.rfind('. '), cut.rfind('! '), cut.rfind('? '))
    if last > max_len // 2:
        return cut[: last + 1].strip()
    return cut.rstrip() + '…'


def _entry_link(entry: dict[str, Any]) -> dict[str, str]:
    url = entry.get('url_path') or '/ajuda'
    frag = entry.get('url_fragment') or ''
    label = {
        'ajuda': 'Ajuda',
        'guia': 'Guia',
        'faq': 'FAQ',
    }.get(entry.get('source') or '', 'Saiba mais')
    return {
        'title': entry.get('title') or label,
        'url': f'{url}{frag}',
        'source': label,
    }


def _chat_ctas(user_id: str | None, query: str) -> list[dict]:
    if not user_id:
        return []
    from flask import url_for
    from db import get_owned_bands, get_user_bands
    q = _normalize(query)
    ctas: list[dict] = []
    bands = get_owned_bands(user_id) or get_user_bands(user_id)
    first_band = bands[0]['id'] if bands else None

    if any(t in q for t in ('cifra', 'musica', 'musica', 'importar', 'adicionar')):
        if first_band:
            ctas.append({'label': 'Adicionar cifra', 'url': url_for('cifras.add', band_id=first_band)})
    if any(t in q for t in ('setlist', 'roteiro', 'show', 'ensaio')):
        if first_band:
            ctas.append({'label': 'Criar setlist', 'url': url_for('setlists.create', band_id=first_band)})
    if any(t in q for t in ('estudio', 'sala', 'reserv', 'agend')):
        from models_studio import list_studios_by_owner
        owned = list_studios_by_owner(user_id)
        if owned:
            ctas.append({'label': 'Painel do estúdio', 'url': url_for('studios.my_studios')})
        else:
            ctas.append({'label': 'Cadastrar estúdio', 'url': url_for('studios.register_studio')})
        ctas.append({'label': 'Buscar estúdios', 'url': url_for('studios.search')})
    if any(t in q for t in ('financeiro', 'receita', 'despesa', 'faturamento', 'liquido', 'lucro', 'cache', 'cachê')):
        from models_studio import list_studios_by_owner
        from db import get_owned_bands, get_user_bands
        owned_studios = list_studios_by_owner(user_id)
        owned_bands = get_owned_bands(user_id)
        member_bands = get_user_bands(user_id)
        finance_band = owned_bands[0] if owned_bands else (member_bands[0] if member_bands else None)
        if finance_band:
            ctas.append({
                'label': 'Financeiro da banda',
                'url': url_for('bands.finance', band_id=finance_band['id']),
            })
        if owned_studios:
            ctas.append({
                'label': 'Financeiro do estúdio',
                'url': url_for('studios.owner_finance', studio_id=owned_studios[0]['id']),
            })
        ctas.append({
            'label': 'Ajuda financeiro estúdio',
            'url': url_for('ajuda.index') + '#estudio-financeiro',
        })
        if finance_band:
            ctas.append({
                'label': 'Ajuda financeiro banda',
                'url': url_for('ajuda.index') + '#financeiro-banda',
            })
    if any(t in q for t in ('voucher', 'codigo', 'código', 'promoc', 'cupom')):
        from models_studio import list_studios_by_owner
        ctas.append({
            'label': 'Resgatar voucher',
            'url': url_for('assinatura_bp.planos') + '#estudio',
        })
        if list_studios_by_owner(user_id):
            ctas.append({
                'label': 'Ajuda voucher estúdio',
                'url': url_for('ajuda.index') + '#estudio-voucher',
            })
        else:
            ctas.append({
                'label': 'Cadastrar estúdio',
                'url': url_for('studios.register_studio'),
            })
    if any(t in q for t in ('plano', 'pro', 'premium', 'assinar', 'trial', 'limite')):
        ctas.append({'label': 'Ver planos', 'url': url_for('assinatura_bp.planos')})
    if any(t in q for t in ('pagamento', 'cobranc', 'cartao', 'cartão', 'segur', 'mercado', 'pago')):
        ctas.append({'label': 'Ver planos', 'url': url_for('assinatura_bp.planos')})
        ctas.append({'label': 'Cobrança na Ajuda', 'url': url_for('ajuda.index') + '#cobranca'})
    if any(t in q for t in ('modo', 'tocar', 'palco')):
        if first_band:
            ctas.append({'label': 'Modo Tocar', 'url': url_for('cifras.tocar_band', band_id=first_band)})
        ctas.append({'label': 'Ajuda Modo Tocar', 'url': url_for('ajuda.index') + '#modo-tocar'})
    if any(t in q for t in ('pedal', 'bluetooth', 'footswitch', 'page up')):
        ctas.append({'label': 'Pedal no palco', 'url': url_for('ajuda.index') + '#modo-tocar'})
    if any(t in q for t in ('offline', 'pwa', 'sem internet')):
        ctas.append({'label': 'Offline e PWA', 'url': url_for('ajuda.index') + '#pwa'})
    if any(t in q for t in ('sync', 'sincron', 'lider', 'banda no palco')):
        ctas.append({'label': 'Sync no palco', 'url': url_for('ajuda.index') + '#modo-tocar'})
    if any(t in q for t in ('indic', 'convid', 'voucher', 'referr', 'ganhar')):
        ctas.append({'label': 'Indicar banda', 'url': url_for('assinatura_bp.voucher_indicar')})
    if any(t in q for t in ('ajuda', 'roadmap', 'novidade')):
        ctas.append({'label': 'Roadmap', 'url': url_for('roadmap.index')})
    return ctas[:3]


def answer_question(query: str, *, user_id: str | None = None, limit: int = 3) -> dict[str, Any]:
    q = (query or '').strip()
    if not q:
        return {
            'ok': False,
            'error': 'Digite uma pergunta.',
            'suggestions': default_suggestions(),
        }

    tokens = _tokenize(q)
    if not tokens:
        return {
            'ok': True,
            'answer': (
                'Não entendi bem a pergunta. Tente palavras como '
                '<strong>cifra</strong>, <strong>setlist</strong>, <strong>agenda</strong>, '
                '<strong>estúdio</strong> ou <strong>plano</strong>.'
            ),
            'title': None,
            'links': [
                {'title': 'Central de Ajuda', 'url': '/ajuda', 'source': 'Ajuda'},
                {'title': 'Guia SetSync', 'url': '/guia', 'source': 'Guia'},
            ],
            'suggestions': default_suggestions(),
        }

    ranked: list[tuple[float, dict[str, Any]]] = []
    for entry in get_knowledge_base():
        score = _score_entry(tokens, entry)
        if score > 0:
            ranked.append((score, entry))
    ranked.sort(key=lambda x: (-x[0], x[1].get('title') or ''))

    if not ranked:
        return {
            'ok': True,
            'answer': (
                'Não encontrei uma resposta exata na Ajuda ou no Guia. '
                'Confira a <a href="/ajuda">central de ajuda</a> ou fale conosco pelo WhatsApp.'
            ),
            'title': None,
            'links': [
                {'title': 'Central de Ajuda', 'url': '/ajuda', 'source': 'Ajuda'},
                {'title': 'Guia SetSync', 'url': '/guia', 'source': 'Guia'},
            ],
            'suggestions': default_suggestions(),
        }

    best = ranked[0][1]
    answer = best.get('answer') or _excerpt(best.get('text') or '')
    links: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for _, entry in ranked[:limit]:
        link = _entry_link(entry)
        if link['url'] in seen_urls:
            continue
        seen_urls.add(link['url'])
        links.append(link)

    return {
        'ok': True,
        'answer': answer,
        'title': best.get('title'),
        'links': links,
        'suggestions': default_suggestions(),
        'ctas': _chat_ctas(user_id, q),
    }
