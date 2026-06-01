"""Planos, assinaturas e verificação de limites do modelo freemium."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from db import (
    count_band_cifras,
    count_band_members,
    count_band_setlists,
    count_owned_bands,
    get_assinatura,
    owner_has_worship_ativa,
)

PLANO_GRATIS = 'gratis'
PLANO_PRO = 'pro'
PLANO_WORSHIP = 'worship'

PLANOS_PAGOS = (PLANO_PRO, PLANO_WORSHIP)
STATUS_ATIVA = 'ativa'
STATUS_CANCELADA = 'cancelada'
STATUS_INADIMPLENTE = 'inadimplente'

LIMITES_GRATIS = {
    'musica': 30,
    'integrante': 5,
    'setlist': 10,
    'banda': 1,
}


@dataclass(frozen=True)
class Plano:
    """Definição estática de um plano comercial."""

    id: str
    nome: str
    preco_mensal: float | None
    limites: dict[str, int] | None

    @property
    def sem_limites(self) -> bool:
        return self.limites is None


PLANOS: dict[str, Plano] = {
    PLANO_GRATIS: Plano(
        id=PLANO_GRATIS,
        nome='Grátis',
        preco_mensal=None,
        limites=dict(LIMITES_GRATIS),
    ),
    PLANO_PRO: Plano(
        id=PLANO_PRO,
        nome='Pro',
        preco_mensal=29.0,
        limites=None,
    ),
    PLANO_WORSHIP: Plano(
        id=PLANO_WORSHIP,
        nome='Worship',
        preco_mensal=69.0,
        limites=None,
    ),
}


@dataclass(frozen=True)
class PlanoSite:
    """Plano formatado para landings públicas (home, igrejas)."""

    id: str
    nome: str
    preco_label: str
    sufixo: str
    destaque: bool
    features: tuple[str, ...]
    cta: str
    cta_outline: bool


def _preco_label(valor: float | None) -> str:
    if valor is None or valor <= 0:
        return 'R$ 0'
    if valor == int(valor):
        return f'R$ {int(valor)}'
    return f'R$ {valor:.2f}'.replace('.', ',')


def planos_para_site() -> list[PlanoSite]:
    """Lista de planos com preços e limites para templates públicos."""
    lim = LIMITES_GRATIS
    pro = PLANOS[PLANO_PRO]
    worship = PLANOS[PLANO_WORSHIP]
    return [
        PlanoSite(
            id=PLANO_GRATIS,
            nome=PLANOS[PLANO_GRATIS].nome,
            preco_label=_preco_label(None),
            sufixo='',
            destaque=False,
            features=(
                f'Até {lim["musica"]} músicas',
                f'Até {lim["integrante"]} integrantes',
                f'Até {lim["setlist"]} setlists',
                f'{lim["banda"]} banda por conta',
            ),
            cta='Começar grátis',
            cta_outline=True,
        ),
        PlanoSite(
            id=PLANO_PRO,
            nome=pro.nome,
            preco_label=_preco_label(pro.preco_mensal),
            sufixo='/banda/mês',
            destaque=True,
            features=(
                'Músicas, setlists e integrantes ilimitados',
                'Exportar setlist em PDF',
                'Por banda ou ministério',
            ),
            cta='Criar conta',
            cta_outline=False,
        ),
        PlanoSite(
            id=PLANO_WORSHIP,
            nome=worship.nome,
            preco_label=_preco_label(worship.preco_mensal),
            sufixo='/congregação/mês',
            destaque=False,
            features=(
                'Múltiplas bandas na mesma conta',
                'Sem limites em todos os ministérios',
                'Para igrejas e equipes de louvor',
            ),
            cta='Criar conta',
            cta_outline=True,
        ),
    ]


class Assinatura:
    """Assinatura de uma banda (wrapper sobre registro do banco)."""

    def __init__(self, row: dict[str, Any]):
        self._row = row

    @property
    def id(self) -> str:
        return self._row['id']

    @property
    def banda_id(self) -> str:
        return self._row['banda_id']

    @property
    def plano(self) -> str:
        return self._row['plano']

    @property
    def status(self) -> str:
        return self._row['status']

    @property
    def mp_subscription_id(self) -> str | None:
        return self._row.get('mp_subscription_id')

    @property
    def mp_preapproval_id(self) -> str | None:
        return self._row.get('mp_preapproval_id')

    @property
    def data_inicio(self) -> datetime | None:
        return _parse_dt(self._row.get('data_inicio'))

    @property
    def data_proxima_cobranca(self) -> datetime | None:
        return _parse_dt(self._row.get('data_proxima_cobranca'))

    @property
    def data_cancelamento(self) -> datetime | None:
        return _parse_dt(self._row.get('data_cancelamento'))

    @classmethod
    def from_row(cls, row: dict[str, Any] | None) -> Assinatura | None:
        if not row:
            return None
        return cls(row)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._row)

    def plano_efetivo(self) -> Plano:
        return PLANOS.get(self.plano, PLANOS[PLANO_GRATIS])

    def tem_acesso_premium(self) -> bool:
        """Pro/Worship com assinatura ativa (paga ou voucher futuro)."""
        return (
            self.plano in PLANOS_PAGOS
            and self.status in (STATUS_ATIVA, 'voucher')
        )


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(value[:19], fmt[: len(value)])
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


def _formatar_data_curta(dt: datetime | None) -> str:
    if not dt:
        return ''
    return dt.strftime('%d/%m/%Y')


def plano_badge_ui(banda_id: str) -> dict[str, Any]:
    """
    Dados para exibir o plano da banda na UI (badge Bootstrap + texto).
    """
    assinatura = get_assinatura_banda(banda_id)
    plano = assinatura.plano
    status = assinatura.status
    nome = PLANOS.get(plano, PLANOS[PLANO_GRATIS]).nome
    badge = 'secondary'
    label = nome

    if status == 'voucher':
        badge = 'success'
        label = f'{nome} · período promocional'
        expira = assinatura.data_proxima_cobranca
        if expira:
            label += f' (até {_formatar_data_curta(expira)})'
    elif plano == PLANO_PRO and status == STATUS_ATIVA:
        badge = 'primary'
        label = 'Pro'
    elif plano == PLANO_WORSHIP and status == STATUS_ATIVA:
        badge = 'info'
        label = 'Worship'
    elif status == STATUS_INADIMPLENTE:
        badge = 'warning'
        label = f'{nome} · pagamento pendente'
    elif status == STATUS_CANCELADA:
        badge = 'secondary'
        label = 'Grátis · assinatura cancelada'
    elif status == 'expirado':
        badge = 'secondary'
        label = 'Grátis · promoção encerrada'
    elif plano == PLANO_GRATIS:
        badge = 'secondary'
        label = 'Grátis'

    return {
        'label': label,
        'badge': badge,
        'plano_id': plano,
        'status': status,
        'premium': assinatura.tem_acesso_premium(),
    }


def enrich_bands_plano(bands: list[dict]) -> list[dict]:
    """Anexa ``plano_ui`` em cada banda para templates."""
    result = []
    for band in bands:
        b = dict(band)
        b['plano_ui'] = plano_badge_ui(b['id'])
        result.append(b)
    return result


def resumo_planos_usuario(owned_bands: list[dict]) -> dict[str, Any]:
    """Resumo de planos das bandas do usuário (dono) para o dashboard."""
    if not owned_bands:
        return {'tem_banda': False, 'itens': [], 'destaque': None, 'multiplas': False}
    itens = [
        {'band_name': b['name'], 'band_id': b['id'], **plano_badge_ui(b['id'])}
        for b in owned_bands
    ]
    return {
        'tem_banda': True,
        'itens': itens,
        'destaque': itens[0] if len(itens) == 1 else None,
        'multiplas': len(itens) > 1,
    }


def get_assinatura_banda(banda_id: str) -> Assinatura:
    """Retorna a assinatura da banda; cria grátis se não existir."""
    row = get_assinatura(banda_id)
    if row:
        return Assinatura(row)
    from db import create_assinatura_gratis

    row = create_assinatura_gratis(banda_id)
    return Assinatura(row)


def _plano_sem_limites_para_banda(banda: dict, assinatura: Assinatura) -> bool:
    if assinatura.tem_acesso_premium():
        return True
    return False


def check_limite(banda: dict, recurso: str) -> bool:
    """
    Verifica se a banda (ou seu dono) pode criar mais um recurso.

    Args:
        banda: dict da banda (de get_band), com pelo menos ``id`` e ``owner_id``.
        recurso: ``musica``, ``integrante``, ``setlist`` ou ``banda``.

    Returns:
        True se pode criar; False se atingiu o limite do plano grátis.
    """
    recurso = recurso.lower().strip()
    banda_id = banda['id']
    owner_id = banda['owner_id']
    assinatura = get_assinatura_banda(banda_id)

    if recurso == 'banda':
        if owner_has_worship_ativa(owner_id):
            return True
        limite = LIMITES_GRATIS['banda']
        return count_owned_bands(owner_id) < limite

    if _plano_sem_limites_para_banda(banda, assinatura):
        return True

    limite = LIMITES_GRATIS.get(recurso)
    if limite is None:
        return True

    if recurso == 'musica':
        atual = count_band_cifras(banda_id)
    elif recurso == 'integrante':
        atual = count_band_members(banda_id)
    elif recurso == 'setlist':
        atual = count_band_setlists(banda_id)
    else:
        return True

    return atual < limite


def pode_exportar_pdf(banda_id: str) -> bool:
    """Exportação PDF exige assinatura ativa (paga ou voucher)."""
    assinatura = get_assinatura_banda(banda_id)
    return assinatura.tem_acesso_premium()


def resposta_limite_plano():
    """Resposta HTTP 402 padronizada (JSON ou redirect)."""
    from flask import jsonify, redirect, flash, request

    payload = {
        'erro': 'limite_plano',
        'mensagem': 'Você atingiu o limite do plano grátis.',
        'upgrade_url': '/assinatura/planos',
    }
    if request.accept_mimetypes.best == 'application/json' or request.is_json:
        return jsonify(payload), 402
    flash(payload['mensagem'], 'warning')
    return redirect(payload['upgrade_url'])


def resposta_plano_necessario():
    """Resposta HTTP 402 para feature premium."""
    from flask import jsonify

    return jsonify({
        'erro': 'plano_necessario',
        'upgrade_url': '/assinatura/planos',
    }), 402
