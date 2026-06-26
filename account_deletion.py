"""Exclusão de conta e bloqueios (LGPD — direito de eliminação)."""

from __future__ import annotations

from db import (
    delete_all_push_subscriptions,
    get_db,
    get_owned_bands,
    get_user_bands,
    is_superadmin,
    delete_band,
)
from models_studio import list_studios_by_owner


def account_deletion_blockers(user_id: str) -> list[str]:
    """Motivos que impedem exclusão imediata; lista vazia = pode excluir."""
    if is_superadmin(user_id):
        return ['Contas de superadmin não podem ser excluídas pelo app. Fale com a equipe técnica.']

    blockers: list[str] = []
    for band in get_owned_bands(user_id):
        members = _count_band_members(band['id'])
        if members > 1:
            blockers.append(
                f'A banda «{band["name"]}» tem outros integrantes. '
                f'Remova os membros ou exclua a banda em Configurações antes de apagar sua conta.'
            )
    studios = list_studios_by_owner(user_id)
    if studios:
        names = ', '.join(s['nome'] for s in studios[:3])
        extra = f' (+{len(studios) - 3})' if len(studios) > 3 else ''
        blockers.append(
            f'Você ainda tem estúdio(s) cadastrado(s): {names}{extra}. '
            f'Entre em contato com { _privacy_email() } para remover o cadastro do estúdio.'
        )
    return blockers


def _privacy_email() -> str:
    from lgpd import privacy_contact_email
    return privacy_contact_email()


def _count_band_members(band_id: str) -> int:
    db = get_db()
    c = db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM band_members WHERE band_id = ?', (band_id,))
    row = c.fetchone()
    db.close()
    return int((row or {}).get('n') or 0)


def delete_user_account(user_id: str) -> tuple[bool, str]:
    """Remove conta e dados pessoais vinculados. Retorna (ok, mensagem)."""
    blockers = account_deletion_blockers(user_id)
    if blockers:
        return False, blockers[0]

    for band in get_owned_bands(user_id):
        delete_band(band['id'])

    delete_all_push_subscriptions(user_id)

    db = get_db()
    c = db.cursor()

    tables_user_id = [
        'DELETE FROM notifications WHERE user_id = ?',
        'DELETE FROM user_instruments WHERE user_id = ?',
        'DELETE FROM user_availability_blockouts WHERE user_id = ?',
        'DELETE FROM cifra_user_drafts WHERE user_id = ?',
        'DELETE FROM cifra_play_drawings WHERE user_id = ?',
        'DELETE FROM push_subscriptions WHERE user_id = ?',
        'DELETE FROM studio_voucher_usos WHERE user_id = ?',
        'DELETE FROM studio_subscriptions WHERE user_id = ?',
        'DELETE FROM band_member_invites WHERE user_id = ?',
        'DELETE FROM band_members WHERE user_id = ?',
        'DELETE FROM band_event_assignments WHERE user_id = ?',
        'DELETE FROM band_lineup_members WHERE user_id = ?',
        'DELETE FROM band_role_pool WHERE user_id = ?',
    ]
    for sql in tables_user_id:
        try:
            c.execute(sql, (user_id,))
        except Exception:
            pass

    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    deleted = c.rowcount
    db.commit()
    db.close()

    if not deleted:
        return False, 'Conta não encontrada.'
    return True, 'Conta excluída.'


def user_data_summary(user_id: str) -> dict:
    """Resumo dos dados pessoais para exibição ao titular."""
    from db import get_user

    user = get_user(user_id) or {}
    bands = get_user_bands(user_id)
    studios = list_studios_by_owner(user_id)
    return {
        'user': {
            'username': user.get('username'),
            'display_name': user.get('display_name'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'created_at': user.get('created_at'),
            'privacy_accepted_at': user.get('privacy_accepted_at'),
        },
        'bands_count': len(bands),
        'bands': [{'name': b.get('name'), 'role': 'membro'} for b in bands[:20]],
        'studios_count': len(studios),
        'studios': [{'nome': s.get('nome'), 'cidade': s.get('cidade')} for s in studios[:20]],
    }
