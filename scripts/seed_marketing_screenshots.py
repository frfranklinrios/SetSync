#!/usr/bin/env python3
"""Seed de bandas/estúdio para screenshots de marketing (BR + gospel + financeiro rico)."""

from __future__ import annotations

import os
import sys
from datetime import timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from marketing_shots import (
    PACK_BR,
    PACK_GOSPEL,
    rotate_songs,
    slot_for_date,
    songs_br,
    songs_gospel,
)

DEMO_PASSWORD = "UníssonoShowcase2026!"

BR = {
    "username": "showcase",
    "email": "showcase@unissono.app",
    "display": "Ana Costa",
    "band": "Maré Alta",
    "band_desc": "Covers de MPB e rock — Fortaleza, CE.",
    "setlist": "Sábado — Bar do Porto",
    "meta_key": "marketing_pack",
    "meta_val": PACK_BR,
}

GOSPEL = {
    "username": "igreja_showcase",
    "email": "igreja.showcase@unissono.app",
    "display": "Pr. Marina Louvor",
    "band": "Ministério Fonte",
    "band_desc": "Ministério de louvor — culto de domingo e ensaios.",
    "setlist": "Culto domingo — manhã",
    "meta_key": "marketing_pack",
    "meta_val": PACK_GOSPEL,
}

STUDIO = {
    "username": "carlos_groove",
    "email": "carlos.groove@unissono.app",
    "password": "UníssonoGroove2026!",
    "display": "Carlos Mendes",
    "nome": "Groove Box Ensaios",
    # Usuários legados a migrar (sem recriar o estúdio)
    "legacy_usernames": ("estudio_teste",),
}


def _ensure_user(username: str, email: str, password: str, display: str) -> str:
    from werkzeug.security import generate_password_hash

    from db import (
        create_user,
        dismiss_onboarding_checklist,
        get_db,
        get_user_by_username,
        set_privacy_accepted,
        touch_user_last_login,
        update_user_display_name,
        update_user_profile,
    )

    u = get_user_by_username(username)
    if u:
        update_user_display_name(u["id"], display)
        uid = u["id"]
    else:
        uid = create_user(username, email, password, display_name=display)
        if not uid:
            u = get_user_by_username(username)
            if not u:
                raise RuntimeError(f"Falha ao criar {username}")
            uid = u["id"]
    db = get_db()
    c = db.cursor()
    c.execute(
        """UPDATE users SET password_hash = ?, email = ?, display_name = ?
           WHERE id = ?""",
        (generate_password_hash(password), email, display, uid),
    )
    db.commit()
    db.close()
    update_user_profile(
        uid,
        display_name=display,
        phone="85999990000",
        whatsapp_notify=True,
        email_notify=True,
    )
    dismiss_onboarding_checklist(uid)
    touch_user_last_login(uid)
    set_privacy_accepted(uid)
    return uid


def _migrate_legacy_username(
    legacy: str,
    new_username: str,
    email: str,
    display: str,
    password: str,
) -> str | None:
    """Renomeia conta antiga (ex.: estudio_teste → carlos_groove)."""
    from werkzeug.security import generate_password_hash

    from db import get_db, get_user_by_username

    old = get_user_by_username(legacy)
    if not old:
        return None
    existing_new = get_user_by_username(new_username)
    if existing_new and existing_new["id"] != old["id"]:
        return existing_new["id"]
    db = get_db()
    c = db.cursor()
    c.execute(
        """UPDATE users SET username = ?, email = ?, display_name = ?, password_hash = ?
           WHERE id = ?""",
        (new_username, email, display, generate_password_hash(password), old["id"]),
    )
    db.commit()
    db.close()
    return old["id"]


def _create_prepared_cifra(band_id: str, song: dict) -> str:
    from blueprints.cifras import _prepare_conteudo_for_save
    from db import create_cifra

    conteudo, cifra_json = _prepare_conteudo_for_save(
        song["conteudo"],
        titulo=song["titulo"],
        artista=song["artista"],
        tom_original=song["tom"],
    )
    return create_cifra(
        song["titulo"],
        song["artista"],
        song["tom"],
        conteudo,
        band_id,
        cifra_json=cifra_json,
        bpm=song.get("bpm"),
    )


