# Importador de cifras (módulo integrado `cifras_tool/`)

O SetSync possui uma ferramenta integrada em `/cifras/import/tool` que:

1. Raspa a cifra (Cifra Club / Cifras.com.br)
2. Gera uma **grade harmônica** a partir dos acordes da cifra
3. Monta o pacote JSON compatível com SetSync
4. Envia o resultado de volta para o formulário (Adicionar/Editar) via `postMessage`

## Requisitos

- `ffmpeg` no PATH
- Dependências Python do projeto instaladas (inclui `yt-dlp`, `librosa`, `curl-cffi`, `beautifulsoup4`, `playwright`)

## Fluxo dentro do SetSync

- UI do iframe: `templates/cifras_tool/embed.html` + `static/cifras-tool/embed.js`
- Endpoint de processamento: `POST /cifras/import/api/processar-cifra`
- Busca na biblioteca local: `GET /cifras/import/api/buscar?q=...` e `GET /cifras/import/api/api-cifras/<artista>/<musica>`
- Download de artefatos: `GET /cifras/import/api/download/<job_id>/<arquivo>`

## Observações

- A raspagem pode levar alguns segundos (Playwright em links com player embutido no Cifra Club).
- Tudo roda no mesmo processo Flask deste repositório; não há dependência de pasta irmã nem de outro servidor.

