# Deploy na Contabo (VPS)

Checklist para subir o Uníssono em produção. Domínio canônico: **`https://unissono.app`**. O schema evolui via `init_db()` → `_run_schema_migrations()` (mesmo caminho em **SQLite** e **PostgreSQL**).

## 1. Servidor

- Ubuntu 22.04+ (ou similar)
- Domínio `unissono.app` (e `www`) apontando para o IP da VPS
- Portas **80/443** abertas no firewall da Contabo
- Legado: `setsync.com.br` pode permanecer no DNS e redirecionar 301 via app (`SETSYNC_ALLOWED_HOSTS`)

## 2. Opção A — Docker (recomendado)

```bash
cd /opt/setsync   # clone do repositório
cp .env.example .env
nano .env         # SECRET_KEY, Postgres, MP, mail, canônico
mkdir -p data

docker compose -f docker-compose.prod.yml up -d --build
```

Serviços típicos no compose: `web`, `postgres`, `mail`, `evolution` (WhatsApp), `api-cifras`.

O app escuta na rede Docker (ex.: porta 5000). Coloque o **Nginx Proxy Manager** (ou Nginx) na frente com HTTPS.

**Não use** o `docker-compose.yml` de desenvolvimento na VPS (ele monta `.:/app` e sobrescreve o código dentro do container).

### Domínio e TLS (Nginx Proxy Manager)

1. Proxy Host com `server_name`: `unissono.app` `www.unissono.app` (+ hosts legados se quiser).
2. Certificado Let's Encrypt cobrindo **unissono.app** e **www.unissono.app** (e opcionalmente `setsync.com.br`).
3. Force SSL + HSTS.
4. No `.env`:

```env
SETSYNC_CANONICAL_URL=https://unissono.app
SETSYNC_ALLOWED_HOSTS=unissono.app,www.unissono.app,setsync.com.br,www.setsync.com.br,localhost,127.0.0.1
TRUST_PROXY=1
```

Hosts legados em `ALLOWED_HOSTS` recebem **301** para o canônico.

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

## 4. PostgreSQL (produção)

No `.env`:

```env
DATABASE_URL=postgresql://setsync:SENHA@postgres:5432/setsync
POSTGRES_PASSWORD=SENHA
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
```

Backup: `pg_dump` agendado (não só cópia de arquivo SQLite).

## 5. Variáveis obrigatórias (.env)

| Variável | Produção |
|----------|----------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | string longa e aleatória |
| `DATABASE_URL` | Postgres (recomendado) ou `sqlite:///data/banda.db` |
| `SETSYNC_CANONICAL_URL` | `https://unissono.app` |
| `SETSYNC_ALLOWED_HOSTS` | unissono + legados setsync |
| `SETSYNC_SUPERADMIN_USERNAMES` / `_EMAILS` | admin |
| `CIFRAS_YOUTUBE_NO_SERVER` | `1` |
| `SESSION_COOKIE_SECURE` | `1` com HTTPS |
| `MAIL_*` | SMTP (container `mail` ou externo) |
| `MP_ACCESS_TOKEN` / `MP_ENVIRONMENT` | Mercado Pago |
| `MP_WEBHOOK_SECRET` | validação IPN |

## 6. E-mail (`contato@unissono.app`)

DNS no Registro.br (ou provedor):

| Tipo | Nome | Valor |
|------|------|--------|
| A | `mail` | IP da VPS |
| MX | `@` | `mail.unissono.app` (prioridade 10) |
| TXT | `@` | `v=spf1 ip4:IP_DA_VPS -all` |
| TXT | `unissono._domainkey` | chave DKIM do `mail_server` |

Teste:

```bash
docker compose -f docker-compose.prod.yml exec web python3 scripts/send_test_email.py voce@exemplo.com
```

> IPs Contabo podem cair em blocklist Microsoft (S3150). Monitore reputação; se Outlook rejeitar, use relay (Zoho/SES) ou peça delist.

## 7. Mercado Pago

1. Webhook de produção: `https://unissono.app/assinatura/webhook`
2. Eventos: `subscription_preapproval`, `payment`
3. Smoke de credenciais: `python3 scripts/test_mp_sandbox.py check` (também valida token de produção se `MP_ENVIRONMENT=production`)

## 8. Google OAuth

No [Google Cloud Console](https://console.cloud.google.com/):

- URIs autorizados: `https://unissono.app`
- Redirect: `https://unissono.app/google/callback`
- Mantenha `https://setsync.com.br/...` só enquanto o legado ainda recebe tráfego

## 9. Google Ads / Maps

- Ads: ver `docs/google-ads-inscricoes.md` (URL canônica `unissono.app`)
- Maps referers: `https://unissono.app/*`, `https://www.unissono.app/*`

## 10. Admin global

```bash
uv run python scripts/create_superadmin.py --username seu_usuario
```

## 11. PWA / cache

Após deploy, usuários podem precisar de atualização forçada ou reinstalar o PWA (`sw.js` com versão nova).

## 12. Backup

- Postgres: `pg_dump`
- Volumes: `./data` (exports, tmp, uploads)
- Certificados NPM / Let's Encrypt

## 13. Problemas comuns

| Sintoma | Causa provável |
|---------|----------------|
| Login não mantém sessão | HTTPS ausente com `SESSION_COOKIE_SECURE=1` |
| Google OAuth redirect errado | Domínio diferente do Console / sem `X-Forwarded-Proto` |
| Host 403 | Falta o host em `SETSYNC_ALLOWED_HOSTS` |
| TLS `unrecognized name` | Apex/www fora do `server_name` do NPM |
| E-mails não chegam | MX/DKIM ausentes ou IP em blocklist |
| Webhook MP não ativa plano | URL antiga (`setsync.dados.tec.br`) — use `unissono.app` |

Ver também `docs/05-troubleshooting.md`.
