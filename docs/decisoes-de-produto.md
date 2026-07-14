# Decisões de produto pendentes (precisam da sua escolha)

Itens levantados na revisão de UX/produto que **não** foram implementados porque
são decisões de negócio/estratégia — não bugs. Cada um com a recomendação.

## 1. Foco de produto
Hoje o app abraça Banda (cifras/setlist), **Estúdios** (marketplace), **Igrejas/Worship**
e integração WhatsApp. É muita superfície para um time pequeno; a home tenta vender
todos ao mesmo tempo.
**Recomendação:** eleger um "produto-âncora" (provavelmente banda) e tratar os demais
como extensões, simplificando a home ao redor dele.

## 2. Tier gratuito x conversão (tensão introduzida)
A coleção pessoal ilimitada + Modo Tocar grátis destrava ativação, mas entrega quase
tudo ao músico solo — o gatilho pago virou só "compartilhar".
**Recomendação:** medir a conversão solo→Individual por algumas semanas (painel admin →
Ativação/Stickiness). Se cair, colocar um limite *suave* no grátis (ex.: recursos
avançados/PDF no pago) sem voltar a bloquear o "aha".

## 3. Complexidade de planos
Individual/Pro/Worship/Premium/Estúdio é muita opção — decisão difícil não converte.
**Recomendação:** reduzir a página de planos a 2–3 escolhas óbvias por persona.

## 4. Anúncios para usuário grátis logado
O gating atual já é sensato: **pagante, superadmin, Modo Tocar e PDF não veem ads**;
só o plano grátis vê (freemium clássico). Remover ads do grátis = abrir mão de receita.
**Recomendação:** manter como está, salvo decisão de posicionamento premium.

## 5. Isolamento de servidor (infra)
O host roda ~14 containers de projetos diferentes junto do app. Um vizinho pesado pode
degradar o app no meio de um culto/ensaio.
**Recomendação:** isolar o Uníssono (VPS dedicada ou limites de CPU/memória no compose).

---
_As melhorias de engenharia relacionadas (telefone opcional, painel admin sem trabalho
duplicado, CI, backup agendado, índices, logs, Sentry opcional) já foram implementadas._
