# Screenshots de marketing (rotação diária)

Assets usados na seção **Veja o Uníssono em ação** e nas landings.

## Packs

| Pack | Onde | Repertório |
|------|------|------------|
| `br` | `/bandas`, home | Músicas brasileiras |
| `gospel` | `/igrejas` | Louvor / gospel |
| `estudio` | `/estudios`, home | Painel + financeiro rico |

## Rotação

- Job diário **03:15** (Fortaleza) regenera o slot do dia (`day % 7`).
- Arquivos vivos em `data/screenshots/{pack}/slot-N/` e espelho em `…/current/`.
- URL pública: `/marketing/shots/<pack>/<nome>.png?v=YYYYMMDD`
- Fallback: PNGs antigos em `static/screenshots/` se ainda não houver captura.

## Regenerar agora

```bash
# no host (com app rodando) ou no container web:
python3 scripts/seed_marketing_screenshots.py
SCREENSHOT_BASE_URL=http://127.0.0.1:5000 python3 scripts/capture_marketing_screenshots.py
```

No Docker:

```bash
docker exec setsync-web-1 python3 scripts/capture_marketing_screenshots.py
```
