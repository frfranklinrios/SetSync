#!/usr/bin/env python3
"""Testes automatizados da repaginação UX/UI (Cockpit, Paleta Ctrl+K, Filtros e Estúdio)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

test_db = os.path.join(tempfile.mkdtemp(), "test_ux_revamp.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-ux-revamp-key-min-32-chars!!"
os.environ["SETSYNC_CANONICAL_URL"] = ""
os.environ["WTF_CSRF_ENABLED"] = "false"

from datetime import timedelta  # noqa: E402

import db  # noqa: E402
from app import app as flask_app  # noqa: E402
from config import app_now_naive  # noqa: E402
from models_agenda import create_band_event  # noqa: E402
from models_setlist import add_cifra_to_setlist, create_setlist  # noqa: E402


class UxRevampTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        flask_app.config["TESTING"] = True
        flask_app.config["WTF_CSRF_ENABLED"] = False
        with flask_app.app_context():
            db.init_db()
            cls.user_id = db.create_user(
                "ux_musico",
                "ux_musico@example.com",
                "senha12345",
                display_name="Músico UX",
            )
            cls.band_id = db.create_band("Banda Aurora", "Pop Rock", cls.user_id)
            cls.cifra1_id = db.create_cifra(
                titulo="Águas de Março",
                artista="Tom Jobim",
                tom_original="B",
                conteudo="[B]É pau, é [E]pedra, é o [F#7]fim do ca[B]minho",
                band_id=cls.band_id,
                bpm=112,
                duracao_seg=210,
                owner_user_id=cls.user_id,
            )
            cls.cifra2_id = db.create_cifra(
                titulo="Tempo Perdido",
                artista="Legião Urbana",
                tom_original="G",
                conteudo="[C]Todos os [Am]dias quando a[Bm]cordo [Em]cedo",
                band_id=cls.band_id,
                bpm=124,
                owner_user_id=cls.user_id,
            )
            db.update_cifra_readiness(cls.cifra2_id, "ensaio")
            cls.personal_id = db.create_personal_cifra(
                cls.user_id,
                "Evidências",
                "Chitãozinho e Xororó",
                "E",
                "[E]Quando eu digo que deixei de te [B7]amar",
            )
            cls.setlist_id = create_setlist(cls.band_id, "Show Sábado")
            add_cifra_to_setlist(cls.setlist_id, cls.cifra1_id, position=1)
            add_cifra_to_setlist(cls.setlist_id, cls.cifra2_id, position=2)
            starts_at = (app_now_naive() + timedelta(days=5)).strftime("%Y-%m-%d 20:00:00")
            cls.event_id = create_band_event(
                cls.band_id,
                title="Ensaio Geral",
                event_type="ensaio",
                starts_at=starts_at,
                created_by=cls.user_id,
                location="Estúdio Central",
                setlist_id=cls.setlist_id,
            )

    def _auth_client(self):
        client = flask_app.test_client()
        with client.session_transaction() as sess:
            sess["user_id"] = self.user_id
            sess["username"] = "ux_musico"
            sess["display_name"] = "Músico UX"
            sess["skip_comecar"] = True
        return client

    def test_quick_nav_requires_login(self):
        client = flask_app.test_client()
        resp = client.get("/cifras/api/quick-nav", follow_redirects=False)
        self.assertIn(resp.status_code, (302, 303, 401))

    def test_quick_nav_returns_expected_payload(self):
        client = self._auth_client()
        resp = client.get("/cifras/api/quick-nav")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["ok"])
        self.assertTrue(any(b["name"] == "Banda Aurora" for b in data["bands"]))
        self.assertTrue(any(s["name"] == "Show Sábado" for s in data["setlists"]))
        titulos = {c["titulo"] for c in data["cifras"]}
        self.assertIn("Águas de Março", titulos)
        self.assertIn("Evidências", titulos)
        self.assertTrue(any(e["title"] == "Ensaio Geral" for e in data["events"]))
        self.assertTrue(any(a["id"] == "play_mode" for a in data["actions"]))

    def test_command_palette_js_with_node(self):
        node_script = """
        const assert = require('assert');
        const Palette = require('./static/js/global-command-palette.js');

        const items = Palette.buildFlatItems({
            bands: [{ id: 'b1', name: 'Banda Aurora', role: 'admin', cifras_count: 2, url: '/bands/b1', play_url: '/cifras/band/b1/tocar' }],
            setlists: [{ id: 's1', name: 'Show Sábado', band_name: 'Banda Aurora', url: '/setlists/s1', play_url: '/setlists/s1/tocar' }],
            cifras: [
                { id: 'c1', titulo: 'Águas de Março', artista: 'Tom Jobim', tom: 'B', readiness: 'pronta', scope: 'Banda Aurora', url: '/cifras/c1', play_url: '/cifras/band/b1/tocar?start=c1' },
                { id: 'c2', titulo: 'Tempo Perdido', artista: 'Legião Urbana', tom: 'G', readiness: 'ensaio', scope: 'Banda Aurora', url: '/cifras/c2', play_url: '/cifras/band/b1/tocar?start=c2' }
            ],
            events: [{ id: 'e1', title: 'Ensaio Geral', band_name: 'Banda Aurora', starts_at: '20/12/2026 às 20:00', event_type: 'ensaio', url: '/agenda/e1' }],
            actions: [{ id: 'play_mode', label: 'Modo Tocar (Palco)', subtitle: 'Abrir palco', icon: 'fa-play', url: '/cifras/band/b1/tocar' }]
        });

        assert.strictEqual(items.length, 6);

        // Busca sem acento ("aguas" -> "Águas de Março")
        const resAcc = Palette.filterPaletteItems(items, 'aguas', 'all');
        assert.strictEqual(resAcc.length, 1);
        assert.strictEqual(resAcc[0].title, 'Águas de Março');

        // Busca por tom ("tom:G" -> "Tempo Perdido")
        const resTom = Palette.filterPaletteItems(items, 'tom:G', 'cifras');
        assert.strictEqual(resTom.length, 1);
        assert.strictEqual(resTom[0].title, 'Tempo Perdido');

        // Filtro por aba setlists
        const resSl = Palette.filterPaletteItems(items, '', 'setlists');
        assert.strictEqual(resSl.length, 1);
        assert.strictEqual(resSl[0].title, 'Show Sábado');

        console.log('node palette ok');
        """
        res = subprocess.run(
            ["node", "-e", node_script],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, res.stderr)

    def test_navbar_and_dashboard_cockpit(self):
        client = self._auth_client()
        resp = client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("global-cmd-trigger", html)
        self.assertIn("global-command-palette.js", html)
        self.assertIn("ux-revamp.css", html)
        self.assertIn("/agenda/minha", html)
        self.assertIn("Modo Tocar", html)
        self.assertIn("dash-summary", html)
        self.assertIn("dash-hub", html)

    def test_band_hub_filter_and_readiness(self):
        client = self._auth_client()
        resp = client.get(f"/bands/{self.band_id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("band-repertoire-toolbar", html)
        self.assertIn("band-cifra-filter", html)
        self.assertIn("band-cifra-sort", html)
        self.assertIn("data-readiness-summary", html)
        self.assertIn("row-readiness-sel", html)
        self.assertIn("repertoire-filter.js", html)

    def test_cifra_view_study_studio(self):
        client = self._auth_client()
        resp = client.get(f"/cifras/{self.cifra1_id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("cifra-study-toolbar", html)
        self.assertIn("view-pitch-pipe-btn", html)
        self.assertIn("view-font-down", html)
        self.assertIn("view-font-up", html)
        self.assertIn("view-cols-toggle", html)
        self.assertIn("view-autoscroll-toggle", html)
        self.assertIn("cifra-unique-chords-bar", html)
        self.assertIn("cifra-study-tools.js", html)

    def test_setlist_duration_and_readiness_filter(self):
        client = self._auth_client()
        resp = client.get(f"/setlists/{self.setlist_id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("setlist-duration-badge", html)
        self.assertIn("min de show", html)
        self.assertIn("setlist-readiness-chips", html)


if __name__ == "__main__":
    unittest.main()
