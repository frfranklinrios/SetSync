"""Seeds de depoimentos e posts do blog (desenvolvimento / primeira instalação)."""

from __future__ import annotations

from datetime import datetime, timedelta
from config import app_now_naive, app_now_str


def seed_testimonials(c) -> None:
    c.execute('SELECT COUNT(*) AS n FROM testimonials')
    if (c.fetchone()['n'] or 0) > 0:
        return
    samples = [
        {
            'nome': 'Rafael Mendes',
            'cidade': 'Campinas, SP',
            'descricao': 'Guitarrista — Banda Ágape',
            'texto': (
                'Antes do SetSync a gente perdia 20 minutos de ensaio só transpondo cifra no papel. '
                'Hoje abrimos o Modo Tocar e cada cantor vê a música no tom certo. Mudou nosso culto.'
            ),
            'foto_url': '',
            'ordem': 1,
        },
        {
            'nome': 'Juliana Costa',
            'cidade': 'Recife, PE',
            'descricao': 'Líder de louvor — Igreja Nova Vida',
            'texto': (
                'Gerencio três ministérios com o plano Worship. Convidei toda a equipe por link e '
                'ninguém mais manda print de cifra desatualizada no grupo do WhatsApp.'
            ),
            'foto_url': '',
            'ordem': 2,
        },
        {
            'nome': 'Marcos Oliveira',
            'cidade': 'Belo Horizonte, MG',
            'descricao': 'Baixista — Banda Independente',
            'texto': (
                'Uso no bar e na igreja. O app funciona offline no palco e o setlist em PDF '
                'salvou nosso ensaio de quinta. Vale cada centavo do Pro.'
            ),
            'foto_url': '',
            'ordem': 3,
        },
    ]
    for s in samples:
        c.execute(
            '''INSERT INTO testimonials (nome, cidade, descricao, texto, foto_url, ativo, ordem)
               VALUES (?, ?, ?, ?, ?, 1, ?)''',
            (s['nome'], s['cidade'], s['descricao'], s['texto'], s['foto_url'], s['ordem']),
        )


