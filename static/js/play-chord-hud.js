/**
 * Uníssono (SetSync) - Mini HUD Flutuante de Acordes no Modo Tocar (Quick Chord HUD)
 * Exibe um popover compacto e não intrusivo com a digitação do acorde no braço do instrumento
 * sem cobrir a cifra ou parar o fluxo do show.
 */
(function (global) {
    'use strict';

    var ChordHud = {};

    var state = {
        isOpen: false,
        symbol: '',
        chordData: null,
        instrument: 'violao',
        shapeIndex: 0,
        shapes: [],
        dom: {}
    };

    var INSTRUMENTS = [
        { id: 'violao', label: 'Violão' },
        { id: 'ukulele', label: 'Ukulele' },
        { id: 'cavaco', label: 'Cavaco' },
        { id: 'baixo', label: 'Baixo' }
    ];

    function createHudElement() {
        if (typeof document === 'undefined') return;
        if (document.getElementById('play-chord-hud')) return;

        var hud = document.createElement('div');
        hud.id = 'play-chord-hud';
        hud.className = 'play-chord-hud d-none';
        hud.setAttribute('role', 'region');
        hud.setAttribute('aria-label', 'Diagrama rápido de acorde');

        hud.innerHTML =
            '<div class="play-chord-hud-header">' +
                '<div class="play-chord-hud-title-wrap">' +
                    '<span class="play-chord-hud-symbol" id="play-chord-hud-symbol">—</span>' +
                    '<span class="play-chord-hud-notes" id="play-chord-hud-notes"></span>' +
                '</div>' +
                '<button type="button" class="play-chord-hud-close" id="play-chord-hud-close" aria-label="Fechar">✕</button>' +
            '</div>' +
            '<div class="play-chord-hud-inst-tabs" id="play-chord-hud-insts">' +
                INSTRUMENTS.map(function (inst) {
                    return '<button type="button" class="play-chord-hud-inst-btn' + (inst.id === state.instrument ? ' active' : '') +
                           '" data-inst="' + inst.id + '">' + inst.label + '</button>';
                }).join('') +
            '</div>' +
            '<div class="play-chord-hud-body" id="play-chord-hud-body">' +
                '<div class="play-chord-hud-svg-wrap" id="play-chord-hud-svg"></div>' +
            '</div>' +
            '<div class="play-chord-hud-footer">' +
                '<div class="play-chord-hud-shape-nav" id="play-chord-hud-shape-nav">' +
                    '<button type="button" class="play-chord-hud-nav-btn" id="play-chord-prev-shape" title="Forma anterior">‹</button>' +
                    '<span class="play-chord-hud-shape-lbl" id="play-chord-shape-lbl">1/1</span>' +
                    '<button type="button" class="play-chord-hud-nav-btn" id="play-chord-next-shape" title="Próxima forma">›</button>' +
                '</div>' +
                '<button type="button" class="play-chord-hud-more-btn" id="play-chord-hud-more" title="Abrir análise teórica completa">' +
                    'Teoria ↗' +
                '</button>' +
            '</div>';

        document.body.appendChild(hud);

        state.dom.hud = hud;
        state.dom.symbol = hud.querySelector('#play-chord-hud-symbol');
        state.dom.notes = hud.querySelector('#play-chord-hud-notes');
        state.dom.svgWrap = hud.querySelector('#play-chord-hud-svg');
        state.dom.shapeLbl = hud.querySelector('#play-chord-shape-lbl');
        state.dom.closeBtn = hud.querySelector('#play-chord-hud-close');
        state.dom.prevBtn = hud.querySelector('#play-chord-prev-shape');
        state.dom.nextBtn = hud.querySelector('#play-chord-next-shape');
        state.dom.moreBtn = hud.querySelector('#play-chord-hud-more');

        state.dom.closeBtn.addEventListener('click', function () {
            ChordHud.hide();
        });

        state.dom.prevBtn.addEventListener('click', function () {
            ChordHud.cycleShape(-1);
        });

        state.dom.nextBtn.addEventListener('click', function () {
            ChordHud.cycleShape(1);
        });

        state.dom.moreBtn.addEventListener('click', function () {
            var sym = state.symbol;
            ChordHud.hide();
            if (window.SetSyncChordDiagram && window.SetSyncChordDiagram.initChordDiagramModal) {
                var modalApi = window.SetSyncChordDiagram.initChordDiagramModal();
                if (modalApi && modalApi.openChordModal) {
                    modalApi.openChordModal(sym);
                }
            }
        });

        hud.querySelectorAll('.play-chord-hud-inst-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var inst = btn.getAttribute('data-inst');
                ChordHud.setInstrument(inst);
            });
        });
    }

    function renderContent() {
        if (!state.dom.hud) return;

        state.dom.symbol.textContent = state.symbol;

        var CD = window.SetSyncChordDiagram;
        if (!CD) {
            state.dom.svgWrap.innerHTML = '<div class="text-muted p-2 small">Diagrama indisponível</div>';
            return;
        }

        // Tentar obter informações do acorde através da base de dados do SetSync
        var clean = CD.sanitizeChordText ? CD.sanitizeChordText(state.symbol) : state.symbol;
        var chordObj = null;

        if (CD.findChordByName) {
            chordObj = CD.findChordByName(clean);
        }

        // Se tiver notas teóricas
        if (chordObj && Array.isArray(chordObj.notes) && chordObj.notes.length) {
            state.dom.notes.textContent = chordObj.notes.join(' · ');
        } else if (CD.detectChordNotes) {
            var detected = CD.detectChordNotes(clean);
            state.dom.notes.textContent = Array.isArray(detected) ? detected.join(' · ') : '';
        } else {
            state.dom.notes.textContent = '';
        }

        // Gerar shape options para o instrumento atual
        if (CD.buildShapeOptions) {
            state.shapes = CD.buildShapeOptions(state.instrument, chordObj || { name: clean }) || [];
        } else {
            state.shapes = [];
        }

        if (state.shapeIndex >= state.shapes.length) {
            state.shapeIndex = 0;
        }

        var currentShape = state.shapes[state.shapeIndex] || null;

        var totalShapes = Math.max(1, state.shapes.length);
        state.dom.shapeLbl.textContent = (state.shapeIndex + 1) + '/' + totalShapes;
        state.dom.prevBtn.disabled = (totalShapes <= 1);
        state.dom.nextBtn.disabled = (totalShapes <= 1);

        // Atualizar aba de instrumentos
        state.dom.hud.querySelectorAll('.play-chord-hud-inst-btn').forEach(function (btn) {
            btn.classList.toggle('active', btn.getAttribute('data-inst') === state.instrument);
        });

        // Renderizar SVG
        if (CD.renderChordDiagramSvg) {
            var frets = currentShape ? currentShape.frets : null;
            var fingers = currentShape ? currentShape.fingers : null;
            var barres = currentShape ? currentShape.barres : null;

            var svgHtml = CD.renderChordDiagramSvg({
                instrument: state.instrument,
                chord: chordObj || { name: clean },
                frets: frets,
                fingers: fingers,
                barres: barres,
                labelMode: 'dedos',
                leftHanded: false
            });

            state.dom.svgWrap.innerHTML = svgHtml;
        } else {
            state.dom.svgWrap.innerHTML = '<div class="text-muted p-2 small">Diagrama simplificado</div>';
        }
    }

    ChordHud.show = function (symbol, clickX, clickY) {
        if (!symbol) return;
        createHudElement();

        state.symbol = String(symbol).trim();
        state.shapeIndex = 0;
        state.isOpen = true;

        renderContent();

        var hud = state.dom.hud;
        hud.classList.remove('d-none');

        // Posicionamento inteligente no palco:
        // Mantém fixo de forma elegante no canto inferior direito ou segue clique com segurança
        var viewportW = window.innerWidth;
        var viewportH = window.innerHeight;
        var hudW = 230;
        var hudH = 310;

        var left = (viewportW > 600) ? Math.min(viewportW - hudW - 20, Math.max(20, (clickX || (viewportW - hudW - 20)))) : (viewportW - hudW) / 2;
        var top = (viewportH > 500) ? Math.min(viewportH - hudH - 60, Math.max(60, (clickY || (viewportH - hudH - 60)))) : 60;

        hud.style.left = left + 'px';
        hud.style.top = top + 'px';
    };

    ChordHud.hide = function () {
        if (state.dom.hud) {
            state.dom.hud.classList.add('d-none');
        }
        state.isOpen = false;
    };

    ChordHud.cycleShape = function (delta) {
        if (!state.shapes.length) return;
        state.shapeIndex = (state.shapeIndex + delta + state.shapes.length) % state.shapes.length;
        renderContent();
    };

    ChordHud.setInstrument = function (inst) {
        if (state.instrument === inst) return;
        state.instrument = inst;
        state.shapeIndex = 0;
        renderContent();
    };

    ChordHud.isOpen = function () {
        return state.isOpen;
    };

    ChordHud.init = function () {
        if (typeof document === 'undefined') return;
        createHudElement();

        // Intercepta cliques nos acordes com prioridade (fase de captura)
        document.addEventListener('click', function (e) {
            if (!document.body.classList.contains('play-mode')) return;

            var target = e.target.closest('.chord, .cj-chord, .sp-chord, .grade-chord, .grade-chord-play, .grade-visual-chord, .chord-text, .chord-sheet-chord, .cs-chord, .cifra-tab-chord');
            if (target) {
                var symbol = (target.getAttribute('data-chord') || target.textContent || '').trim();
                if (symbol && symbol !== '\u00a0') {
                    e.preventDefault();
                    e.stopPropagation(); // Evita abrir o modal escurecedor do Bootstrap
                    ChordHud.show(symbol, e.clientX, e.clientY);
                    return;
                }
            }

            // Fechar HUD ao clicar fora
            if (state.isOpen && state.dom.hud && !state.dom.hud.contains(e.target)) {
                ChordHud.hide();
            }
        }, true);

        // Fechar com Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && state.isOpen) {
                e.preventDefault();
                ChordHud.hide();
            }
        });
    };

    global.SetSyncChordHud = ChordHud;

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ChordHud;
    }
})(typeof window !== 'undefined' ? window : globalThis);
