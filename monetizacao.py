"""Planos, assinaturas e verificação de limites do modelo freemium."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from db import (
    count_band_cifras,
    count_band_members,
    count_band_setlists,
    count_owned_bands,
    get_assinatura,
    owner_has_individual_ativa,
    owner_has_worship_ativa,
)

PLANO_GRATIS = 'gratis'
PLANO_INDIVIDUAL = 'individual'
PLANO_PRO = 'pro'
PLANO_WORSHIP = 'worship'

PLANOS_PAGOS = (PLANO_INDIVIDUAL, PLANO_PRO, PLANO_WORSHIP)
PRECO_INDIVIDUAL_ANUAL = 149.0
PRECO_PRO_ANUAL = 249.0
PRECO_WORSHIP_ANUAL = 599.0

LIMITES_INDIVIDUAL = {
    'integrante': 1,
    'banda': 1,
}
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
    PLANO_INDIVIDUAL: Plano(
        id=PLANO_INDIVIDUAL,
        nome='Individual',
        preco_mensal=15.0,
        limites=dict(LIMITES_INDIVIDUAL),
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
    preco_anual_label: str = ''
    sufixo_anual: str = '/ano'
    economia_anual: str = ''
    preco_mensal_equivalente_label: str = ''
    cobrado_anual_label: str = ''
    desconto_anual_pct: int = 0


def _preco_label(valor: float | None) -> str:
    if valor is None or valor <= 0:
        return 'R$ 0'
    if valor == int(valor):
        return f'R$ {int(valor)}'
    return f'R$ {valor:.2f}'.replace('.', ',')


def _desconto_anual_pct(preco_mensal: float, preco_anual: float) -> int:
    total_mensal = preco_mensal * 12
    if total_mensal <= 0:
        return 0
    return round((1 - preco_anual / total_mensal) * 100)


def _preco_mensal_equivalente_label(preco_anual: float) -> str:
    equiv = preco_anual / 12
    if equiv == int(equiv):
        return f'R$ {int(equiv)}/mês'
    return f'R$ {equiv:.2f}'.replace('.', ',') + '/mês'


def _cobrado_anual_label(preco_anual: float) -> str:
    return f'cobrado anualmente — {_preco_label(preco_anual)}/ano'


def _economia_anual_label(preco_mensal: float, preco_anual: float) -> str:
    economia = preco_mensal * 12 - preco_anual
    if economia <= 0:
        return ''
    return f'Economize {_preco_label(economia)}/ano'


def planos_para_site() -> list[PlanoSite]:
    """Lista de planos com preços e limites para templates públicos."""
    lim = LIMITES_GRATIS
    individual = PLANOS[PLANO_INDIVIDUAL]
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
            id=PLANO_INDIVIDUAL,
            nome=individual.nome,
            preco_label=_preco_label(individual.preco_mensal),
            sufixo='/mês',
            destaque=False,
            features=(
                'Para quem toca sozinho',
                '1 banda · só você no elenco',
                'Músicas e setlists ilimitados',
                'Exportar setlist em PDF',
            ),
            cta='Começar solo',
            cta_outline=True,
            preco_anual_label=_preco_label(PRECO_INDIVIDUAL_ANUAL),
            economia_anual=_economia_anual_label(individual.preco_mensal, PRECO_INDIVIDUAL_ANUAL),
            preco_mensal_equivalente_label=_preco_mensal_equivalente_label(PRECO_INDIVIDUAL_ANUAL),
            cobrado_anual_label=_cobrado_anual_label(PRECO_INDIVIDUAL_ANUAL),
            desconto_anual_pct=_desconto_anual_pct(individual.preco_mensal, PRECO_INDIVIDUAL_ANUAL),
        ),
        PlanoSite(
            id=PLANO_PRO,
            nome=pro.nome,
            preco_label=_preco_label(pro.preco_mensal),
            sufixo='/banda/mês',
            destaque=True,
            features=(
                'Banda com vários integrantes',
                'Músicas, setlists e membros ilimitados',
                'Exportar setlist em PDF',
            ),
            cta='Criar conta',
            cta_outline=False,
            preco_anual_label=_preco_label(PRECO_PRO_ANUAL),
            economia_anual=_economia_anual_label(pro.preco_mensal, PRECO_PRO_ANUAL),
            preco_mensal_equivalente_label=_preco_mensal_equivalente_label(PRECO_PRO_ANUAL),
            cobrado_anual_label=_cobrado_anual_label(PRECO_PRO_ANUAL),
            desconto_anual_pct=_desconto_anual_pct(pro.preco_mensal, PRECO_PRO_ANUAL),
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
            preco_anual_label=_preco_label(PRECO_WORSHIP_ANUAL),
            economia_anual=_economia_anual_label(worship.preco_mensal, PRECO_WORSHIP_ANUAL),
            preco_mensal_equivalente_label=_preco_mensal_equivalente_label(PRECO_WORSHIP_ANUAL),
            cobrado_anual_label=_cobrado_anual_label(PRECO_WORSHIP_ANUAL),
            desconto_anual_pct=_desconto_anual_pct(worship.preco_mensal, PRECO_WORSHIP_ANUAL),
        ),
    ]


def plano_worship_para_site() -> PlanoSite | None:
    """Plano Worship formatado para landings de igrejas."""
    for plano in planos_para_site():
        if plano.id == PLANO_WORSHIP:
            return plano
    return None


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

    @property
    def trial_inicio(self) -> datetime | None:
        return _parse_dt(self._row.get('trial_inicio'))

    @property
    def trial_fim(self) -> datetime | None:
        return _parse_dt(self._row.get('trial_fim'))

    @property
    def trial_usado(self) -> bool:
        return bool(self._row.get('trial_usado'))

    def trial_ativo(self) -> bool:
        if not self.trial_usado or not self.trial_fim:
            return False
        return _agora_utc() < self.trial_fim

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
        """Pro/Worship com assinatura ativa (paga ou voucher futuro) ou trial Pro."""
        if self.trial_ativo():
            return True
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


def _agora_utc() -> datetime:
    return datetime.utcnow()


def _dias_calendario(de: datetime, ate: datetime) -> int:
    """Diferença em dias de calendário (fim − início)."""
    return (ate.date() - de.date()).days


def _texto_dias_restantes(dias: int, fim: datetime | None) -> str:
    fim_txt = _formatar_data_curta(fim)
    if dias > 30:
        return f'Restam {dias} dias (até {fim_txt})'
    if dias > 1:
        return f'Restam {dias} dias'
    if dias == 1:
        return f'Vence amanhã ({fim_txt})'
    if dias == 0:
        return f'Vence hoje ({fim_txt})'
    if dias == -1:
        return f'Venceu ontem ({fim_txt})'
    return f'Venceu há {abs(dias)} dias ({fim_txt})'


def _urgencia_periodo(dias_restantes: int, status: str) -> str:
    if status == 'expirado' or dias_restantes < 0:
        return 'expirado'
    if dias_restantes <= 3:
        return 'critico'
    if dias_restantes <= 14:
        return 'atencao'
    return 'ok'


def sincronizar_voucher_vencido(assinatura: Assinatura) -> Assinatura:
    """Rebaixa voucher expirado na leitura (não depende só do cron diário)."""
    if assinatura.status != 'voucher':
        return assinatura
    expira = assinatura.data_proxima_cobranca
    if expira and expira.year >= 2090:
        return assinatura
    if not expira or expira > _agora_utc():
        return assinatura
    from db import get_assinatura, update_assinatura

    agora = _agora_utc().strftime('%Y-%m-%d %H:%M:%S')
    update_assinatura(
        assinatura.banda_id,
        plano=PLANO_GRATIS,
        status='expirado',
        data_cancelamento=agora,
    )
    row = get_assinatura(assinatura.banda_id)
    return Assinatura(row) if row else assinatura


def periodo_assinatura_ui(assinatura: Assinatura) -> dict[str, Any]:
    """Metadados de período (promo, assinatura paga) para templates."""
    vazio: dict[str, Any] = {
        'tem_periodo': False,
        'tipo': None,
        'inicio': None,
        'fim': None,
        'dias_restantes': None,
        'dias_totais': None,
        'progresso_pct': None,
        'urgencia': 'ok',
        'texto_restante': '',
        'texto_detalhe': '',
    }
    status = assinatura.status
    agora = _agora_utc()

    if status == 'voucher':
        inicio = assinatura.data_inicio
        fim = assinatura.data_proxima_cobranca
        if not fim:
            return vazio
        if fim.year >= 2090:
            nome = PLANOS.get(assinatura.plano, PLANOS[PLANO_GRATIS]).nome
            return {
                'tem_periodo': True,
                'tipo': 'voucher_vitalicio',
                'inicio': _formatar_data_curta(inicio),
                'fim': None,
                'dias_restantes': None,
                'dias_totais': None,
                'progresso_pct': None,
                'urgencia': 'ok',
                'texto_restante': 'Acesso vitalício',
                'texto_dia': None,
                'texto_detalhe': f'Plano {nome} — sem data de vencimento',
            }
        if not inicio:
            inicio = fim - timedelta(days=max(_dias_calendario(agora, fim), 1))
        dias_totais = max(1, _dias_calendario(inicio, fim))
        dias_restantes = _dias_calendario(agora, fim)
        dias_decorridos = min(dias_totais, max(1, _dias_calendario(inicio, agora) + 1))
        progresso = min(100, max(1 if dias_decorridos > 0 else 0, round(100 * dias_decorridos / dias_totais)))
        urgencia = _urgencia_periodo(dias_restantes, status)
        nome = PLANOS.get(assinatura.plano, PLANOS[PLANO_GRATIS]).nome
        return {
            'tem_periodo': True,
            'tipo': 'voucher',
            'inicio': _formatar_data_curta(inicio),
            'fim': _formatar_data_curta(fim),
            'dias_restantes': dias_restantes,
            'dias_totais': dias_totais,
            'dias_decorridos': dias_decorridos,
            'progresso_pct': progresso,
            'urgencia': urgencia,
            'texto_restante': _texto_dias_restantes(dias_restantes, fim),
            'texto_dia': f'Dia {dias_decorridos} de {dias_totais}',
            'texto_detalhe': (
                f'Período promocional {nome} · {_formatar_data_curta(inicio)} — {_formatar_data_curta(fim)}'
            ),
        }

    if assinatura.plano in PLANOS_PAGOS and status == STATUS_ATIVA:
        proxima = assinatura.data_proxima_cobranca
        if not proxima:
            return vazio
        dias_restantes = _dias_calendario(agora, proxima)
        nome = PLANOS.get(assinatura.plano, PLANOS[PLANO_PRO]).nome
        return {
            'tem_periodo': True,
            'tipo': 'assinatura',
            'inicio': _formatar_data_curta(assinatura.data_inicio),
            'fim': _formatar_data_curta(proxima),
            'dias_restantes': dias_restantes,
            'dias_totais': None,
            'progresso_pct': None,
            'urgencia': _urgencia_periodo(dias_restantes, status),
            'texto_restante': (
                f'Próxima cobrança em {_formatar_data_curta(proxima)}'
                if dias_restantes > 7
                else _texto_dias_restantes(dias_restantes, proxima).replace('Vence', 'Renova')
            ),
            'texto_detalhe': f'Assinatura {nome} ativa',
        }

    if status == 'expirado':
        fim = assinatura.data_proxima_cobranca or assinatura.data_cancelamento
        dias_restantes = _dias_calendario(agora, fim) if fim else -1
        return {
            'tem_periodo': True,
            'tipo': 'expirado',
            'inicio': _formatar_data_curta(assinatura.data_inicio),
            'fim': _formatar_data_curta(fim),
            'dias_restantes': dias_restantes,
            'dias_totais': None,
            'progresso_pct': 100,
            'urgencia': 'expirado',
            'texto_restante': _texto_dias_restantes(dias_restantes, fim),
            'texto_detalhe': 'Período promocional encerrado — assine para continuar no Pro',
        }

    return vazio


def plano_badge_ui(banda_id: str) -> dict[str, Any]:
    """
    Dados para exibir o plano da banda na UI (badge Bootstrap + texto).
    """
    assinatura = get_assinatura_banda(banda_id)
    plano = assinatura.plano
    status = assinatura.status
    nome = PLANOS.get(plano, PLANOS[PLANO_GRATIS]).nome
    periodo = periodo_assinatura_ui(assinatura)
    badge = 'secondary'
    label = nome
    label_curto = nome

    if status == 'voucher':
        badge = {'ok': 'success', 'atencao': 'warning', 'critico': 'danger'}.get(
            periodo.get('urgencia'), 'success',
        )
        if periodo.get('tipo') == 'voucher_vitalicio':
            label_curto = f'{nome} · vitalício'
        else:
            label_curto = f'{nome} · promocional'
        label = label_curto
        if periodo.get('texto_restante'):
            label = f'{label_curto} · {periodo["texto_restante"]}'
    elif plano == PLANO_INDIVIDUAL and status == STATUS_ATIVA:
        badge = 'primary'
        label_curto = 'Individual'
        label = 'Individual · solo'
        if periodo.get('texto_restante'):
            label = f'Individual · {periodo["texto_restante"]}'
    elif plano == PLANO_PRO and status == STATUS_ATIVA:
        badge = 'primary'
        label_curto = 'Pro'
        label = 'Pro'
        if periodo.get('texto_restante'):
            label = f'Pro · {periodo["texto_restante"]}'
    elif plano == PLANO_WORSHIP and status == STATUS_ATIVA:
        badge = 'info'
        label_curto = 'Worship'
        label = 'Worship'
        if periodo.get('texto_restante'):
            label = f'Worship · {periodo["texto_restante"]}'
    elif status == STATUS_INADIMPLENTE:
        badge = 'warning'
        label = f'{nome} · pagamento pendente'
        label_curto = label
    elif status == STATUS_CANCELADA:
        badge = 'secondary'
        label = 'Grátis · assinatura cancelada'
        label_curto = 'Grátis'
    elif status == 'expirado':
        badge = 'secondary'
        label_curto = 'Grátis · promo encerrada'
        label = periodo.get('texto_restante') or label_curto
    elif plano == PLANO_GRATIS:
        badge = 'secondary'
        label = 'Grátis'
        label_curto = 'Grátis'

    if assinatura.trial_ativo():
        dias = dias_restantes_trial(banda_id)
        badge = 'success'
        label_curto = f'Trial Pro · {dias} dias' if dias is not None else 'Trial Pro'
        label = label_curto
        periodo = {
            'tem_periodo': True,
            'tipo': 'trial',
            'texto_restante': f'{dias} dias restantes' if dias is not None else 'Trial ativo',
            'urgencia': 'ok' if (dias or 0) > 3 else 'atencao',
        }

    return {
        'label': label,
        'label_curto': label_curto,
        'badge': badge,
        'plano_id': plano,
        'status': status,
        'premium': assinatura.tem_acesso_premium(),
        'periodo': periodo,
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
        assinatura = Assinatura(row)
        return sincronizar_voucher_vencido(assinatura)
    from db import create_assinatura_gratis

    row = create_assinatura_gratis(banda_id)
    return Assinatura(row)


def _plano_sem_limites_para_banda(banda: dict, assinatura: Assinatura) -> bool:
    if assinatura.trial_ativo():
        return True
    if not assinatura.tem_acesso_premium():
        return False
    return assinatura.plano != PLANO_INDIVIDUAL


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
        if owner_has_individual_ativa(owner_id):
            return count_owned_bands(owner_id) < LIMITES_INDIVIDUAL['banda']
        return count_owned_bands(owner_id) < LIMITES_GRATIS['banda']

    if _plano_sem_limites_para_banda(banda, assinatura):
        return True

    if assinatura.tem_acesso_premium() and assinatura.plano == PLANO_INDIVIDUAL:
        if recurso == 'integrante':
            return count_band_members(banda_id) < LIMITES_INDIVIDUAL['integrante']
        if recurso in ('musica', 'setlist'):
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


def get_plano_efetivo(banda_id: str) -> str:
    """Plano real considerando trial Pro ativo."""
    assinatura = get_assinatura_banda(banda_id)
    if assinatura.trial_ativo():
        return PLANO_PRO
    if assinatura.tem_acesso_premium() and assinatura.plano in PLANOS_PAGOS:
        return assinatura.plano
    return assinatura.plano if assinatura.plano else PLANO_GRATIS


def iniciar_trial_banda(banda_id: str) -> bool:
    """Inicia trial Pro de 14 dias na primeira banda elegível."""
    from db import get_assinatura, update_assinatura_trial

    row = get_assinatura(banda_id)
    if not row or row.get('trial_usado'):
        return False
    agora = _agora_utc()
    fim = agora + timedelta(days=14)
    fmt = '%Y-%m-%d %H:%M:%S'
    update_assinatura_trial(
        banda_id,
        trial_inicio=agora.strftime(fmt),
        trial_fim=fim.strftime(fmt),
        trial_usado=1,
    )
    return True


def dias_restantes_trial(banda_id: str) -> int | None:
    assinatura = get_assinatura_banda(banda_id)
    if not assinatura.trial_ativo() or not assinatura.trial_fim:
        return None
    return max(0, _dias_calendario(_agora_utc(), assinatura.trial_fim))


def resposta_limite_plano(recurso: str = 'recursos', limite: int | None = None):
    """Resposta HTTP 402 padronizada (JSON ou redirect)."""
    from flask import jsonify, redirect, flash, request

    limite_val = limite if limite is not None else LIMITES_GRATIS.get(recurso.rstrip('s'), 0)
    payload = {
        'status': 'limite_atingido',
        'erro': 'limite_plano',
        'recurso': recurso,
        'limite': limite_val,
        'plano_atual': 'Grátis',
        'mensagem': f'Você atingiu o limite do plano Grátis ({limite_val} {recurso}).',
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
