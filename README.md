# SetSync

Gerenciador de cifras e setlists para bandas. Organize suas músicas, transpose acordes e execute o setlist ao vivo com o **Modo Tocar**.

## Documentação

- `docs/00-visao-geral.md`
- `docs/01-instalacao.md`
- `docs/02-uso.md`
- `docs/03-importador-cifras.md`
- `docs/04-pwa.md`
- `docs/05-troubleshooting.md`
- `docs/06-deploy-contabo.md` — VPS Contabo / produção

## Funcionalidades

- **Bandas e membros** — crie bandas, convide musicistas por e-mail, gerencie permissões
- **Cifras com destaque de acordes** — detecção automática de linhas de acorde vs. letra
- **Transposição automática** — suba ou desça o tom em tempo real, sem editar o arquivo
- **Setlist ordenado** — navegue entre músicas da banda com ← / →
- **Modo Tocar** — interface fullscreen para o palco
  - Barra de controle fixa com setlist lateral deslizante
  - Navegação por toque (swipe esquerda/direita) e teclado
  - Layout em **2 colunas** para cifras longas (sem precisar de scroll)
  - Auto-scroll configurável
  - Ajuste de tamanho de fonte
- **Dark / Light mode** — persiste entre sessões, acessível pelo navbar ou dentro do Modo Tocar (tecla `T`)
- **Login com Google OAuth** (opcional)

## Tech Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · Flask 3.0 |
| Banco de dados | SQLite 3 (sem ORM) |
| Auth | Flask-Login · Authlib (Google OAuth) |
| Frontend | Bootstrap 5.3 · Font Awesome 6.4 |
| Servidor | Gunicorn |
| Container | Docker / Podman |

## Deploy produção (Contabo / VPS)

Veja **`docs/06-deploy-contabo.md`**. Resumo:

```bash
cp .env.example .env   # FLASK_ENV=production, SECRET_KEY, SETSYNC_SUPERADMIN_*
docker compose -f docker-compose.prod.yml up -d --build
# Nginx + HTTPS na porta 443 → proxy para 127.0.0.1:5001
```

## Rodando com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose up -d
# http://localhost:5001 (mapeamento no compose de dev)
```

## Rodando localmente (sem container)

Use **apenas o ambiente desta pasta** (não ative o `.venv` de outro projeto no shell).

```bash
cd SetSync
uv sync
cp .env.example .env
# edite .env
uv run app.py
# ou: uv run python main.py
```

Alternativa com pip:

```bash
python -m venv .venv
source .venv/bin/activate   # deve apontar para SetSync/.venv
pip install -r requirements.txt
python app.py
```

Requisitos extras do módulo de importação de cifras: `ffmpeg` no PATH e, para o player do Cifra Club, `uv run playwright install chromium`.

### Importar cifra (módulo integrado `cifras_tool/`)

Todo o importador vive **dentro deste repositório** (`cifras_tool/`, `blueprints/cifras_import.py`) e é exposto em `/cifras/import/tool`. **Um único servidor** — não é necessário clonar nem rodar outro projeto ao lado.

Em **Adicionar** ou **Editar** cifra, use **Cifra → SetSync**: cole o link da cifra (Cifra Club / Cifras.com.br) e clique em **Usar no formulário SetSync**.

Arquivos temporários: `data/cifras_tmp`, `data/cifras_exports`.

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta do Flask (obrigatório) |
| `DATABASE_URL` | Caminho do SQLite (padrão: `sqlite:///data/banda.db`) |
| `FLASK_ENV` | `development` ou `production` |
| `SETSYNC_SUPERADMIN_USERNAMES` | Admin global (só `.env`, sem coluna no banco) |
| `CIFRAS_YOUTUBE_NO_SERVER` | `1` na VPS (sem yt-dlp no servidor) |
| `GUNICORN_WORKERS` | `1` com SQLite (padrão no `gunicorn.conf.py`) |
| `GOOGLE_CLIENT_ID` | ID do app no Google Cloud Console (opcional) |
| `GOOGLE_CLIENT_SECRET` | Secret do app no Google Cloud Console (opcional) |
| `CIFRAS_TMP_DIR` | Pasta temporária do pipeline de importação |
| `CIFRAS_YOUTUBE_COOKIES_FILE` | Cookies do YouTube para download de áudio (opcional) |

## Atalhos — Modo Tocar

| Tecla | Ação |
|---|---|
| `P` | Entrar no Modo Tocar |
| `Esc` | Sair do Modo Tocar |
| `← →` | Música anterior / próxima |
| `Espaço` | Ativar / pausar auto-scroll |
| `+ -` | Aumentar / diminuir fonte |
| `C` | Alternar layout 2 colunas |
| `S` | Abrir / fechar setlist |
| `T` | Alternar dark / light mode |
| Swipe ← → | Navegar músicas (touch) |

## Estrutura do projeto

```
├── app.py                  # Factory e registro de blueprints
├── config.py               # Configuração via .env
├── db.py                   # Acesso ao banco (SQLite puro)
├── util.py                 # Filtro Jinja2 highlight_chords
├── models.py               # Modelos Flask-Login
├── google_oauth.py         # Integração OAuth
├── blueprints/
│   ├── auth.py             # Login, registro, OAuth
│   ├── bands.py            # CRUD de bandas e membros
│   └── cifras.py           # CRUD de cifras + transposição
├── templates/
│   ├── index.html          # Base template (dark/light mode)
│   ├── cifras/view.html    # Visualização + Modo Tocar
│   └── ...
├── static/                 # Imagens e assets estáticos
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Licença

MIT

