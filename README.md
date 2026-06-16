# SetSync

**[setsync.com.br](https://setsync.com.br)** — gerenciador de cifras e setlists para bandas e ministérios de louvor. Organize músicas, transpose acordes, monte setlists e use o **Modo Tocar** no palco.

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/00-visao-geral.md](docs/00-visao-geral.md) | Arquitetura e módulos |
| [docs/01-instalacao.md](docs/01-instalacao.md) | Instalação local e Docker |
| [docs/02-uso.md](docs/02-uso.md) | Uso do app (bandas, cifras, setlists) |
| [docs/03-importador-cifras.md](docs/03-importador-cifras.md) | Importador Cifra Club / Cifras.com.br |
| [docs/04-pwa.md](docs/04-pwa.md) | Instalar como app (PWA) |
| [docs/05-troubleshooting.md](docs/05-troubleshooting.md) | Problemas comuns |
| [docs/06-deploy-contabo.md](docs/06-deploy-contabo.md) | Deploy em VPS (Contabo) |
| [docs/MIGRACAO_POSTGRES.md](docs/MIGRACAO_POSTGRES.md) | SQLite → PostgreSQL |
| [docs/chordsheet-formato.md](docs/chordsheet-formato.md) | Formato chord sheet (setsync.chordsheet) |
| [docs/chordsheet-prompt-ia.md](docs/chordsheet-prompt-ia.md) | Prompt para gerar chord sheets com IA |
| [MONETIZACAO.md](MONETIZACAO.md) | Planos, Mercado Pago e vouchers |

## Funcionalidades

- **Bandas e membros** — convites por e-mail, papéis (admin/membro), logo da banda
- **Cantores** — vários vocalistas por banda, tom de transposição por cantor
- **Cifras** — ChordPro, colagem de sites, lead sheet, **chord sheet** (chordsheet.com), tablatura, tons maiores/menores
- **Transposição** — em tempo real; tom salvo para toda a banda e por cantor na setlist
- **Setlists** — ordenação por arrastar, cantor/tom por música, link público de letras
- **PDF e impressão** — folha de palco (lista simples) + cifras em sequência (A4, 2 colunas)
- **Modo Tocar** — tela cheia, setlist lateral, auto-scroll, gestos e atalhos de teclado
- **PWA** — instalar no celular (Android/iOS)
- **Planos** — Grátis, Pro e Worship (Mercado Pago); vouchers promocionais
- **Login** — e-mail/senha e Google OAuth (opcional)
- **Notificações** — convites, assinatura e avisos na banda

## Tech stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.12 · Flask 3.0 · Gunicorn |
| Banco | **PostgreSQL** (produção) ou **SQLite** (`DATABASE_URL`) |
| Camada DB | `database.py` + `db.py` (SQL direto, sem ORM) |
| Auth | Sessão Flask · Authlib (Google OAuth) |
| PDF | Playwright (Chromium) |
| Pagamentos | Mercado Pago |
| Frontend | Bootstrap 5.3 · Font Awesome 6.4 |
| Deploy | Docker · Nginx Proxy Manager |

## Deploy em produção

Produção usa **PostgreSQL** no mesmo `docker-compose` (volume persistente). Dados em `./data` (logos, backup do SQLite).

```bash
cp .env.example .env
# Edite: SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL, SETSYNC_CANONICAL_URL,
# SETSYNC_SUPERADMIN_*, Mercado Pago, etc.

docker compose -f docker-compose.prod.yml up -d --build
# App em http://127.0.0.1:5001 — proxy HTTPS (Nginx) → setsync.com.br
```

Migrar um `banda.db` existente:

```bash
docker compose -f docker-compose.prod.yml exec web \
  python3 scripts/migrate_sqlite_to_postgres.py --sqlite /app/data/banda.db
```

Detalhes: **[docs/06-deploy-contabo.md](docs/06-deploy-contabo.md)**.

## Desenvolvimento

### Docker (app + SQLite)

```bash
cp .env.example .env
# DATABASE_URL=sqlite:///data/banda.db
docker compose up -d
# http://127.0.0.1:5001
```

### Docker (app + PostgreSQL de teste)

```bash
docker compose -f docker-compose.postgres.yml up -d --build
# http://127.0.0.1:5002
```

### Local (uv)

```bash
cd SetSync
uv sync
cp .env.example .env
uv run app.py
```

Requisitos do importador: `ffmpeg` no PATH; `playwright install chromium` para colagem/PDF.

**Importador integrado** (`cifras_tool/`, rota `/cifras/import/tool`): em Adicionar/Editar cifra, use **Cifra → SetSync** com link ou colagem.

## Variáveis de ambiente (principais)

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave longa e aleatória (**obrigatória** em `FLASK_ENV=production`) |
| `DATABASE_URL` | `postgresql://user:pass@postgres:5432/setsync` ou `sqlite:///data/banda.db` |
| `POSTGRES_PASSWORD` | Senha do Postgres (compose de produção) |
| `FLASK_ENV` | `development` ou `production` |
| `SETSYNC_CANONICAL_URL` | URL HTTPS pública (ex.: `https://setsync.com.br`) |
| `SETSYNC_SUPERADMIN_USERNAMES` | Admin global (vírgula) |
| `SETSYNC_INTERNAL_URL` | URL interna para PDF (`http://127.0.0.1:5000` no container) |
| `MP_*` | Mercado Pago (planos Pro/Worship) — ver `MONETIZACAO.md` |
| `ADSENSE_*` | Google AdSense (plano grátis) — ver `MONETIZACAO.md` |
| `GOOGLE_ADS_*` | Conversão de inscrição no Google Ads — ver `docs/google-ads-inscricoes.md` |
| `GOOGLE_CLIENT_ID` / `SECRET` | Login com Google (opcional) |
| `MAIL_*` | SMTP para recuperação de senha e avisos (opcional — ver `.env.example`) |

Lista completa: **`.env.example`**.

## Atalhos — Modo Tocar

| Tecla / gesto | Ação |
|---------------|------|
| `Esc` | Sair do Modo Tocar |
| `←` `→` (bordas) | Rolar uma página; no fim/início troca de música |
| `←` `→` (barra superior) | Música anterior / próxima |
| `Espaço` | Auto-scroll |
| `+` `-` | Fonte maior / menor |
| `C` | 1 ou 2 colunas |
| `L` | Abrir / fechar lista (setlist) |
| `T` | Tema claro / escuro |
| `A` `G` `F` | Diagrama de acorde, arpejo, fullscreen |

Mais atalhos: **[Ajuda](https://setsync.com.br/ajuda)** no app.

## Estrutura do projeto

```
├── app.py                      # App Flask e blueprints
├── config.py                   # Configuração por ambiente
├── database.py                 # Conexão SQLite ou PostgreSQL
├── db.py                       # Schema e acesso aos dados
├── chordpro.py                 # Parse e conversão ChordPro
├── blueprints/                 # auth, bands, cifras, setlists, assinatura, …
├── cifras_tool/                # Importador (scraper, lead sheet, áudio)
├── templates/                  # Jinja2 + Modo Tocar
├── static/                     # CSS, JS, PWA (sw.js, manifest)
├── scripts/                    # migração PG, testes, MP
├── docker-compose.prod.yml     # Produção (web + postgres)
├── docker-compose.yml          # Dev (SQLite)
└── data/                       # banda.db (backup), logos, exports
```

## Licença

MIT
