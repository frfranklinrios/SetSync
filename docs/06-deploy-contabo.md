# Deploy na Contabo (VPS)

Checklist para subir o SetSync em produção **sem mudar o schema do banco** além do que `init_db()` já faz ao iniciar (colunas opcionais em SQLite existente).

## 1. Servidor

- Ubuntu 22.04+ (ou similar)
- Domínio apontando para o IP da VPS (recomendado para OAuth e cookies)
- Portas **80/443** abertas no firewall da Contabo

## 2. Opção A — Docker (recomendado)

```bash
cd /opt/setsync   # clone do repositório
cp .env.example .env
nano .env         # SECRET_KEY, admin, Google OAuth, etc.
mkdir -p data

docker compose -f docker-compose.prod.yml up -d --build
```

O app escuta em **127.0.0.1:5001** (só localhost). Coloque o **Nginx** na frente com HTTPS.

**Não use** o `docker-compose.yml` de desenvolvimento na VPS (ele monta `.:/app` e sobrescreve o código dentro do container).

Persistência: pasta `./data` (banco `data/banda.db`, exports, tmp).

## 3. Opção B — Sem Docker

```bash
sudo apt update
sudo apt install -y python3.12-venv ffmpeg curl

cd /opt/setsync
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env

mkdir -p data
export FLASK_ENV=production
gunicorn --config gunicorn.conf.py app:app
```

Para serviço systemd, use `WorkingDirectory=/opt/setsync`, `EnvironmentFile=/opt/setsync/.env` e o mesmo comando `gunicorn`.

## 4. Nginx (HTTPS)

Exemplo mínimo (Certbot para TLS):

```nginx
server {
    listen 443 ssl http2;
    server_name setsync.seudominio.com;

    # ssl_certificate ... (certbot)

    client_max_body_size 32M;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Com `FLASK_ENV=production` e `TRUST_PROXY=1`, o OAuth Google usa URLs `https://` corretas.

## 5. Variáveis obrigatórias (.env)

| Variável | Produção |
|----------|----------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | string longa e aleatória (nunca o exemplo) |
| `DATABASE_URL` | `sqlite:///data/banda.db` |
| `SETSYNC_SUPERADMIN_USERNAMES` | seu login admin |
| `CIFRAS_YOUTUBE_NO_SERVER` | `1` (recomendado na VPS) |
| `SESSION_COOKIE_SECURE` | `1` com HTTPS; `0` só para teste em HTTP |
| `GUNICORN_WORKERS` | `1` (SQLite) |

## 6. Admin global

1. Registre o usuário pelo app.
2. No `.env`:

```env
SETSYNC_SUPERADMIN_USERNAMES=seu_usuario
```

3. Reinicie o container/serviço.
4. Menu **Admin** → `/admin`.

```bash
uv run python scripts/create_superadmin.py --username seu_usuario
```

(só imprime as linhas para colar no `.env`)

## 7. Google OAuth

No [Google Cloud Console](https://console.cloud.google.com/):

- Tipo: aplicativo Web
- URIs autorizados: `https://setsync.seudominio.com`
- Redirect: `https://setsync.seudominio.com/google/callback`

## 8. PWA / cache

Após deploy, os usuários podem precisar de **atualização forçada** (Ctrl+Shift+R) ou reinstalar o atalho PWA para ver CSS/JS novos (`sw.js` versão `setsync-v7+`).

## 9. Backup

Agende cópia periódica de:

```text
/opt/setsync/data/banda.db
/opt/setsync/data/cifras_exports/
```

## 10. Problemas comuns

| Sintoma | Causa provável |
|---------|----------------|
| Login não mantém sessão | HTTPS ausente com `SESSION_COOKIE_SECURE=1` |
| Google OAuth redirect errado | Nginx sem `X-Forwarded-Proto` ou domínio diferente do Console |
| `database is locked` | `GUNICORN_WORKERS` > 1 com SQLite |
| Admin não aparece | `SETSYNC_SUPERADMIN_*` vazio ou app não reiniciado |

Ver também `docs/05-troubleshooting.md`.