def _wipe_band_content(band_id: str) -> None:
    """Limpa cifras/setlists/eventos/despesas para reseed idempotente."""
    from db import get_db

    db = get_db()
    c = db.cursor()
    c.execute("SELECT id FROM setlists WHERE band_id = ?", (band_id,))
    for row in c.fetchall():
        sid = row["id"]
        c.execute("DELETE FROM setlist_cifras WHERE setlist_id = ?", (sid,))
    c.execute("DELETE FROM setlists WHERE band_id = ?", (band_id,))
    c.execute("SELECT id FROM band_events WHERE band_id = ?", (band_id,))
    for row in c.fetchall():
        eid = row["id"]
        c.execute("DELETE FROM band_event_assignments WHERE event_id = ?", (eid,))
    c.execute("DELETE FROM band_events WHERE band_id = ?", (band_id,))
    c.execute("DELETE FROM band_expenses WHERE band_id = ?", (band_id,))
    c.execute("DELETE FROM cifras WHERE band_id = ?", (band_id,))
    db.commit()
    db.close()


def seed_band_pack(spec: dict, songs: list[dict], *, slot: int) -> dict:
    from config import app_now_naive
    from db import (
        create_band,
        get_user_bands,
        update_assinatura,
        update_event_fees,
    )
    from models_agenda import (
        EVENT_ENSAIO,
        EVENT_SHOW,
        create_band_event,
        respond_event_assignment,
        set_event_assignments,
    )
    from models_band_finance import create_band_expense
    from models_setlist import add_cifra_to_setlist, create_setlist

    owner_id = _ensure_user(
        spec["username"],
        spec["email"],
        DEMO_PASSWORD,
        spec["display"],
    )
    bands = get_user_bands(owner_id)
    band = next((b for b in bands if b.get("name") == spec["band"]), None)
    if band:
        band_id = band["id"]
        _wipe_band_content(band_id)
    else:
        band_id = create_band(spec["band"], spec["band_desc"], owner_id)

    update_assinatura(band_id, plano="pro", status="ativa")

    ordered = rotate_songs(songs, slot)
    cifra_ids = [_create_prepared_cifra(band_id, s) for s in ordered]

    setlist_id = create_setlist(band_id, spec["setlist"], "Set principal para capturas")
    for i, cid in enumerate(cifra_ids):
        add_cifra_to_setlist(setlist_id, cid, position=i + 1)

    now = app_now_naive()
    # Financeiro do mês corrente + shows anteriores no mesmo mês
    month_start = now.replace(day=1, hour=20, minute=0, second=0, microsecond=0)
    fees = [
        (4200, 200, 100, True),
        (2800, 150, 80, True),
        (3500, 180, 0, True),
        (1900, 100, 50, False),
        (5100, 250, 120, True),
        (2400, 120, 60, True),
        (3300, 160, 90, True),
        (2700, 140, 70, True),
    ]
    venues = [
        "Bar do Porto",
        "Casa da Música",
        "Centro de Eventos",
        "Theatre",
        "Rooftop Beira-Mar",
        "Clube Náutico",
        "Arena Club",
        "Studio Live",
    ]
    event_ids = []
    for i, (total, transp, equip, _) in enumerate(fees):
        day = min(28, 2 + i * 3)
        starts = month_start.replace(day=day) + timedelta(hours=(i % 3))
        if starts > now + timedelta(days=40):
            starts = now - timedelta(days=2 + i)
        title = f"Show — {venues[i % len(venues)]}"
        if spec["meta_val"] == PACK_GOSPEL:
            title = [
                "Culto de domingo",
                "Vigília",
                "Ensaio geral",
                "Conferência",
                "Culto jovens",
                "Casamento",
                "Batismo",
                "Culto especial",
            ][i % 8]
        eid = create_band_event(
            band_id,
            title=title,
            event_type=EVENT_SHOW if i % 4 else EVENT_ENSAIO,
            starts_at=starts.strftime("%Y-%m-%d %H:%M:%S"),
            location=venues[i % len(venues)] + " — Fortaleza, CE",
            setlist_id=setlist_id if i % 2 == 0 else None,
            created_by=owner_id,
        )
        event_ids.append(eid)
        update_event_fees(
            eid,
            fee_total=float(total),
            fee_transport_discount=float(transp),
            fee_equipment_discount=float(equip),
            fee_notes="Contrato fechado · rateio entre músicos",
            fee_settled=(i % 3 == 0),
        )
        set_event_assignments(
            eid,
            [{"user_id": owner_id, "role_label": "Vocal"}],
            assigned_by=owner_id,
        )
        respond_event_assignment(eid, owner_id, accepted=True)

    expenses = [
        ("Transporte vans", 450, "transporte"),
        ("Pedágio / estacionamento", 85, "transporte"),
        ("Cordas e palhetas", 120, "equipamento"),
        ("Marketing Instagram", 200, "marketing"),
        ("Alimentação equipe", 310, "alimentacao"),
        ("Taxa casas de show", 150, "outros"),
    ]
    for i, (desc, valor, cat) in enumerate(expenses):
        day = min(28, 3 + i * 4)
        create_band_expense(
            band_id,
            data=month_start.replace(day=day).strftime("%Y-%m-%d"),
            descricao=desc,
            valor=float(valor),
            categoria=cat,
            created_by_user_id=owner_id,
        )

    return {
        "pack": spec["meta_val"],
        "owner_id": owner_id,
        "username": spec["username"],
        "password": DEMO_PASSWORD,
        "display": spec["display"],
        "band_id": band_id,
        "setlist_id": setlist_id,
        "cifra_ids": cifra_ids,
        "month": now.month,
        "year": now.year,
    }


