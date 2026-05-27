# Instalação e execução

## Requisitos

- Python **3.12+**
- `ffmpeg` no PATH (obrigatório para o importador)
- (Opcional, recomendado) Chromium do Playwright para resolver URLs do player do Cifra Club

## Executar localmente com `uv` (recomendado)

```bash
cd SetSync
uv sync
cp .env.example .env
uv run app.py
```

Acesse `http://127.0.0.1:5000`.

### Playwright (opcional)

Se o importador precisar abrir o player do Cifra Club para extrair o vídeo:

```bash
uv run playwright install chromium
```

## Executar com Docker/Podman

Se o repositório tiver `docker-compose.yml`:

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

