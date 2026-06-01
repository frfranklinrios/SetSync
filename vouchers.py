"""Vouchers promocionais e de indicação."""

from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta

from db import (
    count_vouchers_indicacao_ativos,
    create_voucher,
    get_voucher_by_codigo,
    get_voucher_uso_banda,
    increment_voucher_usos,
    insert_voucher_uso,
    update_assinatura,
    get_assinatura,
    get_owned_bands,
    get_user,
)
from monetizacao import (
    PLANO_PRO,
    PLANOS,
    STATUS_ATIVA,
    get_assinatura_banda,
)


VOUCHER_INDICACAO_DIAS = 15
VOUCHER_INDICACAO_MAX_ATIVOS = 5
STATUS_VOUCHER = 'voucher'
STATUS_EXPIRADO = 'expirado'


def gerar_codigo_voucher(prefixo: str | None = None) -> str:
    """
    Gera código único: PREFIXO-XXXX ou SETSYNC-XXXX.
    """
    base = (prefixo or 'SETSYNC').strip().upper().replace(' ', '-')
    alfabeto = string.ascii_uppercase + string.digits
    for _ in range(50):
        sufixo = ''.join(secrets.choice(alfabeto) for _ in range(4))
        codigo = f'{base}-{sufixo}'
        if not get_voucher_by_codigo(codigo):
            return codigo
    raise RuntimeError('Não foi possível gerar código de voucher único')


def banda_tem_assinatura_paga_ativa(banda_id: str) -> bool:
    """Assinatura paga (MP) ativa — bloqueia resgate de voucher."""
    row = get_assinatura(banda_id)
    if not row:
        return False
    return (
        row.get('plano') in ('pro', 'worship')
        and row.get('status') == STATUS_ATIVA
    )


def validar_resgate_voucher(codigo: str, banda_id: str) -> tuple[bool, str]:
    """Retorna (ok, mensagem_erro)."""
    codigo = (codigo or '').strip().upper()
    voucher = get_voucher_by_codigo(codigo)
    if not voucher:
        return False, 'Voucher não encontrado'
    if not voucher.get('ativo'):
        return False, 'Voucher desativado'
    if voucher.get('data_expiracao'):
        exp = _parse_dt(voucher['data_expiracao'])
        if exp and exp < datetime.utcnow():
            return False, 'Voucher expirado'
    max_usos = voucher.get('max_usos')
    if max_usos is not None and int(voucher.get('usos_atual') or 0) >= int(max_usos):
        return False, 'Limite de usos atingido'
    if get_voucher_uso_banda(voucher['id'], banda_id):
        return False, 'Esta banda já utilizou este voucher'
    if banda_tem_assinatura_paga_ativa(banda_id):
        return False, 'Voucher disponível apenas para plano grátis ou assinatura vencida'
    assinatura = get_assinatura(banda_id)
    if assinatura and assinatura.get('status') == STATUS_VOUCHER:
        return False, 'Esta banda já possui acesso por voucher ativo'
    return True, ''


def resgatar_voucher(codigo: str, banda_id: str, banda_nome: str) -> tuple[bool, str, dict | None]:
    """
    Aplica voucher na banda. Retorna (ok, mensagem, info_extra).
    """
    ok, msg = validar_resgate_voucher(codigo, banda_id)
    if not ok:
        return False, msg, None

    voucher = get_voucher_by_codigo(codigo.strip().upper())
    dias = int(voucher['dias'])
    plano = voucher['plano']
    agora = datetime.utcnow()
    expira = agora + timedelta(days=dias)

    insert_voucher_uso(
        voucher_id=voucher['id'],
        banda_id=banda_id,
        usado_em=agora,
        expira_em=expira,
    )
    increment_voucher_usos(voucher['id'])

    update_assinatura(
        banda_id,
        plano=plano,
        status=STATUS_VOUCHER,
        data_inicio=agora.strftime('%Y-%m-%d %H:%M:%S'),
        data_proxima_cobranca=expira.strftime('%Y-%m-%d %H:%M:%S'),
        data_cancelamento=None,
    )

    info = {
        'dias': dias,
        'plano': plano,
        'plano_nome': PLANOS.get(plano).nome if plano in PLANOS else plano,
        'banda_nome': banda_nome,
    }

    if _is_voucher_indicacao(voucher):
        _recompensa_indicacao(voucher)

    return True, f'{dias} dias de {info["plano_nome"]} ativados para {banda_nome}!', info


def _is_voucher_indicacao(voucher: dict) -> bool:
    return bool(voucher.get('eh_indicacao'))


def _recompensa_indicacao(voucher: dict) -> None:
    """Quem indicou ganha 15 dias na banda principal."""
    criador_id = voucher.get('criado_por_id')
    if not criador_id:
        return
    owned = get_owned_bands(criador_id)
    if not owned:
        return
    banda_id = owned[0]['id']
    assinatura = get_assinatura_banda(banda_id)
    agora = datetime.utcnow()
    base = assinatura.data_proxima_cobranca or agora
    if base < agora:
        base = agora
    nova_cobranca = base + timedelta(days=VOUCHER_INDICACAO_DIAS)

    if assinatura.plano in ('gratis',) or assinatura.status in (STATUS_EXPIRADO, 'cancelada'):
        update_assinatura(
            banda_id,
            plano=PLANO_PRO,
            status=STATUS_VOUCHER,
            data_proxima_cobranca=nova_cobranca.strftime('%Y-%m-%d %H:%M:%S'),
        )
    else:
        update_assinatura(
            banda_id,
            data_proxima_cobranca=nova_cobranca.strftime('%Y-%m-%d %H:%M:%S'),
        )

    user = get_user(criador_id)
    if user and user.get('email'):
        from monetizacao_emails import send_indicacao_recompensa_email
        send_indicacao_recompensa_email(user['email'], VOUCHER_INDICACAO_DIAS)


def criar_voucher_indicacao(criado_por_id: str) -> tuple[str | None, str]:
    """Cria voucher de indicação (Pro, 15 dias, uso único)."""
    if count_vouchers_indicacao_ativos(criado_por_id) >= VOUCHER_INDICACAO_MAX_ATIVOS:
        return None, f'Limite de {VOUCHER_INDICACAO_MAX_ATIVOS} vouchers de indicação ativos'
    codigo = gerar_codigo_voucher('SETSYNC')
    create_voucher(
        codigo=codigo,
        plano=PLANO_PRO,
        dias=VOUCHER_INDICACAO_DIAS,
        criado_por_id=criado_por_id,
        max_usos=1,
        eh_indicacao=True,
    )
    return codigo, ''


def _parse_dt(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value)[:19], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None