def _blog_posts_data() -> list[dict]:
    base_date = app_now_naive() - timedelta(days=30)
    posts = [
        {
            'slug': 'como-transpor-cifra-para-qualquer-tom',
            'titulo': 'Como transpor cifra para qualquer tom — guia completo para guitarristas',
            'resumo': 'Aprenda a transpor cifras na prática: intervalos, capotraste, tom do cantor e ferramentas digitais.',
            'autor': 'Equipe SetSync',
            'tags': 'cifras, transposição, guitarra, teoria musical',
            'meta_title': 'Como transpor cifra — guia para guitarristas',
            'meta_description': 'Guia prático de transposição de cifras: entenda intervalos, use capotraste e ferramentas como o SetSync.',
            'conteudo': _POST_TRANSPOSE,
        },
        {
            'slug': 'montar-setlist-culto-gospel-5-passos',
            'titulo': 'Como montar um setlist para culto gospel em 5 passos',
            'resumo': 'Do repertório ao palco: fluxo, tom por cantor, ordem das músicas e link compartilhado com a equipe.',
            'autor': 'Equipe SetSync',
            'tags': 'setlist, culto, louvor, igreja',
            'meta_title': 'Setlist para culto gospel em 5 passos',
            'meta_description': 'Monte setlists de culto gospel com ordem, tom por vocalista e compartilhamento com a banda.',
            'conteudo': _POST_SETLIST,
        },
        {
            'slug': 'melhores-apps-cifras-banda-2026',
            'titulo': 'Os melhores aplicativos de cifras para banda em 2026',
            'resumo': 'Comparativo honesto entre apps de cifra: o que funciona para banda, igreja e ensaio ao vivo.',
            'autor': 'Equipe SetSync',
            'tags': 'apps, cifras, comparativo, banda',
            'meta_title': 'Melhores apps de cifras para banda 2026',
            'meta_description': 'Comparativo dos melhores apps de cifras para bandas e ministérios de louvor em 2026.',
            'conteudo': _POST_APPS,
        },
        {
            'slug': 'organizar-ministerio-louvor-igreja',
            'titulo': 'Como organizar o ministério de louvor da sua igreja',
            'resumo': 'Estrutura, repertório compartilhado, ensaios produtivos e ferramentas que reduzem retrabalho.',
            'autor': 'Equipe SetSync',
            'tags': 'ministério, louvor, igreja, organização',
            'meta_title': 'Organizar ministério de louvor na igreja',
            'meta_description': 'Dicas práticas para organizar o ministério de louvor: repertório, ensaios e ferramentas digitais.',
            'conteudo': _POST_MINISTERIO,
        },
        {
            'slug': 'diferenca-tom-escala-musica',
            'titulo': 'Diferença entre tom e escala: o que todo músico precisa saber',
            'resumo': 'Tom, tonalidade e escala explicados sem jargão — essencial para transpor e comunicar com a banda.',
            'autor': 'Equipe SetSync',
            'tags': 'teoria musical, tom, escala, transposição',
            'meta_title': 'Tom vs escala — guia para músicos',
            'meta_description': 'Entenda a diferença entre tom e escala e como isso afeta cifras, setlists e ensaios.',
            'conteudo': _POST_TOM_ESCALA,
        },
        {
            'slug': 'compartilhar-cifras-com-a-banda',
            'titulo': 'Como compartilhar cifras com a banda sem perder a versão certa',
            'resumo': 'Pare de mandar print no WhatsApp: repertório único, convites por link, setlist sincronizada e letras públicas para a equipe.',
            'autor': 'Equipe SetSync',
            'tags': 'compartilhar cifras, banda, repertório, setlist',
            'meta_title': 'Compartilhar cifras com a banda — guia SetSync',
            'meta_description': 'Aprenda a compartilhar cifras com sua banda: repertório centralizado, convites, setlists e link público de letras.',
            'conteudo': _POST_COMPARTILHAR_CIFRAS,
        },
        {
            'slug': 'gerenciar-bandas-ministerio-louvor',
            'titulo': 'Como gerenciar bandas e ministérios de louvor no mesmo lugar',
            'resumo': 'Convites, permissões, várias bandas na conta Worship e agenda com escalação — sem planilha perdida.',
            'autor': 'Equipe SetSync',
            'tags': 'gerenciar bandas, ministério, louvor, igreja',
            'meta_title': 'Gerenciar bandas de louvor — SetSync',
            'meta_description': 'Guia para gerenciar bandas: convidar músicos, organizar repertório, setlists e múltiplos ministérios na igreja.',
            'conteudo': _POST_GERENCIAR_BANDAS,
        },
        {
            'slug': 'como-funciona-chord-sheet-setsync',
            'titulo': 'Como funciona o Chord Sheet no SetSync',
            'resumo': 'Progressão harmônica em grade, editor com prévia ao vivo, salvamento automático, notação brasileira e uso no Modo Tocar — guia completo.',
            'autor': 'Equipe SetSync',
            'tags': 'chord sheet, acordes, progressão harmônica, editor, modo tocar',
            'meta_title': 'Chord Sheet no SetSync — guia do editor',
            'meta_description': 'Aprenda a montar chord sheets no SetSync: compassos, semi-pulsos, simile, transposição, autosave e visualização no palco.',
            'conteudo': _POST_CHORDSHEET,
        },
        {
            'slug': 'como-cadastrar-estudio-ensino-setsync',
            'titulo': 'Como cadastrar seu estúdio de ensaio no SetSync',
            'resumo': 'Passo a passo para donos de sala: perfil, fotos, salas, Google Maps, disponibilidade e confirmação de reservas.',
            'autor': 'Equipe SetSync',
            'tags': 'estúdio, ensaio, cadastro, reservas',
            'meta_title': 'Cadastrar estúdio no SetSync — tutorial',
            'meta_description': 'Aprenda a cadastrar seu estúdio de ensaio no SetSync: salas, horários, bloqueios e painel de reservas beta gratuito.',
            'conteudo': _POST_ESTUDIO_CADASTRO,
        },
        {
            'slug': 'como-reservar-sala-ensaio-banda-setsync',
            'titulo': 'Como reservar sala de ensaio para sua banda',
            'resumo': 'Busque estúdios por cidade, escolha horário, acompanhe a solicitação e veja o ensaio na agenda quando confirmado.',
            'autor': 'Equipe SetSync',
            'tags': 'estúdio, reserva, banda, ensaio',
            'meta_title': 'Reservar sala de ensaio — tutorial SetSync',
            'meta_description': 'Tutorial para bandas reservarem sala de ensaio no SetSync: busca, solicitação, status e agenda sincronizada.',
            'conteudo': _POST_ESTUDIO_RESERVA,
        },
        {
            'slug': 'como-cadastrar-instrumentos-perfil-setsync',
            'titulo': 'Como cadastrar seus instrumentos no perfil',
            'resumo': 'Marque violão, guitarra, baixo, vocal, bateria e mais — a banda vê na escalação e na lista de membros.',
            'autor': 'Equipe SetSync',
            'tags': 'perfil, instrumentos, escalação, banda',
            'meta_title': 'Instrumentos no perfil — tutorial SetSync',
            'meta_description': 'Cadastre os instrumentos que você toca no SetSync e ajude a banda a montar a escalação sem adivinhar funções.',
            'conteudo': _POST_INSTRUMENTOS,
        },
        {
            'slug': 'como-usar-agenda-escalacao-setsync',
            'titulo': 'Como usar a agenda e escalação no SetSync',
            'resumo': 'Crie ensaios e shows, vincule setlist, escale integrantes, confirme por link e receba lembretes automáticos.',
            'autor': 'Equipe SetSync',
            'tags': 'agenda, escalação, ensaio, show',
            'meta_title': 'Agenda e escalação — tutorial SetSync',
            'meta_description': 'Tutorial completo da agenda SetSync: eventos, escalação com confirmação, formações e lembretes.',
            'conteudo': _POST_AGENDA,
        },
        {
            'slug': 'como-usar-modo-tocar-setsync',
            'titulo': 'Como usar o Modo Tocar no palco',
            'resumo': 'Tela cheia, seções, sync da banda, offline auto, pedal, notas de palco, vocalista e atalhos.',
            'autor': 'Equipe SetSync',
            'tags': 'modo tocar, palco, cifras, setlist, pedal, offline',
            'meta_title': 'Modo Tocar — tutorial SetSync',
            'meta_description': 'Modo Tocar no SetSync: seções, sync, offline automático, pedal Bluetooth, notas de palco e atalhos para o culto.',
            'conteudo': _POST_MODO_TOCAR,
        },
        {
            'slug': 'como-usar-notificacoes-setsync',
            'titulo': 'Como configurar notificações, push e WhatsApp',
            'resumo': 'Alertas imediatos de escalação, resumo diário às 21h, lembretes de agenda e preferências por tipo.',
            'autor': 'Equipe SetSync',
            'tags': 'notificações, whatsapp, push, alertas',
            'meta_title': 'Notificações SetSync — tutorial',
            'meta_description': 'Configure push, e-mail e WhatsApp no SetSync: escalação, convites, estúdio e resumo diário.',
            'conteudo': _POST_NOTIFICACOES,
        },
        {
            'slug': 'como-usar-versao-pessoal-cifras-setsync',
            'titulo': 'Como usar a versão pessoal de cifras',
            'resumo': 'Edite sem alterar a banda na hora, teste no Modo Tocar e publique quando a equipe aprovar.',
            'autor': 'Equipe SetSync',
            'tags': 'versão pessoal, cifras, editor, banda',
            'meta_title': 'Versão pessoal de cifras — tutorial SetSync',
            'meta_description': 'Tutorial da versão pessoal: editar cifras em privado, alternar Banda/Minha e publicar para a equipe.',
            'conteudo': _POST_VERSAO_PESSOAL,
        },
    ]
    for i, p in enumerate(posts):
        p['publicado'] = True
        p['publicado_em'] = (base_date + timedelta(days=i * 5)).strftime('%Y-%m-%d %H:%M:%S')
    return posts


