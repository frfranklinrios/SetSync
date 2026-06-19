from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
    session,
)

from blueprints.auth import login_required
from cifra_referencia import build_referencia_snapshot, meta_from_import_payload
from cifras_tool.pipeline_cifras import (
    executar_apenas_cifra,
    validar_url_cifra,
)
from cifras_tool.api_cifras_client import (
    ApiCifrasError,
    get_cifra_setsync,
    search_songs,
)
from cifras_tool.setsync_export import partes_para_grade_ui
from security import check_rate_limit

cifras_import_bp = Blueprint("cifras_import", __name__, url_prefix="/cifras/import")

OWNER_FILE = ".owner"


def _exports_dir() -> Path:
    root = Path(current_app.root_path)
    pasta = root / "data" / "cifras_exports"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _job_owned_by_user(job_id: str, user_id: str) -> bool:
    owner_path = _exports_dir() / job_id / OWNER_FILE
    if not owner_path.is_file():
        return False
    return owner_path.read_text(encoding="utf-8").strip() == user_id


def _resposta_processamento(resultado, job_id: str, *, embed: bool = True):
    setsync = resultado.setsync
    base = f"/cifras/import/api/download/{job_id}"
    downloads = {
        "setsync_cifra": f"{base}/setsync_cifra.json",
        "setsync_grade": f"{base}/setsync_grade.json",
        "setsync_upload": f"{base}/setsync_upload.json",
    }
    if not embed and resultado.mp3.is_file():
        downloads["mp3"] = f"{base}/mp3"

    return jsonify(
        {
            "job_id": job_id,
            "embed": embed,
            "titulo": resultado.titulo,
            "artista": resultado.artista,
            "tom": resultado.tonalidade,
            "compasso": resultado.compasso,
            "bpm": resultado.bpm,
            "duracao_seg": resultado.duracao_seg,
            "cifra": resultado.cifra,
            "grade": resultado.grade_harmonica,
            "grade_partes": partes_para_grade_ui(resultado.partes_grade),
            "grade_progressao": resultado.grade_progressao_cifra,
            "setsync_cifra": setsync["cifra_json"],
            "setsync_grade": setsync["grade_json"],
            "setsync_upload": setsync,
            "downloads": downloads,
            "mp3_filename": resultado.mp3.name if resultado.mp3.is_file() else None,
            "modo": "audio" if resultado.bpm is not None else "cifra",
        }
    )


@cifras_import_bp.route("/tool")
@login_required
def embed_tool():
    return render_template("cifras_tool/embed.html")


@cifras_import_bp.route("/tool/embed")
@login_required
def embed_tool_legacy():
    return render_template("cifras_tool/embed.html")


@cifras_import_bp.route("/api/processar-cifra", methods=["POST"])
@login_required
def api_processar_cifra():
    """Somente raspagem da cifra + grade pelos acordes."""
    user_id = session["user_id"]
    rate_key = f'import:{user_id}'
    if not check_rate_limit(rate_key, max_attempts=15, window_sec=3600):
        return jsonify({"detail": "Limite de importações por hora atingido. Tente mais tarde."}), 429

    corpo = request.get_json(silent=True) or {}
    url_cifra = (corpo.get("url_cifra") or "").strip()
    compasso = corpo.get("compasso")
    embed = bool(corpo.get("embed", True))

    if len(url_cifra) < 8:
        return jsonify({"detail": "Informe o link da cifra."}), 400

    job_id = str(uuid.uuid4())
    pasta_job = _exports_dir() / job_id

    try:
        validar_url_cifra(url_cifra)
        resultado = executar_apenas_cifra(
            url_cifra,
            pasta_saida=pasta_job,
            compasso_manual=compasso,
        )
        (pasta_job / OWNER_FILE).write_text(user_id, encoding="utf-8")
    except ValueError as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": str(erro)}), 400
    except Exception as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": f"Falha no processamento: {erro}"}), 500

    return _resposta_processamento(resultado, job_id, embed=embed)


