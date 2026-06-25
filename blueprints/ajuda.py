from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from help_chatbot import answer_question, default_suggestions


ajuda_bp = Blueprint("ajuda", __name__)


@ajuda_bp.route("/ajuda")
def index():
    return render_template("ajuda/index.html")


@ajuda_bp.route("/ajuda/chat", methods=["POST"])
def chat():
    from flask import session
    data = request.get_json(silent=True) or {}
    query = (data.get("q") or data.get("message") or "").strip()
    user_id = session.get("user_id")
    return jsonify(answer_question(query, user_id=user_id))


@ajuda_bp.route("/ajuda/chat/sugestoes")
def chat_suggestions():
    return jsonify({"ok": True, "suggestions": default_suggestions()})


@ajuda_bp.route("/ajuda/nps", methods=["POST"])
def nps_submit():
    from flask import session
    from db import save_user_nps
    from blueprints.auth import login_required as _lr
    if "user_id" not in session:
        return jsonify({"ok": False}), 401
    data = request.get_json(silent=True) or {}
    score = int(data.get("score", -1))
    if score < 0 or score > 10:
        return jsonify({"ok": False, "error": "Nota inválida"}), 400
    save_user_nps(session["user_id"], score)
    return jsonify({"ok": True})


@ajuda_bp.route("/ajuda/nps/dismiss", methods=["POST"])
def nps_dismiss():
    from flask import redirect, session, url_for
    from db import dismiss_user_nps
    if "user_id" in session:
        dismiss_user_nps(session["user_id"])
    return redirect(request.referrer or url_for("dashboard"))


@ajuda_bp.route("/ajuda/pwa/dismiss", methods=["POST"])
def pwa_dismiss():
    from flask import redirect, session, url_for
    from db import dismiss_pwa_prompt
    if "user_id" in session:
        dismiss_pwa_prompt(session["user_id"])
    return redirect(request.referrer or url_for("dashboard"))

