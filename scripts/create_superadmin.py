#!/usr/bin/env python3
"""
Verifica usuário e mostra como configurar admin global só via .env (sem alterar o banco).

No servidor Contabo, defina no .env:
  SETSYNC_SUPERADMIN_USERNAMES=seu_usuario
  SETSYNC_SUPERADMIN_EMAILS=admin@seudominio.com
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from db import init_db, create_user, get_user_by_username, get_user_by_email, is_superadmin  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Configura administrador global apenas por variáveis de ambiente.'
    )
    parser.add_argument('--username', required=True, help='Nome de usuário')
    parser.add_argument('--email', help='E-mail (obrigatório ao criar conta nova)')
    parser.add_argument('--password', help='Senha (obrigatória ao criar conta nova)')
    parser.add_argument('--display-name', default='', help='Nome de exibição')
    args = parser.parse_args()

    init_db()

    user = get_user_by_username(args.username)
    if not user and args.email:
        user = get_user_by_email(args.email.strip())

    if not user:
        if not args.email or not args.password:
            print('Usuário não existe. Informe --email e --password para criar a conta.', file=sys.stderr)
            return 1
        user_id = create_user(
            args.username.strip(),
            args.email.strip(),
            args.password,
            display_name=args.display_name.strip() or None,
        )
        if not user_id:
            print('Erro: usuário ou e-mail já cadastrado.', file=sys.stderr)
            return 1
        user = get_user_by_username(args.username)

    print()
    print('Adicione ao arquivo .env no servidor (Contabo) — não altera o banco SQLite:')
    print()
    print(f'SETSYNC_SUPERADMIN_USERNAMES={user["username"]}')
    if user.get('email'):
        print(f'SETSYNC_SUPERADMIN_EMAILS={user["email"]}')
    print()
    print('Reinicie o app após salvar o .env.')
    print()
    print('Para testar localmente agora, exporte as mesmas variáveis no shell ou cole no .env local.')
    print(f'  Usuário: {user["username"]}  |  E-mail: {user.get("email") or "—"}')
    if is_superadmin(user['id']):
        print('  (já reconhecido como admin — variáveis já estão no ambiente)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
