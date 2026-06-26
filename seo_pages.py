"""Páginas públicas de SEO (/guia) — combinações de busca para bandas e músicos."""

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
    if 'financeiro' in obj:
        return (
            'Controle receita de reservas confirmadas, pagamentos e despesas do seu estúdio '
            'de ensaio no SetSync. Preço/hora, resumo mensal e líquido no painel do dono.'
        )
    if 'voucher' in obj and ('estudio' in obj or 'estúdio' in obj):
        return (
            'Resgate voucher Estúdio Premium no SetSync: salas ilimitadas por código promocional, '
            'sem cartão. Passo a passo para donos de sala de ensaio.'
        )
    p = _phrase(verb, obj)
    return (
        f'Como {p} com o SetSync: repertório centralizado, convites por link, '
        f'setlists, transposição e Modo Tocar para bandas e músicos. Comece grátis.'
    )


def _sections(verb: str, obj: str) -> list[dict[str, Any]]:
    phrase = _phrase(verb, obj)
    obj_cap = obj[0].upper() + obj[1:] if obj else ''

    if 'financeiro' in obj:
        return [
            {
                'html': (
                    '<p>O <strong>financeiro do estúdio</strong> no SetSync ajuda donos de sala de ensaio '
                    'a acompanhar <strong>receita das reservas confirmadas</strong>, marcar o que já foi '
                    'pago e registrar <strong>despesas do mês</strong> — tudo no painel, sem planilha paralela.</p>'
                ),
            },
            {
                'h2': 'Como a receita é calculada',
                'html': (
                    '<p>Cadastre o <strong>preço por hora</strong> no perfil do estúdio. Para cada reserva '
                    '<strong>confirmada</strong>, o sistema estima o valor multiplicando a duração '
                    '(hora fim − hora início) pelo preço/hora. Você pode ajustar o valor manualmente em '
                    'reservas com desconto, pacote ou acordo com a banda.</p>'
                ),
            },
            {
                'h2': 'Passo a passo no painel',
                'html': (
                    '<ol>'
                    '<li>Cadastre o estúdio e configure salas, disponibilidade e <strong>preço/hora</strong>.</li>'
                    '<li>Confirme solicitações de bandas no painel — só reservas confirmadas entram no financeiro.</li>'
                    '<li>Abra <strong>Financeiro</strong> no painel do dono (ao lado de Calendário).</li>'
                    '<li>Filtre por mês e ano para ver receita confirmada, recebido, a receber e horas reservadas.</li>'
                    '<li>Em cada reserva, marque <strong>Pago</strong> ou <strong>Pendente</strong> e adicione observações.</li>'
                    '<li>Registre despesas (aluguel, energia, manutenção…) para ver o <strong>líquido</strong> do mês.</li>'
                    '</ol>'
                ),
            },
            {
                'h2': 'Resumo do mês',
                'html': (
                    '<ul>'
                    '<li><strong>Receita confirmada</strong> — soma das reservas confirmadas no período.</li>'
                    '<li><strong>Recebido</strong> — reservas marcadas como pagas.</li>'
                    '<li><strong>A receber</strong> — diferença entre confirmado e recebido.</li>'
                    '<li><strong>Despesas</strong> — lançamentos manuais do mês.</li>'
                    '<li><strong>Líquido</strong> — recebido menos despesas.</li>'
                    '</ul>'
                ),
            },
            {
                'h2': 'Integração com reservas e agenda',
                'html': (
                    '<p>Quando você confirma uma reserva, o ensaio vai para a agenda da banda. O financeiro '
                    'usa os mesmos horários da reserva — não precisa digitar de novo. Bandas acompanham em '
                    '<strong>Minhas reservas</strong>; o controle de pagamento é visível só para o dono do estúdio.</p>'
                    '<p>Detalhes na <a href="/ajuda#estudio-financeiro">Ajuda → Financeiro do estúdio</a>.</p>'
                ),
            },
        ]

    if 'voucher' in obj and ('estudio' in obj or 'estúdio' in obj):
        return [
            {
                'html': (
                    '<p>Donos de estúdio podem ativar o plano <strong>Premium</strong> (salas ilimitadas) '
                    'com um <strong>código voucher</strong> enviado pela equipe SetSync ou em campanhas '
                    'parceiras — sem assinatura no Mercado Pago.</p>'
                ),
            },
            {
                'h2': 'Antes de resgatar',
                'html': (
                    '<ul>'
                    '<li>Use a conta que <strong>cadastrou o estúdio</strong> (dono).</li>'
                    '<li>Tenha pelo menos um estúdio no SetSync — '
                    '<a href="/estudios">cadastre grátis</a> se ainda não tiver.</li>'
                    '<li>O voucher não substitui assinatura <strong>Premium paga</strong> já ativa.</li>'
                    '<li>Cada código vale <strong>uma vez</strong> por conta.</li>'
                    '</ul>'
                ),
            },
            {
                'h2': 'Passo a passo',
                'html': (
                    '<ol>'
                    '<li>Entre no SetSync com sua conta de dono.</li>'
                    '<li>Abra <a href="/assinatura/planos#estudio">Planos → Estúdio</a>.</li>'
                    '<li>Em <strong>Tem um voucher?</strong>, digite o código (ex.: <code>ESTUDIO-XXXX</code>) '
                    'e toque em <strong>Resgatar</strong>.</li>'
                    '<li>Confirme o badge <strong>Estúdio Premium</strong> no painel e cadastre salas além do limite do Básico.</li>'
                    '</ol>'
                ),
            },
            {
                'h2': 'Diferença para voucher de banda',
                'html': (
                    '<p>Códigos de <strong>banda</strong> liberam Pro/Worship na banda selecionada. '
                    'Códigos de <strong>estúdio</strong> liberam Premium na <strong>conta do dono</strong>. '
                    'Se o app avisar que o código é do outro tipo, use a seção correta em Planos.</p>'
                ),
            },
            {
                'h2': 'Validade',
                'html': (
                    '<p>Vouchers por prazo expiram automaticamente; a conta volta ao plano Básico (até 2 salas). '
                    'Você recebe e-mail antes do vencimento. Vouchers <strong>vitalícios</strong> não expiram.</p>'
                    '<p>Mais detalhes na <a href="/ajuda#estudio-voucher">Ajuda → Voucher Estúdio Premium</a>.</p>'
                ),
            },
        ]

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
                f'<p>Isso vale para bandas de bar, grupos acústicos, projetos paralelos e qualquer '
                f'equipe que ensaia junto regularmente.</p>'
            ),
        },
        {
            'h2': 'Como o SetSync ajuda na prática',
            'html': (
                '<ul>'
                '<li><strong>Repertório único</strong> — cifras, letras e grade harmônica na mesma música.</li>'
                '<li><strong>Convites por link</strong> — integre guitarristas, tecladistas, bateristas e vocalistas.</li>'
                '<li><strong>Setlists</strong> — ordem do show ou ensaio, tom por cantor, navegação no Modo Tocar.</li>'
                '<li><strong>Transposição</strong> — cada vocalista com o tom certo; sustenidos e bemóis pela armadura do tom.</li>'
                '<li><strong>Grade harmônica</strong> — editor com salvamento automático, extrair da cifra, notação brasileira e semi-pulsos.</li>'
                '<li><strong>Agenda</strong> — ensaios e shows com setlist vinculada, escalação com confirmação por link, instrumentos no perfil e lembretes.</li>'
                '<li><strong>Estúdios</strong> — busque salas de ensaio, solicite reserva e sincronize com a agenda da banda.</li>'
                '<li><strong>Plano grátis</strong> — comece sem cartão; evolua para Individual, Pro, Worship ou Estúdio (beta).</li>'
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
                '<li>Cadastre seus <strong>instrumentos</strong> em Meu perfil — a banda vê na escalação.</li>'
                '<li>Monte o setlist do ensaio ou show e compartilhe com a equipe.</li>'
                '<li>No palco, abra o Modo Tocar — sync da banda, offline automático da setlist, seções e pedal Bluetooth.</li>'
                '</ol>'
            ),
        },
        {
            'h2': 'Plano Worship — várias bandas',
            'html': (
                '<p>O plano <strong>Worship</strong> cobre <strong>múltiplas bandas</strong> na mesma conta, '
                'cada uma com repertório e setlists próprios. Veja preços em '
                '<a href="/assinatura/planos">Planos</a>.</p>'
            ),
        },
    ]

    if 'igreja' in obj or 'worship' in obj or 'louvor' in obj or 'múltiplas bandas' in obj:
        blocks.append({
            'h2': 'SetSync para igrejas',
            'html': (
                '<p>Se você lidera o louvor em uma congregação com várias equipes, reunimos '
                'comparativos, preços e rotina de culto na página '
                '<a href="/igrejas">SetSync para Igrejas</a>.</p>'
            ),
        })

    if 'igreja' in obj or 'worship' in obj or 'múltiplas bandas' in obj:
        blocks.insert(1, {
            'h2': 'Plano Worship para múltiplas equipes',
            'html': (
                '<p>O <strong>Worship</strong> cobre várias bandas na mesma conta — útil quando você '
                'administra mais de um grupo musical. Detalhes, calculadora de economia e casos de '
                'igreja estão em <a href="/igrejas">SetSync para Igrejas</a>.</p>'
            ),
        })

    if 'cifra' in obj or 'acorde' in obj or 'transpor' in verb:
        blocks.insert(1, {
            'h2': 'Transposição e tom do cantor',
            'html': (
                '<p>Cadastre cada vocalista e a transposição preferida. Na setlist, escolha quem canta '
                'cada música — a cifra abre no tom certo automaticamente, inclusive na grade harmônica. '
                'O SetSync grafia sustenidos e bemóis conforme a armadura do tom (ex.: C→Eb gera Eb, Ab, Bb). '
                'Acabou o "espera, deixa eu subir meio tom no papel".</p>'
            ),
        })

    if 'chord sheet' in obj or 'chord-sheet' in obj or 'grade harmônica' in obj or 'grade harmonica' in obj:
        blocks.insert(1, {
            'h2': 'Grade harmônica profissional',
            'html': (
                '<p>Além da cifra com letra, monte a progressão no editor chordsheet.com integrado: '
                'compassos, simile, seções e semi-pulsos. Use <strong>Extrair da cifra</strong> para gerar um rascunho, '
                'salvamento automático, notação brasileira (C7+, °, m7b5) e notas privadas com <code>!</code>. '
                'No palco, alterne cifra, grade harmônica e letra — com Nashville (1–7), auto-scroll e diagramas ao tocar acordes.</p>'
            ),
        })

    if 'setlist' in obj or verb == 'montar':
        blocks.insert(1, {
            'h2': 'Setlist sincronizada com a banda',
            'html': (
                '<p>Arraste as músicas na ordem do show ou ensaio. Defina cantor e tom por faixa. '
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
                'Perfeito para rotatividade em bandas com integrantes variáveis.</p>'
            ),
        })

    if 'agenda' in obj or 'ensaio' in obj or 'escala' in obj:
        blocks.insert(1, {
            'h2': 'Agenda, ensaios e escalação',
            'html': (
                '<p>Marque ensaios e shows no calendário, vincule a setlist do evento e escale '
                'quem participa por função. Cada músico cadastra <strong>instrumentos no perfil</strong> '
                '— visíveis na escalação. Confirmação em um toque por link no e-mail ou WhatsApp, '
                'formações salvas, sugestão de escala e painel de pendentes no dashboard. '
                'Lembretes automáticos (horário de Fortaleza) e exportação para Google Agenda ou arquivo .ics.</p>'
            ),
        })

    if 'estudio' in obj or 'estúdio' in obj or 'sala de ensaio' in obj or 'reservar' in verb:
        blocks.insert(1, {
            'h2': 'Estúdios de ensaio',
            'html': (
                '<p>Busque estúdios por cidade e bairro, veja fotos e equipamentos, abra o endereço no '
                '<strong>Google Maps</strong> e solicite reserva de sala. Quando o estúdio confirma, o ensaio '
                'entra na agenda da banda. Donos de estúdio cadastram salas, disponibilidade, bloqueios e '
                '<strong>financeiro</strong> (receita, pagamentos e despesas) e <strong>vouchers Premium</strong> '
                '— plano básico gratuito com até 2 salas.</p>'
            ),
        })

    if 'instrumento' in obj or 'músico' in obj or 'perfil' in obj:
        blocks.insert(1, {
            'h2': 'Instrumentos no perfil',
            'html': (
                '<p>Em <strong>Meu perfil</strong>, marque violão, guitarra, baixo, vocal, bateria, teclado e mais. '
                'A banda enxerga isso na lista de membros e na escalação de eventos — sem planilha paralela '
                'de “quem toca o quê”.</p>'
            ),
        })

    if 'pdf' in obj or verb == 'exportar':
        blocks.insert(1, {
            'h2': 'Exportar PDF para ensaio',
            'html': (
                '<p>No plano Pro, exporte setlists formatadas com índice, cifras, letras e grade harmônica '
                '— escolha o que incluir. Útil para quem prefere papel de backup ou arquivo para arquivo.</p>'
            ),
        })

    if 'modo tocar' in obj or 'palco' in obj or 'app' in obj:
        blocks.insert(1, {
            'h2': 'Modo Tocar e app no celular',
            'html': (
                '<p>Tela cheia para o palco: seções, modo vocalista, sync entre músicos, '
                'offline automático da setlist, notas de palco, metrônomo com count-in, '
                'pedal Bluetooth e auto-scroll. '
                'Instale como PWA na tela inicial — ideal no culto ou no ensaio sem internet.</p>'
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
    ('compartilhar', 'grade harmônica'),
    ('compartilhar', 'link público'),
    # gerenciar
    ('gerenciar', 'bandas'),
    ('gerenciar', 'ministério de louvor'),
    ('gerenciar', 'repertório'),
    ('gerenciar', 'músicos'),
    ('gerenciar', 'ensaios'),
    ('gerenciar', 'escalação'),
    ('reservar', 'sala de ensaio'),
    ('buscar', 'estúdio de ensaio'),
    ('cadastrar', 'estúdio de ensaio'),
    ('gerenciar', 'financeiro do estúdio'),
    ('resgatar', 'voucher estúdio premium'),
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
    ('montar', 'grade harmônica'),
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
    'grade harmônica cifra',
    'repertório musical banda',
    'biblioteca cifras igreja',
    'planilha cifras alternativa',
    'cifras whatsapp',
    'louvor igreja app',
    'transposição automática cantor',
    'múltiplas bandas igreja',
    'plano worship igreja',
    'cifras offline celular',
    'pwa cifras banda',
    'pdf setlist banda',
    'ensaios banda gospel',
    'palco cifras tela cheia',
    'software cifras banda',
    'plataforma setlist louvor',
    'estúdio de ensaio online',
    'reservar sala ensaio banda',
    'cadastrar estúdio ensaio',
    'financeiro estúdio ensaio',
    'voucher estúdio premium',
    'código premium estúdio ensaio',
    'instrumentos músico perfil',
    'escalação banda instrumentos',
]


_PREMIUM_SLUGS = frozenset({
    'compartilhar-cifras',
    'compartilhar-setlists',
    'gerenciar-ministerio-de-louvor',
    'gerenciar-bandas',
    'montar-setlist',
    'organizar-repertorio',
    'transpor-cifras',
    'usar-modo-tocar',
    'app-cifras-banda',
    'app-cifras-igreja',
    'setlist-culto-gospel',
    'cifras-gospel-banda',
    'cifras-offline-celular',
    'plano-worship-igreja',
    'multiplas-bandas-igreja',
    'chord-sheet-cifra',
    'grade-harmonica-cifra',
    'convidar-musicos',
    'reservar-sala-de-ensaio',
    'buscar-estudio-de-ensaio',
    'gerenciar-escalacao',
    'instrumentos-musico-perfil',
    'gerenciar-financeiro-do-estudio',
    'financeiro-estudio-ensaio',
    'resgatar-voucher-estudio-premium',
})


def _premium_faq_block(phrase: str) -> dict[str, Any]:
    return {
        'h2': 'Perguntas frequentes',
        'html': (
            '<p><strong>O SetSync é grátis?</strong> Sim, para começar com banda, repertório e Modo Tocar. '
            'Trial Pro de 30 dias na primeira banda; estúdios têm trial Premium no primeiro cadastro.</p>'
            '<p><strong>Preciso instalar app?</strong> Funciona no navegador; instale como PWA. '
            'No Modo Tocar a setlist baixa automaticamente; na banda use Disponibilizar offline para o repertório inteiro.</p>'
            '<p><strong>Plano anual?</strong> Em <a href="/assinatura/planos">Planos</a>, use Mensal/Anual para ver o desconto '
            '(equivalente a 10 meses pagos por 12).</p>'
        ),
    }


_COMPARISON_PAGES: dict[str, dict[str, Any]] = {
    'cifra-club': {
        'slug': 'cifra-club',
        'h1': 'SetSync vs Cifra Club — qual usar na banda?',
        'meta_title': 'SetSync vs Cifra Club para bandas',
        'meta_description': (
            'Compare SetSync e Cifra Club: CC para estudo solo; SetSync para repertório '
            'compartilhado, setlists e transposição por cantor.'
        ),
        'sections': [
            {'html': (
                '<p>O <strong>Cifra Club</strong> é a maior biblioteca de cifras do Brasil. O '
                '<strong>SetSync</strong> foca em <strong>banda colaborativa</strong>: versão única da '
                'música, setlist do show e Modo Tocar com a equipe.</p>'
            )},
            {'h2': 'Comparativo', 'html': (
                '<table><thead><tr><th></th><th>Cifra Club</th><th>SetSync</th></tr></thead><tbody>'
                '<tr><td>Público</td><td>Músico solo</td><td>Banda / equipe</td></tr>'
                '<tr><td>Repertório compartilhado</td><td>Listas pessoais</td><td>Por banda</td></tr>'
                '<tr><td>Setlist ao vivo</td><td>Limitado</td><td>Tom por cantor</td></tr>'
                '<tr><td>Modo palco</td><td>Scroll PRO</td><td>Modo Tocar + offline</td></tr>'
                '<tr><td>Várias bandas</td><td>Não</td><td>Worship</td></tr>'
                '</tbody></table>'
            )},
        ],
    },
    'ipraise': {
        'slug': 'ipraise',
        'h1': 'SetSync vs iPraise',
        'meta_title': 'SetSync vs iPraise para bandas',
        'meta_description': 'iPraise para escalas; SetSync para cifras, setlists e Modo Tocar com plano Worship.',
        'sections': [
            {'html': (
                '<p><strong>iPraise</strong> — escalas e chat. <strong>SetSync</strong> — cifras, '
                'setlists e palco, com agenda nos planos pagos.</p>'
            )},
            {'h2': 'Comparativo', 'html': (
                '<table><thead><tr><th></th><th>iPraise</th><th>SetSync</th></tr></thead><tbody>'
                '<tr><td>Escalas</td><td>Forte</td><td>Agenda Pro/Worship</td></tr>'
                '<tr><td>Modo Tocar</td><td>Básico</td><td>Tela cheia + offline</td></tr>'
                '<tr><td>Import Cifra Club</td><td>Não</td><td>Sim</td></tr>'
                '</tbody></table>'
            )},
        ],
    },
}


def get_comparison_page(slug: str) -> dict[str, Any] | None:
    return _COMPARISON_PAGES.get(slug)


def list_comparison_pages() -> list[dict[str, Any]]:
    return list(_COMPARISON_PAGES.values())


def _build_page(verb: str, obj: str) -> dict[str, Any]:
    if verb:
        slug = slugify(f'{verb}-{obj}')
    else:
        slug = slugify(obj)
    phrase = _phrase(verb, obj)
    sections = _sections(verb, obj)
    if slug in _PREMIUM_SLUGS:
        sections = sections + [_premium_faq_block(phrase)]
    plano_cta = 'worship' if any(x in slug for x in ('igreja', 'worship', 'ministerio', 'louvor')) else None
    return {
        'slug': slug,
        'verb': verb,
        'object': obj,
        'phrase': phrase,
        'h1': f'{phrase.capitalize()} com o SetSync',
        'meta_title': _title_page(verb, obj),
        'meta_description': _meta_desc(verb, obj),
        'sections': sections,
        'keywords': phrase,
        'noindex': slug not in _PREMIUM_SLUGS,
        'premium': slug in _PREMIUM_SLUGS,
        'plano_cta': plano_cta,
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
            'q': 'Como gerenciar várias bandas no SetSync?',
            'a': 'No plano Worship, uma conta administra múltiplas bandas — cada uma com repertório e setlists próprios. Para igrejas e ministérios de louvor, veja setsync.com.br/igrejas.',
        },
        {
            'q': 'Qual a diferença entre Pro e Worship?',
            'a': 'O Pro cobre uma banda com integrantes ilimitados. O Worship cobre várias bandas na mesma conta. Músico solo pode usar o plano Individual.',
        },
        {
            'q': 'Posso montar setlist online para show ou ensaio?',
            'a': 'Sim. Arraste as músicas na ordem desejada, defina cantor e tom por faixa, e abra o Modo Tocar no palco ou exporte PDF no plano Pro.',
        },
        {
            'q': 'O SetSync transpor cifras automaticamente?',
            'a': 'Cadastre vocalistas com transposição preferida. Ao montar a setlist, escolha quem canta — a cifra abre no tom certo, com sustenidos e bemóis pela armadura (Eb, Bb etc.), inclusive na grade harmônica.',
        },
        {
            'q': 'Existe app de cifras para banda grátis?',
            'a': 'O SetSync tem plano grátis para começar: repertório, bandas, setlists e Modo Tocar. Planos Individual (solo), Pro (uma banda) e Worship (várias bandas) ampliam recursos.',
        },
        {
            'q': 'Como convidar músicos para a banda?',
            'a': 'Crie a banda no SetSync e envie o link de convite por WhatsApp ou e-mail. Novos membros entram com permissão de membro ou admin.',
        },
        {
            'q': 'O SetSync serve para igrejas e ministérios de louvor?',
            'a': 'Sim. Temos uma página dedicada com plano Worship, comparativos e rotina de culto em setsync.com.br/igrejas.',
        },
        {
            'q': 'Posso usar cifras offline no celular?',
            'a': 'Instale o SetSync como PWA na tela inicial. Na banda, use Disponibilizar offline no repertório; no Modo Tocar, a setlist baixa automaticamente ao abrir — ideal se a internet falhar no culto.',
        },
        {
            'q': 'O que é o Modo Tocar?',
            'a': 'Tela cheia para o palco: cifra legível, seções (S), modo vocalista (P), auto-scroll, metrônomo com count-in, sync entre músicos, offline automático da setlist, notas de palco, pedal Bluetooth e navegação entre músicas da setlist.',
        },
        {
            'q': 'Como sincronizar a banda no palco?',
            'a': 'No Modo Tocar, ligue o botão Sync — todos seguem a música que o líder avança. Ao abrir pelo evento da agenda (Tocar setlist), o sync costuma vir ligado automaticamente.',
        },
        {
            'q': 'Como configurar pedal Bluetooth no SetSync?',
            'a': 'No Modo Tocar, use o ícone de pedal para mapear teclas ou o assistente (varinha) que detecta Page Up/Down e setas. Por padrão, ↑↓ trocam música e Page Up/Down paginam a cifra.',
        },
        {
            'q': 'Posso exportar setlist em PDF?',
            'a': 'No plano Pro, exporte setlists com índice, cifras, letras e grade harmônica — você escolhe quais seções incluir.',
        },
        {
            'q': 'SetSync substitui planilha de cifras?',
            'a': 'Sim, para bandas que precisam de versão única, transposição e setlist. Acaba o problema de "qual arquivo é o certo?" no grupo do WhatsApp.',
        },
        {
            'q': 'Tem grade harmônica além da cifra tradicional?',
            'a': 'Cada música pode ter cifra, grade harmônica e letra. O editor salva automaticamente, permite extrair acordes da cifra, transpor com grafia correta e notas privadas (!) visíveis só para quem escreveu.',
        },
        {
            'q': 'Como organizar ensaios da banda?',
            'a': 'Use a Agenda: marque ensaio ou show, vincule a setlist, escale por função e envie confirmação por link no e-mail ou WhatsApp. Cadastre seus instrumentos no perfil para a equipe ver na escalação. Lembretes automáticos ajudam a equipe a não esquecer.',
        },
        {
            'q': 'O SetSync tem reserva de estúdio de ensaio?',
            'a': 'Sim. Bandas buscam estúdios por cidade, solicitam horário e acompanham em Minhas reservas. Quando confirmado, o ensaio entra na agenda da banda. Donos cadastram salas, QR na recepção, financeiro (receita e despesas), vouchers Premium promocionais e plano Premium (R$ 49/mês) para salas ilimitadas — trial de 30 dias no primeiro cadastro.',
        },
        {
            'q': 'Como funciona o financeiro do estúdio no SetSync?',
            'a': 'No painel do dono, abra Financeiro. O sistema calcula a receita das reservas confirmadas com base no preço/hora e na duração; você marca pagamentos, ajusta valores e registra despesas do mês. O resumo mostra recebido, a receber e líquido.',
        },
        {
            'q': 'Como resgatar voucher Estúdio Premium?',
            'a': 'Com a conta do dono do estúdio, abra Planos, role até Tem um voucher?, digite o código (ex.: ESTUDIO-XXXX) e resgate. O Premium libera salas ilimitadas pelo período do voucher ou vitalício, sem Mercado Pago. Cada código vale uma vez por conta.',
        },
        {
            'q': 'Qual a diferença entre voucher de banda e voucher de estúdio?',
            'a': 'Voucher de banda ativa Pro/Worship na banda escolhida em Planos. Voucher de estúdio ativa Premium na conta do dono da sala de ensaio — não depende de qual banda você selecionou.',
        },
        {
            'q': 'Como funciona o assistente de ajuda do SetSync?',
            'a': 'O ícone de chat no canto da tela responde com base na Ajuda, Guia e FAQ. Se você estiver logado, as respostas podem incluir atalhos para adicionar cifra, cadastrar estúdio ou ver planos.',
        },
        {
            'q': 'Existe plano anual com desconto?',
            'a': 'Sim. Em Planos, alterne Mensal/Anual para Pro, Worship, Individual e Estúdio Premium. O anual equivale a pagar 10 meses e usar 12.',
        },
        {
            'q': 'Como indicar outra banda e ganhar Pro grátis?',
            'a': 'Após montar sua primeira setlist, o painel pode mostrar indicação. Em Planos → Indicar banda, gere um voucher de 15 dias Pro; quando alguém usar, você ganha mais 15 dias na sua banda principal.',
        },
        {
            'q': 'O que é o selo Verificado do estúdio?',
            'a': 'Estúdios com perfil completo — fotos, endereço, disponibilidade e QR de agendamento — exibem o selo na busca. O dono vê visualizações e cliques no painel.',
        },
        {
            'q': 'Posso cadastrar os instrumentos que toco?',
            'a': 'Em Meu perfil, marque um ou mais instrumentos (violão, guitarra, baixo, vocal, bateria, teclado…). A banda vê isso na lista de membros e na escalação de eventos.',
        },
        {
            'q': 'Quantas músicas posso cadastrar?',
            'a': 'O plano grátis tem limites generosos para começar. Planos pagos ampliam repertório, bandas e recursos como PDF e Worship multi-bandas.',
        },
        {
            'q': 'Como funciona a cobrança no SetSync?',
            'a': 'Ao assinar Pro, Worship, Individual ou Estúdio Premium, você é redirecionado ao Mercado Pago. Lá você autoriza a assinatura recorrente — o SetSync não armazena dados do seu cartão. O trial de 30 dias é sem cartão.',
        },
        {
            'q': 'É seguro pagar pelo SetSync?',
            'a': 'O pagamento é processado pelo Mercado Pago, um dos meios mais usados no Brasil. Seus dados de cartão não passam pelos servidores do SetSync — você confirma tudo no site do MP.',
        },
        {
            'q': 'O SetSync é melhor que mandar cifra no WhatsApp?',
            'a': 'Para equipes que ensaiam junto, sim: uma fonte atualizada, tom por cantor, setlist compartilhada e palco no Modo Tocar — sem prints desatualizados.',
        },
    ]
