"""Cliente HTTP para a API local api-cifras (../api-cifras)."""

from __future__ import annotations

import os
import threading
import time
from typing import Any
from urllib.parse import quote

import requests

from cifras_tool.calibracao import (
    compasso_padrao,
    extrair_acordes_referencia,
    montar_grade_da_cifra,
    resolver_tonalidade,
)
from cifras_tool.setsync_export import montar_pacote_setsync, partes_para_grade_ui


class ApiCifrasError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def api_cifras_base_url() -> str:
    return (os.getenv('API_CIFRAS_URL') or 'http://127.0.0.1:8000').rstrip('/')


def _request(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json_body: dict | None = None,
    timeout: float = 20.0,
) -> Any:
    url = f'{api_cifras_base_url()}{path}'
    try:
        response = requests.request(
            method,
            url,
            params=params,
            json=json_body,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ApiCifrasError(
            'Não foi possível conectar à API de cifras. Verifique se o serviço api-cifras está ativo.'
        ) from exc

    if response.status_code == 404:
        raise ApiCifrasError('Cifra não encontrada no cache local.', status_code=404)
    if response.status_code == 409:
        raise ApiCifrasError('Já existe um sync em andamento.', status_code=409)
    if response.status_code >= 400:
        detail = response.text[:200] if response.text else response.reason
        raise ApiCifrasError(f'API de cifras respondeu com erro ({response.status_code}): {detail}')

    if not response.content:
        return {}
    return response.json()


def search_songs(query: str, *, limit: int = 20) -> dict[str, Any]:
    q = (query or '').strip()
    if len(q) < 2:
        raise ApiCifrasError('Digite pelo menos 2 caracteres para buscar.')
    limit = max(1, min(int(limit), 50))
    return _request('GET', '/search', params={'q': q, 'limit': limit})


def get_cifra_record(artist_slug: str, song_slug: str) -> dict[str, Any]:
    artist = quote((artist_slug or '').strip(), safe='')
    song = quote((song_slug or '').strip(), safe='')
    if not artist or not song:
        raise ApiCifrasError('Artista e música são obrigatórios.')
    return _request('GET', f'/cifras/{artist}/{song}')


def get_cifra_setsync(artist_slug: str, song_slug: str) -> dict[str, Any]:
    """Pacote pronto para o formulário Uníssono (endpoint nativo da api-cifras)."""
    artist = quote((artist_slug or '').strip(), safe='')
    song = quote((song_slug or '').strip(), safe='')
    if not artist or not song:
        raise ApiCifrasError('Artista e música são obrigatórios.')
    return _request('GET', f'/cifras/{artist}/{song}/setsync')


def record_to_setsync_package(record: dict[str, Any]) -> dict[str, Any]:
    """Converte registro bruto; prefere pacote setsync pré-calculado pela API."""
    cached = record.get('setsync')
    if isinstance(cached, dict) and cached.get('cifra_json'):
        pacote = dict(cached)
        pacote.setdefault('artist_slug', record.get('artist_slug') or '')
        pacote.setdefault('song_slug', record.get('song_slug') or '')
        pacote.setdefault('url_cifra', record.get('url') or pacote.get('url_cifra') or '')
        pacote['cached'] = True
        return pacote

    if record.get('cifra_json') and record.get('conteudo'):
        return {
            'titulo': record.get('titulo'),
            'artista': record.get('artista'),
            'tom_original': record.get('tom_original') or record.get('tom'),
            'conteudo': record.get('conteudo'),
            'cifra_json': record.get('cifra_json'),
            'grade_json': record.get('grade_json'),
            'grade_partes': record.get('grade_partes'),
            'bpm': record.get('bpm'),
            'duracao_seg': record.get('duracao_seg'),
            'url_cifra': record.get('url_cifra') or record.get('url') or '',
            'url_youtube': record.get('url_youtube') or '',
            'artist_slug': record.get('artist_slug') or '',
            'song_slug': record.get('song_slug') or '',
            'cached': bool(record.get('cached', True)),
        }
    cifra = (record.get('cifra') or '').strip()
    if not cifra:
        lines = record.get('lines') or []
        cifra = '\n'.join(str(ln) for ln in lines).strip()
    if not cifra:
        raise ApiCifrasError('A cifra retornada pela API está vazia.')

    from util import sanitize_tab_html_artifacts

    cifra = sanitize_tab_html_artifacts(cifra)

    titulo = (record.get('title') or '').strip() or 'Sem título'
    artista = (record.get('artist') or '').strip() or 'Desconhecido'
    tom_site = (record.get('key') or '').strip()
    url_cifra = (record.get('url') or '').strip()

    acordes_ref = extrair_acordes_referencia(cifra)
    compasso = compasso_padrao()
    _, _, _, partes_grade = montar_grade_da_cifra(
        cifra,
        acordes_ref,
        len(acordes_ref) * max(compasso.beats_per_bar, 1),
        compasso=compasso,
    )
    tom_original, _ = resolver_tonalidade(tom_site, acordes_ref)

    pacote = montar_pacote_setsync(
        titulo=titulo,
        artista=artista,
        tom_original=tom_original,
        conteudo=cifra,
        partes_grade=partes_grade,
        url_cifra=url_cifra,
    )
    pacote['grade_partes'] = partes_para_grade_ui(partes_grade)
    pacote['artist_slug'] = record.get('artist_slug') or ''
    pacote['song_slug'] = record.get('song_slug') or ''
    pacote['cached'] = True
    return pacote


def health_check() -> dict[str, Any]:
    return _request('GET', '/health', timeout=3.0)


_stats_lock = threading.Lock()
_stats_cache: dict[str, Any] = {'ts': 0.0, 'data': {'available': False}}
_STATS_TTL_SEC = float(os.getenv('API_CIFRAS_STATS_TTL', '120') or '120')


def get_api_cifras_public_stats() -> dict[str, Any]:
    """
    Estatísticas da biblioteca local para exibir no dashboard.
    Cacheia por TTL para não chamar COUNT no SQLite a cada pageview.
    """
    now = time.monotonic()
    with _stats_lock:
        if now - float(_stats_cache['ts']) < _STATS_TTL_SEC:
            return dict(_stats_cache['data'])

    try:
        # /health é leve; disponibilidade sem COUNT.
        _request('GET', '/health', timeout=2.0)
        data = _request('GET', '/stats', timeout=12.0)
        count = data.get('songs_cached')
        if count is None:
            result = {'available': False}
        else:
            n = int(count)
            result = {
                'available': True,
                'songs_cached': n,
                'songs_cached_fmt': f'{n:,}'.replace(',', '.'),
            }
    except ApiCifrasError:
        result = {'available': False}
    except (TypeError, ValueError):
        result = {'available': False}

    with _stats_lock:
        _stats_cache['ts'] = time.monotonic()
        _stats_cache['data'] = result
    return dict(result)


def get_api_cifras_report() -> dict[str, Any]:
    """Relatório completo (biblioteca + sync + últimas execuções)."""
    return _request('GET', '/report', timeout=15.0)


def get_api_cifras_sync_status() -> dict[str, Any]:
    return _request('GET', '/sync/status', timeout=5.0)


def start_api_cifras_sync(*, mode: str = 'incremental', limit: int | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {'mode': mode or 'incremental'}
    if limit is not None:
        body['limit'] = int(limit)
    return _request('POST', '/sync', json_body=body, timeout=10.0)
