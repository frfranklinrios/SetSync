#!/usr/bin/env python3
"""Runner da suíte de testes (local e CI).

Roda cada scripts/test_*.py como processo isolado (cada um define seu próprio
DATABASE_URL/tempdir no import), com o repo-root no PYTHONPATH para os imports
funcionarem independentemente de ordem de import no arquivo.

Testes que dependem de serviços externos são EXCLUÍDOS explicitamente (logados),
nunca silenciosamente — rode-os à mão quando o serviço estiver disponível.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS = os.path.join(ROOT, 'scripts')

# (arquivo, motivo) — precisam de rede/credenciais/seed que o CI não tem
EXCLUDE = {
    'test_mp_sandbox.py': 'Mercado Pago sandbox (credenciais/rede)',
    'test_admin_outreach.py': 'Evolution/WhatsApp (rede)',
    'test_notification_digest.py': 'requer contexto de app/scheduler',
    'test_onboarding_urls.py': 'requer dados demo semeados',
    'run_tests.py': '(este runner)',
}


def _test_files() -> list[str]:
    return sorted(
        f for f in os.listdir(SCRIPTS)
        if f.startswith('test_') and f.endswith('.py')
    )


def main() -> int:
    env = dict(os.environ)
    env['PYTHONPATH'] = ROOT + os.pathsep + env.get('PYTHONPATH', '')
    env.setdefault('FLASK_ENV', 'development')
    env.setdefault('SECRET_KEY', 'ci-test-key')
    env.setdefault('SETSYNC_CANONICAL_URL', 'http://localhost')
    env.setdefault('SETSYNC_ALLOWED_HOSTS', 'localhost')
    env.setdefault('WTF_CSRF_ENABLED', 'false')

    files = _test_files()
    run, ok, failed, excluded = [], [], [], []
    for f in files:
        if f in EXCLUDE:
            excluded.append((f, EXCLUDE[f]))
            continue
        run.append(f)

    print(f'== Rodando {len(run)} testes (excluídos: {len(excluded)}) ==')
    for f in excluded:
        print(f'  · pulado {f[0]} — {f[1]}')

    for f in run:
        t0 = time.time()
        # cada teste usa seu próprio DATABASE_URL (tempdir) definido no import
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, f)],
            env=env, capture_output=True, text=True, cwd=ROOT,
        )
        dt = time.time() - t0
        out = proc.stdout + proc.stderr
        passed = proc.returncode == 0 and ('FAILED' not in out) and ('Traceback' not in out)
        status = 'ok ' if passed else 'FALHOU'
        print(f'  [{status}] {f} ({dt:.1f}s)')
        (ok if passed else failed).append(f)
        if not passed:
            tail = '\n'.join(out.strip().splitlines()[-12:])
            print(f'    ---\n{tail}\n    ---')

    print(f'\n== Resultado: {len(ok)} ok, {len(failed)} falhas, {len(excluded)} pulados ==')
    if failed:
        print('FALHAS: ' + ', '.join(failed))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
