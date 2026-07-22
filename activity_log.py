"""Histórico global de alterações para o painel Master (/admin/historico)."""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Any

from config import app_now_str
from database import get_db
from db import get_user, user_display_name

logger = logging.getLogger(__name__)

# Namespace fixo para IDs determinísticos no backfill (idempotente).
_BACKFILL_NS = uuid.UUID('6c8f2b1e-4a91-4d3c-9e07-a1b2c3d4e5f6')

_SKIP_NOTIFICATION_TYPES = frozenset({
    'product_update',
    'event_reminder',
    'event_prep_reminder',
})

_backfill_ran = False


def _entity_type_from_action(action: str) -> str:
    raw = (action or '').strip()
    if raw.startswith('admin_'):
        raw = raw[6:]
    for prefix, entity in (
        ('cifra_', 'cifra'),
        ('setlist_', 'setlist'),
        ('band_', 'band'),
        ('event_', 'event'),
        ('vocalist_', 'vocalist'),
        ('member_', 'member'),
        ('subscription_', 'assinatura'),
        ('voucher_', 'voucher'),
        ('user_', 'user'),
        ('testimonial_', 'testimonial'),
        ('invite_', 'invite'),
        ('whatsapp_', 'whatsapp'),
        ('superadmin_', 'user'),
        ('studio_', 'studio'),
    ):
        if raw.startswith(prefix) or action.startswith(prefix):
            return entity
    if 'subscription' in raw:
        return 'assinatura'
    if 'user' in raw or 'registered' in raw:
        return 'user'
    return 'system'


def _entity_id_from_url(url_path: str | None, action: str) -> str | None:
    if not url_path:
        return None
    path = url_path.split('?', 1)[0]
    patterns = (
        (r'^/admin/usuarios/([0-9a-fA-F-]{36})', 'user'),
        (r'^/cifras/([0-9a-fA-F-]{36})', 'cifra'),
        (r'^/setlists/(\d+)', 'setlist'),
        (r'^/agenda/([0-9a-fA-F-]{36})', 'event'),
        (r'^/bands/([0-9a-fA-F-]{36})', 'band'),
    )
    for pat, _kind in patterns:
        m = re.match(pat, path)
        if m:
            return m.group(1)
    return None


def _repair_user_activity_rows() -> int:
    """Corrige cadastros antigos sem entity_type=user / entity_id / URL da ficha."""
    db = get_db()
    c = db.cursor()
    repaired = 0
    try:
        c.execute(
            '''SELECT id, actor_user_id, action, entity_type, entity_id, meta_json
               FROM admin_activity_log
               WHERE action IN ('user_registered', 'admin_user_registered')
                  OR (action LIKE '%user%register%' AND actor_user_id IS NOT NULL)'''
        )
        rows = [dict(r) for r in c.fetchall()]
    except Exception:
        db.close()
        return 0

    for row in rows:
        uid = str(row.get('actor_user_id') or '')
        if not uid:
            continue
        meta = {}
        raw = row.get('meta_json')
        if raw:
            try:
                meta = json.loads(raw) if isinstance(raw, str) else dict(raw)
            except (TypeError, ValueError, json.JSONDecodeError):
                meta = {}
        url = (meta.get('url_path') or '').strip()
        wanted_url = f'/admin/usuarios/{uid}'
        needs = (
            (row.get('entity_type') or '') != 'user'
            or str(row.get('entity_id') or '') != uid
            or url != wanted_url
        )
        if not needs:
            continue
        meta['url_path'] = wanted_url
        meta.setdefault('title', 'Novo usuário no app')
        try:
            c.execute(
                '''UPDATE admin_activity_log
                   SET entity_type = ?, entity_id = ?, meta_json = ?
                   WHERE id = ?''',
                ('user', uid, json.dumps(meta, ensure_ascii=False), row['id']),
            )
            repaired += 1
        except Exception:
            continue
    try:
        db.commit()
    except Exception:
        pass
    db.close()
    return repaired


