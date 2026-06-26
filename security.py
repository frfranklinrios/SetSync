"""Utilitários centralizados de segurança (host, URL canônica, tokens, rate limit)."""
from __future__ import annotations

import os
import time
from collections import defaultdict
from threading import Lock
from urllib.parse import urlparse

from flask import abort, current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

_WEAK_SECRET_KEYS = frozenset({
    '',
    'dev',
    'dev-key-change-in-production',
    'dev-local-only',
    'sua-chave-secreta-aqui-mude-em-producao',
    'gere-uma-chave-longa-aleatoria-aqui',
})

_rate_lock = Lock()
_rate_buckets: dict[str, list[float]] = defaultdict(list)


def is_production_env() -> bool:
    return os.getenv('FLASK_ENV', 'development').lower() == 'production'


def assert_secret_key_usable(secret_key: str | None) -> str:
    """Recusa chave ausente ou fraca em produção."""
    sk = (secret_key or '').strip()
    if sk in _WEAK_SECRET_KEYS:
        if is_production_env():
            raise RuntimeError(
                'SECRET_KEY ausente ou padrão — defina uma chave longa e aleatória no .env'
            )
        sk = sk or 'dev-local-only'
    return sk


def get_allowed_hosts() -> set[str]:
    raw = os.getenv('SETSYNC_ALLOWED_HOSTS', '').strip()
    if raw:
        return {h.strip().lower() for h in raw.split(',') if h.strip()}
    canonical = os.getenv('SETSYNC_CANONICAL_URL', '').strip()
    if canonical:
        host = urlparse(canonical).hostname
        if host:
            return {host.lower(), 'localhost', '127.0.0.1'}
    return {'localhost', '127.0.0.1'}


_SEO_PUBLIC_PATHS = frozenset({
    '/sw.js',
    '/manifest.webmanifest',
    '/health',
    '/ads.txt',
    '/robots.txt',
    '/sitemap.xml',
    '/google47ebf77ba640d99c.html',
})


def validate_request_host():
    """Bloqueia Host header poisoning (403). Redireciona hosts legados ao canônico."""
    from flask import redirect

    if request.path in _SEO_PUBLIC_PATHS:
        return
    host = (request.host or '').split(':')[0].lower()
    if not host:
        return
    allowed = get_allowed_hosts()
    if host not in allowed:
        current_app.logger.warning('Host rejeitado: %s (permitidos: %s)', host, allowed)
        abort(403)

    base = canonical_base_url()
    if base:
        canon_host = (urlparse(base).hostname or '').lower()
        if canon_host and host != canon_host and host in allowed:
            path = request.path or '/'
            qs = (request.query_string or b'').decode('utf-8', errors='replace').strip()
            target = base.rstrip('/') + path + (f'?{qs}' if qs else '')
            return redirect(target, code=301)


def canonical_base_url() -> str | None:
    base = (os.getenv('SETSYNC_CANONICAL_URL') or '').strip().rstrip('/')
    return base or None


def build_canonical_url(path: str) -> str:
    """Monta URL absoluta usando SETSYNC_CANONICAL_URL (nunca Host da requisição)."""
    if not path.startswith('/'):
        path = '/' + path
    base = canonical_base_url()
    if base:
        return base + path
    # Fallback dev: scheme/host da requisição após validação
    scheme = 'https' if request.is_secure else 'http'
    host = request.host or '127.0.0.1:5000'
    return f'{scheme}://{host}{path}'


def external_url_for(endpoint: str, **values) -> str:
    """URL absoluta com host canônico fixo (anti Host poisoning)."""
    from flask import current_app, has_request_context, url_for

    if has_request_context():
        path = url_for(endpoint, **values)
        return build_canonical_url(path)

    base = canonical_base_url() or 'http://127.0.0.1:5000'
    with current_app.test_request_context(base_url=base.rstrip('/') + '/'):
        path = url_for(endpoint, **values)
    return build_canonical_url(path)


def cookie_domain_for_session() -> str:
    base = canonical_base_url()
    if base:
        host = urlparse(base).hostname
        if host:
            return host
    return (request.host or 'localhost').split(':')[0]


def _serializer(salt: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=salt)


def make_pdf_access_token(setlist_id: str, user_id: str) -> str:
    return _serializer('setlist-pdf').dumps(
        {'setlist_id': str(setlist_id), 'user_id': user_id},
    )


def verify_pdf_access_token(token: str, setlist_id: str) -> str | None:
    if not token:
        return None
    try:
        data = _serializer('setlist-pdf').loads(token, max_age=180)
    except (BadSignature, SignatureExpired, TypeError):
        return None
    if str(data.get('setlist_id')) != str(setlist_id):
        return None
    uid = data.get('user_id')
    return str(uid) if uid else None


def make_studio_finance_pdf_token(studio_id: str, user_id: str) -> str:
    return _serializer('studio-finance-pdf').dumps(
        {'studio_id': str(studio_id), 'user_id': user_id},
    )


def verify_studio_finance_pdf_token(token: str, studio_id: str) -> str | None:
    if not token:
        return None
    try:
        data = _serializer('studio-finance-pdf').loads(token, max_age=180)
    except (BadSignature, SignatureExpired, TypeError):
        return None
    if str(data.get('studio_id')) != str(studio_id):
        return None
    uid = data.get('user_id')
    return str(uid) if uid else None


def make_band_finance_pdf_token(band_id: str, user_id: str) -> str:
    return _serializer('band-finance-pdf').dumps(
        {'band_id': str(band_id), 'user_id': user_id},
    )


def verify_band_finance_pdf_token(token: str, band_id: str) -> str | None:
    if not token:
        return None
    try:
        data = _serializer('band-finance-pdf').loads(token, max_age=180)
    except (BadSignature, SignatureExpired, TypeError):
        return None
    if str(data.get('band_id')) != str(band_id):
        return None
    uid = data.get('user_id')
    return str(uid) if uid else None


def make_oauth_state() -> str:
    import secrets
    return secrets.token_urlsafe(32)


def verify_oauth_state(state: str | None) -> bool:
    from flask import session
    expected = session.pop('oauth_state', None)
    return bool(expected and state and expected == state)


def check_rate_limit(key: str, *, max_attempts: int = 8, window_sec: int = 300) -> bool:
    """True se permitido; False se excedeu tentativas."""
    now = time.time()
    with _rate_lock:
        bucket = _rate_buckets[key]
        _rate_buckets[key] = [t for t in bucket if now - t < window_sec]
        if len(_rate_buckets[key]) >= max_attempts:
            return False
        _rate_buckets[key].append(now)
        return True


def clear_rate_limit(key: str) -> None:
    with _rate_lock:
        _rate_buckets.pop(key, None)


def safe_redirect_path(path: str | None) -> str | None:
    """Path interno seguro para ?next= (não APIs nem JSON)."""
    if not path or not path.startswith('/') or path.startswith('//'):
        return None
    low = path.lower().split('?', 1)[0]
    if '/api/' in low or low.endswith('.json') or low.endswith('.webmanifest'):
        return None
    return path
