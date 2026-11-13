# Changelog — Uníssono

## 2026-11-13

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
