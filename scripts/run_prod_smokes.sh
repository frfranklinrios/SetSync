#!/usr/bin/env bash
# Pacote de smokes de produção (rodar no host ou via compose exec).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== prod_status ==="
docker compose -f docker-compose.prod.yml exec -T web python3 scripts/prod_status.py || true

echo "=== smoke público ==="
SCREENSHOT_BASE_URL="${SCREENSHOT_BASE_URL:-http://127.0.0.1:5001}" \
  python3 scripts/smoke_playwright_public.py

echo "=== smoke auth ==="
docker compose -f docker-compose.prod.yml exec -T web python3 scripts/smoke_auth_flow.py

echo "=== verify backup ==="
bash scripts/verify_backup.sh || true

echo "Pacote de smoke OK"
