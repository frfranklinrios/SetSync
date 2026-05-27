# Visão geral — SetSync

O SetSync é um gerenciador de **cifras** e **setlists** para bandas, com foco em execução ao vivo:

- Cadastro de bandas e músicas
- Cifras com destaque de acordes e suporte a tablaturas
- Transposição de tom sem reescrever a cifra
- **Modo Tocar** (tela cheia, atalhos, 2 colunas, auto-scroll)
- Importação assistida de cifras e grade harmônica via módulo integrado `cifras_tool/`

## Conceitos

- **Banda**: agrupador principal de músicas e setlists.
- **Cifra**: letra + acordes (com tom de referência). Pode incluir tablaturas.
- **Setlist**: lista ordenada de cifras para uma apresentação/ensaio.
- **Modo Tocar**: visualização otimizada para palco; a cifra pode ser transposta em tempo real.

## Onde ficam as coisas

- **Backend**: Flask em `app.py` + blueprints em `blueprints/`.
- **Banco**: SQLite (arquivo em `data/` por padrão).
- **Templates**: Jinja2 em `templates/`.
- **PWA**: `static/sw.js`, `static/manifest.webmanifest` e ícones em `static/icons/`.
- **Importador de cifras**: `blueprints/cifras_import.py` + pacote `cifras_tool/` + UI em `templates/cifras_tool/embed.html`.

