#!/usr/bin/env python3
"""Testes rápidos da elegibilidade AdSense (plano grátis vs premium)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monetizacao import Assinatura, PLANO_GRATIS, PLANO_PRO, STATUS_ATIVA


def _row(plano: str, status: str) -> dict:
    return {
        'id': 'a1',
        'banda_id': 'b1',
        'plano': plano,
        'status': status,
        'mp_subscription_id': None,
        'mp_preapproval_id': None,
        'data_inicio': None,
        'data_proxima_cobranca': None,
        'data_cancelamento': None,
    }


def test_premium_sem_anuncio():
    a = Assinatura(_row(PLANO_PRO, STATUS_ATIVA))
    assert a.tem_acesso_premium()


def test_gratis_com_anuncio_logic():
    a = Assinatura(_row(PLANO_GRATIS, STATUS_ATIVA))
    assert not a.tem_acesso_premium()


def test_config_disabled_without_client(monkeypatch=None):
    os.environ.pop('ADSENSE_CLIENT', None)
    os.environ['ADSENSE_ENABLED'] = '1'
    from adsense import get_adsense_config

    cfg = get_adsense_config()
    assert not cfg['enabled']


def test_normalize_client():
    from adsense import _normalize_client

    assert _normalize_client('ca-pub-1234567890123456') == 'ca-pub-1234567890123456'
    assert _normalize_client('1234567890123456') == 'ca-pub-1234567890123456'


def test_ads_txt():
    os.environ['ADSENSE_CLIENT'] = 'ca-pub-9778803349526985'
    from adsense import ads_txt_body, publisher_id

    assert publisher_id() == 'pub-9778803349526985'
    body = ads_txt_body()
    assert 'google.com, pub-9778803349526985, DIRECT' in body


if __name__ == '__main__':
    test_premium_sem_anuncio()
    test_gratis_com_anuncio_logic()
    test_config_disabled_without_client()
    test_normalize_client()
    print('ok: test_adsense_eligibility')
