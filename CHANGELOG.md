# Changelog — Uníssono

## 2026-11-13

### Estúdios Parceiros Oficiais 100% Grátis (Canal de Crescimento B2B2C / Product-Led Growth)
- **Acesso Gratuito com Salas Ilimitadas**:
  - Eliminação de fricção de cobrança de R$ 49/mês para estúdios de ensaio. Todos os donos de estúdio contam com salas ilimitadas, agendamento online e controle financeiro de forma 100% gratuita.
  - O estúdio passa a atuar como hub parceiro de distribuição física e digital do Uníssono para as bandas que ensaiam no local.
- **Cartaz da Sala de Ensaio Imprimível em Folha A4 (`/<studio_id>/cartaz-sala`)**:
  - Template de altíssima definição formatado em folha A4 com instruções de 3 passos para os músicos.
  - QR Code dinâmico do estúdio para que as bandas abram na hora as cifras, letras, metrônomo e modo tocar na sala de ensaio.
  - Botão de 1 clique para imprimir ou salvar como PDF no painel do estúdio.
- **Painel do Estúdio Modernizado**:
  - Substituição dos alertas de trial expirado por cartão de boas-vindas do Parceiro Oficial.
  - Acesso direto ao download do QR Code da sala e geração de cupons promocionais para bandas clientes.
- **Validação Automatizada de Testes**:
  - Novo teste `scripts/test_studio_free_partner.py` cobrindo checagem de salas ilimitadas, badge de parceiro oficial, rota do cartaz A4 e vitrine de planos.
  - 32 testes executados com 100% de sucesso.

### Aprimoramentos de Alta Performance para Palco & Show ao Vivo
- **Quick Song Jumper (Paleta Spotlight de Busca Rápida de Músicas)**:
  - Busca instantânea e salto direto para qualquer música do setlist sem sair da tela ou abrir a gaveta lateral (atalhos `/` ou `J`, ou botão de lupa na barra superior).
  - Filtragem em tempo real com relevância ponderada por número da faixa (ex: `#3`), título (com suporte a acentuação fonética), artista e tom da música.
  - Navegação suave e ergonômica por teclado (`ArrowDown`, `ArrowUp`, `Enter` para saltar imediatamente e `Esc` para fechar).
  - Badges informativos de status: "Tocando agora", versão pessoal ("Minha") e tom da cifra.
- **Relógio de Palco & Cronômetro de Apresentação (Show Clock & Live Timer)**:
  - Widget integrado no topo da barra do Modo Tocar com display digital tabular.
  - Alternância imediata com um clique entre **Relógio Real** (hora local `21:45`) e **Cronômetro do Show** (`⏱ 34:12`).
  - Controles compactos de iniciar, pausar e zerar o tempo da apresentação.
  - Persistência em `sessionStorage` para resistir a recarregamentos acidentais da página durante a apresentação ao vivo.
- **Auto-Scroll Inteligente Sincronizado por Duração Musical**:
  - Botão de duração (`⏱ Tempo`) integrado diretamente à pílula flutuante de velocidade (`#speed-pill`) e modal de ajuste rápido com presets de 1 toque (2:00, 2:30, 3:00, 3:30, 4:00, 5:00 min) ou minutos/segundos customizados.
  - Cálculo preciso de velocidade de rolagem em `px/ms` baseado na distância restante (`scrollHeight - clientHeight`) e tempo da música.
  - Preparação inicial suave (lead-in delay de 3 segundos) para o músico começar a tocar antes do movimento da cifra.
  - Rótulo dinâmico na barra de rolagem informando o tempo restante ou ritmo do auto-scroll.
- **Mini HUD Flutuante de Acordes no Modo Tocar (Quick Chord HUD Popover)**:
  - Popover compacto, suspenso e não intrusivo acionado ao tocar em qualquer acorde (`.chord`) da cifra no palco.
  - Substitui o modal escurecedor em tela cheia do Bootstrap durante o show, mantendo a visibilidade total da letra e cifras.
  - Renderização instantânea do diagrama SVG em altíssima resolução com pestanas e dedos.
  - Alternador rápido de instrumento (Violão, Guitarra, Ukulele, Cavaco e Baixo) e navegador de inversões/shapes (1/3, 2/3, etc.).
  - Opção discreta "Teoria ↗" para quem desejar abrir a análise harmônica completa de escalas e arpejos.
