# Decisões de produto (recomendação aplicada no código)

Itens da revisão de UX/produto. Onde a recomendação era clara, **já implementamos**.
O que ainda exige medição fica marcado.

## 1. Foco de produto — ✅ âncora em banda
Home lidera com banda (cifras / setlist / Modo Tocar). Igreja e estúdio viraram
extensões (barra de perfil + bloco compacto "Também serve…"), sem competir no hero.
Landings `/igrejas` e `/estudios` continuam intactas.

## 2. Tier gratuito x conversão — ⏳ medir
Coleção pessoal + Modo Tocar grátis; **PDF e compartilhar** pedem plano
(**Individual** para solo sem banda / 1 integrante; Pro/Worship para banda).
Repertório da banda no grátis tem limites. Upsells no dashboard perto do limite.

## 3. Complexidade de planos — ✅ página enxuta
Primeira dobra: **Grátis · Pro (destaque) · Individual**.
Worship, estúdio e voucher ficam em `<details>`.

## 4. Anúncios para usuário grátis — ✅ manter
Pagante, superadmin, Modo Tocar e PDF sem ads; grátis vê (freemium).

## 5. Isolamento de servidor — ✅ limites no compose
CPU/RAM em web, postgres, mail, api-cifras e Evolution. VPS dedicada continua
opcional se vizinhos ainda ruirem o host.

---
_Engenharia relacionada (Sentry opcional, backup, índices, CSRF, empty states) já
está no app. `SENTRY_DSN` no `.env` ativa o SDK._
