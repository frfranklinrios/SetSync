#!/usr/bin/env bash
# Backup do Postgres do Uníssono com rotação. Agende via cron (ver docs abaixo).
#
# Uso:
#   BACKUP_DIR=/opt/setsync-backups ./scripts/backup_postgres.sh
#
# Variáveis (com defaults sensatos p/ o docker-compose.prod.yml):
#   PG_CONTAINER   nome do container postgres   (default: setsync-postgres-1)
#   PG_USER        usuário                       (default: setsync)
#   PG_DB          database                      (default: setsync)
#   BACKUP_DIR     destino dos dumps             (default: ./backups)
#   KEEP_DAYS      dias de retenção              (default: 14)
#   OFFSITE_CMD    comando opcional p/ enviar off-site (recebe o arquivo em $1)
#
# Cron diário às 03:30 (crontab -e):
#   30 3 * * * BACKUP_DIR=/opt/setsync-backups OFFSITE_CMD='rclone copy "$1" remote:setsync' \
#              /opt/setsync/scripts/backup_postgres.sh >> /var/log/setsync-backup.log 2>&1
set -euo pipefail

PG_CONTAINER="${PG_CONTAINER:-setsync-postgres-1}"
PG_USER="${PG_USER:-setsync}"
PG_DB="${PG_DB:-setsync}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
OUT="$BACKUP_DIR/setsync-$TS.sql.gz"

echo "[backup] $(date -Is) dump $PG_DB -> $OUT"
# --clean --if-exists deixa o dump restaurável de forma idempotente
docker exec "$PG_CONTAINER" pg_dump -U "$PG_USER" -d "$PG_DB" --clean --if-exists \
  | gzip -9 > "$OUT"

if [ ! -s "$OUT" ]; then
  echo "[backup] ERRO: dump vazio" >&2
  rm -f "$OUT"
  exit 1
fi
echo "[backup] ok ($(du -h "$OUT" | cut -f1))"

# Envio off-site opcional (rclone/scp/aws s3 cp …)
if [ -n "${OFFSITE_CMD:-}" ]; then
  echo "[backup] off-site: $OFFSITE_CMD"
  bash -c "$OFFSITE_CMD" _ "$OUT" || echo "[backup] AVISO: off-site falhou" >&2
fi

# Rotação local
find "$BACKUP_DIR" -name 'setsync-*.sql.gz' -mtime "+$KEEP_DAYS" -delete
echo "[backup] retenção: mantidos últimos $KEEP_DAYS dias"
