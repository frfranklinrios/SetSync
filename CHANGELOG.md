# Changelog — Uníssono

## 2026-11-12

### Otimizações, Tecnologias e Novas Features de Palco
- **Diapasão Acústico de Referência (Pitch Pipe)**: Síntese de fundamental e harmônicos via Web Audio API nativo com envelope sonoro suave ao tocar no badge do Tom (ou atalho `O`).
- **Suporte Total a Pedais Bluetooth**: Assistente `#play-pedal-wizard` e captura de teclas personalizadas no Modo Tocar com carregamento dos módulos de pedal e suporte a PageFlip, AirTurn, Donner e Lekato.
- **Otimização de Inicialização e Resiliência**: Verificação de status da Evolution API com timeout cirúrgico não-bloqueante (1.5s/2.5s), reduzindo tempo de subida e execução de suítes de testes em mais de 50%.
- **Padronização de Dependências (uv)**: Sincronização e integração completa de pacotes no `pyproject.toml` (ruff, pytest, flask-wtf, psycopg2, pywebpush, qrcode, gunicorn) gerenciados estritamente pelo Astral uv.
- **Gerenciamento Admin WhatsApp**: Rota de desconexão e status aprimorado com modo pareamento.

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