def seed_studio_finance(*, slot: int) -> dict:
    from config import app_now_naive
    from db import create_band, get_db, get_user_bands
    from models_studio import (
        create_booking,
        create_room,
        create_studio,
        get_studio,
        list_rooms,
        list_studios_by_owner,
        replace_weekly_availability,
        update_booking_status,
        update_room,
        update_studio,
    )
    from models_studio_finance import create_studio_expense, update_booking_finance
    from studio_scheduling import BOOKING_CONFIRMADO

    # Migra conta legada (estudio_teste → carlos_groove) antes de criar outra
    for legacy in STUDIO.get("legacy_usernames") or ():
        _migrate_legacy_username(
            legacy,
            STUDIO["username"],
            STUDIO["email"],
            STUDIO["display"],
            STUDIO["password"],
        )

    owner_id = _ensure_user(
        STUDIO["username"],
        STUDIO["email"],
        STUDIO["password"],
        STUDIO["display"],
    )
    existing = list_studios_by_owner(owner_id)
    if existing:
        studio_id = existing[0]["id"]
        update_studio(
            studio_id,
            nome=STUDIO["nome"],
            cidade="Fortaleza",
            bairro="Aldeota",
            endereco="Av. Santos Dumont, 1200",
            telefone="(85) 3222-1000",
            whatsapp="85999887766",
            preco_hora=90.0,
            descricao="Salas climatizadas com PA e isolamento — Aldeota, Fortaleza.",
        )
    else:
        studio_id = create_studio(
            owner_id,
            nome=STUDIO["nome"],
            cidade="Fortaleza",
            bairro="Aldeota",
            endereco="Av. Santos Dumont, 1200",
            telefone="(85) 3222-1000",
            whatsapp="85999887766",
            descricao="Salas climatizadas com PA e isolamento — Aldeota, Fortaleza.",
            preco_hora=90.0,
        )

    rooms = list_rooms(studio_id, active_only=False)
    if not rooms:
        create_room(
            studio_id,
            nome="Sala A — Banda completa",
            capacidade_pessoas=8,
            equipamentos=["Bateria", "PA"],
            preco_hora=120.0,
        )
        create_room(
            studio_id,
            nome="Sala B — Acústico",
            capacidade_pessoas=4,
            equipamentos=["Violão"],
            preco_hora=70.0,
        )
        rooms = list_rooms(studio_id, active_only=False)
    else:
        for i, r in enumerate(rooms[:2]):
            update_room(r["id"], preco_hora=120.0 if i == 0 else 70.0)

    weekly = [
        {"dia_semana": dow, "hora_inicio": "09:00", "hora_fim": "22:00"}
        for dow in range(6)
    ]
    for r in rooms:
        replace_weekly_availability(r["id"], weekly)

    # Bandas clientes com nomes reais (não “teste”)
    client_band_names = [
        "Maré Alta",
        "Trio Vento",
        "Worship House",
        "Som do Beco",
        "Os Originais",
        "Banda Norte",
        "Louvor Vivo",
        "Quinteto Azul",
        "Samba Groove",
        "Rock Aldeota",
        "MPB Session",
        "Nova Geração",
    ]
    owned = {b["name"]: b["id"] for b in get_user_bands(owner_id)}
    # Renomeia bandas antigas com “teste”/“test”/“fin” genéricos
    db = get_db()
    c = db.cursor()
    for b in get_user_bands(owner_id):
        name_l = (b.get("name") or "").lower()
        if any(
            tok in name_l for tok in ("teste", "test", "banda fin", "clientes groove")
        ):
            new_name = client_band_names[hash(b["id"]) % len(client_band_names)]
            # evita colisão
            while new_name in owned and owned[new_name] != b["id"]:
                new_name = f"{new_name} CE"
            c.execute("UPDATE bands SET name = ? WHERE id = ?", (new_name, b["id"]))
            owned[new_name] = b["id"]
    db.commit()
    db.close()
    owned = {b["name"]: b["id"] for b in get_user_bands(owner_id)}

    client_band_ids: list[str] = []
    for name in client_band_names:
        if name in owned:
            client_band_ids.append(owned[name])
        else:
            client_band_ids.append(
                create_band(name, "Banda parceira do Groove Box", owner_id)
            )

    now = app_now_naive()
    ym = now.strftime("%Y-%m")
    db = get_db()
    c = db.cursor()
    c.execute(
        """DELETE FROM studio_bookings
           WHERE room_id IN (SELECT id FROM studio_rooms WHERE studio_id = ?)
             AND data LIKE ?""",
        (studio_id, f"{ym}%"),
    )
    c.execute(
        "DELETE FROM studio_expenses WHERE studio_id = ? AND data LIKE ?",
        (studio_id, f"{ym}%"),
    )
    db.commit()
    db.close()

    room_ids = [r["id"] for r in rooms]
    for i in range(12):
        day = min(28, 1 + ((i + slot) % 27))
        data = now.replace(day=day).strftime("%Y-%m-%d")
        room_id = room_ids[i % len(room_ids)]
        band_id = client_band_ids[i % len(client_band_ids)]
        hi = 10 + (i % 8)
        hf = hi + 2
        bid = create_booking(
            room_id,
            band_id,
            owner_id,
            data=data,
            hora_inicio=f"{hi:02d}:00",
            hora_fim=f"{hf:02d}:00",
            observacao="Ensaio agendado",
        )
        update_booking_status(bid, BOOKING_CONFIRMADO)
        valor = 140.0 + (i * 25) + (slot * 10)
        update_booking_finance(
            bid,
            valor_cobrado=valor,
            paid=(i % 3 != 2),
            finance_notes="PIX" if i % 2 == 0 else "Cartão",
        )

    expenses = [
        ("Energia elétrica", 890, "utilidades"),
        ("Internet fibra", 149, "utilidades"),
        ("Manutenção ar-condicionado", 320, "manutencao"),
        ("Limpeza mensal", 400, "servicos"),
        ("Troca de cabos XLR", 180, "equipamento"),
        ("Anúncio Instagram Ads", 250, "marketing"),
        ("Água mineral parceiros", 95, "outros"),
        ("Segurança noturna", 600, "servicos"),
    ]
    for i, (desc, valor, cat) in enumerate(expenses):
        day = min(28, 2 + i * 3)
        create_studio_expense(
            studio_id,
            data=now.replace(day=day).strftime("%Y-%m-%d"),
            descricao=desc,
            valor=float(valor),
            categoria=cat,
            created_by_user_id=owner_id,
        )

    studio = get_studio(studio_id)
    return {
        "pack": "estudio",
        "owner_id": owner_id,
        "username": STUDIO["username"],
        "password": STUDIO["password"],
        "display": STUDIO["display"],
        "studio_id": studio_id,
        "studio_nome": studio["nome"] if studio else STUDIO["nome"],
        "month": now.month,
        "year": now.year,
    }


def main(slot: int | None = None) -> dict:
    from db import init_db

    init_db()
    slot = slot_for_date() if slot is None else int(slot)
    br = seed_band_pack(BR, songs_br(), slot=slot)
    gospel = seed_band_pack(GOSPEL, songs_gospel(), slot=slot)
    estudio = seed_studio_finance(slot=slot)
    return {"slot": slot, "br": br, "gospel": gospel, "estudio": estudio}


if __name__ == "__main__":
    slot_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    info = main(slot_arg)
    print(f"Seed marketing OK — slot {info['slot']}")
    print(f"  BR:     {info['br']['username']} / banda {info['br']['band_id']}")
    print(f"  Gospel: {info['gospel']['username']} / banda {info['gospel']['band_id']}")
    print(f"  Estúdio:{info['estudio']['username']} / {info['estudio']['studio_id']}")