# Posts cujo conteúdo no seed deve sobrescrever o banco (tutoriais atualizados)
_REFRESH_CONTENT_SLUGS = frozenset({'como-usar-modo-tocar-setsync'})


def seed_blog_posts(c) -> None:
    """Insere posts iniciais; em deploys seguintes só adiciona slugs novos."""
    for p in _blog_posts_data():
        c.execute('SELECT id FROM blog_posts WHERE slug = ?', (p['slug'],))
        row = c.fetchone()
        if row:
            if p['slug'] not in _REFRESH_CONTENT_SLUGS:
                continue
            c.execute(
                '''UPDATE blog_posts SET titulo=?, resumo=?, conteudo=?, meta_title=?,
                   meta_description=?, tags=?, atualizado_em=? WHERE slug=?''',
                (
                    p['titulo'], p['resumo'], p['conteudo'],
                    p['meta_title'], p['meta_description'], p['tags'],
                    p['publicado_em'], p['slug'],
                ),
            )
            continue
        c.execute(
            '''INSERT INTO blog_posts
               (slug, titulo, resumo, conteudo, autor, publicado, publicado_em,
                atualizado_em, meta_title, meta_description, imagem_capa, tags)
               VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)''',
            (
                p['slug'], p['titulo'], p['resumo'], p['conteudo'], p['autor'],
                p['publicado_em'], p['publicado_em'],
                p['meta_title'], p['meta_description'], '', p['tags'],
            ),
        )


_POST_TRANSPOSE = """
<h2>Por que transpor é tão comum no palco?</h2>
<p>Toda banda de igreja ou bar já passou pela cena: a cifra está em G, mas a cantora canta confortável em A. Transpor não é luxo — é necessidade. Guitarristas, tecladistas e até baixistas precisam entender o processo para não travar o ensaio.</p>
<p>A transposição move todos os acordes mantendo a mesma relação harmônica. Se você sobe dois semitons, cada acorde sobe dois semitons. Simples na teoria; na prática exige agilidade ou uma ferramenta confiável.</p>
<h2>Intervalos e semitons</h2>
<p>O segredo está nos semitons. De C para D são dois semitons (C → C# → D). Memorize a ordem cromática: C, C#, D, D#, E, F, F#, G, G#, A, A#, B. Com isso você transponde mentalmente acordes com sustenidos e bemóis.</p>
<p>Acordes com baixo — como D/F# — também sobem integralmente: em E vira E/G#. Não esqueça extensões (m7, sus4, add9); elas permanecem iguais, só muda a raiz.</p>
<h2>Capotraste: atalho físico</h2>
<p>O capo desloca a sonoridade sem reescrever a cifra. Capo na 2ª casa com forma de G soa em A. Útil quando a progressão usa pestanas abertas. Limite: nem toda música aceita capo sem mudar timbre ou dificuldade de solo.</p>
<h2>Tom do cantor no SetSync</h2>
<p>No SetSync você cadastra cantores e define transposição por vocalista. Ao montar o setlist, escolhe quem canta e a cifra abre no tom certo — inclusive no Modo Tocar, tela cheia com auto-scroll. Acaba o caderno rabiscado e o "espera, deixa eu transpor".</p>
<h2>Checklist rápido antes do culto</h2>
<ul>
<li>Confirme o tom de cada música com quem vai cantar.</li>
<li>Revise acordes com baixo alternativo (slash chords).</li>
<li>Teste no Modo Tocar com fonte legível à distância.</li>
<li>Compartilhe o setlist com a banda para todos verem a mesma versão.</li>
</ul>
<p>Transpor bem é habilidade + processo. Domine os intervalos, use capo quando fizer sentido e deixe a tecnologia cuidar do repetitivo — você foca na música.</p>
"""

_POST_SETLIST = """
<h2>Passo 1: Defina o fluxo do culto</h2>
<p>Antes de escolher músicas, alinhe com a liderança o fluxo: quantas canções de adoração, transição para palavra, encerramento. O setlist não é só uma lista — é roteiro emocional e litúrgico.</p>
<h2>Passo 2: Selecione do repertório da banda</h2>
<p>Use o repertório centralizado no SetSync. Evite músicas que a equipe não ensaiou há meses. Marque tom original e confirme se há versão atualizada da cifra.</p>
<h2>Passo 3: Tom por cantor</h2>
<p>Para cada faixa, defina quem canta. No SetSync, o tom do vocalista aplica transposição automática. Isso evita surpresas quando a cantora de turno não é quem ensaiou na semana passada.</p>
<h2>Passo 4: Ordene e teste transições</h2>
<p>Arraste as músicas na ordem do culto. Pense em tonalidades vizinhas para transições suaves (ex.: de G para D). Faça um ensaio seco só navegando entre as músicas no app.</p>
<h2>Passo 5: Compartilhe com a equipe</h2>
<p>Ative o link público ou garanta que todos os membros acessem a banda no SetSync. No culto, abra o Modo Tocar — auto-scroll, tela cheia, tema escuro se o ambiente for escuro.</p>
<p>Com esses cinco passos você reduz improviso de última hora e entrega um culto mais fluido. O setlist vira documento vivo: atualize após cada culto com o que funcionou.</p>
"""

