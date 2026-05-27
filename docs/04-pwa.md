# PWA (instalação e offline)

O SetSync é servido como PWA:

- Manifest: `/manifest.webmanifest`
- Service worker: `/sw.js`
- Página offline: `/offline`
- Script de instalação: `static/js/pwa.js`

## Instalação

### Android / Chrome / Edge (desktop)

Use o botão **Instalar** na barra superior quando aparecer, ou o prompt do navegador.

### iPhone / iPad (Safari)

O iOS **não** exibe o prompt automático do Chrome. O botão **Instalar** abre um guia passo a passo:

1. Abra o site no **Safari** (não no Chrome do iOS).
2. Toque em **Compartilhar** (ícone com seta para cima).
3. Escolha **Adicionar à Tela de Início**.
4. Confirme em **Adicionar**.

Requisitos: site em **HTTPS** (produção). Em HTTP local o service worker não registra, mas “Adicionar à Tela de Início” ainda pode funcionar no Safari.

### Já instalado

Se o app abrir em tela cheia (sem barra do Safari), o botão Instalar some automaticamente.

## Cache e atualizações

O service worker mantém ícones, manifest e página `/offline`, e faz cache de páginas visitadas para uso sem rede.

Se alterou o app e o navegador não atualiza:

- **Desktop:** `Ctrl` + `Shift` + `R`
- **iOS:** Ajustes → Safari → Avançado → Dados dos Sites → remover o domínio do SetSync, ou desinstalar o ícone da tela inicial e adicionar de novo
- **Chrome:** DevTools → Application → Service Workers → Unregister

A versão do cache está em `CACHE_VERSION` dentro de `static/sw.js` (ex.: `setsync-v5`).

## Produção (nginx / proxy)

Garanta que o proxy encaminhe sem alterar:

- `GET /sw.js` com `Content-Type: application/javascript`
- `GET /manifest.webmanifest` com `Content-Type: application/manifest+json`
- Cabeçalho `Service-Worker-Allowed: /` no `/sw.js`

O app não deve enviar `Set-Cookie` nem variar o service worker por sessão (já tratado em `app.py`).