- **Suíte de Testes Automatizados**:
  - Novo script `scripts/test_stage_enhancements.py` cobrindo validação de módulos JS em Node.js, cálculos de rolagem por tempo e integração dos novos elementos no template Flask.
  - Total geral de 31 testes aprovados com 100% de sucesso e 0 falhas.

### Inovações Inspiradas em Referências de Palco Open-Source (GitHub)
- **Metrônomo Profissional com Tap Tempo & Pulso Visual Silencioso** (*chordbook/metronome* & *Rexaintreal/Resonate*):
  - Botão **Tap Tempo** integrado à barra do Modo Tocar (atalho `B`), permitindo marcar o andamento em 3–4 batidas.
  - **Barra de Pulso Visual de LEDs** sincronizada com o compasso: acento no tempo 1 (âmbar) e pulso rítmico nos demais tempos (ciano).
  - Modo silencioso/mudo com um toque na barra de LEDs, permitindo aos músicos seguirem o tempo no palco sem ruído sonoro.
- **Calculadora e Transpositor de Capotraste Inteligente (CAGED)** (*sepandhaghighi/capo* & *VitamintK/Capoless*):
  - Módulo `capo-calculator.js` que calcula a equivalência matemática de casas 1 a 7 e formas abertas sem pestana.
  - Sugestões automáticas baseadas no tom real da música, destacando a melhor casa para tocar com digitações simples do CAGED (C, A, G, E, D).
  - Transposição visual instantânea na cifra (atalho `K`), permitindo ao instrumentista ler os acordes relativos ao Capo enquanto a banda e o vocalista mantêm o tom original de apresentação.
- **Colas Pessoais de Palco (Personal Musician Cues)** (*ParriauxMaxime/open-setlist*):
  - Sistema de anotações 100% privadas por música para cada integrante da banda (atalho `Q`).
  - Permite ao baterista, baixista ou guitarrista salvar observações particulares (ex: "Começar no chimbal", "Solo na 2ª volta em Am") sem poluir a cifra compartilhada da equipe.
  - Banner destacado no topo da cifra no Modo Tocar com modal rápido de edição e persistência local.
- **Status de Prontidão da Música no Repertório (Song Readiness)** (*ParriauxMaxime/open-setlist*):
  - Classificação do repertório em `pronta`, `ensaio` ou `aprender`, com indicador visual nos cards e badges da banda.
  - Barra de Prontidão Geral do Show no Setlist (`85% Prontas para o Show`), com contadores e gráfico proporcional.
  - Dropdown interativo na lista do setlist com atualização assíncrona instantânea via API `/cifras/<id>/readiness`.
  - Testes automatizados dedicados em `scripts/test_github_features.py` (30/30 testes com 100% de sucesso).

## 2026-11-12

### Desativação Temporária do WhatsApp
- **Suspensão de Notificações e Envio Automático**: Configuração padrão `WHATSAPP_NOTIFICATIONS_ENABLED=0`, pulando inicialização de contêineres e bloqueando disparos em segundo plano.
- **Botão Flutuante e Painel Admin**: Ocultação automática do botão flutuante e exibição de aviso claro no painel administrativo de que o WhatsApp está desativado no momento.

### Transformação Comercial & Máxima Conversão de Planos
- **Redesign Completo da Página de Planos (`/assinatura/planos`)**:
  - Exibição em destaque dos 3 planos comerciais: **Individual** (R$ 15), **Pro** (R$ 29 - Mais Popular) e **Worship** (R$ 69 - Igrejas & Ministérios), tirando o plano Worship de dentro de detalhes ocultos.
  - **Garantia Blindada de 7 Dias**: Selo de confiança e 100% de reembolso sem perguntas caso a banda não se adapte.
  - **Facilidade de Pagamento Mercado Pago**: Destaque para Pix com liberação imediata e Cartão em até 12x.
  - **Zero Fricção no Checkout**: Criação automática de banda no checkout do Worship caso o usuário ainda não tenha banda criada.
  - **Prova Social**: Bloco de depoimentos reais de líderes de ministério e músicos que usam a plataforma.
  - **FAQ de Conversão**: Respostas diretas quebrando as principais objeções de compra (rateio, multi-bandas, funcionamento offline).
