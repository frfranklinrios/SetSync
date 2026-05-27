# Importador de cifras (módulo integrado `cifras_tool/`)

O SetSync possui uma ferramenta integrada em `/cifras/import/tool` que:

1. Raspa a cifra (Cifra Club / Cifras.com.br)
2. Resolve o áudio do YouTube e baixa/normaliza quando necessário
3. Gera uma **grade harmônica** e um pacote JSON compatível com SetSync
4. Envia o resultado de volta para o formulário (Adicionar/Editar) via `postMessage`

## Requisitos

- `ffmpeg` no PATH
- Dependências Python do projeto instaladas (inclui `yt-dlp`, `librosa`, `curl-cffi`, `beautifulsoup4`, `playwright`)

## Fluxo dentro do SetSync

- UI do iframe: `templates/cifras_tool/embed.html` + `static/cifras-tool/embed.js`
- Endpoint de processamento: `POST /cifras/import/api/processar`
- Download de artefatos: `GET /cifras/import/api/download/<job_id>/<arquivo>`

## Observações

- O processamento pode demorar alguns minutos (baixa/análise de áudio).
- Para alguns links do Cifra Club, o vídeo aparece em um player; nesses casos, o Playwright pode ser necessário.
- Se o YouTube bloquear downloads, configure `CIFRAS_YOUTUBE_COOKIES_FILE` apontando para um arquivo de cookies.

