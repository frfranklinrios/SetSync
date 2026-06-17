#!/usr/bin/env python3
"""Gera par de chaves VAPID para Web Push (cole no .env)."""

import base64

from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid

v = Vapid()
v.generate_keys()

raw = v.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint,
)
public_key = base64.urlsafe_b64encode(raw).decode().rstrip('=')
private_key = v.private_pem().decode()

print('# Cole no .env do SetSync:')
print(f'VAPID_PUBLIC_KEY={public_key}')
print('VAPID_PRIVATE_KEY=' + private_key.replace('\n', '\\n'))
print('VAPID_SUBJECT=mailto:contato@setsync.com.br')
