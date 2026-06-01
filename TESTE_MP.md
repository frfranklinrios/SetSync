# Teste rápido — Mercado Pago

## 1. Cole o token no `.env`

Painel MP → **Credenciais de teste** → **Access Token** (não Public Key):

```env
MP_ACCESS_TOKEN_TEST=TEST-...ou-APP_USR-...
```

## 2. Um comando prepara tudo

```bash
cd /home/rios/Documentos/setsync
chmod +x scripts/preparar_teste_mp.sh
uv run bash scripts/preparar_teste_mp.sh
```

Isso valida o token, cria os planos e mostra os IDs para colar no `.env` (se ainda vazios).

## 3. Subir o app

```bash
uv run python main.py
```

- Login: `franklin` (banco copiado do VPS)
- **Planos** → **Assinar Pro**
- Cartão sandbox: `5031 4332 1540 6351`, CVV `123`

## 4. Testar sem pagar

- **Vouchers:** `/admin/vouchers` (superadmin `franklin`) ou resgate na página de planos
- **Limites grátis:** criar 31ª música → modal de upgrade

## Produção (depois)

No VPS, use credenciais de **produção** e renove tokens se foram expostos. Ver `MONETIZACAO.md`.