_POST_APPS = """
<h2>O que uma banda realmente precisa?</h2>
<p>Apps de cifra abundam, mas poucos resolvem o problema da <strong>banda</strong>: repertório compartilhado, setlist com tom por cantor, modo palco e convites à equipe. Avalie sempre esses critérios antes de adotar.</p>
<h2>Cifra Club e similares</h2>
<p>Excelentes para consulta individual e descoberta de músicas. Para banda, falta gestão de repertório próprio, setlists sincronizados e controle de permissões. Muitas equipes ainda exportam print ou PDF manualmente.</p>
<h2>Planilhas e PDFs</h2>
<p>Funcionam até certo ponto. Quebram quando alguém edita a cifra e esquece de avisar, ou quando o cantor muda e ninguém transõe a tempo. Não há Modo Tocar nativo nem transposição automática por vocalista.</p>
<h2>SetSync em 2026</h2>
<p>Feito para bandas e igrejas brasileiras: plano grátis generoso, Pro por banda, Worship para múltiplos ministérios. Destaques: transposição por cantor, setlists, Modo Tocar com auto-scroll, PDF no Pro, PWA offline e convites por link.</p>
<h2>Como escolher</h2>
<ul>
<li>Teste com sua equipe real, não só você.</li>
<li>Verifique offline no templo ou palco.</li>
<li>Compare limites do plano grátis vs. custo do Pro.</li>
<li>Prefira ferramentas que centralizem cifra + setlist + equipe.</li>
</ul>
<p>Não existe app perfeito para tudo. Para <em>banda ensaiando e tocando junto</em>, priorize sincronização e palco — não só biblioteca de cifras.</p>
"""

_POST_MINISTERIO = """
<h2>Estrutura clara de liderança</h2>
<p>Defina quem decide repertório, quem agenda ensaios e quem cuida da comunicação com a igreja. Ministérios confusos geram cifras duplicadas e integrantes desmotivados.</p>
<h2>Repertório único e atualizado</h2>
<p>Centralize músicas aprovadas. No SetSync, cada ministério pode ser uma banda; no plano Worship, várias bandas na mesma conta. Admins editam; membros tocam. Acabou a pasta "Cifras Final FINAL2".</p>
<h2>Ensaios com pauta</h2>
<p>Chegue com setlist pronto, tom confirmado e link enviado antes. Use os primeiros minutos para passar o Modo Tocar com todos — especialmente novos integrantes.</p>
<h2>Onboarding de voluntários</h2>
<p>Convite por link, nome de exibição, papel (admin ou membro). Documente tom padrão de cada cantor fixo. Quem entra no meio do mês não deve depender de PDF antigo.</p>
<h2>Métricas simples</h2>
<p>Quantas músicas no repertório, quantos ensaios por mês, feedback pós-culto em duas perguntas. Ferramentas como SetSync mostram crescimento do acervo e facilitam upgrade quando o plano grátis aperta.</p>
<p>Organizar louvor é servir pessoas, não só notas. Processos leves liberam tempo para pastorear músicos e adorar com excelência.</p>
"""

_POST_TOM_ESCALA = """
<h2>O que é tom (tonalidade)?</h2>
<p>Tom é o "centro" harmônico da música — a sensação de repouso. Quando dizemos "música em D", normalmente a tonica é D e a escala major de D organiza a maioria dos acordes. Cantores falam "meu tom é A" referindo-se ao tom que cabe na voz.</p>
<h2>O que é escala?</h2>
<p>Escala é a sequência de notas disponíveis (ex.: D major = D E F# G A B C#). Acordes diatônicos vêm dessa escala. Confundir tom com escala gera erro: "escala de D" pode ser major, minor, modes — o contexto importa.</p>
<h2>Na prática da cifra</h2>
<p>A cifra lista acordes; o tom indica a referência. Transpor muda o tom mantendo funções (I, IV, V). Se a cantora precisa cantar mais agudo, sobe-se o tom inteiro — não misture acordes de tons diferentes.</p>
<h2>Comunicação na banda</h2>
<p>Use linguagem comum: "tom G, cantora Juliana" em vez de "tenta um tom mais alto". No SetSync, cadastre vocalistas e deixe explícito na setlist quem canta cada faixa.</p>
<h2>Erros comuns</h2>
<ul>
<li>Achar que tom e escala menor/major são sempre a mesma coisa (relative minor confunde).</li>
<li>Transpor só alguns acordes.</li>
<li>Ignorar modulação no meio da música.</li>
</ul>
<p>Entender tom vs. escala acelera ensaios e evita friction entre teoria e palco. Estude o básico e automatize o resto com ferramentas que respeitam o tom de cada cantor.</p>
"""

_POST_COMPARTILHAR_CIFRAS = """
<h2>O problema do print no WhatsApp</h2>
<p>Toda banda já viveu isso: alguém manda a cifra errada, uma versão antiga ou um tom que não combina com o cantor do culto. Compartilhar cifras de verdade exige <strong>uma fonte única</strong> que todos confiem.</p>
<h2>Repertório centralizado no SetSync</h2>
<p>Cadastre cada música uma vez. Admins editam; membros da banda só tocam a versão aprovada. Cifra, letra e chord sheet ficam na mesma ficha — sem pastas "final_v3".</p>
<h2>Convite por link</h2>
<p>Crie a banda e envie o link de convite por WhatsApp ou e-mail. Guitarristas, tecladistas, bateristas e vocalistas entram na mesma equipe com permissões claras.</p>
<h2>Setlist + tom por cantor</h2>
<p>Ao montar o culto, escolha quem canta cada música. A transposição abre automaticamente no tom certo — inclusive no Modo Tocar, tela cheia no palco.</p>
<h2>Link público de letras</h2>
<p>Para quem não precisa ver acordes (projeção ou equipe de apoio), use o link público de letras da setlist sem expor o repertório inteiro da banda.</p>
<p>Compartilhar cifras bem é menos sobre tecnologia e mais sobre processo. O SetSync elimina o retrabalho para você focar no ensaio.</p>
"""

