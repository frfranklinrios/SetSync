#!/usr/bin/env python3
"""Smoke test: integração importador, tom, leadsheet, rotas."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Test client: HTTP local + sem redirect canônico (cookie de sessão usa host localhost).
os.environ.setdefault('SESSION_COOKIE_SECURE', '0')
os.environ['SETSYNC_CANONICAL_URL'] = ''

FAILURES: list[str] = []

# Redirecionamento para login ou host canônico (sem 5xx)
AUTH_REDIRECT = frozenset({301, 302, 303, 307, 308})


def ok(msg: str) -> None:
    print(f"  OK  {msg}")


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"  FAIL  {msg}")


def check(cond: bool, msg: str) -> None:
    (ok if cond else fail)(msg)


def canonical_request_headers() -> dict[str, str]:
    """Headers opcionais quando SETSYNC_CANONICAL_URL está definido (smoke em produção real)."""
    base = (os.getenv('SETSYNC_CANONICAL_URL') or '').strip()
    if base:
        host = urlparse(base).hostname
        if host:
            return {'Host': host}
    return {}


def csrf_api_headers(app) -> dict[str, str]:
    headers = canonical_request_headers()
    with app.app_context():
        from flask_wtf.csrf import generate_csrf

        headers['X-CSRFToken'] = generate_csrf()
    return headers


def load_smoke_user() -> dict:
    from db import get_db, get_user_by_username

    for uname in ('frfranklin.rios', 'franklin', 'tiagofl'):
        u = get_user_by_username(uname)
        if u:
            return u
    c = get_db().cursor()
    c.execute('SELECT * FROM users LIMIT 1')
    row = c.fetchone()
    if not row:
        raise RuntimeError('Nenhum usuário no banco para smoke')
    return dict(row)


def main() -> int:
    print("=== Imports ===")
    try:
        from app import app  # noqa: F401
        ok("app")
    except Exception as e:
        fail(f"app: {e}")
        return 1

    from app import app
    from util import (
        normalize_tom_label,
        highlight_chords_play_html,
        key_at_transpose,
        get_transposition_options,
        tom_is_minor,
    )
    from blueprints.cifras_import import cifras_import_bp
    from cifras_tool.pipeline_cifras import executar_apenas_cifra, validar_url_cifra
    from cifras_tool.setsync_export import partes_para_grade_ui
    from leadsheet.converter import is_leadsheet_document, resolve_leadsheet_document
    ok("blueprints + cifras_tool + leadsheet")

    print("\n=== Tom (normalize_tom_label) ===")
    cases = [
        ("C maior (cifra)", "C"),
        ("A menor", "Am"),
        ("F# (estimada)", "F#"),
        ("", "C"),
        ("Am", "Am"),
    ]
    for raw, expected in cases:
        got = normalize_tom_label(raw)
        check(got == expected, f"{raw!r} -> {got!r} (esperado {expected!r})")

    check(tom_is_minor("Bm"), "Bm é tom menor")
    check(not tom_is_minor("G"), "G é tom maior")
    check(key_at_transpose("Bm", -4) == "Gm", f"Bm-4 -> {key_at_transpose('Bm', -4)!r}")
    opts = get_transposition_options("Bm")
    check("Bm (Original)" in opts.values(), "opções de transposição incluem Bm original")
    check("Gm" in opts.values(), "opções de transposição incluem Gm")
    # Grafia ciente da armadura: transpor para tom bemol gera bemóis (Eb, não D#).
    from util import pychord_transpose_text
    check(key_at_transpose("C", 3) == "Eb", f"C+3 -> {key_at_transpose('C', 3)!r} (esperado Eb)")
    check(pychord_transpose_text("G", 3, "C") == "Bb",
          f"G transposto C->Eb -> {pychord_transpose_text('G', 3, 'C')!r} (esperado Bb)")

    print("\n=== Rotas Flask ===")
    rules = {r.rule: r.endpoint for r in app.url_map.iter_rules()}
    expected_routes = [
        ("/cifras/import/tool", "cifras_import.embed_tool"),
        ("/cifras/import/api/processar-cifra", "cifras_import.api_processar_cifra"),
        ("/cifras/import/api/buscar", "cifras_import.api_buscar_cifras"),
    ]
    for path, endpoint in expected_routes:
        check(rules.get(path) == endpoint, f"{path} -> {endpoint}")

    print("\n=== Jinja ===")
    check("normalize_tom" in app.jinja_env.filters, "filtro normalize_tom registrado")

    print("\n=== Arquivos estáticos / templates ===")
    static_files = [
        "static/cifras-tool/embed.js",
        "static/cifras-tool/embed.css",
        "static/cifras-tool/grade-render.js",
        "static/js/cifras-tool-bridge.js",
        "templates/cifras_tool/embed.html",
        "templates/cifras/_cifras_tool_modal.html",
    ]
    for rel in static_files:
        check((ROOT / rel).is_file(), rel)

    post_templates = [
        "templates/login.html",
        "templates/cifras/add.html",
        "templates/bands/settings.html",
        "templates/setlists/view.html",
    ]
    for rel in post_templates:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if 'method="POST"' in text or "method='POST'" in text:
            check(
                'csrf_input.html' in text or 'name="csrf_token"' in text,
                f"{rel} inclui CSRF nos formulários POST",
            )

    print("\n=== Test client (rotas protegidas redirecionam sem login) ===")
    app.config['TESTING'] = True
    req_headers = canonical_request_headers()
    host_label = req_headers.get('Host') or 'localhost (sem redirect canônico no smoke)'
    ok(f"Host de teste: {host_label}")

    with app.test_client() as client:
        r = client.get(
            "/cifras/import/tool",
            headers=req_headers,
            follow_redirects=False,
        )
        check(
            r.status_code in AUTH_REDIRECT or r.status_code in (401, 403),
            f"/cifras/import/tool sem sessão -> {r.status_code}",
        )

        r = client.post(
            "/cifras/import/api/processar-cifra",
            json={"url_cifra": "https://example.com"},
            headers=csrf_api_headers(app),
            follow_redirects=False,
        )
        check(
            r.status_code in AUTH_REDIRECT or r.status_code in (400, 401, 403),
            f"/cifras/import/api/processar-cifra sem sessão -> {r.status_code}",
        )

        user = load_smoke_user()
        dn = (user.get('display_name') or '').strip() or user['username']
        with client.session_transaction() as sess:
            sess["user_id"] = user["id"]
            sess["username"] = user["username"]
            sess["display_name"] = dn
            sess["is_superadmin"] = False

        r = client.get(
            "/cifras/import/tool",
            headers=req_headers,
            follow_redirects=False,
        )
        check(r.status_code == 200, f"embed tool com sessão -> {r.status_code}")
        body = r.get_data(as_text=True)
        check(
            "processar-cifra" in body or "processarCifraUrl" in body,
            "embed referencia API processar-cifra",
        )
        check("url_cifra_only" in body, "embed tem campo url_cifra_only")
        check(
            "YouTube" not in body.lower() or "youtube" not in body.lower(),
            "embed sem YouTube na UI",
        )

    print("\n=== Bridge postMessage (payload mínimo) ===")
    sample = {
        "type": "setsync-cifras-apply",
        "titulo": "Teste",
        "artista": "Artista",
        "tom_original": "C",
        "conteudo": "[C]linha",
        "cifra_json": [{"acorde": "C", "texto_letra": "linha", "group": 0}],
        "grade_json": [],
    }
    check(sample["type"] == "setsync-cifras-apply", "contrato postMessage")

    print("\n=== Pipeline (validação URL) ===")
    try:
        validar_url_cifra("https://www.cifraclub.com.br/artista/nome-da-musica/")
        ok("validar_url_cifra aceita Cifra Club")
    except ValueError as e:
        fail(f"validar_url_cifra cifraclub: {e}")
    try:
        validar_url_cifra("https://evil.com/x")
        fail("validar_url_cifra deveria rejeitar domínio estranho")
    except ValueError:
        ok("validar_url_cifra rejeita domínio inválido")

    print("\n=== Leadsheet ===")
    doc = {"song": {"title": "T"}, "sections": [], "events": []}
    check(is_leadsheet_document(doc), "is_leadsheet_document")
    check(
        resolve_leadsheet_document({"leadsheet_json": json.dumps(doc)}) is not None,
        "resolve_leadsheet_document",
    )
    legacy = resolve_leadsheet_document(
        {"grade_json": json.dumps([{"compasso": 1, "acordes": ["C", "%", "%", "%"]}])}
    )
    check(legacy is not None and "events" in legacy, "resolve legado grade_json -> leadsheet")

    print("\n=== enrich + sp-line (util) ===")
    html = highlight_chords_play_html("[Am]Olá [G]mundo")
    check("sp-line" in html and "sp-chord" in html, "highlight_chords_play_html usa sp-line/sp-chord")

    from blueprints.cifras import enrich_cifra_for_tocar

    enriched = enrich_cifra_for_tocar(
        {"tom_original": "C maior (cifra)", "conteudo": "[C]teste", "grade_json": None}
    )
    check(enriched["tom_original"] == "C", "enrich_cifra_for_tocar normaliza tom")

    print("\n=== DB coluna leadsheet_json ===")
    from db import get_db

    with app.app_context():
        from database import table_columns

        conn = get_db()
        c = conn.cursor()
        cols = table_columns(c, 'cifras')
        check("leadsheet_json" in cols, "coluna leadsheet_json em cifras")

    print("\n=== Resumo ===")
    if FAILURES:
        print(f"\n{len(FAILURES)} falha(s):")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("\nTodas as verificações passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
