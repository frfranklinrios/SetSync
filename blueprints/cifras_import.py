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
)

from blueprints.auth import login_required
from cifras_tool.pipeline_cifras import executar, validar_url_cifra
from cifras_tool.setsync_export import partes_para_grade_ui

cifras_import_bp = Blueprint("cifras_import", __name__, url_prefix="/cifras/import")


def _exports_dir() -> Path:
  root = Path(current_app.root_path)
  pasta = root / "data" / "cifras_exports"
  pasta.mkdir(parents=True, exist_ok=True)
  return pasta


@cifras_import_bp.route("/tool")
@login_required
def embed_tool():
  return render_template("cifras_tool/embed.html")


@cifras_import_bp.route("/tool/embed")
@login_required
def embed_tool_legacy():
  """Compatibilidade com URLs antigas do iframe."""
  return render_template("cifras_tool/embed.html")


@cifras_import_bp.route("/api/processar", methods=["POST"])
@login_required
def api_processar():
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

  setsync = resultado.setsync
  base = f"/cifras/import/api/download/{job_id}"
  downloads = {
    "setsync_cifra": f"{base}/setsync_cifra.json",
    "setsync_grade": f"{base}/setsync_grade.json",
    "setsync_upload": f"{base}/setsync_upload.json",
  }
  if not embed:
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
      "mp3_filename": resultado.mp3.name,
    }
  )


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