def _resposta_api_cifras(pacote: dict) -> dict:
    return {
        "titulo": pacote.get("titulo"),
        "artista": pacote.get("artista"),
        "tom_original": pacote.get("tom_original"),
        "tom": pacote.get("tom_original"),
        "conteudo": pacote.get("conteudo"),
        "cifra_json": pacote.get("cifra_json"),
        "grade_json": pacote.get("grade_json"),
        "grade_partes": pacote.get("grade_partes"),
        "bpm": pacote.get("bpm"),
        "duracao_seg": pacote.get("duracao_seg"),
        "url_cifra": pacote.get("url_cifra"),
        "artist_slug": pacote.get("artist_slug"),
        "song_slug": pacote.get("song_slug"),
        "cached": bool(pacote.get("cached")),
        "modo": "api-cifras",
    }


@cifras_import_bp.route("/api/preview", methods=["POST"])
@login_required
def api_preview_cifra():
    """Renderiza HTML da cifra para exibição no modal (sem salvar)."""
    from cifra_user_draft import cifra_dict_from_import
    from blueprints.cifras import prepare_cifra_sheet

    data = request.get_json(silent=True) or {}
    fake = cifra_dict_from_import(data)
    if not (fake.get('conteudo') or fake.get('cifra_json') or fake.get('grade_json')):
        return jsonify({"detail": "Cifra sem conteúdo para visualizar."}), 400

    sheet = prepare_cifra_sheet(fake)
    html = render_template("partials/cifra_sheet_body.html", sheet=sheet)
    return jsonify({
        "titulo": fake.get("titulo"),
        "artista": fake.get("artista"),
        "tom_original": fake.get("tom_original"),
        "html": html,
        "has_content": bool(sheet.get("has_content")),
    })


@cifras_import_bp.route("/api/para-banda/<band_id>", methods=["POST"])
@login_required
def api_import_para_banda(band_id: str):
    """Importa cifra da biblioteca direto para o repertório da banda."""
    from flask import url_for
    import json

    from db import count_band_cifras, create_cifra, get_band, is_band_editor
    import band_notifications as bn
    from monetizacao import check_limite, LIMITES_GRATIS

    user_id = session["user_id"]
    band = get_band(band_id)
    if not band or not is_band_editor(band_id, user_id):
        return jsonify({"detail": "Sem permissão para importar nesta banda."}), 403

    rate_key = f'import:{user_id}'
    if not check_rate_limit(rate_key, max_attempts=30, window_sec=3600):
        return jsonify({"detail": "Limite de importações por hora atingido. Tente mais tarde."}), 429

    if not check_limite(band, 'musica'):
        return jsonify({
            "detail": f"Limite do plano atingido ({LIMITES_GRATIS['musica']} músicas).",
            "upgrade": True,
        }), 402

    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo") or "").strip()
    artista = (data.get("artista") or "").strip()
    if not titulo or not artista:
        return jsonify({"detail": "Título e artista são obrigatórios."}), 400

    tom_original = (data.get("tom_original") or data.get("tom") or "C").strip()
    conteudo = data.get("conteudo") or ""
    cifra_json = data.get("cifra_json")
    grade_json = data.get("grade_json")
    if cifra_json is not None and not isinstance(cifra_json, str):
        cifra_json = json.dumps(cifra_json, ensure_ascii=False)
    if grade_json is not None and not isinstance(grade_json, str):
        grade_json = json.dumps(grade_json, ensure_ascii=False)

    referencia_json = build_referencia_snapshot(
        source="api-cifras",
        titulo=titulo,
        artista=artista,
        tom_original=tom_original,
        conteudo=conteudo,
        cifra_json=cifra_json,
        grade_json=grade_json,
        meta=meta_from_import_payload(data),
    )

    cifras_antes = count_band_cifras(band_id)
    cifra_id = create_cifra(
        titulo,
        artista,
        tom_original,
        conteudo,
        band_id,
        cifra_json=cifra_json,
        grade_json=grade_json,
        bpm=data.get("bpm"),
        duracao_seg=data.get("duracao_seg"),
        referencia_json=referencia_json,
    )
    if cifras_antes == 0:
        from google_ads import mark_funnel_event
        mark_funnel_event('primeira_cifra')
    bn.cifra_created(band_id, user_id, cifra_id, titulo)

    return jsonify({
        "cifra_id": cifra_id,
        "titulo": titulo,
        "view_url": url_for("cifras.view", cifra_id=cifra_id),
        "edit_url": url_for("cifras.edit", cifra_id=cifra_id),
    })


