# Google Ads — monitorar inscrições (cadastros)

O SetSync dispara uma **conversão de inscrição** quando alguém cria conta (formulário ou Google OAuth).

## URL para o assistente do Google Ads

No passo **“Onde você quer medir isso?”** → **URL**:

| Campo | Valor |
|-------|--------|
| **Tipo** | A URL contém |
| **URL** | `setsync.com.br/auth/cadastro-concluido` |

URL completa (referência): `https://setsync.com.br/auth/cadastro-concluido`

Só quem acabou de se cadastrar passa por essa página (uma vez). Quem acessa o link direto é redirecionado sem contar conversão de novo.

## 1. Obter os IDs no Google Ads

1. Acesse [Google Ads](https://ads.google.com/) → **Objetivos** → **Conversões**.
2. Crie uma conversão do tipo **Inscrição** (ou **Cadastro**) para `https://setsync.com.br`.
3. Anote:
   - **ID de conversão** (`AW-XXXXXXXXX`)
   - **Rótulo de conversão** (string após a barra, ex.: `AbCdEfGhIjK`)

Opcional: vincule o [Google Analytics 4](https://analytics.google.com/) e use o ID de medição `G-XXXXXXXX`.

## 2. Configurar o `.env`

### Opção A — tag direta (mais simples)

```env
GOOGLE_ADS_ENABLED=1
GOOGLE_ADS_ID=AW-XXXXXXXXX
GOOGLE_ADS_CONVERSION_SIGNUP=AbCdEfGhIjK
GOOGLE_ANALYTICS_ID=G-XXXXXXXX          # opcional
GOOGLE_ADS_CONVERSION_VALUE=1.0         # opcional
GOOGLE_ADS_CONVERSION_CURRENCY=BRL      # opcional
```

### Opção B — Google Tag Manager (recomendado para várias tags)

```env
GOOGLE_ADS_ENABLED=1
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX
```

No GTM, crie:

1. **Acionador** — evento personalizado: `setsync_signup`
2. **Tag** — Conversão do Google Ads usando esse acionador

O app envia no `dataLayer`:

```javascript
{ event: 'setsync_signup', conversion_value: 1.0, conversion_currency: 'BRL' }
```

## 3. Validar

```bash
docker compose -f docker-compose.prod.yml exec web python3 scripts/validar_google_ads.py
```

Teste real: abra o site em aba anônima, conclua um cadastro e verifique em **Google Ads → Conversões** (pode levar algumas horas ou use a extensão **Tag Assistant**).

## 4. Deploy

Após alterar o `.env`:

```bash
docker compose -f docker-compose.prod.yml up -d web
```

## Debug

```env
GOOGLE_ADS_DEBUG=1
```

No navegador, abra o console após cadastrar — deve aparecer `[SetSync] Google Ads signup conversion` ou `GTM event: setsync_signup`.
