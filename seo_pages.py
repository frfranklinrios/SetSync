"""Páginas públicas de SEO (/guia) — combinações de busca para bandas e louvor."""

from __future__ import annotations

import re
import unicodedata
from typing import Any


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return text


def _phrase(verb: str, obj: str) -> str:
    if verb:
        return f'{verb} {obj}'
    return obj


def _title_page(verb: str, obj: str) -> str:
    p = _phrase(verb, obj)
    return f'{p.capitalize()} — SetSync'


def _meta_desc(verb: str, obj: str) -> str:
    p = _phrase(verb, obj)
    return (
        f'Como {p} com o SetSync: repertório centralizado, convites por link, '
        f'setlists, transposição e Modo Tocar para bandas e ministérios de louvor. Comece grátis.'
    )


def _sections(verb: str, obj: str) -> list[dict[str, Any]]:
    phrase = _phrase(verb, obj)
    obj_cap = obj[0].upper() + obj[1:] if obj else ''

    intro = (
        f'<p>O SetSync foi feito para quem precisa <strong>{phrase}</strong> sem depender de '
        f'prints no WhatsApp, planilhas desatualizadas ou PDFs que ninguém sabe qual é a versão certa. '
        f'Centralize o repertório da banda, convide musicistas por link e use setlists com transposição '
        f'automática por cantor — no ensaio e no palco.</p>'
    )

    blocks = [
        {
            'h2': f'Por que {phrase} de forma organizada?',
            'html': (
                f'<p>Quando cada músico guarda a cifra no celular de um jeito, o ensaio vira adivinhação. '
                f'{obj_cap} compartilhado significa uma única fonte: quem edita atualiza para todos. '
                f'No SetSync, admins da banda controlam o repertório; membros tocam a versão aprovada.</p>'
                f'<p>Isso vale para ministérios de louvor, bandas de bar, equipes de jovens e qualquer '
                f'grupo que ensaia junto regularmente.</p>'
            ),
        },
        {
            'h2': 'Como o SetSync ajuda na prática',
            'html': (
                '<ul>'
                '<li><strong>Repertório único</strong> — cifras, letras e chord sheet na mesma música.</li>'
                '<li><strong>Convites por link</strong> — integre guitarristas, tecladistas, bateristas e vocalistas.</li>'
                '<li><strong>Setlists</strong> — ordem do culto ou show, tom por cantor, navegação no Modo Tocar.</li>'
                '<li><strong>Transposição</strong> — cada vocalista com o tom certo sem reescrever acordes.</li>'
                '<li><strong>Agenda</strong> — ensaios e cultos com setlist vinculada e escalação (planos Pro/Worship).</li>'
                '<li><strong>Plano grátis</strong> — comece sem cartão; evolua para Pro ou Worship quando precisar.</li>'
                '</ul>'
            ),
        },
        {
            'h2': f'Passo a passo para {phrase}',
            'html': (
                '<ol>'
                '<li>Crie sua conta grátis no SetSync.</li>'
                '<li>Monte a banda e envie o link de convite aos integrantes.</li>'
                '<li>Cadastre as músicas do repertório (importe cifras ou digite).</li>'
                '<li>Defina vocalistas e transposição por cantor, se necessário.</li>'
                '<li>Monte o setlist do ensaio ou culto e compartilhe com a equipe.</li>'
                '<li>No palco, abra o Modo Tocar — tela cheia, auto-scroll e tema escuro.</li>'
                '</ol>'
            ),
        },
        {
            'h2': 'Para igrejas com várias equipes',
            'html': (
                '<p>No plano <strong>Worship</strong>, uma conta gerencia várias bandas de louvor — '
                'cada ministério com repertório e setlists próprios. Ideal para igrejas com equipe '
                'de domingo, jovens e vigília sem misturar cifras.</p>'
                '<p>Veja também o <a href="/igrejas">SetSync para igrejas</a> e artigos no '
                '<a href="/blog">blog</a>.</p>'
            ),
        },
    ]

    if 'cifra' in obj or 'acorde' in obj or 'transpor' in verb:
        blocks.insert(1, {
            'h2': 'Transposição e tom do cantor',
            'html': (
                '<p>Cadastre cada vocalista e a transposição preferida. Na setlist, escolha quem canta '
                'cada música — a cifra abre no tom certo automaticamente, inclusive no chord sheet. '
                'Acabou o "espera, deixa eu subir meio tom no papel".</p>'
            ),
        })

    if 'setlist' in obj or verb == 'montar':
        blocks.insert(1, {
            'h2': 'Setlist sincronizada com a banda',
            'html': (
                '<p>Arraste as músicas na ordem do culto ou show. Defina cantor e tom por faixa. '
                'Exporte PDF no plano Pro ou navegue ao vivo com setas e toque no Modo Tocar. '
                'Todos veem a mesma ordem — sem "qual música vem depois?".</p>'
            ),
        })

    if 'banda' in obj or 'músico' in obj or 'membro' in obj or verb == 'gerenciar':
        blocks.insert(1, {
            'h2': 'Gerenciar membros e permissões',
            'html': (
                '<p>Admins editam repertório e convidam pessoas; membros tocam e consultam. '
                'Convite por link ou e-mail — quem entra no meio do mês já acessa tudo atualizado. '
                'Perfeito para rotatividade em ministérios voluntários.</p>'
            ),
        })

    if 'agenda' in obj or 'ensaio' in obj or 'escala' in obj:
        blocks.insert(1, {
            'h2': 'Agenda, ensaios e escalação',
            'html': (
                '<p>Marque ensaios e cultos no calendário, vincule a setlist do evento e escale '
                'quem participa. Lembretes por e-mail e WhatsApp ajudam a equipe a não esquecer. '
                'Local com busca no Google Maps facilita chegar no lugar certo.</p>'
            ),
        })

    if 'pdf' in obj or verb == 'exportar':
        blocks.insert(1, {
            'h2': 'Exportar PDF para ensaio',
            'html': (
                '<p>No plano Pro, exporte setlists formatadas com índice, cifras, letras e chord sheet '
                '— escolha o que incluir. Útil para quem prefere papel de backup ou arquivo para arquivo.</p>'
            ),
        })

    if 'modo tocar' in obj or 'palco' in obj or 'app' in obj:
        blocks.insert(1, {
            'h2': 'Modo Tocar e app no celular',
            'html': (
                '<p>Tela cheia para o palco: fonte grande, auto-scroll, duas colunas e tema claro ou escuro. '
                'Instale como PWA na tela inicial e use offline quando precisar — ideal no culto ou no bar.</p>'
            ),
        })

    return [{'html': intro}] + blocks


