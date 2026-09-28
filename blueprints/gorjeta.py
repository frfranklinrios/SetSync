"""Gorjeta pública via Pix — sem comissão; dinheiro vai direto à chave do músico."""

from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from band_finance import parse_money_field
from blueprints.auth import login_required
from db import (
    count_song_requests,
    create_band_gorjeta,
    create_song_request,
    get_band,
    get_band_by_gorjeta_slug,
    is_band_editor,
    is_band_member,
    list_band_gorjetas,
    list_song_requests,
    sum_band_gorjetas,
    update_song_request_status,
)
from gorjeta_repertoire import resolve_public_repertoire
from gorjeta_service import banda_gorjeta_pronta, montar_gorjeta_qr

gorjeta_bp = Blueprint("gorjeta", __name__)

_MAX_REQUESTS_SESSION = 8


def _public_kwargs(
    slug, *, event_id=None, setlist_id=None, valor=None, ok=None, pedido=None
):
    kw = {"slug": slug}
    if event_id:
        kw["event"] = event_id
    if setlist_id:
        kw["setlist"] = setlist_id
    if valor:
        kw["valor"] = valor
    if ok:
        kw["ok"] = 1
    if pedido:
        kw["pedido"] = 1
    return kw


@gorjeta_bp.route("/gorjeta/<slug>")
def publica(slug):
    band = get_band_by_gorjeta_slug(slug)
    if not band or not banda_gorjeta_pronta(band):
        return render_template("gorjeta/indisponivel.html", slug=slug), 404

    valor = parse_money_field(request.args.get("valor"))
    try:
        tip = montar_gorjeta_qr(band, valor=valor if valor and valor > 0 else None)
    except ValueError:
        return render_template("gorjeta/indisponivel.html", slug=slug), 404

    event_id = (request.args.get("event") or "").strip() or None
    setlist_id = (request.args.get("setlist") or "").strip() or None
    repertoire = resolve_public_repertoire(
        band, setlist_id=setlist_id, event_id=event_id
    )
    if repertoire.get("setlist_id") and not setlist_id:
        setlist_id = repertoire["setlist_id"]

    return render_template(
        "gorjeta/publica.html",
        band=band,
        tip=tip,
        event_id=event_id,
        setlist_id=setlist_id,
        repertoire=repertoire,
        confirmed=request.args.get("ok") == "1",
        pedido_ok=request.args.get("pedido") == "1",
    )


@gorjeta_bp.route("/gorjeta/<slug>/confirmar", methods=["POST"])
def confirmar(slug):
    """Registra no placar (honor system). O Pix já caiu na conta do músico."""
    band = get_band_by_gorjeta_slug(slug)
    if not band or not banda_gorjeta_pronta(band):
        flash("Gorjeta indisponível.", "warning")
        return redirect(url_for("index"))

    valor = parse_money_field(request.form.get("valor"))
    event_id = (request.form.get("event_id") or "").strip() or None
    setlist_id = (request.form.get("setlist_id") or "").strip() or None
    if valor is None or valor <= 0:
        flash("Informe o valor que você enviou.", "warning")
        return redirect(
            url_for(
                "gorjeta.publica",
                **_public_kwargs(slug, event_id=event_id, setlist_id=setlist_id),
            )
        )

    nota = (request.form.get("nota") or "").strip()[:120] or None
    create_band_gorjeta(
        band["id"],
        valor=valor,
        event_id=event_id,
        nota=nota,
        source="public",
    )
    return redirect(
        url_for(
            "gorjeta.publica",
            **_public_kwargs(
                slug,
                event_id=event_id,
                setlist_id=setlist_id,
                ok=1,
                valor=f"{valor:.2f}",
            ),
        )
    )


