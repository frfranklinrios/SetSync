#!/usr/bin/env bash
# Verifica se um dump recente existe e tem tamanho mínimo.
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-/root/SetSync/backups}"
MIN_BYTES="${MIN_BYTES:-100000}"
latest="$(ls -1t "$BACKUP_DIR"/setsync-*.sql.gz 2>/dev/null | head -1 || true)"
if [ -z "$latest" ]; then
  echo "[verify] ERRO: nenhum dump em $BACKUP_DIR" >&2
  exit 1
fi
size="$(stat -c%s "$latest")"
echo "[verify] latest=$latest size=$size"
if [ "$size" -lt "$MIN_BYTES" ]; then
  echo "[verify] ERRO: dump pequeno demais" >&2
  exit 1
fi
gzip -t "$latest"
echo "[verify] gzip ok"