# verb + objeto → slug e conteúdo
_KEYWORD_PAIRS: list[tuple[str, str]] = [
    # compartilhar
    ('compartilhar', 'cifras'),
    ('compartilhar', 'setlists'),
    ('compartilhar', 'letras'),
    ('compartilhar', 'repertório'),
    ('compartilhar', 'chord sheet'),
    ('compartilhar', 'link público'),
    # gerenciar
    ('gerenciar', 'bandas'),
    ('gerenciar', 'ministério de louvor'),
    ('gerenciar', 'repertório'),
    ('gerenciar', 'músicos'),
    ('gerenciar', 'ensaios'),
    ('gerenciar', 'escalação'),
    # organizar
    ('organizar', 'cifras'),
    ('organizar', 'setlists'),
    ('organizar', 'banda'),
    ('organizar', 'ministério de louvor'),
    ('organizar', 'repertório gospel'),
    ('organizar', 'ensaio'),
    # montar
    ('montar', 'setlist'),
    ('montar', 'setlist gospel'),
    ('montar', 'setlist culto'),
    ('montar', 'repertório'),
    # transpor
    ('transpor', 'cifras'),
    ('transpor', 'acordes'),
    ('transpor', 'cifras online'),
    ('transpor', 'cifras por cantor'),
    # criar
    ('criar', 'banda'),
    ('criar', 'setlist online'),
    ('criar', 'repertório digital'),
    # usar
    ('usar', 'modo tocar'),
    ('usar', 'agenda da banda'),
    ('usar', 'app de cifras'),
    # exportar
    ('exportar', 'setlist pdf'),
    ('exportar', 'cifras pdf'),
    # convidar
    ('convidar', 'músicos'),
    ('convidar', 'membros da banda'),
    # sincronizar
    ('sincronizar', 'repertório'),
    ('sincronizar', 'setlist'),
    ('sincronizar', 'cifras'),
]

# termos compostos (sem verbo)
_STANDALONE_TOPICS: list[str] = [
    'cifras gospel',
    'cifras gospel banda',
    'cifras igreja',
    'cifras igreja online',
    'cifras banda online',
    'app cifras banda',
    'app cifras igreja',
    'app setlist banda',
    'setlist online',
    'setlist online banda',
    'setlist culto gospel',
    'modo tocar cifras',
    'modo tocar palco',
    'agenda banda louvor',
    'agenda ensaio culto',
    'chord sheet cifra',
    'repertório musical banda',
    'biblioteca cifras igreja',
    'planilha cifras alternativa',
    'cifras whatsapp',
    'louvor igreja app',
    'transposição automática cantor',
    'múltiplas bandas igreja',
    'cifras offline celular',
    'pwa cifras banda',
    'pdf setlist banda',
    'ensaios banda gospel',
    'palco cifras tela cheia',
    'software cifras banda',
    'plataforma setlist louvor',
]


def _build_page(verb: str, obj: str) -> dict[str, Any]:
    if verb:
        slug = slugify(f'{verb}-{obj}')
    else:
        slug = slugify(obj)
    phrase = _phrase(verb, obj)
    return {
        'slug': slug,
        'verb': verb,
        'object': obj,
        'phrase': phrase,
        'h1': f'{phrase.capitalize()} com o SetSync',
        'meta_title': _title_page(verb, obj),
        'meta_description': _meta_desc(verb, obj),
        'sections': _sections(verb, obj),
        'keywords': phrase,
    }


