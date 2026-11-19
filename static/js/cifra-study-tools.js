/**
 * Uníssono — Estúdio de Estudo e Prática (Visualização da Cifra)
 * - Barra de acordes únicos clicáveis (abre diagrama SVG)
 * - Diapasão Web Audio no tom atual
 * - Ajuste de tamanho da fonte, modo 1/2 colunas e auto-scroll de estudo
 */
(function (global) {
    'use strict';

    var FONT_KEY = 'unissono_view_font_pct';
    var COLS_KEY = 'unissono_view_two_cols';

    var NOTE_SEMITONES = {
        'C': 0, 'B#': 0,
        'C#': 1, 'DB': 1,
        'D': 2,
        'D#': 3, 'EB': 3,
        'E': 4, 'FB': 4,
        'F': 5, 'E#': 5,
        'F#': 6, 'GB': 6,
        'G': 7,
        'G#': 8, 'AB': 8,
        'A': 9,
        'A#': 10, 'BB': 10,
        'B': 11, 'CB': 11
    };

    function keyToFreq(keyLabel) {
        if (!keyLabel) return 261.63; // C4
        var m = String(keyLabel).trim().match(/^([A-Ga-g][#b]?)/);
        if (!m) return 261.63;
        var root = m[1].toUpperCase();
        var semi = NOTE_SEMITONES[root];
        if (typeof semi !== 'number') return 261.63;
        // C4 = MIDI 60, A4 = MIDI 69 (440 Hz)
        var midi = 60 + semi;
        if (midi > 67) midi -= 12; // mantém região grave-média agradável (C3#..G4)
        return 440 * Math.pow(2, (midi - 69) / 12);
    }

    function playPitchTone(keyLabel, btn) {
        var AudioCtx = global.AudioContext || global.webkitAudioContext;
        if (!AudioCtx) return;

        try {
            var ctx = new AudioCtx();
            var now = ctx.currentTime;
            var freq = keyToFreq(keyLabel);
            var isMinor = /m(?!aj)/i.test(String(keyLabel || ''));

            var master = ctx.createGain();
            master.gain.setValueAtTime(0.001, now);
            master.gain.exponentialRampToValueAtTime(0.16, now + 0.06);
            master.gain.exponentialRampToValueAtTime(0.0008, now + 1.55);
            master.connect(ctx.destination);

            // Fundamental + quinta (e terça sutil para referência harmônica)
            var ratios = [1, isMinor ? Math.pow(2, 3 / 12) : Math.pow(2, 4 / 12), Math.pow(2, 7 / 12)];
            ratios.forEach(function (ratio, idx) {
                var osc = ctx.createOscillator();
                var gain = ctx.createGain();
                osc.type = idx === 0 ? 'triangle' : 'sine';
                osc.frequency.setValueAtTime(freq * ratio, now);
                gain.gain.setValueAtTime(idx === 0 ? 0.65 : 0.22, now);
                osc.connect(gain);
                gain.connect(master);
                osc.start(now);
                osc.stop(now + 1.6);
            });

            if (btn) {
                btn.classList.add('active');
                setTimeout(function () {
                    btn.classList.remove('active');
                    if (ctx && typeof ctx.close === 'function') {
                        ctx.close().catch(function () {});
                    }
                }, 1600);
            }
        } catch (e) { /* audio bloqueado ou indisponível */ }
    }

    function buildUniqueChordsBar() {
        var cifraBody = document.getElementById('cifra-body');
        var bar = document.getElementById('cifra-unique-chords-bar');
        var list = document.getElementById('cifra-unique-chords-list');
        if (!cifraBody || !bar || !list) return;

        var seen = {};
        var chords = [];
        cifraBody.querySelectorAll('.chord, .sp-chord, .cj-chord, .cifra-tab-chord').forEach(function (el) {
            var sym = (el.getAttribute('data-chord') || el.textContent || '').replace(/\u00a0/g, ' ').trim();
            if (!sym || sym.length > 18) return;
            if (!/^[A-G]/.test(sym)) return;
            if (!seen[sym]) {
                seen[sym] = true;
                chords.push(sym);
            }
        });

        if (!chords.length) {
            bar.classList.add('d-none');
            return;
        }

        list.innerHTML = '';
        chords.forEach(function (sym) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'chord study-chord-chip';
            btn.setAttribute('data-chord', sym);
            btn.setAttribute('title', 'Ver diagrama de ' + sym);
            btn.textContent = sym;
            list.appendChild(btn);
        });
        bar.classList.remove('d-none');
    }

    function initStudyToolbar() {
        var toolbar = document.getElementById('cifra-study-toolbar');
        var cifraBody = document.getElementById('cifra-body');
        if (!toolbar || !cifraBody) return;

        // 1. Diapasão
        var pitchBtn = document.getElementById('view-pitch-pipe-btn');
        if (pitchBtn) {
            pitchBtn.addEventListener('click', function () {
                playPitchTone(pitchBtn.getAttribute('data-key') || '', pitchBtn);
            });
        }

        // 2. Tamanho da fonte
        var fontPct = 100;
        try {
            var savedFont = parseInt(localStorage.getItem(FONT_KEY) || '100', 10);
            if (savedFont >= 85 && savedFont <= 160) fontPct = savedFont;
        } catch (e) { /* ignore */ }

        var fontVal = document.getElementById('view-font-val');
        var fontDown = document.getElementById('view-font-down');
        var fontUp = document.getElementById('view-font-up');

        function applyFont(pct) {
            fontPct = Math.max(85, Math.min(160, pct));
            cifraBody.style.fontSize = (fontPct / 100) + 'rem';
            document.querySelectorAll('.letra-pane').forEach(function (el) {
                el.style.fontSize = (fontPct / 100) + 'rem';
            });
            if (fontVal) fontVal.textContent = fontPct + '%';
            try { localStorage.setItem(FONT_KEY, String(fontPct)); } catch (e) { /* ignore */ }
        }
        applyFont(fontPct);

        if (fontDown) fontDown.addEventListener('click', function () { applyFont(fontPct - 10); });
        if (fontUp) fontUp.addEventListener('click', function () { applyFont(fontPct + 10); });

        // 3. 1 / 2 Colunas
        var colsBtn = document.getElementById('view-cols-toggle');
        var twoCols = false;
        try { twoCols = localStorage.getItem(COLS_KEY) === '1'; } catch (e) { /* ignore */ }

        function applyCols(on) {
            twoCols = !!on;
            cifraBody.classList.toggle('cifra-two-cols', twoCols);
            if (colsBtn) {
                colsBtn.classList.toggle('active', twoCols);
                colsBtn.setAttribute('aria-pressed', twoCols ? 'true' : 'false');
            }
            try { localStorage.setItem(COLS_KEY, twoCols ? '1' : '0'); } catch (e) { /* ignore */ }
        }
        applyCols(twoCols);

        if (colsBtn) {
            colsBtn.addEventListener('click', function () { applyCols(!twoCols); });
        }

        // 4. Auto-scroll de estudo
        var scrollBtn = document.getElementById('view-autoscroll-toggle');
        var speedSel = document.getElementById('view-autoscroll-speed');
        var rafId = null;
        var scrolling = false;
        var lastTs = 0;
        var carryPx = 0;

        function stopAutoScroll() {
            scrolling = false;
            if (rafId) {
                cancelAnimationFrame(rafId);
                rafId = null;
            }
            if (scrollBtn) {
                scrollBtn.classList.remove('active');
                scrollBtn.innerHTML = '<i class="fas fa-angle-double-down"></i><span>Auto-scroll</span>';
            }
        }

        function tick(ts) {
            if (!scrolling) return;
            if (!lastTs) lastTs = ts;
            var dt = Math.min(100, ts - lastTs);
            lastTs = ts;
            var pxPerSec = parseFloat(speedSel ? speedSel.value : '28') || 28;
            carryPx += (pxPerSec * dt) / 1000;
            if (carryPx >= 1) {
                var step = Math.floor(carryPx);
                carryPx -= step;
                global.scrollBy(0, step);
            }
            var atBottom = (global.innerHeight + global.scrollY) >= (document.documentElement.scrollHeight - 4);
            if (atBottom) {
                stopAutoScroll();
                return;
            }
            rafId = requestAnimationFrame(tick);
        }

        if (scrollBtn) {
            scrollBtn.addEventListener('click', function () {
                if (scrolling) {
                    stopAutoScroll();
                } else {
                    scrolling = true;
                    lastTs = 0;
                    carryPx = 0;
                    scrollBtn.classList.add('active');
                    scrollBtn.innerHTML = '<i class="fas fa-pause"></i><span>Pausar</span>';
                    rafId = requestAnimationFrame(tick);
                }
            });
        }
    }

    function init() {
        buildUniqueChordsBar();
        initStudyToolbar();
    }

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    }
})(typeof window !== 'undefined' ? window : globalThis);
