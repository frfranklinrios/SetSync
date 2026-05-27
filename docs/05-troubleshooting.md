# Troubleshooting

## PWA não instala no iPhone

- Use o **Safari**, não o Chrome do iOS.
- Toque **Instalar** na barra do app e siga o guia (Compartilhar → Adicionar à Tela de Início).
- O site precisa estar em **HTTPS** em produção.
- Se abriu pelo Instagram/WhatsApp, use “Abrir no Safari” antes de instalar.

## “Not Found” ao abrir Cifra → SetSync

- Verifique se a rota abre no navegador: `/cifras/import/tool`
- Faça hard refresh (`Ctrl` + `Shift` + `R`) para evitar cache do PWA

## `ModuleNotFoundError` (yt_dlp / bs4 / curl_cffi / playwright / soundfile)

- Rode `uv sync` (ou reinstale dependências do projeto)

## `ffmpeg` não encontrado

Instale o ffmpeg no sistema e confirme:

```bash
ffmpeg -version
```

## Playwright / Chromium

```bash
uv run playwright install chromium
```

## YouTube bloqueando download

Configure cookies para o `yt-dlp`:

- `CIFRAS_YOUTUBE_COOKIES_FILE=/app/data/youtube_cookies.txt` (no Docker)
- O arquivo deve estar em formato **Netscape** e conter cookies de login (`SAPISID`, `__Secure-1PSID`, `LOGIN_INFO`).

## YouTube: “Signature solving failed” / “No supported JavaScript runtime”

O `yt-dlp` recente precisa de **Deno** (ou Node) + pacote `yt-dlp[default]` para resolver desafios do YouTube.

No Docker, faça rebuild:

```bash
docker compose up -d --build
docker compose exec web deno --version
docker compose exec web yt-dlp --cookies /app/data/youtube_cookies.txt --skip-download "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Banco SQLite

Se o app não “encontra” dados esperados, confirme o arquivo:

- `DATABASE_URL=sqlite:///data/banda.db`

e se a pasta `data/` existe e tem permissão de escrita.

