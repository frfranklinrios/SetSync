#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')
from db import init_db, get_db
from monetizacao import get_assinatura_banda, periodo_assinatura_ui, plano_badge_ui, _agora_utc

init_db()
c = get_db().cursor()
c.execute(
    """
  SELECT b.id, b.name, a.plano, a.status, a.data_inicio, a.data_proxima_cobranca,
         a.data_cancelamento
  FROM bands b
  LEFT JOIN assinaturas a ON a.banda_id = b.id
  WHERE LOWER(b.name) LIKE %s
  ORDER BY b.name
""",
    ('%teste%',),
)
rows = [dict(r) for r in c.fetchall()]
print('count', len(rows))
print('agora', _agora_utc())
for r in rows:
    print('BAND', r)
    if not r.get('id'):
        continue
    a = get_assinatura_banda(r['id'])
    p = periodo_assinatura_ui(a)
    ui = plano_badge_ui(r['id'])
    print('  periodo', p)
    print('  ui curto', ui['label_curto'], 'urg', ui['periodo'].get('urgencia'),
          'rest', ui['periodo'].get('texto_restante'), 'det', ui['periodo'].get('texto_detalhe'))

c.execute("""
  SELECT b.name, a.banda_id, a.plano, a.status, a.data_proxima_cobranca
  FROM assinaturas a JOIN bands b ON b.id=a.banda_id
  WHERE a.status='ativa' AND a.plano IN ('pro','worship','individual')
    AND a.data_proxima_cobranca IS NOT NULL
    AND a.data_proxima_cobranca < NOW()
  LIMIT 15
""")
print('overdue actives', [dict(r) for r in c.fetchall()])
