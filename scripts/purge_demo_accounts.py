#!/usr/bin/env python3
"""Remove contas, bandas e estúdios demo/showcase do banco de dados de forma segura e idempotente."""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _existing_tables(cur) -> set[str]:
    from database import IS_POSTGRES

    if IS_POSTGRES:
        cur.execute(
            "SELECT table_name AS name FROM information_schema.tables WHERE table_schema = 'public'"
        )
    else:
        cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    return {str(r["name"]) for r in cur.fetchall()}


def _exec_if_table(cur, tables: set[str], table: str, sql: str, params: tuple | list) -> None:
    if table in tables:
        cur.execute(sql, params)


def _delete_studio_cascade(cur, tables: set[str], studio_id: str) -> None:
    if "studio_rooms" in tables:
        cur.execute("SELECT id FROM studio_rooms WHERE studio_id = ?", (studio_id,))
        room_ids = [str(r["id"]) for r in cur.fetchall()]
        for rid in room_ids:
            for tbl in (
                "studio_bookings",
                "studio_room_photos",
                "studio_room_availability",
                "studio_room_blocks",
            ):
                _exec_if_table(cur, tables, tbl, f"DELETE FROM {tbl} WHERE room_id = ?", (rid,))
    for tbl in ("studio_expenses", "studio_rooms", "studio_photos", "studio_onboarding_emails"):
        _exec_if_table(cur, tables, tbl, f"DELETE FROM {tbl} WHERE studio_id = ?", (studio_id,))
    _exec_if_table(cur, tables, "studios", "DELETE FROM studios WHERE id = ?", (studio_id,))


def _delete_band_satellites(cur, tables: set[str], band_id: str) -> None:
    if "band_events" in tables:
        cur.execute("SELECT id FROM band_events WHERE band_id = ?", (band_id,))
        event_ids = [str(r["id"]) for r in cur.fetchall()]
        for eid in event_ids:
            for tbl in (
                "band_event_assignments",
                "band_event_fee_lines",
                "band_event_guests",
                "event_reminders",
            ):
                _exec_if_table(cur, tables, tbl, f"DELETE FROM {tbl} WHERE event_id = ?", (eid,))
            _exec_if_table(
                cur,
                tables,
                "band_gorjetas",
                "UPDATE band_gorjetas SET event_id = NULL WHERE event_id = ?",
                (eid,),
            )
            _exec_if_table(
                cur,
                tables,
                "studio_bookings",
                "UPDATE studio_bookings SET band_event_id = NULL WHERE band_event_id = ?",
                (eid,),
            )
    if "band_lineups" in tables:
        cur.execute("SELECT id FROM band_lineups WHERE band_id = ?", (band_id,))
        lineup_ids = [str(r["id"]) for r in cur.fetchall()]
        for lid in lineup_ids:
            _exec_if_table(
                cur,
                tables,
                "band_lineup_members",
                "DELETE FROM band_lineup_members WHERE lineup_id = ?",
                (lid,),
            )
    for tbl in (
        "band_events",
        "band_expenses",
        "band_gorjetas",
        "band_lineups",
        "band_member_invites",
        "band_role_substitutes",
        "band_roles",
        "band_song_requests",
        "notifications",
        "notification_digest_queue",
        "whatsapp_cifra_digest",
        "studio_bookings",
    ):
        _exec_if_table(cur, tables, tbl, f"DELETE FROM {tbl} WHERE band_id = ?", (band_id,))


