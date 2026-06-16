#!/usr/bin/env python3
"""Valida variáveis de ambiente do Google Ads (tag + conversão de inscrição)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app import app
    from google_ads import get_google_ads_config, signup_conversion_url

    cfg = get_google_ads_config()
    print('=== Google Ads / inscrições ===')
    with app.app_context():
        print(f'  URL de conversão:   {signup_conversion_url()}')
    print(f"  GOOGLE_ADS_ENABLED: {(os.getenv('GOOGLE_ADS_ENABLED') or '').strip() or '(vazio)'}")
    print(f"  ativo no app:       {cfg['enabled']}")
    print(f"  GTM:                {cfg['gtm_id'] or '(não)'}")
    print(f"  Ads ID (AW-):       {cfg['aw_id'] or '(não)'}")
    print(f"  GA4 (G-):           {cfg['ga_id'] or '(opcional)'}")
    print(f"  conversão signup:   {cfg['signup_send_to'] or '(não)'}")

    if not cfg['enabled']:
        print('\nConfigure no .env:')
        print('  GOOGLE_ADS_ENABLED=1')
        print('  GOOGLE_TAG_MANAGER_ID=GTM-XXXX   # ou GOOGLE_ADS_ID=AW-XXXX')
        print('  GOOGLE_ADS_CONVERSION_SIGNUP=LABEL  # obrigatório sem GTM')
        return 1

    if cfg['use_gtm']:
        print('\nOK — use GTM com evento personalizado "setsync_signup" na conversão.')
    elif cfg['track_signup_direct']:
        print('\nOK — tag gtag + conversão direta de inscrição.')
    else:
        print('\nAVISO: defina GOOGLE_ADS_CONVERSION_SIGNUP com o rótulo da conversão.')
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
