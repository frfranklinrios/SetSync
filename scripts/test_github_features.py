#!/usr/bin/env python3
"""Teste automatizado das novas funcionalidades inspiradas em referências do GitHub:

1. Status de Prontidão da Música (Song Readiness) e estatísticas de setlist.
2. Endpoint API /cifras/<id>/readiness.
3. Compatibilidade e integridade da migração de banco de dados.
"""

from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Configurar ambiente de teste limpo
test_db = os.path.join(tempfile.mkdtemp(), "test_features.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
os.environ["FLASK_ENV"] = "development"
os.environ["SETSYNC_CANONICAL_URL"] = ""

from app import app as flask_app

flask_app.config["TESTING"] = True
flask_app.config["WTF_CSRF_ENABLED"] = False
import db
from models_setlist import add_cifra_to_setlist, create_setlist


def test_features():
    print("Iniciando testes de novas features do GitHub...")

    with flask_app.app_context():
        # Inicializar banco
        db.init_db()

        # Criar usuário e banda
        user_id = db.create_user(
            "musico",
            "musico@example.com",
            "senha123",
            display_name="Músico de Teste",
        )
        assert user_id, "Usuário deve ser criado"

        band = db.create_band("Banda Teste GitHub", "Descricao", user_id)
        assert band, "Banda deve ser criada"
        band_id = band["id"] if isinstance(band, dict) else band

        # 1. Testar criação de cifras com prontidão padrão
        cifra1_id = db.create_cifra(
            titulo="Música Pronta",
            artista="Banda Teste",
            tom_original="E",
            conteudo="[A]Uma [B]música [E]linda",
            band_id=band_id,
            bpm=128,
            owner_user_id=user_id,
        )
        assert cifra1_id, "Cifra 1 deve ser criada"
        c1 = db.get_cifra(cifra1_id)
        assert c1.get("readiness") == "pronta", "Readiness padrão deve ser 'pronta'"

        cifra2_id = db.create_cifra(
            titulo="Música em Ensaio",
            artista="Banda Teste",
            tom_original="C",
            conteudo="[C]Outra [G]música [Am]aqui",
            band_id=band_id,
            bpm=95,
            owner_user_id=user_id,
        )
        assert cifra2_id, "Cifra 2 deve ser criada"

        # 2. Atualizar prontidão
        db.update_cifra_readiness(cifra2_id, "ensaio")
        c2_updated = db.get_cifra(cifra2_id)
        assert c2_updated["readiness"] == "ensaio", "Status deve ter mudado para 'ensaio'"

        cifra3_id = db.create_cifra(
            titulo="Música Nova a Aprender",
            artista="Banda Teste",
            tom_original="D",
            conteudo="[D]Música [A]difícil",
            band_id=band_id,
            owner_user_id=user_id,
        )
        db.update_cifra_readiness(cifra3_id, "aprender")
        c3_updated = db.get_cifra(cifra3_id)
        assert c3_updated["readiness"] == "aprender", "Status deve ter mudado para 'aprender'"

        # 3. Criar setlist e verificar estatísticas de prontidão
        setlist_id = create_setlist(band_id, "Show de Sábado")
        add_cifra_to_setlist(setlist_id, cifra1_id, position=1)
        add_cifra_to_setlist(setlist_id, cifra2_id, position=2)
        add_cifra_to_setlist(setlist_id, cifra3_id, position=3)

        stats = db.get_setlist_readiness_stats(setlist_id)
        assert stats["total"] == 3, f"Esperado total=3, obteve {stats['total']}"
        assert stats["pronta"] == 1, f"Esperado pronta=1, obteve {stats['pronta']}"
        assert stats["ensaio"] == 1, f"Esperado ensaio=1, obteve {stats['ensaio']}"
        assert stats["aprender"] == 1, f"Esperado aprender=1, obteve {stats['aprender']}"
        assert stats["percent_ready"] == 33, f"Esperado 33%, obteve {stats['percent_ready']}"
        print("✓ Teste de banco e estatísticas de prontidão passou com sucesso!")

    # 4. Testar Endpoint Flask via test_client com sessão autenticada
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = "musico"
            sess["display_name"] = "Músico de Teste"

        # Atualizar cifra1 para 'ensaio' via API
        resp = client.post(
            f"/cifras/{cifra1_id}/readiness",
            json={"readiness": "ensaio"},
        )
        if resp.status_code != 200:
            print("STATUS:", resp.status_code, "DATA:", resp.get_data(as_text=True))
        assert resp.status_code == 200, f"Status code: {resp.status_code}"
        data = resp.get_json()
        assert data.get("ok") is True
        assert data.get("readiness") == "ensaio"

        with flask_app.app_context():
            c1_check = db.get_cifra(cifra1_id)
            assert c1_check["readiness"] == "ensaio"
        print("✓ Teste de endpoint API /cifras/<id>/readiness passou com sucesso!")

        # 5. Testar validação de input inválido
        resp_invalid = client.post(
            f"/cifras/{cifra1_id}/readiness",
            json={"readiness": "invalido"},
        )
        assert resp_invalid.status_code == 400, "Deve rejeitar readiness inválido"
        print("✓ Validação de integridade de dados passou com sucesso!")

    print("\nTODOS OS TESTES DE RECURSOS DO GITHUB PASSARAM COM SUCESSO! 🎉")


if __name__ == "__main__":
    try:
        test_features()
    except Exception as exc:
        print(f"ERRO: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