_POST_GERENCIAR_BANDAS = """
<h2>Mais de uma equipe, um só lugar</h2>
<p>Igrejas com louvor de domingo, jovens e vigília costumam espalhar cifras em grupos diferentes. Gerenciar bandas com clareza evita confusão de versões e integrantes perdidos.</p>
<h2>Plano Worship: várias bandas na conta</h2>
<p>Uma assinatura Worship cobre múltiplos ministérios. Cada banda tem repertório, setlists e convites próprios — sem misturar músicas entre equipes.</p>
<h2>Permissões: admin e membro</h2>
<p>Admins cadastram músicas, montam setlists e convidam pessoas. Membros consultam e tocam. Ideal para rotatividade de voluntários que entram e saem ao longo do ano.</p>
<h2>Agenda e escalação</h2>
<p>Marque ensaios e cultos, vincule a setlist do evento e escale quem participa. Lembretes por e-mail e WhatsApp reduzem faltas de última hora.</p>
<h2>Métricas do ministério</h2>
<p>Veja quantas músicas há no acervo, quantos setlists foram montados e quando a equipe ensaiou. Dados simples para liderança pastoral e musical.</p>
<p>Gerenciar bandas de louvor não precisa ser planilha infinita. Centralize repertório, pessoas e agenda — e deixe o grupo do WhatsApp só para comunicação rápida.</p>
"""

_POST_CHORDSHEET = """
<h2>O que é o Chord Sheet?</h2>
<p>Além da <strong>cifra com letra</strong>, cada música no SetSync pode ter um <strong>Chord Sheet</strong>: uma folha só com <strong>acordes e compassos</strong>, sem letra — ideal para tecladista, guitarrista e direção musical enxergarem a progressão de relance.</p>
<p>O formato é compatível com o <a href="https://www.chordsheet.com/manual/" target="_blank" rel="noopener">Chord Sheet Maker</a> (chordsheet.com): grade com barras verticais, seções, simile, repetições e navegação (D.C., coda, voltas). O padrão do SetSync é <strong>4 compassos por linha</strong>, ajustável de 1 a 8.</p>

<h2>Onde encontrar no app</h2>
<ul>
<li><strong>Visualizar música</strong> — abas <strong>Cifra</strong>, <strong>Chord Sheet</strong> e <strong>Letra</strong> (quando existirem).</li>
<li><strong>Editar</strong> — aba <strong>Chord Sheet</strong> (papel <strong>Editor</strong>, admin ou titular da banda).</li>
<li><strong>Modo Tocar</strong> — alterne com o menu ou a tecla <strong>G</strong> entre cifra, chord sheet e letra.</li>
<li><strong>PDF da setlist</strong> (planos Pro/Worship) — inclua chord sheets por música na exportação.</li>
</ul>
<p>O chord sheet usa a <strong>mesma transposição</strong> da cifra: tom do cantor na setlist, botões de tom no palco e sustenidos/bemóis corretos para a tonalidade (ex.: C → Eb gera Eb, Ab, Bb).</p>

<h2>O editor: texto à esquerda, folha à direita</h2>
<p>Ao abrir <strong>Editar → Chord Sheet</strong>, você vê duas áreas:</p>
<ul>
<li><strong>Texto-fonte</strong> — onde você digita a progressão em linhas (como um “código” simples).</li>
<li><strong>Prévia ao vivo</strong> — a folha renderizada atualiza enquanto você escreve.</li>
</ul>
<p>Título, artista, tom e BPM ficam no topo da página de edição da música — <strong>uma vez só</strong> para cifra e chord sheet.</p>
<p>Recursos do editor:</p>
<ul>
<li><strong>Salvamento automático</strong> no servidor alguns segundos após cada alteração (status: <em>Salvo</em>, <em>Salvando…</em> ou <em>Alterações pendentes</em>).</li>
<li><strong>Desfazer alterações</strong> — volta ao último estado salvo no servidor.</li>
<li><strong>Rascunho local</strong> — se fechar a aba antes de salvar, o navegador pode restaurar na próxima abertura.</li>
<li>Menu <strong>Exemplos</strong> — modelos prontos (simile, seções, semi-pulsos, navegação).</li>
<li>Botões <strong>♭ −1</strong> e <strong>♯ +1</strong> — transpoem o texto-fonte com grafia correta.</li>
<li><strong>Enter</strong> no texto-fonte inicia uma nova linha na folha, mesmo com menos de 4 compassos na linha anterior.</li>
</ul>

<h2>A regra mais importante: espaço, underscore e ampersand</h2>
<p>No texto-fonte, três símbolos mudam tudo. Memorize esta tabela:</p>
<ul>
<li><strong>Espaço</strong> entre acordes → cada um em um <strong>compasso</strong> diferente.<br>
Ex.: <code>C Am F G</code> = quatro compassos.</li>
<li><strong>Underscore <code>_</code></strong> → vários <strong>pulsos</strong> no <em>mesmo</em> compasso.<br>
Ex.: <code>C_Am</code> em 4/4 → compasso com C no 1º tempo e Am no 2º.</li>
<li><strong>Ampersand <code>&amp;</code></strong> → dois acordes no <strong>mesmo tempo</strong> (semi-pulso).<br>
Ex.: <code>C&amp;D</code> → dois acordes dividindo o primeiro pulso.</li>
</ul>
<p>Na prévia, um compasso em 4/4 mostra sempre <strong>todos os pulsos</strong>. Se você escreve só <code>C</code>, a folha exibe <code>C . . .</code> — o acorde no primeiro tempo e pontos nos demais.</p>
<p>Compasso vazio: token <code>*</code> sozinho. Pulso vazio dentro do compasso: <code>*</code> entre acordes, como em <code>C_*_D</code>.</p>

<h2>Seções, simile e repetições</h2>
<ul>
<li><code>= Refrão</code> — seção com barra dupla; <code>: Intro</code> — rótulo sem barra dupla.</li>
<li><code>- Verso: texto…</code> — rótulo visível para toda a banda acima da pauta.</li>
<li><code># comentário</code> — ignorado na folha (só para quem edita).</li>
<li><code>! nota privada</code> — só você vê (lembrete pessoal no ensaio).</li>
<li><code>%</code> — repete o compasso anterior; <code>%%</code> os dois anteriores; <code>%2</code>…<code>%4</code> para N compassos.</li>
<li><code>|: C Am F G :|</code> — ritornello com repetição.</li>
<li><code>(A B C D)x2</code> — grupo repetido sem duplicar compassos no texto.</li>
<li><code>+</code> ou <code>+ Verso 2</code> — quebra de página na impressão.</li>
</ul>
<p>Linhas de navegação (<code>D.C.</code>, <code>D.S. al coda</code>, <code>fine</code>, etc.) ficam sozinhas em uma linha, como no padrão chordsheet.com.</p>

<h2>Notação e layout</h2>
<p>Em <strong>Preferências de layout → Notação</strong>, escolha o estilo da banda:</p>
<ul>
<li><strong>Brasil</strong> (padrão) — <code>C7+</code>, <code>G°</code>, <code>Cm7b5</code>, fonte monoespaçada.</li>
<li><strong>Internacional</strong> — jazz: <code>CΔ7</code>, <code>Cø7</code>, símbolos musicais.</li>
<li><strong>Americana</strong> — <code>Cmaj7</code>, <code>Gdim</code>, convenção dos EUA.</li>
</ul>
<p>Você também ajusta <strong>compassos por linha</strong>, tamanho da fonte, espaçamento, alinhamento dos acordes e <strong>estilo de barra</strong> (Tab — padrão SetSync — ou Regular, mais próximo do PDF clássico do chordsheet.com).</p>

<h2>No palco e na setlist</h2>
<p>Na visualização da música ou no <strong>Modo Tocar</strong>, pressione <strong>G</strong> para alternar cifra → chord sheet → letra. O tema claro ou escuro do app se aplica à folha (tecla <strong>T</strong> no Modo Tocar).</p>
<p>Se a prévia do palco parecer desatualizada logo após editar, force atualização com <strong>Ctrl+Shift+R</strong> — o Modo Tocar pode guardar cache do HTML renderizado.</p>

<h2>Fluxo sugerido para a banda</h2>
<ol>
<li>Cadastre a música e a cifra com letra (ou importe de um site de cifras).</li>
<li>Abra <strong>Chord Sheet</strong> e monte a progressão — comece pelo menu <strong>Exemplos</strong> se for a primeira vez.</li>
<li>Defina seções (<code>= Refrão</code>) e simile onde a música repete.</li>
<li>Na setlist, escolha cantor e tom; confira o chord sheet transposto antes do show.</li>
<li>No evento, abra o Modo Tocar e use <strong>G</strong> para a vista que cada músico preferir.</li>
</ol>
<p>O Chord Sheet não substitui a cifra com letra — <strong>complementa</strong>. Quem canta usa a cifra; quem conduz harmonia usa a grade. Tudo na mesma música, sincronizado com a banda.</p>
<p>Quer o passo a passo técnico completo? Veja a <a href="/ajuda#chord-sheet">central de ajuda do SetSync</a> ou crie uma conta grátis e teste em uma música da sua banda.</p>
"""