@gorjeta_bp.route("/gorjeta/<slug>/pedir", methods=["POST"])
def pedir_musica(slug):
    band = get_band_by_gorjeta_slug(slug)
    if not band or not banda_gorjeta_pronta(band):
        return redirect(url_for("index"))

    event_id = (request.form.get("event_id") or "").strip() or None
    setlist_id = (request.form.get("setlist_id") or "").strip() or None
    cifra_id = (request.form.get("cifra_id") or "").strip() or None
    titulo = (request.form.get("titulo") or "").strip()
    artista = (request.form.get("artista") or "").strip() or None
    requester = (request.form.get("requester_name") or "").strip() or None
    nota = (request.form.get("nota") or "").strip() or None

    # Se veio de uma música do repertório, confere o título
    if cifra_id and not titulo:
        from db import get_cifra

        c = get_cifra(cifra_id)
        if c and str(c.get("band_id") or "") == str(band["id"]):
            titulo = (c.get("titulo") or "").strip()
            artista = (c.get("artista") or "").strip() or artista

    if not titulo or len(titulo) < 2:
        flash("Escolha ou digite o nome da música.", "warning")
        return redirect(
            url_for(
                "gorjeta.publica",
                **_public_kwargs(slug, event_id=event_id, setlist_id=setlist_id),
            )
        )

    used = int(session.get("song_req_count") or 0)
    if used >= _MAX_REQUESTS_SESSION:
        flash("Você já pediu várias músicas. Aguarde um pouco.", "warning")
        return redirect(
            url_for(
                "gorjeta.publica",
                **_public_kwargs(slug, event_id=event_id, setlist_id=setlist_id),
            )
        )

    create_song_request(
        band["id"],
        titulo=titulo,
        artista=artista,
        cifra_id=cifra_id,
        setlist_id=setlist_id,
        event_id=event_id,
        requester_name=requester,
        nota=nota,
    )
    session["song_req_count"] = used + 1
    return redirect(
        url_for(
            "gorjeta.publica",
            **_public_kwargs(slug, event_id=event_id, setlist_id=setlist_id, pedido=1),
        )
    )


@gorjeta_bp.route("/bands/<band_id>/gorjetas/manual", methods=["POST"])
@login_required
def registrar_manual(band_id):
    user_id = session["user_id"]
    band = get_band(band_id)
    if not band or not is_band_editor(band_id, user_id):
        flash("Sem permissão.", "danger")
        return redirect(url_for("dashboard"))

    valor = parse_money_field(request.form.get("valor"))
    if valor is None or valor <= 0:
        flash("Informe um valor válido.", "warning")
        return redirect(request.referrer or url_for("bands.finance", band_id=band_id))

    event_id = (request.form.get("event_id") or "").strip() or None
    nota = (request.form.get("nota") or "").strip()[:120] or None
    create_band_gorjeta(
        band_id,
        valor=valor,
        event_id=event_id,
        nota=nota,
        source="manual",
        created_by_user_id=user_id,
    )
    flash(f"Gorjeta de R$ {valor:.2f} registrada.", "success")
    return redirect(request.referrer or url_for("bands.finance", band_id=band_id))


@gorjeta_bp.route("/bands/<band_id>/gorjetas/live.json")
@login_required
def live_json(band_id):
    user_id = session["user_id"]
    if not is_band_member(band_id, user_id):
        return jsonify({"ok": False}), 403

    event_id = (request.args.get("event_id") or "").strip() or None
    from_date = (request.args.get("from") or "").strip() or None
    to_date = (request.args.get("to") or "").strip() or None
    total = sum_band_gorjetas(
        band_id,
        event_id=event_id,
        from_date=from_date,
        to_date=to_date,
    )
    items = list_band_gorjetas(
        band_id,
        event_id=event_id,
        from_date=from_date,
        to_date=to_date,
        limit=30,
    )
    pending = list_song_requests(band_id, event_id=event_id, status="pending", limit=40)
    return jsonify(
        {
            "ok": True,
            "total": total,
            "count": len(items),
            "items": [
                {
                    "id": g["id"],
                    "valor": float(g["valor"] or 0),
                    "nota": g.get("nota") or "",
                    "source": g.get("source") or "",
                    "created_at": str(g.get("created_at") or ""),
                }
                for g in items
            ],
            "requests": [
                {
                    "id": r["id"],
                    "titulo": r.get("titulo") or "",
                    "artista": r.get("artista") or "",
                    "requester_name": r.get("requester_name") or "",
                    "nota": r.get("nota") or "",
                    "cifra_id": r.get("cifra_id") or "",
                    "created_at": str(r.get("created_at") or ""),
                }
                for r in pending
            ],
            "requests_count": count_song_requests(
                band_id, event_id=event_id, status="pending"
            ),
        }
    )


@gorjeta_bp.route("/bands/<band_id>/pedidos/<request_id>/status", methods=["POST"])
@login_required
def pedido_status(band_id, request_id):
    user_id = session["user_id"]
    if not is_band_member(band_id, user_id):
        return jsonify({"ok": False}), 403
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or request.form.get("status") or "").strip()
    if not update_song_request_status(request_id, band_id, status):
        return jsonify({"ok": False, "error": "Não atualizado"}), 400
    return jsonify({"ok": True, "status": status})