def _delete_user_cascade(cur, tables: set[str], user_id: str) -> None:
    _exec_if_table(
        cur,
        tables,
        "cifras",
        "UPDATE cifras SET owner_user_id = NULL WHERE owner_user_id = ? AND band_id IS NOT NULL",
        (user_id,),
    )
    if "cifras" in tables:
        cur.execute(
            "SELECT id FROM cifras WHERE owner_user_id = ? AND band_id IS NULL",
            (user_id,),
        )
        personal_ids = [str(r["id"]) for r in cur.fetchall()]
        for cid in personal_ids:
            for tbl in (
                "cifra_play_drawings",
                "cifra_shares",
                "cifra_user_drafts",
                "cifra_vocalist_transpose",
                "setlist_cifras",
            ):
                _exec_if_table(cur, tables, tbl, f"DELETE FROM {tbl} WHERE cifra_id = ?", (cid,))
            cur.execute("DELETE FROM cifras WHERE id = ?", (cid,))

    user_deletes: list[tuple[str, str]] = [
        ("studio_voucher_usos", "DELETE FROM studio_voucher_usos WHERE user_id = ?"),
        ("studio_subscriptions", "DELETE FROM studio_subscriptions WHERE user_id = ?"),
        ("cifra_shares", "DELETE FROM cifra_shares WHERE shared_with_user_id = ?"),
        ("cifra_shares", "DELETE FROM cifra_shares WHERE shared_by_user_id = ?"),
        ("cifra_user_drafts", "DELETE FROM cifra_user_drafts WHERE user_id = ?"),
        ("cifra_play_drawings", "DELETE FROM cifra_play_drawings WHERE user_id = ?"),
        ("band_members", "DELETE FROM band_members WHERE user_id = ?"),
        ("band_member_invites", "DELETE FROM band_member_invites WHERE user_id = ?"),
        ("band_member_invites", "UPDATE band_member_invites SET invited_by = NULL WHERE invited_by = ?"),
        ("band_event_assignments", "DELETE FROM band_event_assignments WHERE user_id = ?"),
        ("band_event_assignments", "DELETE FROM band_event_assignments WHERE assigned_by = ?"),
        ("band_event_guests", "DELETE FROM band_event_guests WHERE invited_by = ?"),
        ("band_events", "DELETE FROM band_events WHERE created_by = ?"),
        ("band_expenses", "DELETE FROM band_expenses WHERE created_by_user_id = ?"),
        ("band_vocalists", "UPDATE band_vocalists SET user_id = NULL WHERE user_id = ?"),
        ("band_lineup_members", "DELETE FROM band_lineup_members WHERE user_id = ?"),
        ("band_role_substitutes", "DELETE FROM band_role_substitutes WHERE user_id = ?"),
        ("band_role_pool", "DELETE FROM band_role_pool WHERE user_id = ?"),
        ("user_instruments", "DELETE FROM user_instruments WHERE user_id = ?"),
        ("user_availability_blockouts", "DELETE FROM user_availability_blockouts WHERE user_id = ?"),
        ("push_subscriptions", "DELETE FROM push_subscriptions WHERE user_id = ?"),
        ("notifications", "DELETE FROM notifications WHERE user_id = ?"),
        ("notifications", "UPDATE notifications SET actor_user_id = NULL WHERE actor_user_id = ?"),
        ("notification_digest_queue", "DELETE FROM notification_digest_queue WHERE user_id = ?"),
        ("onboarding_emails", "DELETE FROM onboarding_emails WHERE usuario_id = ?"),
        ("retention_emails", "DELETE FROM retention_emails WHERE usuario_id = ?"),
        ("studio_onboarding_emails", "DELETE FROM studio_onboarding_emails WHERE owner_user_id = ?"),
        ("event_reminders", "DELETE FROM event_reminders WHERE user_id = ?"),
        ("whatsapp_cifra_digest", "DELETE FROM whatsapp_cifra_digest WHERE user_id = ?"),
        ("whatsapp_cifra_digest", "UPDATE whatsapp_cifra_digest SET actor_user_id = NULL WHERE actor_user_id = ?"),
        ("admin_activity_log", "UPDATE admin_activity_log SET actor_user_id = NULL WHERE actor_user_id = ?"),
        ("admin_whatsapp_invites", "DELETE FROM admin_whatsapp_invites WHERE sent_by_user_id = ?"),
        ("band_prospects", "DELETE FROM band_prospects WHERE created_by_user_id = ?"),
        ("studio_prospects", "DELETE FROM studio_prospects WHERE created_by_user_id = ?"),
        ("studio_bookings", "DELETE FROM studio_bookings WHERE requested_by_user_id = ?"),
        ("studio_expenses", "DELETE FROM studio_expenses WHERE created_by_user_id = ?"),
        ("product_funnel_events", "UPDATE product_funnel_events SET user_id = NULL WHERE user_id = ?"),
        ("vouchers", "DELETE FROM vouchers WHERE criado_por_id = ?"),
    ]
    for tbl, sql in user_deletes:
        _exec_if_table(cur, tables, tbl, sql, (user_id,))
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))