def _deterministic_id(*parts: Any) -> str:
    key = '|'.join('' if p is None else str(p) for p in parts)
    return str(uuid.uuid5(_BACKFILL_NS, key))


def log_activity(
    *,
    actor_user_id: str | None,
    action: str,
    summary: str,
    title: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    band_id: str | None = None,
    url_path: str | None = None,
    meta: dict | None = None,
    entry_id: str | None = None,
    created_at: str | None = None,
) -> str | None:
    """Registra uma linha no histórico. Nunca propaga erro ao fluxo principal."""
    ok, eid = _insert_activity(
        actor_user_id=actor_user_id,
        action=action,
        summary=summary,
        title=title,
        entity_type=entity_type,
        entity_id=entity_id,
        band_id=band_id,
        url_path=url_path,
        meta=meta,
        entry_id=entry_id,
        created_at=created_at,
    )
    return eid if ok or eid else None


def _insert_activity(
    *,
    actor_user_id: str | None,
    action: str,
    summary: str,
    title: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    band_id: str | None = None,
    url_path: str | None = None,
    meta: dict | None = None,
    entry_id: str | None = None,
    created_at: str | None = None,
) -> tuple[bool, str | None]:
    """Retorna (inseriu_agora, entry_id)."""
    action = (action or '').strip()
    summary = (summary or '').strip()
    if not action or not summary:
        return False, None
    entry_id = entry_id or str(uuid.uuid4())
    entity = (entity_type or _entity_type_from_action(action)).strip() or 'system'
    payload = dict(meta or {})
    if url_path:
        payload.setdefault('url_path', url_path)
    if title:
        payload.setdefault('title', title)
    try:
        db = get_db()
        c = db.cursor()
        c.execute(
            '''INSERT INTO admin_activity_log
               (id, created_at, actor_user_id, action, entity_type, entity_id,
                band_id, summary, meta_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (id) DO NOTHING''',
            (
                entry_id,
                created_at or app_now_str(),
                actor_user_id,
                action[:80],
                entity[:40],
                (str(entity_id) if entity_id is not None else None),
                band_id,
                summary[:2000],
                json.dumps(payload, ensure_ascii=False) if payload else None,
            ),
        )
        inserted = (c.rowcount or 0) > 0
        db.commit()
        db.close()
        return inserted, entry_id
    except Exception:
        try:
            db.close()
        except Exception:
            pass
        return False, None


def _norm_ts(value: Any) -> str:
    if value is None:
        return ''
    text = str(value).replace('T', ' ')
    return text[:19]