def _all_pages() -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    seen: set[str] = set()
    for verb, obj in _KEYWORD_PAIRS:
        p = _build_page(verb, obj)
        if p['slug'] not in seen:
            seen.add(p['slug'])
            pages.append(p)
    for topic in _STANDALONE_TOPICS:
        p = _build_page('', topic)
        if p['slug'] not in seen:
            seen.add(p['slug'])
            pages.append(p)
    for p in pages:
        obj_key = slugify(p['object'] or p['phrase'])
        verb_key = slugify(p['verb']) if p['verb'] else ''
        related = []
        for other in pages:
            if other['slug'] == p['slug']:
                continue
            if verb_key and slugify(other['verb']) == verb_key:
                related.append(other)
            elif slugify(other['object'] or other['phrase']) == obj_key:
                related.append(other)
        p['related'] = related[:6]
    return pages


_PAGES: list[dict[str, Any]] | None = None


def list_seo_pages() -> list[dict[str, Any]]:
    global _PAGES
    if _PAGES is None:
        _PAGES = _all_pages()
    return _PAGES


def get_seo_page(slug: str) -> dict[str, Any] | None:
    for p in list_seo_pages():
        if p['slug'] == slug:
            return p
    return None


def faq_entries() -> list[dict[str, str]]:
    """Perguntas frequentes para schema.org e home."""
    return [
        {
            'q': 'O SetSync serve para compartilhar cifras com a banda?',
            'a': 'Sim. Você centraliza o repertório, convida musicistas por link e todos acessam a mesma versão da cifra, com transposição por cantor e setlists sincronizadas.',
        },
        {
            'q': 'Como gerenciar várias bandas de louvor?',
            'a': 'No plano Worship, uma conta administra múltiplas bandas — cada ministério com repertório e setlists próprios. Convites e permissões por equipe.',
        },
        {
            'q': 'Posso montar setlist para culto gospel online?',
            'a': 'Sim. Arraste as músicas na ordem do culto, defina cantor e tom por faixa, e abra o Modo Tocar no palco ou exporte PDF no plano Pro.',
        },
        {
            'q': 'O SetSync transpor cifras automaticamente?',
            'a': 'Cadastre vocalistas com transposição preferida. Ao montar a setlist, escolha quem canta — a cifra abre no tom certo, inclusive chord sheet.',
        },
        {
            'q': 'Existe app de cifras para banda grátis?',
            'a': 'O SetSync tem plano grátis para começar: repertório, bandas, setlists e Modo Tocar. Planos Pro e Worship liberam mais recursos.',
        },
        {
            'q': 'Como convidar músicos para a banda?',
            'a': 'Crie a banda no SetSync e envie o link de convite por WhatsApp ou e-mail. Novos membros entram com permissão de membro ou admin.',
        },
        {
            'q': 'Funciona para ministério de louvor na igreja?',
            'a': 'Sim. Feito para igrejas brasileiras: repertório gospel, setlists de culto, agenda de ensaios, escalação e lembretes por WhatsApp.',
        },
        {
            'q': 'Posso usar cifras offline no celular?',
            'a': 'Instale o SetSync como PWA na tela inicial. O app funciona offline para consultar repertório e tocar no Modo Tocar quando a internet falhar.',
        },
        {
            'q': 'O que é o Modo Tocar?',
            'a': 'Tela cheia para o palco: cifra legível à distância, auto-scroll, navegação entre músicas da setlist e tema escuro para ambientes com pouca luz.',
        },
        {
            'q': 'Posso exportar setlist em PDF?',
            'a': 'No plano Pro, exporte setlists com índice, cifras, letras e chord sheet — você escolhe quais seções incluir.',
        },
        {
            'q': 'SetSync substitui planilha de cifras?',
            'a': 'Sim, para bandas que precisam de versão única, transposição e setlist. Acaba o problema de "qual arquivo é o certo?" no grupo do WhatsApp.',
        },
        {
            'q': 'Tem chord sheet além da cifra tradicional?',
            'a': 'Cada música pode ter cifra, chord sheet e letra. A transposição e a grafia dos acordes ficam alinhadas entre os formatos.',
        },
        {
            'q': 'Como organizar ensaios da banda?',
            'a': 'Use a Agenda: marque ensaio ou culto, vincule a setlist, escale quem participa e envie lembretes automáticos à equipe.',
        },
        {
            'q': 'Quantas músicas posso cadastrar?',
            'a': 'O plano grátis tem limites generosos para começar. Planos pagos ampliam repertório, bandas e recursos como PDF e Worship multi-bandas.',
        },
        {
            'q': 'O SetSync é melhor que mandar cifra no WhatsApp?',
            'a': 'Para equipes que ensaiam junto, sim: uma fonte atualizada, tom por cantor, setlist compartilhada e palco no Modo Tocar — sem prints desatualizados.',
        },
    ]
