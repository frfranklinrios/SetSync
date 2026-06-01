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

## Usuários não funcionam igual ao VPS

O login usa o arquivo SQLite **desta máquina**. Contas criadas em `https://setsync.dados.tec.br/` **não existem** no seu PC até você copiar o banco ou criar a conta de novo aqui.

### Sintomas comuns

| Sintoma | Causa | Solução |
|--------|--------|---------|
| “Usuário ou senha incorretos” com credencial do VPS | Banco local diferente | Copiar `banda.db` do servidor (abaixo) ou registrar de novo |
| Entra e logo volta para o login | `SESSION_COOKIE_SECURE=1` em HTTP local | `.env`: `FLASK_ENV=development` ou `ALLOW_HTTP_SESSION=1` |
| Admin não aparece localmente | Falta `SETSYNC_SUPERADMIN_*` no `.env` local | Copiar as mesmas linhas do `.env` do VPS |
| Google login falha local | Redirect URI só no domínio de produção | Adicionar `http://127.0.0.1:5000/google/callback` no Google Cloud |

### Copiar usuários do VPS (banco inteiro)

No servidor (ajuste usuário e caminho):

```bash
# Na sua máquina
scp usuario@seu-vps:/caminho/do/projeto/data/banda.db ./data/banda.db
```

Pare o app local antes de substituir o arquivo. **Não** sobrescreva o banco de produção a partir do local.

### Conferir usuários no banco local

```bash
uv run python -c "
from db import init_db, get_all_users
init_db()
for u in get_all_users():
    print(u['username'], u['email'])
"
```

### Login

O formulário aceita **username ou e-mail** (igual costuma ser no VPS se você lembrava do e-mail).