def backfill_admin_activity(*, force: bool = False) -> dict[str, int]:
    """Importa ações antigas a partir de notifications (+ convites WhatsApp).

    Idempotente: IDs determinísticos + ON CONFLICT DO NOTHING.
    """
    global _backfill_ran
    if _backfill_ran and not force:
        return {'skipped': 1}

    inserted = 0
    seen_notif = 0
    skipped_noise = 0
    wa_inserted = 0

    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            '''SELECT type, title, body, actor_user_id, band_id, url_path, created_at
               FROM notifications
               ORDER BY created_at ASC'''
        )
        rows = [dict(r) for r in c.fetchall()]
    except Exception as exc:
        db.close()
        logger.warning('Backfill notifications falhou: %s', exc)
        return {'error': 1}
    db.close()

    dedupe: dict[str, dict] = {}
    for row in rows:
        seen_notif += 1
        action = (row.get('type') or '').strip()
        if not action or action in _SKIP_NOTIFICATION_TYPES:
            skipped_noise += 1
            continue
        summary = (row.get('body') or row.get('title') or '').strip()
        if not summary:
            continue
        created = _norm_ts(row.get('created_at'))
        key = _deterministic_id(
            'notif',
            action,
            row.get('actor_user_id'),
            summary,
            row.get('band_id'),
            created,
        )
        # Mantém o mais antigo se houver colisão de chave parcial.
        if key not in dedupe:
            dedupe[key] = row

    for entry_id, row in dedupe.items():
        action = (row.get('type') or '').strip()
        summary = (row.get('body') or row.get('title') or '').strip()
        url_path = (row.get('url_path') or '').strip() or None
        created = _norm_ts(row.get('created_at'))
        entity_id = _entity_id_from_url(url_path, action)
        if not entity_id and action in (
            'admin_user_registered', 'user_registered',
        ) and row.get('actor_user_id'):
            entity_id = str(row['actor_user_id'])
            if not url_path or url_path.rstrip('/') in ('/admin', '/admin/'):
                url_path = f'/admin/usuarios/{entity_id}'
        ok, _ = _insert_activity(
            actor_user_id=row.get('actor_user_id'),
            action=action,
            title=(row.get('title') or '').strip() or None,
            summary=summary,
            entity_type='user' if entity_id and action in (
                'admin_user_registered', 'user_registered',
            ) else None,
            entity_id=entity_id,
            band_id=row.get('band_id'),
            url_path=url_path,
            meta={'source': 'backfill_notifications'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1

    # Convites WhatsApp do admin
    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            '''SELECT id, target_type, target_id, phone, sent_by_user_id,
                      success, created_at
               FROM admin_whatsapp_invites
               ORDER BY created_at ASC'''
        )
        invites = [dict(r) for r in c.fetchall()]
    except Exception:
        invites = []
    db.close()

    for inv in invites:
        created = _norm_ts(inv.get('created_at'))
        phone = inv.get('phone') or ''
        ok_flag = 'ok' if inv.get('success') else 'falhou'
        entry_id = _deterministic_id('wa', inv.get('id') or phone, created)
        ok, _ = _insert_activity(
            actor_user_id=inv.get('sent_by_user_id'),
            action='whatsapp_invite',
            title='Convite WhatsApp',
            summary=(
                f'Convite WhatsApp ({inv.get("target_type") or "lead"}) '
                f'para {phone} — {ok_flag}.'
            ),
            entity_type='whatsapp',
            entity_id=str(inv.get('target_id') or ''),
            url_path='/admin/#tab-convites',
            meta={'source': 'backfill_whatsapp', 'invite_id': inv.get('id')},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            wa_inserted += 1

    entities_inserted = _backfill_from_entities()
    repaired_users = _repair_user_activity_rows()

    _backfill_ran = True
    result = {
        'notifications_scanned': seen_notif,
        'unique_events': len(dedupe),
        'inserted': inserted,
        'skipped_noise': skipped_noise,
        'whatsapp_inserted': wa_inserted,
        'entities_inserted': entities_inserted,
        'repaired_users': repaired_users,
        'total': count_admin_activity(),
    }
    logger.info('Backfill activity_log: %s', result)
    return result


def _actor_label(user_id: str | None) -> str:
    if not user_id:
        return 'Alguém'
    user = get_user(user_id)
    return user_display_name(user) if user else 'Alguém'


def _existing_activity_keys() -> set[tuple[str, str]]:
    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            "SELECT entity_id, action FROM admin_activity_log "
            "WHERE entity_id IS NOT NULL AND entity_id != ''"
        )
        keys = {(str(r['entity_id']), str(r['action'])) for r in c.fetchall()}
    except Exception:
        keys = set()
    db.close()
    return keys


def _backfill_from_entities() -> int:
    """Completa lacunas de seed/scripts sem notificação (ex.: showcase)."""
    inserted = 0
    existing = _existing_activity_keys()
    db = get_db()
    c = db.cursor()

    # Mapa banda → owner (para cifras/setlists sem created_by)
    band_owner: dict[str, str] = {}
    band_name: dict[str, str] = {}
    try:
        c.execute('SELECT id, name, owner_id, created_at FROM bands')
        bands = [dict(r) for r in c.fetchall()]
    except Exception:
        bands = []

    for band in bands:
        bid = str(band['id'])
        owner = band.get('owner_id')
        if owner:
            band_owner[bid] = owner
        band_name[bid] = band.get('name') or 'Banda'
        actions = ('band_created', 'admin_band_created')
        if any((bid, a) in existing for a in actions):
            continue
        actor = owner
        name = band_name[bid]
        who = _actor_label(actor)
        created = _norm_ts(band.get('created_at'))
        entry_id = _deterministic_id('entity', 'band_created', bid)
        ok, _ = _insert_activity(
            actor_user_id=actor,
            action='band_created',
            title=f'{name} — banda criada',
            summary=f'{who} criou a banda «{name}».',
            entity_type='band',
            entity_id=bid,
            band_id=bid,
            url_path=f'/bands/{bid}',
            meta={'source': 'backfill_entities'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1
            existing.add((bid, 'band_created'))

    # Cadastros de usuário
    try:
        c.execute(
            '''SELECT id, username, display_name, email, google_id, password_hash, created_at
               FROM users ORDER BY created_at ASC'''
        )
        users = [dict(r) for r in c.fetchall()]
    except Exception:
        users = []

    for user in users:
        uid = str(user['id'])
        if (uid, 'user_registered') in existing or (uid, 'admin_user_registered') in existing:
            continue
        who = _actor_label(uid)
        login = user.get('username') or ''
        via = 'Google' if user.get('google_id') and not user.get('password_hash') else 'cadastro'
        created = _norm_ts(user.get('created_at'))
        entry_id = _deterministic_id('entity', 'user_registered', uid)
        ok, _ = _insert_activity(
            actor_user_id=uid,
            action='user_registered',
            title='Novo usuário no app',
            summary=f'{who} (@{login}) criou conta via {via}.',
            entity_type='user',
            entity_id=uid,
            url_path=f'/admin/usuarios/{uid}',
            meta={'source': 'backfill_entities'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1
            existing.add((uid, 'user_registered'))

    # Cifras (ator = owner da banda ou owner_user_id)
    try:
        c.execute(
            '''SELECT id, band_id, owner_user_id, titulo, created_at, updated_at
               FROM cifras ORDER BY created_at ASC'''
        )
        cifras = [dict(r) for r in c.fetchall()]
    except Exception:
        cifras = []

    for row in cifras:
        cid = str(row['id'])
        if (cid, 'cifra_created') in existing:
            continue
        bid = str(row['band_id']) if row.get('band_id') else None
        actor = row.get('owner_user_id') or (band_owner.get(bid) if bid else None)
        titulo = row.get('titulo') or 'Sem título'
        who = _actor_label(actor)
        bname = band_name.get(bid or '', 'Banda')
        created = _norm_ts(row.get('created_at'))
        entry_id = _deterministic_id('entity', 'cifra_created', cid)
        ok, _ = _insert_activity(
            actor_user_id=actor,
            action='cifra_created',
            title=f'{bname} — nova cifra',
            summary=f'{who} adicionou a cifra «{titulo}».',
            entity_type='cifra',
            entity_id=cid,
            band_id=bid,
            url_path=f'/cifras/{cid}',
            meta={'source': 'backfill_entities'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1
            existing.add((cid, 'cifra_created'))

        # Edição posterior (quando updated_at difere de created_at)
        upd = _norm_ts(row.get('updated_at'))
        if upd and created and upd != created and (cid, 'cifra_updated') not in existing:
            entry_upd = _deterministic_id('entity', 'cifra_updated', cid, upd)
            ok2, _ = _insert_activity(
                actor_user_id=actor,
                action='cifra_updated',
                title=f'{bname} — cifra editada',
                summary=f'{who} editou a cifra «{titulo}».',
                entity_type='cifra',
                entity_id=cid,
                band_id=bid,
                url_path=f'/cifras/{cid}',
                meta={'source': 'backfill_entities'},
                entry_id=entry_upd,
                created_at=upd,
            )
            if ok2:
                inserted += 1
                existing.add((cid, 'cifra_updated'))

    # Setlists
    try:
        c.execute('SELECT id, band_id, name, created_at FROM setlists ORDER BY created_at ASC')
        setlists = [dict(r) for r in c.fetchall()]
    except Exception:
        setlists = []

    for row in setlists:
        sid = str(row['id'])
        if (sid, 'setlist_created') in existing:
            continue
        bid = str(row['band_id']) if row.get('band_id') else None
        actor = band_owner.get(bid) if bid else None
        name = row.get('name') or 'Setlist'
        who = _actor_label(actor)
        bname = band_name.get(bid or '', 'Banda')
        created = _norm_ts(row.get('created_at'))
        entry_id = _deterministic_id('entity', 'setlist_created', sid)
        ok, _ = _insert_activity(
            actor_user_id=actor,
            action='setlist_created',
            title=f'{bname} — nova setlist',
            summary=f'{who} criou a setlist «{name}».',
            entity_type='setlist',
            entity_id=sid,
            band_id=bid,
            url_path=f'/setlists/{sid}',
            meta={'source': 'backfill_entities'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1
            existing.add((sid, 'setlist_created'))

    # Eventos da agenda (created_by confiável)
    try:
        c.execute(
            '''SELECT id, band_id, title, event_type, created_by, created_at
               FROM band_events ORDER BY created_at ASC'''
        )
        events = [dict(r) for r in c.fetchall()]
    except Exception:
        events = []

    for row in events:
        eid = str(row['id'])
        if (eid, 'event_created') in existing:
            continue
        bid = str(row['band_id']) if row.get('band_id') else None
        actor = row.get('created_by') or (band_owner.get(bid) if bid else None)
        title = row.get('title') or 'Evento'
        who = _actor_label(actor)
        bname = band_name.get(bid or '', 'Banda')
        created = _norm_ts(row.get('created_at'))
        entry_id = _deterministic_id('entity', 'event_created', eid)
        ok, _ = _insert_activity(
            actor_user_id=actor,
            action='event_created',
            title=f'{bname} — evento agendado',
            summary=f'{who} marcou «{title}» na agenda.',
            entity_type='event',
            entity_id=eid,
            band_id=bid,
            url_path=f'/agenda/{eid}',
            meta={'source': 'backfill_entities'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1
            existing.add((eid, 'event_created'))

    # Membros (exceto dono já coberto pela criação da banda)
    try:
        c.execute(
            '''SELECT bm.band_id, bm.user_id, bm.role, bm.joined_at, b.owner_id
               FROM band_members bm
               JOIN bands b ON b.id = bm.band_id
               ORDER BY bm.joined_at ASC'''
        )
        members = [dict(r) for r in c.fetchall()]
    except Exception:
        members = []

    for row in members:
        bid = str(row['band_id'])
        mid = str(row['user_id'])
        if mid == str(row.get('owner_id') or ''):
            continue
        key_id = f'{bid}:{mid}'
        if (key_id, 'member_joined') in existing:
            continue
        who = _actor_label(mid)
        bname = band_name.get(bid, 'Banda')
        created = _norm_ts(row.get('joined_at'))
        entry_id = _deterministic_id('entity', 'member_joined', bid, mid)
        ok, _ = _insert_activity(
            actor_user_id=mid,
            action='member_joined',
            title=f'{bname} — novo membro',
            summary=f'{who} entrou na banda {bname}.',
            entity_type='member',
            entity_id=key_id,
            band_id=bid,
            url_path=f'/bands/{bid}',
            meta={'source': 'backfill_entities'},
            entry_id=entry_id,
            created_at=created or None,
        )
        if ok:
            inserted += 1
            existing.add((key_id, 'member_joined'))

    db.close()
    return inserted


def count_admin_activity_by_type() -> dict[str, int]:
    """Contagem por entity_type para filtros rápidos no painel."""
    db = get_db()
    c = db.cursor()
    try:
        c.execute(
            '''SELECT entity_type, COUNT(*) AS n
               FROM admin_activity_log
               GROUP BY entity_type'''
        )
        out = {str(r['entity_type'] or 'system'): int(r['n'] or 0) for r in c.fetchall()}
    except Exception:
        out = {}
    db.close()
    return out


def list_admin_activity(
    *,
    limit: int = 100,
    offset: int = 0,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_user_id: str | None = None,
    related_user_id: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit or 100), 500))
    offset = max(0, int(offset or 0))
    clauses: list[str] = []
    params: list[Any] = []
    if entity_type:
        clauses.append('entity_type = ?')
        params.append(entity_type)
    if entity_id:
        clauses.append('entity_id = ?')
        params.append(str(entity_id))
    if related_user_id:
        clauses.append('(actor_user_id = ? OR entity_id = ?)')
        params.extend([str(related_user_id), str(related_user_id)])
    elif actor_user_id:
        clauses.append('actor_user_id = ?')
        params.append(actor_user_id)
    if q:
        clauses.append('(summary LIKE ? OR action LIKE ?)')
        like = f'%{q.strip()}%'
        params.extend([like, like])
    where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT id, created_at, actor_user_id, action, entity_type, entity_id,
                   band_id, summary, meta_json
            FROM admin_activity_log
            {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?''',
        (*params, limit, offset),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()

    for row in rows:
        actor = get_user(row.get('actor_user_id')) if row.get('actor_user_id') else None
        row['actor_name'] = user_display_name(actor) if actor else 'Sistema'
        row['actor_username'] = (actor or {}).get('username') or ''
        meta = {}
        raw_meta = row.get('meta_json')
        if raw_meta:
            try:
                meta = json.loads(raw_meta) if isinstance(raw_meta, str) else dict(raw_meta)
            except (TypeError, ValueError, json.JSONDecodeError):
                meta = {}
        row['meta'] = meta
        row['url_path'] = _resolve_activity_url(row, meta)
        row['title'] = meta.get('title') or ''
        from demo_accounts import is_demo_user

        row['is_demo'] = is_demo_user(actor)
    return rows


def _resolve_activity_url(row: dict[str, Any], meta: dict | None = None) -> str:
    """URL clicável; reconstrói quando o meta antigo aponta só para /admin/."""
    meta = meta or {}
    raw = (meta.get('url_path') or '').strip()
    entity = (row.get('entity_type') or '').strip()
    eid = str(row.get('entity_id') or '').strip()
    band_id = str(row.get('band_id') or '').strip()
    actor = str(row.get('actor_user_id') or '').strip()

    def _ok(path: str) -> bool:
        p = (path or '').split('?', 1)[0].rstrip('/')
        return bool(p) and p not in ('/admin',)

    if _ok(raw):
        return raw

    if entity == 'user' and (eid or actor):
        return f'/admin/usuarios/{eid or actor}'
    if entity == 'band' and (eid or band_id):
        return f'/bands/{eid or band_id}'
    if entity == 'cifra' and eid:
        return f'/cifras/{eid}'
    if entity == 'setlist' and eid:
        return f'/setlists/{eid}'
    if entity == 'event' and eid:
        return f'/agenda/{eid}'
    if entity == 'member' and band_id:
        return f'/bands/{band_id}/members'
    if entity == 'assinatura':
        return '/admin/'
    if entity == 'whatsapp':
        return '/admin/#tab-convites'
    if band_id:
        return f'/bands/{band_id}'
    return raw or ''


def count_admin_activity(
    *,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_user_id: str | None = None,
    related_user_id: str | None = None,
    q: str | None = None,
) -> int:
    clauses: list[str] = []
    params: list[Any] = []
    if entity_type:
        clauses.append('entity_type = ?')
        params.append(entity_type)
    if entity_id:
        clauses.append('entity_id = ?')
        params.append(str(entity_id))
    if related_user_id:
        clauses.append('(actor_user_id = ? OR entity_id = ?)')
        params.extend([str(related_user_id), str(related_user_id)])
    elif actor_user_id:
        clauses.append('actor_user_id = ?')
        params.append(actor_user_id)
    if q:
        clauses.append('(summary LIKE ? OR action LIKE ?)')
        like = f'%{q.strip()}%'
        params.extend([like, like])
    where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
    db = get_db()
    c = db.cursor()
    c.execute(f'SELECT COUNT(*) AS n FROM admin_activity_log {where}', params)
    row = c.fetchone()
    db.close()
    return int((row['n'] if row else 0) or 0)
