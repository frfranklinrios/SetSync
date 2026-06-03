"""Google AdSense — exibição apenas para plano grátis (sem premium na banda/contexto)."""

from __future__ import annotations

import os
import re
from typing import Any

from flask import Request, has_request_context, request

_CA_PUB_RE = re.compile(r'^ca-pub-\d+$', re.I)


def _env_flag(name: str, default: bool = False) -> bool:
    v = (os.getenv(name) or '').strip().lower()
    if v in ('1', 'true', 'yes', 'on'):
        return True
    if v in ('0', 'false', 'no', 'off'):
        return False
    return default


def _normalize_client(raw: str) -> str:
    s = (raw or '').strip()
    if not s:
        return ''
    if s.lower().startswith('ca-pub-'):
        return s if _CA_PUB_RE.match(s) else ''
    digits = re.sub(r'\D', '', s)
    return f'ca-pub-{digits}' if digits else ''


def get_adsense_config() -> dict[str, Any]:
    """Configuração lida do ambiente (sem segredos além do client id público)."""
    client = _normalize_client(os.getenv('ADSENSE_CLIENT', ''))
    enabled_env = _env_flag('ADSENSE_ENABLED', default=bool(client))
    enabled = enabled_env and bool(client)
    return {
        'enabled': enabled,
        'client': client,
        'slots': {
            'footer': (os.getenv('ADSENSE_SLOT_FOOTER') or '').strip(),
            'content': (os.getenv('ADSENSE_SLOT_CONTENT') or '').strip(),
        },
    }


def adsense_ativo() -> bool:
    return get_adsense_config()['enabled']


def publisher_id(client: str | None = None) -> str:
    """ID numérico para ads.txt (ca-pub-123 → pub-123)."""
    c = _normalize_client(client or os.getenv('ADSENSE_CLIENT', ''))
    if c.lower().startswith('ca-pub-'):
        return 'pub-' + c[7:]
    return ''


def ads_txt_path() -> str:
    """Caminho do arquivo ads.txt na raiz do app (deploy)."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ads.txt')


def ads_txt_body() -> str:
    """
    Conteúdo de /ads.txt exigido pelo AdSense.
    Usa ads.txt do repositório se existir; senão gera a partir de ADSENSE_CLIENT.
    """
    path = ads_txt_path()
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            text = f.read().strip()
        if text:
            return text + '\n'
    pub = publisher_id()
    if not pub:
        return ''
    lines = [f'google.com, {pub}, DIRECT, f08c47fec0942fa0']
    extra = (os.getenv('ADSENSE_ADS_TXT_EXTRA') or '').strip()
    if extra:
        lines.extend(ln.strip() for ln in extra.splitlines() if ln.strip())
    return '\n'.join(lines) + '\n'


_ENDPOINTS_SEM_ANUNCIOS = frozenset({
    'auth.login',
    'auth.register',
    'auth.logout',
    'health',
})


def pagina_permite_anuncios(req: Request | None = None) -> bool:
    """Telas onde anúncios atrapalham (login, admin, modo tocar)."""
    if not has_request_context():
        return True
    req = req or request
    ep = req.endpoint or ''
    if ep in _ENDPOINTS_SEM_ANUNCIOS:
        return False
    if ep.startswith('admin.'):
        return False
    if ep.endswith('.tocar') or 'play_mode' in ep:
        return False
    if '/imprimir' in (req.path or '') or req.path.endswith('/exportar-pdf'):
        return False
    return True


def _band_id_from_view_args(view_args: dict[str, Any] | None) -> str | None:
    if not view_args:
        return None
    bid = view_args.get('band_id')
    if bid:
        return str(bid)
    cifra_id = view_args.get('cifra_id')
    if cifra_id:
        from db import get_cifra

        cifra = get_cifra(cifra_id)
        if cifra and cifra.get('band_id'):
            return str(cifra['band_id'])
    setlist_id = view_args.get('setlist_id')
    if setlist_id:
        from models_setlist import get_setlist

        sl = get_setlist(setlist_id)
        if sl and sl.get('band_id'):
            return str(sl['band_id'])
    return None


def resolve_band_id_context(view_args: dict[str, Any] | None = None) -> str | None:
    if has_request_context():
        view_args = view_args if view_args is not None else request.view_args
    return _band_id_from_view_args(view_args)


def usuario_deve_ver_anuncios(
    user_id: str | None = None,
    band_id: str | None = None,
    *,
    cfg: dict[str, Any] | None = None,
) -> bool:
    """
    True se a página pode exibir AdSense:
    - conta/banda no plano grátis (sem Pro/Worship/voucher ativo na banda em foco);
    - dono com Worship ativa ou qualquer banda própria premium → sem anúncios.
    """
    cfg = cfg or get_adsense_config()
    if not cfg['enabled']:
        return False
    if not pagina_permite_anuncios():
        return False

    from monetizacao import get_assinatura_banda

    if user_id:
        from db import is_superadmin, owner_has_worship_ativa

        if is_superadmin(user_id):
            return False
        if owner_has_worship_ativa(user_id):
            return False

    if band_id:
        return not get_assinatura_banda(band_id).tem_acesso_premium()

    if user_id:
        from db import get_owned_bands, get_user_bands

        owned = get_owned_bands(user_id)
        if owned:
            return all(
                not get_assinatura_banda(b['id']).tem_acesso_premium()
                for b in owned
            )
        bands = get_user_bands(user_id)
        if bands:
            return any(
                not get_assinatura_banda(b['id']).tem_acesso_premium()
                for b in bands
            )
        return True

    return True


def adsense_exibir_na_requisicao(
    user_id: str | None = None,
    view_args: dict[str, Any] | None = None,
) -> bool:
    """Combina config, rota e contexto de banda da URL."""
    cfg = get_adsense_config()
    if not cfg['enabled']:
        return False
    band_id = resolve_band_id_context(view_args)
    return usuario_deve_ver_anuncios(user_id, band_id, cfg=cfg)
