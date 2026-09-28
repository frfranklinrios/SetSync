# Decisões de produto (recomendação aplicada no código)

Itens da revisão de UX/produto. Onde a recomendação era clara, **já implementamos**.
O que ainda exige medição fica marcado.

## 1. Foco de produto — ✅ âncora em banda
Home lidera com banda (cifras / setlist / Modo Tocar). Igreja e estúdio viraram
extensões (barra de perfil + bloco compacto "Também serve…"), sem competir no hero.
Landings `/igrejas` e `/estudios` continuam intactas.

## 2. Tier gratuito x conversão — ✅ muro de valor (ago/2026)
Grátis = demo + até **3 cifras reais** + **1 abertura** do Modo Tocar.
**Banda / setlist / PDF / offline / Modo Tocar de ensaio** pedem Pro (R$ 29) ou Individual (R$ 15).
Limites de banda no Grátis: **3 músicas · 2 integrantes · 0 setlists**.
Extras Grátis (prova do aha): **1 evento · 1 freela/show · 1 fechamento de cachê**;
PDF do caixa da banda e WA «ensaio amanhã» = Pro.
**Sem trial automático**; trial Pro 7d **opt-in** no fechamento do show.
Pack **Noite pronta** no checkout Pro. Recuperação de checkout abandonado (in-app + e-mail).
Checkout Mercado Pago com default **mensal** (`?plano=&go=1`).
E-mail `activated_unpaid_3` para quem tocou e não pagou.

## 3. Complexidade de planos — ✅ página enxuta
Primeira dobra: **Grátis · Pro (destaque / Noite pronta) · Individual**.
Worship, estúdio e voucher ficam em `<details>`. Worship D0: 2ª banda após ativar.

## 4. Anúncios para usuário grátis — ✅ manter
Pagante, superadmin, Modo Tocar e PDF sem ads; grátis vê (freemium).

## 5. Isolamento de servidor — ✅ limites no compose
CPU/RAM em web, postgres, mail, api-cifras e Evolution. VPS dedicada continua
opcional se vizinhos ainda ruirem o host.

---
_Engenharia relacionada (Sentry opcional, backup, índices, CSRF, empty states) já
está no app. `SENTRY_DSN` no `.env` ativa o SDK._
