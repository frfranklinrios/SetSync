from __future__ import annotations

import shutil
import tempfile
import uuid
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
)

from blueprints.auth import login_required
from cifras_tool.config import settings
from cifras_tool.pipeline_cifras import (
    executar,
    executar_apenas_cifra,
    executar_com_audio,
    validar_url_cifra,
)
from cifras_tool.setsync_export import partes_para_grade_ui

cifras_import_bp = Blueprint("cifras_import", __name__, url_prefix="/cifras/import")

_AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".aac"}


def _exports_dir() -> Path:
    root = Path(current_app.root_path)
    pasta = root / "data" / "cifras_exports"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


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
    return render_template(
        "cifras_tool/embed.html",
        youtube_no_server=settings.youtube_no_server,
    )


@cifras_import_bp.route("/tool/embed")
@login_required
def embed_tool_legacy():
    return render_template(
        "cifras_tool/embed.html",
        youtube_no_server=settings.youtube_no_server,
    )


@cifras_import_bp.route("/api/processar", methods=["POST"])
@login_required
def api_processar():
    if settings.youtube_no_server:
        return jsonify(
            {
                "detail": (
                    "Neste servidor o YouTube não é acessado (sem login nem cookies). "
                    "Use «Enviar áudio» com um MP3/WAV da faixa, ou «Somente cifra»."
                ),
                "code": "youtube_disabled",
            }
        ), 503

    corpo = request.get_json(silent=True) or {}
    url_cifra = (corpo.get("url_cifra") or "").strip()
    url_youtube = (corpo.get("url_youtube") or "").strip()
    compasso = corpo.get("compasso")
    embed = bool(corpo.get("embed", True))

    if len(url_cifra) < 8 or len(url_youtube) < 8:
        return jsonify({"detail": "Informe URL da cifra e do YouTube."}), 400

    job_id = str(uuid.uuid4())
    pasta_job = _exports_dir() / job_id

    try:
        validar_url_cifra(url_cifra)
        resultado = executar(
            url_cifra,
            pasta_saida=pasta_job,
            youtube_url=url_youtube,
            compasso_manual=compasso,
        )
    except ValueError as erro:
        return jsonify({"detail": str(erro)}), 400
    except Exception as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": f"Falha no processamento: {erro}"}), 500

    return _resposta_processamento(resultado, job_id, embed=embed)


@cifras_import_bp.route("/api/processar-audio", methods=["POST"])
@login_required
def api_processar_audio():
    """Cifra + arquivo de áudio enviado pelo usuário (sem YouTube no servidor)."""
    url_cifra = (request.form.get("url_cifra") or "").strip()
    url_youtube = (request.form.get("url_youtube") or "").strip()
    compasso = request.form.get("compasso")
    embed = request.form.get("embed", "true").lower() in ("1", "true", "yes")
    arquivo = request.files.get("audio")

    if len(url_cifra) < 8:
        return jsonify({"detail": "Informe o link da cifra."}), 400
    if not arquivo or not arquivo.filename:
        return jsonify({"detail": "Envie um arquivo de áudio (MP3, WAV, etc.)."}), 400

    ext = Path(arquivo.filename).suffix.lower()
    if ext not in _AUDIO_EXT:
        return jsonify(
            {"detail": f"Formato não suportado ({ext}). Use MP3, WAV, M4A, OGG ou FLAC."}
        ), 400

    job_id = str(uuid.uuid4())
    pasta_job = _exports_dir() / job_id
    pasta_job.mkdir(parents=True, exist_ok=True)

    tmp_path: Path | None = None
    try:
        validar_url_cifra(url_cifra)
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=ext, dir=pasta_job
        ) as tmp:
            arquivo.save(tmp.name)
            tmp_path = Path(tmp.name)

        resultado = executar_com_audio(
            url_cifra,
            tmp_path,
            pasta_saida=pasta_job,
            youtube_url=url_youtube or None,
            compasso_manual=compasso,
        )
    except ValueError as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": str(erro)}), 400
    except Exception as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": f"Falha no processamento: {erro}"}), 500
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return _resposta_processamento(resultado, job_id, embed=embed)


@cifras_import_bp.route("/api/processar-cifra", methods=["POST"])
@login_required
def api_processar_cifra():
    """Somente raspagem da cifra + grade pelos acordes (sem áudio, sem YouTube)."""
    corpo = request.get_json(silent=True) or {}
    url_cifra = (corpo.get("url_cifra") or "").strip()
    url_youtube = (corpo.get("url_youtube") or "").strip()
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
            youtube_url=url_youtube or None,
            compasso_manual=compasso,
        )
    except ValueError as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": str(erro)}), 400
    except Exception as erro:
        if pasta_job.exists():
            shutil.rmtree(pasta_job, ignore_errors=True)
        return jsonify({"detail": f"Falha no processamento: {erro}"}), 500

    return _resposta_processamento(resultado, job_id, embed=embed)


@cifras_import_bp.route("/api/download/<job_id>/<nome_arquivo>")
@login_required
def api_download(job_id: str, nome_arquivo: str):
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
