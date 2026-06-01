#!/usr/bin/env bash
# Prepara Mercado Pago para teste local: valida .env e cria planos no sandbox.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Arquivo .env não encontrado. Copie .env.example ou use o .env da raiz do projeto."
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

echo "=== SetSync — preparar teste Mercado Pago ==="
echo "Ambiente: ${MP_ENVIRONMENT:-sandbox}"
echo ""

if [[ -z "${MP_ACCESS_TOKEN_TEST:-}" ]] && [[ "${MP_ENVIRONMENT:-sandbox}" != "production" ]]; then
  echo "⚠  Edite .env e preencha MP_ACCESS_TOKEN_TEST (Access Token de TESTE do painel MP)."
  echo "   Credenciais de teste: https://www.mercadopago.com.br/developers/panel/app"
  echo ""
fi

if [[ "${MP_ENVIRONMENT:-sandbox}" == "production" ]]; then
  export MP_ACCESS_TOKEN="${MP_ACCESS_TOKEN:-}"
else
  export MP_ACCESS_TOKEN="${MP_ACCESS_TOKEN_TEST:-${MP_ACCESS_TOKEN:-}}"
fi

echo "→ Verificando dependências..."
uv run python -c "import mercadopago" 2>/dev/null || uv pip install mercadopago

echo ""
echo "→ Verificando configuração..."
if ! uv run python scripts/test_mp_sandbox.py check; then
  echo ""
  echo "Corrija o .env e rode este script de novo."
  exit 1
fi

if [[ -z "${MP_PLAN_PRO_ID:-}" ]] || [[ -z "${MP_PLAN_WORSHIP_ID:-}" ]]; then
  echo ""
  echo "→ Criando planos Pro e Worship no Mercado Pago..."
  uv run python scripts/criar_planos_mp.py | tee /tmp/setsync_mp_planos.txt
  echo ""
  echo "Copie as linhas MP_PLAN_PRO_ID e MP_PLAN_WORSHIP_ID para o seu .env"
  echo "(arquivo temporário: /tmp/setsync_mp_planos.txt)"
else
  echo ""
  echo "✓ Planos já definidos no .env"
fi

echo ""
echo "=== Próximo passo ==="
echo "  uv run python main.py"
echo "  Abra http://127.0.0.1:5000 → login → Planos → Assinar Pro"
echo ""
echo "Cartão teste (sandbox): 5031 4332 1540 6351 | CVV 123 | validade futura"
echo "Usuário teste MP: test_user@testuser.com (cadastre no painel de desenvolvedores)"
