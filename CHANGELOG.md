# Changelog — Uníssono

## 2026-07-13

### Conversão e domínio canônico
- Funil de venda: CTAs na nav/home, cadastro mais curto, Planos logado com Pro em destaque e preço anual vivo
- Paywall 402 unificado com copy de valor; upsells do dashboard com preço
- Landings igrejas/estúdios/comece e CTAs públicos alinhados a trial → Pro/Worship/Premium
- Domínio canônico `https://unissono.app` (+ TLS, redirects e docs)

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
