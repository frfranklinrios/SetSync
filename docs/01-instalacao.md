# Instalação e execução

## Requisitos

- Python **3.12+**
- `ffmpeg` no PATH (obrigatório para o importador)
- (Opcional, recomendado) Chromium do Playwright para resolver URLs do player do Cifra Club

## Executar localmente com `uv` (recomendado)

Use o ambiente **somente deste diretório**. Se o shell tiver `VIRTUAL_ENV` apontando para outro projeto (ex.: `banda-app/.venv`), rode `deactivate` antes ou use sempre `uv run` dentro de `SetSync` — o `uv` cria e usa `SetSync/.venv` automaticamente.

```bash
cd SetSync
uv sync
cp .env.example .env
uv run app.py
```

Equivalente: `uv run python main.py`.

Acesse `http://127.0.0.1:5000`.

### Administrador global (sem alterar o banco)

Ideal para deploy na **Contabo**: o admin é definido só no `.env`, sem migração de tabelas.

1. Crie o usuário normalmente pelo app (registro/login).
2. No `.env` do servidor:

```env
SETSYNC_SUPERADMIN_USERNAMES=seu_usuario
SETSYNC_SUPERADMIN_EMAILS=admin@seudominio.com
```

Vários usuários: separe por vírgula. Use **username** ou **e-mail** (ou os dois).

3. Reinicie o app. Menu **Admin** ou `/admin`.

Para gerar as linhas do `.env` localmente:

```bash
uv run python scripts/create_superadmin.py --username seu_usuario
```

### Playwright (opcional)

Se o importador precisar abrir o player do Cifra Club para extrair o vídeo:

```bash
uv run playwright install chromium
```

## Deploy na Contabo (produção)

Guia completo: **[06-deploy-contabo.md](06-deploy-contabo.md)** — `.env`, Docker prod, Nginx, HTTPS, admin, backup.

```bash
cp .env.example .env
# edite FLASK_ENV=production, SECRET_KEY, SETSYNC_SUPERADMIN_*
docker compose -f docker-compose.prod.yml up -d --build
```

## Executar com Docker/Podman (desenvolvimento)

`docker-compose.yml` monta o código local (`.:/app`) — **não use na VPS**.

```bash
cp .env.example .env
docker compose up -d
```

## Variáveis de ambiente

Veja `.env.example`. Principais:

- `SECRET_KEY`: obrigatório em produção
- `DATABASE_URL`: caminho do SQLite (padrão `sqlite:///data/banda.db`)
- `FLASK_ENV`: `development` ou `production`
- `CIFRAS_TMP_DIR`: diretório temporário do pipeline (opcional)
- `CIFRAS_YOUTUBE_COOKIES_FILE`: cookies para `yt-dlp` (opcional, ajuda em vídeos com restrição)