- **Navbar Comercial Global**: Botão chamativo "Assinar Pro" com ícone de coroa dourada para usuários logados e badge de status Pro para assinantes.
- **Vitrine Comercial na Home**: Seção `#planos` na página inicial com os 3 planos e alternador dinâmico de faturamento Mensal/Anual (2 meses grátis).
- **Testes Automatizados**: Suíte de validação dedicada (`scripts/test_comercial_e_whatsapp_disabled.py`) com 100% de cobertura nos fluxos comerciais.

## 2026-07-13

### Camadas de ativação, retenção e conversão in-app
- Pós-cadastro, login, banda, empty states e setlist pública empurram até o Modo Tocar
- Trial mid-cycle (7/3 dias) + e-mails de estúdio/Premium; dashboard e checklist com CTAs de preço
- Funil de marketing (nav, Planos, paywall, landings) e domínio canônico `unissono.app`

## 2026-07-09

### Rebrand: SetSync → Uníssono
- Nome do app atualizado em toda a interface, e-mails, PWA, SEO e documentação
- Módulo `branding.py` centraliza `app_name` nos templates
- Aviso na tela de login/cadastro e banner “Entendi” para quem já usa o app
- Domínio legado `setsync.com.br` mantido com redirect para `unissono.app`

### Painel master (superadmin)
- Login e menu “Painel” levam direto ao `/admin`
- Funil de ativação em português, alerta de usuários sem banda, busca na aba Usuários

## 2026-06-06

### Admin — acesso corrigido
- Coluna persistente `users.is_superadmin` + sincronização com `SETSYNC_SUPERADMIN_*` no `.env`
- Promoção/revogação de admin global em `/admin` (aba Usuários)
- Ambas contas master (`franklin` e `frfranklin.rios`) configuradas no `.env`

### Tarefa 1 — WhatsApp
- Variáveis `WHATSAPP_NUMBER` e `WHATSAPP_MESSAGE` (compatível com `SETSYNC_WHATSAPP`)
- Link dinâmico com `urlencode` em `/igrejas`

### Tarefa 2 — AdSense removido
- Meta tag e scripts removidos de `index.html`, `public_letras.html` e context processor

### Tarefa 3 — Depoimentos
- Tabela `testimonials`, seeds de exemplo, seção na homepage
- Admin `/admin/depoimentos` (CRUD)

### Tarefa 4 — Estatísticas homepage
- Contadores reais (bandas, músicas, setlists) com animação Intersection Observer

### Tarefa 5 — Screenshots
- Seção "Veja o Uníssono em ação" + `static/screenshots/README.md`

### Tarefa 6 — Onboarding e-mail
- Tabela `onboarding_emails`, 5 e-mails, job diário via scheduler

### Tarefa 7 — Modal upgrade
- `static/js/modal-upgrade.js` intercepta HTTP 402 com payload `limite_atingido`

### Tarefa 8 — Trial Pro 14 dias
- Campos `trial_*` em `assinaturas`, ativação na criação da banda, banner no dashboard

### Tarefa 9 — Preços anuais
- Toggle mensal/anual em `planos_publicos.html` (Pro R$249/ano, Worship R$599/ano)

### Tarefa 10 — Blog
- Rotas `/blog`, `/blog/<slug>`, 5 posts seed, SEO (OG, canonical, JSON-LD)

### Tarefa 11 — Sitemap
- Rota `/sitemap.xml` com páginas públicas e posts do blog

### Testes
- `scripts/test_monetizacao_negocio.py` — limites, trial, onboarding