_POST_ESTUDIO_CADASTRO = """
<h2>Para quem é</h2>
<p>Se você tem <strong>sala de ensaio</strong> e quer receber bandas sem depender só de telefone e Instagram, o módulo <strong>Estúdios</strong> do SetSync centraliza cadastro, agenda e confirmações. O plano <strong>beta é gratuito</strong> com até <strong>2 salas</strong>.</p>

<h2>Passo 1: criar conta e cadastrar o estúdio</h2>
<ol>
<li>Crie sua conta no SetSync (e-mail ou Google).</li>
<li>No menu, acesse <strong>Estúdios → Cadastrar meu estúdio</strong>.</li>
<li>Preencha nome, descrição, cidade e bairro.</li>
<li>No campo de endereço, use a <strong>busca do Google Maps</strong> para preencher rua e coordenadas automaticamente.</li>
<li>Envie <strong>fotos</strong> do espaço — ajudam bandas a escolher sua sala.</li>
</ol>

<h2>Passo 2: cadastrar salas</h2>
<p>Cada sala pode ter nome, capacidade e lista de <strong>equipamentos</strong> (PA, bateria, amplis). No plano beta gratuito você cadastra até <strong>duas salas</strong>; precisando de mais, fale com a equipe SetSync sobre o plano premium.</p>

<h2>Passo 3: disponibilidade e bloqueios</h2>
<ul>
<li>Defina <strong>horários semanais</strong> em que cada sala aceita reserva (ex.: seg–sex 14h–22h).</li>
<li>Marque <strong>bloqueios</strong> pontuais — feriados, manutenção ou horário já fechado com outro cliente.</li>
</ul>

<h2>Passo 4: painel e confirmações</h2>
<p>Contas de estúdio abrem no <strong>painel do dono</strong> após o login. Lá você vê solicitações <strong>pendentes</strong> e pode <strong>confirmar</strong> ou <strong>recusar</strong>. Ao confirmar, o ensaio entra na <strong>agenda da banda</strong> automaticamente.</p>

<h2>Dicas</h2>
<ul>
<li>Mantenha fotos e equipamentos atualizados — bandas comparam estúdios antes de reservar.</li>
<li>Responda pedidos em até 24h para não perder o horário para concorrentes.</li>
<li>Ative notificações no perfil para receber aviso de nova solicitação.</li>
</ul>
<p>Mais detalhes na <a href="/ajuda#estudios">ajuda de estúdios</a> ou <a href="/estudios/buscar">veja como as bandas encontram você</a>.</p>
"""

