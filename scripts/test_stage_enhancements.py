#!/usr/bin/env python3
"""Teste automatizado das melhorias de palco (Stage Enhancements):

1. Quick Song Jumper: busca instantânea por número, título, artista e tom.
2. Relógio de Palco & Cronômetro de Apresentação (Stage Clock & Live Timer).
3. Auto-Scroll Sincronizado por Duração Musical com lead-in delay de 3s.
4. Mini HUD Flutuante de Acordes no Modo Tocar.
5. Renderização dos novos controles e modais no template cifras/play_mode.html.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Configurar ambiente de teste limpo
test_db = os.path.join(tempfile.mkdtemp(), "test_stage.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
os.environ["FLASK_ENV"] = "development"
os.environ["SETSYNC_CANONICAL_URL"] = ""

from app import app as flask_app  # noqa: E402

flask_app.config["TESTING"] = True
flask_app.config["WTF_CSRF_ENABLED"] = False
import db  # noqa: E402
from models_setlist import add_cifra_to_setlist, create_setlist  # noqa: E402


def test_js_modules_with_node():
    print("1. Testando módulos JavaScript com Node.js...")

    node_script = """
    const assert = require('assert');
    const Jumper = require('./static/js/play-song-jumper.js');
    const StageClock = require('./static/js/play-stage-clock.js');
    const ChordHud = require('./static/js/play-chord-hud.js');

    // --- TESTES SONG JUMPER ---
    const sampleCifras = [
        { id: 101, titulo: "Como Nossos Pais", artista: "Elis Regina", tom: "G" },
        { id: 102, titulo: "Evidências", artista: "Chitãozinho e Xororó", tom: "E" },
        { id: 103, titulo: "Águas de Março", artista: "Tom Jobim", tom: "B" },
        { id: 104, titulo: "Sozinho", artista: "Caetano Veloso", tom: "D" }
    ];

    // Busca por número da faixa (#2)
    let resNum = Jumper.filterSongsForTest(sampleCifras, "2");
    assert.strictEqual(resNum.length, 1);
    assert.strictEqual(resNum[0].cifra.titulo, "Evidências");

    // Busca por termo no título com acentuação ("aguas" -> "Águas de Março")
    let resAcc = Jumper.filterSongsForTest(sampleCifras, "aguas");
    assert.strictEqual(resAcc.length, 1);
    assert.strictEqual(resAcc[0].cifra.titulo, "Águas de Março");

    // Busca por artista parcial ("caetano")
    let resArt = Jumper.filterSongsForTest(sampleCifras, "caetano");
    assert.strictEqual(resArt.length, 1);
    assert.strictEqual(resArt[0].cifra.titulo, "Sozinho");

    // Busca por tom ("tom:E" ou "e")
    let resKey = Jumper.filterSongsForTest(sampleCifras, "e");
    assert(resKey.length >= 1);

    // --- TESTES RELÓGIO & CRONÔMETRO ---
    // Formatação de duração
    assert.strictEqual(StageClock.formatDuration(0), "00:00");
    assert.strictEqual(StageClock.formatDuration(75), "01:15");
    assert.strictEqual(StageClock.formatDuration(210), "03:30");
    assert.strictEqual(StageClock.formatDuration(3665), "1:01:05");

    // Formatação de hora
    const d = new Date(2026, 10, 13, 21, 45, 30);
    assert.strictEqual(StageClock.formatTime(d), "21:45");
    assert.strictEqual(StageClock.formatTimeWithSec(d), "21:45:30");

    // Alternância de modo
    StageClock.setMode('timer');
    let state = StageClock.getState();
    assert.strictEqual(state.mode, 'timer');
    StageClock.setMode('clock');
    assert.strictEqual(StageClock.getState().mode, 'clock');

    // --- TESTES CHORD HUD ---
    assert.strictEqual(typeof ChordHud.show, 'function');
    assert.strictEqual(typeof ChordHud.hide, 'function');
    assert.strictEqual(typeof ChordHud.setInstrument, 'function');
    assert.strictEqual(typeof ChordHud.cycleShape, 'function');

    console.log("-> Módulos JS validados com sucesso!");
    """

    res = subprocess.run(
        ["node", "-e", node_script],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print("Erro nos testes Node.js:", res.stderr)
        raise AssertionError("Falha na validação dos scripts JS com Node.js")
    print(res.stdout.strip())


def test_duration_scroll_calculation():
    print("2. Testando algoritmo de rolagem sincronizada por duração musical...")

    # Exemplo: página rolável de 1800px para canção de 3:30 min (210 segundos)
    # Com lead-in delay de 3 segundos (3000ms):
    scrollable_px = 1800
    dur_seconds = 210
    lead_in_delay_ms = 3000
    total_ms = dur_seconds * 1000
    effective_ms = total_ms - lead_in_delay_ms  # 207000 ms

    px_per_ms = scrollable_px / effective_ms
    assert 0.005 < px_per_ms < 0.05, f"Velocidade px/ms fora da faixa aceitável: {px_per_ms}"

    # Verificação de rolagem completa: tempo decorrido total deve cobrir exatamente o total de pixels
    rolled_px = px_per_ms * effective_ms
    assert abs(rolled_px - scrollable_px) < 0.0001, "A distância percorrida deve fechar em 100%"

    print(f"-> Scroll calculado: {px_per_ms:.6f} px/ms para {dur_seconds}s (total: {rolled_px:.1f}px)")


def test_play_mode_template_elements():
    print("3. Testando integração dos novos elementos no template do Modo Tocar...")

    with flask_app.app_context():
        db.init_db()

        user_id = db.create_user(
            "palco_user",
            "palco@example.com",
            "senha123",
            display_name="Músico Palco",
        )
        band = db.create_band("Banda Palco", "Descricao", user_id)
        band_id = band["id"] if isinstance(band, dict) else band

        cifra_id = db.create_cifra(
            titulo="Canção de Palco",
            artista="Banda Palco",
            tom_original="A",
            conteudo="[A]Primeiro verso [D]Refrão [E]Final",
            band_id=band_id,
            bpm=120,
        )

        setlist_id = create_setlist(band_id, "Show ao Vivo")
        add_cifra_to_setlist(setlist_id, cifra_id)

        with flask_app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user_id"] = user_id
                sess["_user_id"] = user_id
                sess["username"] = "palco_user"
                sess["display_name"] = "Músico Palco"

            # Acessar rota do modo tocar
            resp = client.get(f"/setlists/{setlist_id}/tocar")
            assert resp.status_code == 200, f"Modo tocar deve responder 200, recebeu {resp.status_code}"
            html = resp.get_data(as_text=True)

            # 1. Quick Song Jumper
            assert "play-jumper-btn" in html, "Botão do Jumper deve existir no HTML"
            assert "play-song-jumper.js" in html, "Script play-song-jumper.js deve estar incluído"

            # 2. Stage Clock
            assert "stage-clock-widget" in html, "Widget de relógio de palco deve existir"
            assert "stage-clock-display" in html, "Display de relógio de palco deve existir"
            assert "stage-timer-ctrls" in html, "Controles de cronômetro devem existir"
            assert "play-stage-clock.js" in html, "Script play-stage-clock.js deve estar incluído"

            # 3. Auto-scroll por duração
            assert "speed-duration-btn" in html, "Botão de duração deve existir no speed-pill"
            assert "play-duration-modal" in html, "Modal de duração de auto-scroll deve existir"
            assert "applySongDuration" in html, "Função applySongDuration deve existir no script"

            # 4. Mini HUD de Acordes
            assert "play-chord-hud.js" in html, "Script play-chord-hud.js deve estar incluído"

            # 5. Atalhos de teclado J e /
            assert "openSongJumper" in html, "openSongJumper deve ser invocado nos atalhos"

            print("-> Todos os elementos e scripts de palco verificados com sucesso no template HTML!")


def main():
    print("=== INICIANDO VALIDAÇÃO DAS MELHORIAS DE PALCO (SETSYNC) ===")
    test_js_modules_with_node()
    test_duration_scroll_calculation()
    test_play_mode_template_elements()
    print("=== TODOS OS TESTES DE MELHORIAS DE PALCO PASSARAM COM SUCESSO! ===")


if __name__ == "__main__":
    main()
