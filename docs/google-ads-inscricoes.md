# Google Ads — monitorar inscrições (cadastros)

O Uníssono dispara uma **conversão de inscrição** quando alguém cria conta (formulário ou Google OAuth).

## URL para o assistente do Google Ads

No passo **“Onde você quer medir isso?”** → **URL**:

| Campo | Valor |
|-------|--------|
| **Tipo** | A URL contém |
| **URL** | `unissono.app/auth/cadastro-concluido` |

URL completa (referência): `https://unissono.app/auth/cadastro-concluido`

Só quem acabou de se cadastrar passa por essa página (uma vez). Quem acessa o link direto é redirecionado sem contar conversão de novo.

## 1. Obter os IDs no Google Ads

1. Acesse [Google Ads](https://ads.google.com/) → **Objetivos** → **Conversões**.
2. Crie uma conversão do tipo **Inscrição** (ou **Cadastro**) para `https://unissono.app`.
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

### Funil (rótulos opcionais)

Sem rótulo dedicado, o app ainda dispara eventos GA4 `setsync_<evento>` (ex.: `setsync_primeira_banda`). Com rótulo no `.env`, vira conversão Ads:

```env
GOOGLE_ADS_CONVERSION_PRIMEIRA_BANDA=
GOOGLE_ADS_CONVERSION_PRIMEIRA_CIFRA=
GOOGLE_ADS_CONVERSION_TRIAL=
GOOGLE_ADS_CONVERSION_PAGO=
```

### Opção B — Google Tag Manager

```env
GOOGLE_ADS_ENABLED=1
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX
```

Eventos no dataLayer: `setsync_signup`, `setsync_primeira_banda`, etc.

## 3. Conferir

1. Cadastre uma conta de teste em `https://unissono.app/auth/register`.
2. Você deve cair em `/auth/cadastro-concluido` e o Tag Assistant / debug Ads deve mostrar a conversão.
3. Em produção, confirme domínio canônico `SETSYNC_CANONICAL_URL=https://unissono.app`.
