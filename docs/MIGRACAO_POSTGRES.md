# Migração SQLite → PostgreSQL (branch `migrar`)

## Testar localmente

```bash
docker compose -f docker-compose.postgres.yml up -d --build
```

App em http://127.0.0.1:5002 — Postgres em `127.0.0.1:5433`.

## Importar cópia do SQLite de produção

1. Copie `data/banda.db` para o servidor de teste.
2. Defina `DATABASE_URL` apontando para o Postgres de teste.
3. Rode:

```bash
docker compose -f docker-compose.postgres.yml exec web \
  python3 scripts/migrate_sqlite_to_postgres.py --sqlite /app/data/banda.db
```

Dry-run (só contagens):

```bash
python3 scripts/migrate_sqlite_to_postgres.py --dry-run
```

## Produção (quando aprovarem)

1. Backup: `cp data/banda.db data/banda.db.bak-$(date +%F)`
2. Subir serviço Postgres e `DATABASE_URL=postgresql://...`
3. Rodar script de migração
4. Smoke: login, banda, cifra, setlist, assinatura
5. Manter backup SQLite por alguns dias

## Compatibilidade

- `DATABASE_URL=sqlite:///data/banda.db` — comportamento atual (main).
- `DATABASE_URL=postgresql://user:pass@host:5432/setsync` — usa `database.py` + schema Postgres.