_POST_ESTUDIO_RESERVA = """
<h2>Quando usar</h2>
<p>Sua banda já organiza cifras e setlists no SetSync — agora dá para <strong>reservar sala de ensaio</strong> no mesmo app, sem ligar para dez estúdios diferentes.</p>

<h2>Passo 1: buscar estúdio</h2>
<ol>
<li>Menu <strong>Estúdios → Buscar</strong>.</li>
<li>Informe <strong>cidade</strong> e, se quiser, <strong>bairro</strong>.</li>
<li>Abra o perfil do estúdio: fotos, equipamentos e link para <strong>Google Maps</strong>.</li>
</ol>

<h2>Passo 2: solicitar horário</h2>
<ol>
<li>Escolha a <strong>sala</strong> e toque em <strong>Reservar</strong>.</li>
<li>Selecione <strong>data</strong>, <strong>horário</strong> e a <strong>banda</strong> que vai ensaiar.</li>
<li>Envie a solicitação — o status fica <strong>pendente</strong> até o estúdio responder.</li>
</ol>

<h2>Passo 3: acompanhar e ensaiar</h2>
<ul>
<li>Em <strong>Minhas reservas</strong> você vê pendente, confirmado ou recusado.</li>
<li>Se <strong>confirmado</strong>, o evento aparece na <strong>Agenda da banda</strong> com badge <em>via Estúdio</em>.</li>
<li>Você pode <strong>cancelar</strong> antes do horário, se os planos mudarem.</li>
</ul>

<h2>Integração com a rotina da banda</h2>
<p>Depois de confirmado, vincule a <strong>setlist</strong> do ensaio no evento e use <strong>Tocar setlist</strong> na página do evento para ir direto ao Modo Tocar.</p>
<p>Tutorial completo em <a href="/ajuda#estudios">/ajuda#estudios</a>.</p>
"""

_POST_INSTRUMENTOS = """
<h2>Por que cadastrar</h2>
<p>Na escalação de um show, o admin precisa saber quem é guitarrista, quem é baterista, quem toca teclado. Em vez de perguntar no grupo toda vez, cada músico deixa isso claro no <strong>perfil</strong>.</p>

<h2>Como cadastrar</h2>
<ol>
<li>Abra <strong>Meu perfil</strong> no menu do usuário.</li>
<li>Na seção <strong>Instrumentos</strong>, marque tudo que você toca.</li>
<li>Opções incluem violão, guitarra, baixo, vocal, bateria, teclado/piano, ukulele, cavaquinho, som e mais.</li>
<li>Toque em <strong>Salvar instrumentos</strong>.</li>
</ol>

<h2>Onde a banda vê</h2>
<ul>
<li><strong>Membros</strong> da banda — lista com e-mail e instrumentos de cada integrante.</li>
<li><strong>Escalação</strong> do evento — abaixo do nome, antes de definir a função naquele show.</li>
</ul>
<p>Os instrumentos do perfil são <strong>informativos</strong>; na escalação você ainda pode definir a função específica daquele evento (ex.: guitarra base vs. solo).</p>

<h2>Combine com indisponibilidade</h2>
<p>No mesmo perfil, marque <strong>datas em que você não pode tocar</strong>. Quem escala vê o aviso ao montar o evento.</p>
<p>Veja também <a href="/ajuda#perfil">ajuda do perfil</a> e <a href="/ajuda#agenda">escalação na agenda</a>.</p>
"""

_POST_AGENDA = """
<h2>Visão geral</h2>
<p>Cada banda tem uma <strong>Agenda</strong> para ensaios e shows. Você cria eventos, vincula setlist, escala quem participa e envia confirmação por link.</p>

<h2>Criar um evento</h2>
<ol>
<li>Abra a banda → aba <strong>Agenda</strong> → <strong>Novo evento</strong>.</li>
<li>Informe título, tipo (ensaio ou show), data/hora e local.</li>
<li>Use a busca de <strong>Google Maps</strong> no campo local quando disponível.</li>
<li>Vincule a <strong>setlist</strong> do ensaio ou show, se já existir.</li>
</ol>

<h2>Escalar a equipe</h2>
<ol>
<li>No evento, abra <strong>Escalação</strong>.</li>
<li>Marque integrantes e opcionalmente a <strong>função</strong> (Vocal, Bateria…).</li>
<li>Use <strong>formações salvas</strong> ou <strong>Sugerir escala</strong> para preencher mais rápido.</li>
<li>Salve — quem foi escalado recebe notificação com link para <strong>confirmar ou recusar</strong>.</li>
</ol>

<h2>Confirmação e lembretes</h2>
<ul>
<li>Status: pendente, confirmado ou recusado.</li>
<li>O dashboard mostra <strong>escalações pendentes</strong> da banda.</li>
<li><strong>24 horas antes</strong>, lembrete por push, e-mail e WhatsApp (se configurado).</li>
<li>Horários seguem o fuso de <strong>Fortaleza (UTC−3)</strong>.</li>
</ul>

<h2>Extras</h2>
<ul>
<li>Exporte <strong>.ics</strong> ou adicione ao Google Agenda.</li>
<li>Em shows, cadastre <strong>cachê</strong> e divisão entre confirmados.</li>
<li>Ensaios via estúdio aparecem com badge <em>via Estúdio</em>.</li>
</ul>
<p>Detalhes em <a href="/ajuda#agenda">/ajuda#agenda</a>.</p>
"""