@cifras_import_bp.route("/api/buscar")
@login_required
def api_buscar_cifras():
    user_id = session["user_id"]
    rate_key = f'api-cifras-search:{user_id}'
    if not check_rate_limit(rate_key, max_attempts=120, window_sec=3600):
        return jsonify({"detail": "Limite de buscas por hora atingido. Tente mais tarde."}), 429

    q = (request.args.get("q") or "").strip()
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20

    try:
        payload = search_songs(q, limit=limit)
    except ApiCifrasError as erro:
        status = 503 if erro.status_code is None else 400
        return jsonify({"detail": str(erro)}), status

    return jsonify(payload)


@cifras_import_bp.route("/api/api-cifras/<artist_slug>/<song_slug>")
@login_required
def api_import_api_cifras(artist_slug: str, song_slug: str):
    """Importa cifra do cache local (api-cifras) ou busca online se solicitado."""
    user_id = session["user_id"]
    rate_key = f'import:{user_id}'
    if not check_rate_limit(rate_key, max_attempts=30, window_sec=3600):
        return jsonify({"detail": "Limite de importações por hora atingido. Tente mais tarde."}), 429

    scrape = request.args.get("scrape", "1").lower() in ("1", "true", "yes")

    try:
        pacote = get_cifra_setsync(artist_slug, song_slug)
        return jsonify(pacote)
    except ApiCifrasError as erro:
        if erro.status_code != 404 or not scrape:
            status = 404 if erro.status_code == 404 else 503
            return jsonify({"detail": str(erro)}), status

    url_cifra = (
        f"https://www.cifraclub.com.br/{artist_slug.strip('/')}/"
        f"{song_slug.strip('/')}/"
    )
    job_id = str(uuid.uuid4())
    pasta_job = _exports_dir() / job_id
    try:
        validar_url_cifra(url_cifra)
        resultado = executar_apenas_cifra(url_cifra, pasta_saida=pasta_job)
        (pasta_job / OWNER_FILE).write_text(user_id, encoding="utf-8")
        setsync = resultado.setsync
        resp = _resposta_api_cifras(setsync)
        resp["grade_partes"] = partes_para_grade_ui(resultado.partes_grade)
        resp["artist_slug"] = artist_slug.strip("/")
        resp["song_slug"] = song_slug.strip("/")
        resp["cached"] = False
        resp["url_cifra"] = url_cifra
        return jsonify(resp)
    except ValueError as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": str(erro)}), 400
    except Exception as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": f"Falha ao importar: {erro}"}), 500


@cifras_import_bp.route("/api/download/<job_id>/<nome_arquivo>")
@login_required
def api_download(job_id: str, nome_arquivo: str):
    user_id = session["user_id"]
    if not _job_owned_by_user(job_id, user_id):
        return jsonify({"detail": "Acesso negado."}), 403

    pasta = _exports_dir() / job_id
    if not pasta.is_dir():
        return jsonify({"detail": "Sessão expirada ou não encontrada."}), 404

    if nome_arquivo == "mp3":
        mp3s = list(pasta.glob("*.mp3"))
        if not mp3s:
            return jsonify({"detail": "MP3 não encontrado."}), 404
        return send_file(mp3s[0], mimetype="audio/mpeg", as_attachment=True)

    permitidos = {
        "setsync_cifra.json": pasta / "setsync_cifra.json",
        "setsync_grade.json": pasta / "setsync_grade.json",
        "setsync_upload.json": pasta / "setsync_upload.json",
    }
    alvo = permitidos.get(nome_arquivo)
    if not alvo or not alvo.is_file():
        return jsonify({"detail": "Arquivo não encontrado."}), 404

    return send_file(alvo, mimetype="application/json", as_attachment=True)
