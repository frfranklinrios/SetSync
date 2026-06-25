# Monetização SetSync — Mercado Pago

Guia para configurar planos pagos, webhooks e vouchers no SetSync.

## 1. Conta Mercado Pago

1. Crie uma conta em [https://www.mercadopago.com.br](https://www.mercadopago.com.br).
2. Acesse **Suas integrações** → **Credenciais**.
3. Copie o **Access Token de produção** (`APP_USR-...`) e o de **teste** (`TEST-...` ou `APP_USR-` no modo teste).

## 2. Variáveis de ambiente

Adicione ao `.env` na raiz do projeto:

| Variável | Descrição |
|----------|-----------|
| `MP_ACCESS_TOKEN` | Token de **produção** (`APP_USR-...`) |
| `MP_ACCESS_TOKEN_TEST` | Token de **sandbox** para desenvolvimento |
| `MP_WEBHOOK_SECRET` | Segredo para validar notificações (`x-signature`) |
| `MP_PLAN_INDIVIDUAL_ID` | ID do plano Individual (R$ 15/mês) — referência no painel MP |
| `MP_PLAN_PRO_ID` | ID do plano de recorrência Pro (R$ 29/mês) |
| `MP_PLAN_WORSHIP_ID` | ID do plano Worship (R$ 69/mês) |
| `MP_ENVIRONMENT` | `sandbox` ou `production` |
| `MP_BACK_URL` | URL opcional usada ao criar planos via script |
| `SETSYNC_WHATSAPP` | Número WhatsApp na landing `/igrejas` (ex: `5511999999999`) |

### E-mail (vouchers e avisos)

Opcional até configurar SMTP. Sem `MAIL_PASSWORD`, o app funciona — só não envia e-mails.

| Variável | Descrição |
|----------|-----------|
| `MAIL_SERVER` | Ex: `smtp.zoho.com` (Registro.br + Zoho) ou `smtp.gmail.com` (Google Workspace) |
| `MAIL_PORT` | `587` (TLS) ou `465` (SSL) |
| `MAIL_USE_TLS` | `1` na porta 587 |
| `MAIL_USE_SSL` | `1` na porta 465 |
| `MAIL_USERNAME` | Ex: `contato@setsync.com.br` |
| `MAIL_PASSWORD` | Senha da caixa ou senha de app |
| `MAIL_DEFAULT_SENDER` | Ex: `SetSync <contato@setsync.com.br>` |

Teste: `python scripts/send_test_email.py seu@email.com`

## 3. Criar planos de recorrência

Com o token configurado:

```bash
export MP_ACCESS_TOKEN=APP_USR-...
python3 scripts/criar_planos_mp.py
```

O script imprime algo como:

```
MP_PLAN_PRO_ID=2c938084...
MP_PLAN_WORSHIP_ID=2c938084...
```

Copie os valores para o `.env`.

> **Checkout:** o SetSync cria a assinatura **sem** `preapproval_plan_id` (valores R$ 29 / R$ 69 em `monetizacao.py`) e redireciona ao `init_point` do MP. Com plano associado na API, o MP exige `card_token_id` (checkout transparente). Os `MP_PLAN_*` servem para validação e referência no painel.

## 4. Webhook no painel Mercado Pago

1. Em **Suas integrações** → sua aplicação → **Webhooks**.
2. URL de produção: `https://setsync.dados.tec.br/assinatura/webhook`
3. Eventos recomendados:
   - `subscription_preapproval`
   - `payment`
4. Defina o mesmo valor de `MP_WEBHOOK_SECRET` no painel (assinatura `x-signature`).

Em desenvolvimento local, use [ngrok](https://ngrok.com/) ou similar para expor a porta 5000.

## 5. Sandbox vs produção

| `MP_ENVIRONMENT` | Token usado | URL de checkout |
|------------------|-------------|-----------------|
| `sandbox` | `MP_ACCESS_TOKEN_TEST` | `sandbox_init_point` |
| `production` | `MP_ACCESS_TOKEN` | `init_point` |

O código em `mercadopago_client.checkout_init_point()` escolhe automaticamente.

### Cartões de teste (sandbox)

Consulte a documentação oficial: [Cartões de teste](https://www.mercadopago.com.br/developers/pt/docs/checkout-api/integration-test/test-cards).

Exemplos comuns:

- **Aprovado:** Mastercard `5031 4332 1540 6351`, CVV `123`, validade futura.
- **Recusado:** use os cartões listados como recusados na doc do MP.

## 6. Rotas implementadas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/assinatura/planos` | Página de planos + resgate de voucher |
| POST | `/assinatura/iniciar/<plano>` | Inicia checkout MP (`pro` ou `worship`) |
| GET | `/assinatura/sucesso` | Retorno após aprovação |
| GET | `/assinatura/pendente` | Pagamento pendente |
| GET | `/assinatura/falha` | Pagamento recusado |
| POST | `/assinatura/webhook` | IPN Mercado Pago |
| GET | `/setlist/<id>/exportar-pdf` | PDF premium (WeasyPrint) |
| GET | `/igrejas` | Landing para igrejas |
| POST | `/voucher/resgatar` | Resgate AJAX |
| GET/POST | `/voucher/indicar` | Voucher de indicação |
| GET | `/admin/vouchers` | Painel admin (superadmin) |

## 7. Planos e limites

| Plano | Preço | Limites |
|-------|-------|---------|
| Grátis | R$ 0 | 30 músicas, 5 integrantes, 10 setlists, 1 banda (owner) |
| Pro | R$ 29/banda/mês | Sem limites + PDF |
| Worship | R$ 69/congregação/mês | Múltiplas bandas, sem limites |

## 8. Vouchers

- Admin: `/admin/vouchers` (requer `SETSYNC_SUPERADMIN_*` no `.env`).
- **Vitalício:** marque a opção ao criar — acesso ao plano sem vencimento (ignorado pelo job de expiração).
- Indicação: `/voucher/indicar` — até 5 vouchers ativos por usuário (Pro, 15 dias, uso único).
- Job diário (06:00 UTC): expira vouchers e envia e-mails de aviso (3 dias antes e no vencimento).

## 9. Dependências de sistema

### WeasyPrint (PDF)

```bash
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libcairo2
pip install weasyprint
```

### Python

```bash
pip install mercadopago APScheduler weasyprint
# ou
uv sync
```

## 10. Testar em sandbox (passo a passo)

### 10.1 Configurar `.env`

```env
FLASK_ENV=development
MP_ENVIRONMENT=sandbox
MP_ACCESS_TOKEN_TEST=TEST-...          # credencial de teste do painel MP
MP_WEBHOOK_SECRET=minha-chave-secreta-teste
MP_PLAN_PRO_ID=...                     # saída do criar_planos_mp.py
MP_PLAN_WORSHIP_ID=...
```

Crie os planos com o **mesmo token de teste**:

```bash
export MP_ACCESS_TOKEN=$MP_ACCESS_TOKEN_TEST
python3 scripts/criar_planos_mp.py
```

### 10.2 Script de verificação

```bash
python3 scripts/test_mp_sandbox.py check
```

Deve listar ✓ para token, planos e API.

### 10.3 Checkout manual no navegador

1. `python3 main.py` (ou `uv run python main.py`)
2. Faça login, vá em **Planos** → **Assinar Pro**
3. No checkout sandbox, use um **usuário de teste** do MP (mesmo e-mail cadastrado no painel de desenvolvedores, ex: `test_user@testuser.com`)
4. Cartão aprovado (exemplo Mastercard): `5031 4332 1540 6351`, CVV `123`, validade futura, CPF `12345678909`

Após pagar, você deve voltar para `/assinatura/sucesso` e ver plano **ativa**.

### 10.4 Testar webhook com ngrok

O Mercado Pago precisa alcançar sua máquina:

```bash
# Terminal 1
python3 main.py

# Terminal 2
ngrok http 5000
```

No painel MP → Webhooks → URL:

```text
https://SEU-ID.ngrok-free.app/assinatura/webhook?secret=minha-chave-secreta-teste
```

Eventos: `subscription_preapproval`, `payment`.

> O parâmetro `?secret=` equivale ao header `X-Webhook-Secret` e deve ser igual a `MP_WEBHOOK_SECRET`.

### 10.5 Simular webhook localmente (sem ngrok)

Com o app rodando e uma assinatura já criada:

```bash
python3 scripts/test_mp_sandbox.py webhook \
  --preapproval-id 2c938084726fca480172750000000000 \
  --secret minha-chave-secreta-teste
```

Confira os logs do Flask (`Webhook MP recebido…`) e o SQLite:

```bash
sqlite3 data/banda.db "SELECT banda_id, plano, status FROM assinaturas;"
```

### 10.6 Criar preapproval só pela API (debug)

```bash
python3 scripts/test_mp_sandbox.py preapproval --email test_user@testuser.com
```

Abra o `init_point` / `sandbox_init_point` impresso no terminal.

## 11. Produção (setsync.dados.tec.br)

1. `MP_ENVIRONMENT=production`
2. `MP_ACCESS_TOKEN=APP_USR-...` (produção)
3. Webhook: `https://setsync.dados.tec.br/assinatura/webhook` (sem `?secret=` se usar só `x-signature` do painel)
4. Recrie ou use planos criados com token de produção nos IDs do `.env`

## 12. Testar fluxo completo no app

1. `MP_ENVIRONMENT=sandbox` e token de teste no `.env`.
2. Rode `python3 scripts/criar_planos_mp.py` com token de teste.
3. Inicie o app: `uv run python main.py`.
4. Acesse `/assinatura/planos`, escolha banda e assine Pro.
5. Use cartão de teste no checkout.
6. Confirme assinatura ativa no banco (`assinaturas.status = ativa`).
7. Teste exportar PDF em `/setlists/<id>/exportar-pdf`.

## 13. HTTP 402 no frontend

O script `static/js/plano-limite.js` intercepta respostas `402` com `erro: limite_plano` ou `plano_necessario` e abre modal com link para `/assinatura/planos`.

## 14. Google AdSense (plano grátis)

Anúncios aparecem **somente** quando a banda em contexto (ou todas as bandas do dono) está no **plano grátis**, sem Pro/Worship/voucher ativo. Usuários com Worship ativa, superadmin ou qualquer banda própria premium **não** veem anúncios.

### Variáveis

| Variável | Descrição |
|----------|-----------|
| `ADSENSE_ENABLED` | `1` para ligar (padrão: ligado se `ADSENSE_CLIENT` estiver definido) |
| `ADSENSE_CLIENT` | ID do editor (`ca-pub-...`) do painel AdSense |
| `ADSENSE_SLOT_FOOTER` | Slot opcional do bloco no rodapé das páginas |
| `ADSENSE_SLOT_CONTENT` | Slot opcional (use `{% block adsense_content %}` nos templates) |

### Onde entra no site

- Layout principal (`templates/index.html`): script no `<head>` e slot acima do footer.
- Páginas públicas (home, planos) e usuários grátis logados.
- Link público de letras (`/setlists/letras/<token>`) se a banda for grátis.
- **Sem** anúncios: login/registro, admin, modo tocar, impressão/PDF.

### Ativar em produção

1. Aprove a conta no [Google AdSense](https://www.google.com/adsense/) com o domínio `https://setsync.com.br`.
2. Copie o **data-ad-client** (`ca-pub-...`) para o `.env` da VPS.
3. Confirme `https://setsync.com.br/ads.txt` (arquivo na raiz + Nginx na borda). No AdSense → **Sites** → verificar ads.txt → **Verificar novamente** após deploy.
4. No AdSense → **Anúncios** → **Por unidade de anúncio** → **Display ads** → responsivo; copie o número de `data-ad-slot` para `ADSENSE_SLOT_FOOTER` no `.env` (melhora preenchimento e relatórios).
5. Rebuild do container: `docker compose -f docker-compose.prod.yml up -d --build`.

Teste local da lógica (sem rede):

```bash
python3 scripts/test_adsense_eligibility.py
```

> **LGPD:** se exigir consentimento de cookies para publicidade, adicione um banner de opt-in antes de carregar o script — o SetSync hoje só prepara a carga condicional por plano.

## Plano Estúdio (beta gratuito)

Módulo de agendamento de salas de ensaio (`/estudios`). Na v1 **não há cobrança** via Mercado Pago.

| Plano | ID interno | Limite |
|-------|------------|--------|
| Estúdio básico | `estudio_basico` | até **2 salas** por dono (padrão no beta) |
| Estúdio premium | `estudio_premium` | salas ilimitadas (futuro) |

- Assinatura em `studio_subscriptions` (por `user_id` do dono), criada automaticamente no cadastro.
- Checkout MP e taxa sobre agendamentos ficam como item futuro.