_POST_MODO_TOCAR = """
<h2>O que é</h2>
<p>O <strong>Modo Tocar</strong> é a tela cheia para o palco: cifra legível, navegação entre músicas da setlist, auto-scroll e recursos para a banda tocar junta. Abra pela setlist, pela lista de cifras ou por <strong>Tocar setlist</strong> no evento da agenda (com banner do culto e sync automático).</p>

<h2>Primeiros passos</h2>
<ol>
<li>Abra uma setlist ou cifra e toque em <strong>Tocar</strong>.</li>
<li>Escolha cantora/cantor no topo se houver transposição por vocalista.</li>
<li>Use <strong>← →</strong> ou toque nas bordas para paginar a cifra; <strong>↑ ↓</strong> para trocar de música.</li>
<li><strong>Espaço</strong> liga o auto-scroll (velocidade <strong>Auto</strong> se a música tiver duração cadastrada).</li>
<li>Na primeira visita, um overlay explica atalhos e oferece configurar o <strong>count-in</strong> do metrônomo.</li>
</ol>

<h2>Cifra, grade e letra</h2>
<ul>
<li>Menu ou tecla <strong>G</strong> alterna cifra → grade harmônica → letra.</li>
<li><strong>N</strong> ativa modo <strong>Nashville</strong> (1–7) na grade.</li>
<li><strong>S</strong> abre o índice de <strong>seções</strong> (Intro, Refrão, Ponte…) — toque para pular direto.</li>
<li><strong>P</strong> ativa o <strong>modo vocalista</strong> (letra grande, sem distrações).</li>
<li><strong>Toque em um acorde</strong> para ver diagrama (violão, guitarra, baixo, ukulele, cavaquinho, piano).</li>
</ul>

<h2>Sync, notas e culto</h2>
<ul>
<li><strong>Sync</strong> na barra: quando ligado, todos seguem a música que o <strong>líder</strong> avança.</li>
<li>Ao abrir pelo <strong>evento da agenda</strong>, o sync costuma vir ligado — útil com vários tablets no culto.</li>
<li><strong>Notas de palco</strong> — cadastre na setlist (campo por música) ou edite no aviso amarelo ao trocar de faixa.</li>
<li>BPM, capo e compasso aparecem na barra de metadados.</li>
</ul>

<h2>Versão Banda / Minha</h2>
<p>Se você editou uma música e manteve só para si, use os botões <strong>Banda</strong> e <strong>Minha</strong> (ou tecla <strong>V</strong>) para alternar versões no palco.</p>

<h2>Metrônomo, loop e desenho</h2>
<ul>
<li><strong>M</strong> — metrônomo com acento no tempo 1 e count-in configurável.</li>
<li><strong>R</strong> — loop de trecho (marque pontos A e B para repetir um refrão).</li>
<li><strong>D</strong> — desenhar sobre a cifra (salvo na sua conta).</li>
</ul>

<h2>Offline e pedal</h2>
<ul>
<li>Ao abrir o Modo Tocar, o app <strong>baixa automaticamente</strong> as músicas da setlist — indicador <em>X/Y prontas</em> na barra.</li>
<li>Instale o SetSync como <strong>PWA</strong> para reforçar o uso sem internet.</li>
<li><strong>Pedal Bluetooth</strong>: ícone de sapato para mapear teclas; ícone <strong>varinha</strong> para o assistente passo a passo. Padrão: Page Up/Down paginam, ↑↓ trocam música.</li>
</ul>

<h2>Palco e celular</h2>
<ul>
<li><strong>F</strong> — tela cheia · <strong>T</strong> — tema claro/escuro</li>
<li><strong>+ / −</strong> — tamanho da fonte · <strong>C</strong> — duas colunas · <strong>L</strong> — lista lateral</li>
</ul>
<p>Lista completa de atalhos em <a href="/ajuda#modo-tocar">/ajuda#modo-tocar</a>.</p>
"""

_POST_NOTIFICACOES = """
<h2>Onde configurar</h2>
<p>Tudo em <strong>Meu perfil → Notificações</strong>. Cadastre o <strong>WhatsApp</strong> (com DDD) antes de ativar alertas por mensagem.</p>

<h2>Canais</h2>
<ul>
<li><strong>Push</strong> — no celular ou navegador; ative por dispositivo no perfil.</li>
<li><strong>E-mail</strong> — convites, escalação e lembretes (padrão ligado).</li>
<li><strong>WhatsApp</strong> — mesmos avisos por mensagem; exige número salvo.</li>
</ul>

<h2>O que chega na hora</h2>
<p>Escalação, convites de banda, lembretes de agenda (24h antes) e reservas de <strong>estúdio</strong> (solicitação, confirmação, recusa).</p>

<h2>Resumo diário</h2>
<p>Mudanças de cifras, setlists e outras atualizações da banda entram em um <strong>resumo diário</strong> por volta das <strong>21h</strong> (horário de Fortaleza). Você escolhe por tipo na tabela do perfil.</p>

<h2>Dicas</h2>
<ul>
<li>Desligue categorias que não usa para reduzir ruído.</li>
<li>Músicos de palco: mantenha push ligado para escalação de última hora.</li>
<li>Donos de estúdio: ative alertas da categoria estúdio.</li>
</ul>
<p>Mais em <a href="/ajuda#notificacoes">/ajuda#notificacoes</a>.</p>
"""

_POST_VERSAO_PESSOAL = """
<h2>O problema que resolve</h2>
<p>Você quer testar uma arrumação na cifra antes de mostrar para a banda — mas não pode apagar a versão que todo mundo usa no culto de domingo. A <strong>versão pessoal</strong> guarda suas alterações só para você até publicar.</p>

<h2>Fluxo ao editar</h2>
<ol>
<li>Abra <strong>Editar música</strong> (papel Editor ou admin).</li>
<li>Altere cifra, grade ou letra e salve com <strong>Salvar minha versão</strong>.</li>
<li>Escolha <strong>Manter só para mim</strong> ou <strong>Enviar para a banda</strong>.</li>
</ol>

<h2>Onde ver cada versão</h2>
<ul>
<li>Na página da música: aviso com botões <strong>Ver minha versão</strong> / <strong>Ver versão da banda</strong>.</li>
<li>No <strong>Modo Tocar</strong>: botões <strong>Banda</strong> e <strong>Minha</strong> (tecla <strong>V</strong>).</li>
</ul>

<h2>Quando publicar</h2>
<p>Depois do ensaio, se a banda aprovar, edite de novo e salve escolhendo <strong>Enviar para a banda</strong>. Todos passam a ver a versão atualizada.</p>
<p>Leia a seção completa em <a href="/ajuda#versao-pessoal">/ajuda#versao-pessoal</a>.</p>
"""
