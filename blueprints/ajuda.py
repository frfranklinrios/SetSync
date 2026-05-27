from __future__ import annotations

from flask import Blueprint, render_template


ajuda_bp = Blueprint("ajuda", __name__)


@ajuda_bp.route("/ajuda")
def index():
    return render_template("ajuda/index.html")