def purge_demo_accounts(*, apply: bool = False, force: bool = False) -> dict:
    """Lista ou remove contas, bandas e estúdios demo."""
    import db
    from demo_accounts import demo_band_ids, demo_user_ids

    conn = db.get_db()
    cur = conn.cursor()
    tables = _existing_tables(cur)

    raw_user_ids = sorted(demo_user_ids())
    demo_users: list[dict] = []
    if raw_user_ids:
        ph = ",".join("?" for _ in raw_user_ids)
        cur.execute(
            f"SELECT id, username, email, COALESCE(is_superadmin, 0) AS is_superadmin "
            f"FROM users WHERE id IN ({ph})",
            raw_user_ids,
        )
        for row in cur.fetchall():
            r = dict(row)
            if int(r.get("is_superadmin") or 0) == 1:
                continue
            demo_users.append(r)

    safe_user_ids = {str(u["id"]) for u in demo_users}
    raw_band_ids = sorted(demo_band_ids(safe_user_ids)) if safe_user_ids else []
    demo_bands: list[dict] = []
    if raw_band_ids:
        ph_b = ",".join("?" for _ in raw_band_ids)
        cur.execute(
            f"SELECT id, name, owner_id FROM bands WHERE id IN ({ph_b})",
            raw_band_ids,
        )
        demo_bands = [dict(r) for r in cur.fetchall()]
    safe_band_ids = {str(b["id"]) for b in demo_bands}

    demo_studios: list[dict] = []
    if safe_user_ids and "studios" in tables:
        ph_u = ",".join("?" for _ in safe_user_ids)
        cur.execute(
            f"SELECT id, nome, owner_user_id FROM studios WHERE owner_user_id IN ({ph_u})",
            sorted(safe_user_ids),
        )
        demo_studios = [dict(r) for r in cur.fetchall()]

    # Segurança: verificar vínculos de contas reais antes de apagar
    if safe_band_ids and "band_members" in tables:
        ph_b = ",".join("?" for _ in safe_band_ids)
        cur.execute(
            f"SELECT band_id, user_id FROM band_members WHERE band_id IN ({ph_b})",
            sorted(safe_band_ids),
        )
        real_in_demo_band = [
            dict(r) for r in cur.fetchall() if str(r["user_id"]) not in safe_user_ids
        ]
        if real_in_demo_band and not force:
            conn.close()
            raise RuntimeError(
                f"Encontrados {len(real_in_demo_band)} vínculo(s) de usuário(s) reais em bandas demo. "
                "Use --force para continuar."
            )

    if demo_studios and "studio_bookings" in tables and "studio_rooms" in tables:
        ph_s = ",".join("?" for _ in demo_studios)
        cur.execute(
            f"SELECT sb.id, sb.requested_by_user_id FROM studio_bookings sb "
            f"JOIN studio_rooms sr ON sr.id = sb.room_id WHERE sr.studio_id IN ({ph_s})",
            [s["id"] for s in demo_studios],
        )
        real_bookings = [
            dict(r)
            for r in cur.fetchall()
            if str(r.get("requested_by_user_id") or "") not in safe_user_ids
        ]
        if real_bookings and not force:
            conn.close()
            raise RuntimeError(
                f"Encontradas {len(real_bookings)} reserva(s) de usuários reais em estúdios demo. "
                "Use --force para continuar."
            )

    result = {
        "apply": apply,
        "demo_users": [u["username"] for u in demo_users],
        "demo_bands": [b["name"] for b in demo_bands],
        "demo_studios": [s["nome"] for s in demo_studios],
        "deleted_studios": 0,
        "deleted_bands": 0,
        "deleted_users": 0,
    }

    if not apply:
        conn.close()
        return result

    for studio in demo_studios:
        _delete_studio_cascade(cur, tables, str(studio["id"]))
        result["deleted_studios"] += 1
    conn.commit()

    for band in demo_bands:
        _delete_band_satellites(cur, tables, str(band["id"]))
        conn.commit()
        db.delete_band(band["id"])
        result["deleted_bands"] += 1

    for u in demo_users:
        _delete_user_cascade(cur, tables, str(u["id"]))
        result["deleted_users"] += 1

    conn.commit()
    conn.close()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove dados demo/showcase do Uníssono")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Apenas exibe o que seria removido (padrão)")
    mode.add_argument("--apply", action="store_true", help="Executa a remoção definitivamente")
    parser.add_argument("--force", action="store_true", help="Ignora travas de vínculo cruzado")
    args = parser.parse_args()

    from app import app as flask_app

    with flask_app.app_context():
        res = purge_demo_accounts(apply=bool(args.apply), force=bool(args.force))

    label = "APLICADO" if res["apply"] else "DRY-RUN"
    print(f"[{label}] Usuários demo encontrados ({len(res['demo_users'])}): {res['demo_users']}")
    print(f"[{label}] Bandas demo encontradas ({len(res['demo_bands'])}): {res['demo_bands']}")
    print(f"[{label}] Estúdios demo encontrados ({len(res['demo_studios'])}): {res['demo_studios']}")
    if res["apply"]:
        print(
            f"[APLICADO] Removidos: {res['deleted_users']} usuários, "
            f"{res['deleted_bands']} bandas, {res['deleted_studios']} estúdios."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
