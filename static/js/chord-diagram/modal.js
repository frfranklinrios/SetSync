/** Modal de diagramas — acordes, escalas e preferências */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});
  var PREFS_KEY = 'setsync_diagram_prefs';

  function loadPrefs() {
    try {
      return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}') || {};
    } catch (e) {
      return {};
    }
  }

  function savePrefs(state) {
    try {
      localStorage.setItem(PREFS_KEY, JSON.stringify({
        instrument: state.instrument,
        labelMode: state.labelMode,
        leftHanded: state.leftHanded,
        bassType: state.bassType,
      }));
    } catch (e) { /* ignore */ }
  }

  function initChordDiagramModal() {
    var modalEl = document.getElementById('chordModal');
    if (!modalEl || typeof bootstrap === 'undefined') return null;

    var modal = new bootstrap.Modal(modalEl);
    var prefs = loadPrefs();
    var state = {
      instrument: prefs.instrument || 'violao',
      viewMode: 'chord',
      labelMode: prefs.labelMode || 'dedos',
      leftHanded: !!prefs.leftHanded,
      rawSymbol: '',
      chords: [],
      selectedChord: 0,
      bassType: prefs.bassType || '4',
      shapeOptions: [],
      selectedShape: 0,
      scaleOptions: [],
      selectedScale: 0,
      scaleStart: 0,
      arpPatternBass: 'root',
      arpLoadToken: 0,
    };

    function renderOpts() {
      return {
        labelMode: state.labelMode,
        leftHanded: state.leftHanded,
        scaleStart: state.scaleStart,
        scaleRows: 12,
        chordTones: CD.chordToneSet(currentChord()),
      };
    }

    function currentBassTuning() {
      if (state.bassType === '6') return CD.TUNINGS.baixo6;
      if (state.bassType === '5') return CD.TUNINGS.baixo5;
      return CD.TUNINGS.baixo4;
    }

    function currentChord() {
      return state.chords[state.selectedChord];
    }

    function updateShapeOptions(chord) {
      if (!chord || state.instrument === 'baixo') {
        state.shapeOptions = [];
        state.selectedShape = 0;
        return;
      }
      if (chord.positions && chord.positions.length) {
        state.shapeOptions = CD.positionsToShapeOptions(chord.positions);
      } else {
        state.shapeOptions = CD.buildShapeOptions(state.instrument, chord);
      }
      if (state.selectedShape >= state.shapeOptions.length) state.selectedShape = 0;
    }

    function updateScaleOptions(chord) {
      state.scaleOptions = CD.suggestScalesForChord(chord);
      if (state.selectedScale >= state.scaleOptions.length) state.selectedScale = 0;
      var sc = state.scaleOptions[state.selectedScale];
      if (sc) {
        state.scaleStart = CD.defaultScaleStart(CD.TUNINGS[state.instrument] || [], sc.root);
      }
    }

    function syncDisplayToggles() {
      document.querySelectorAll('[data-label-mode]').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-label-mode') === state.labelMode);
      });
      var lh = document.getElementById('diagram-left-handed');
      if (lh) lh.checked = state.leftHanded;
    }

    function renderViewTabs() {
      var tabs = document.getElementById('diagram-view-tabs');
      if (!tabs) return;
      tabs.querySelectorAll('[data-view]').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-view') === state.viewMode);
      });
      tabs.style.display = state.instrument === 'baixo' ? 'none' : 'flex';
      tabs.querySelectorAll('[data-view="notation"]').forEach(function (btn) {
        btn.style.display = state.instrument === 'baixo' ? 'none' : '';
      });
    }

    function renderScaleNav() {
      var row = document.getElementById('scale-nav-row');
      var label = document.getElementById('scale-nav-label');
      if (!row) return;
      if (state.viewMode !== 'scale' || state.instrument === 'baixo') {
        row.classList.remove('show');
        return;
      }
      row.classList.add('show');
      if (label) label.textContent = 'Casa ' + state.scaleStart + ' – ' + (state.scaleStart + 12);
    }

    function renderChordChips() {
      var chipsEl = document.getElementById('chord-chips');
      if (!chipsEl) return;
      if (!state.chords.length || state.chords.length === 1) {
        chipsEl.style.display = 'none';
        chipsEl.innerHTML = '';
        return;
      }
      chipsEl.style.display = 'flex';
      chipsEl.innerHTML = state.chords.map(function (c, i) {
        var cls = 'chord-chip' + (i === state.selectedChord ? ' active' : '');
        return '<button type="button" class="' + cls + '" data-chip="' + i + '">' + CD.escText(c.display) + '</button>';
      }).join('');
    }

    function renderShapeOptions() {
      var row = document.getElementById('shape-options-row');
      var el = document.getElementById('shape-options');
      if (!row || !el) return;
      if (state.viewMode !== 'chord' || state.instrument === 'baixo' || !state.shapeOptions.length) {
        row.classList.remove('show');
        el.innerHTML = '';
        return;
      }
      row.classList.add('show');
      el.innerHTML = state.shapeOptions.map(function (opt, idx) {
        var cls = 'chord-chip' + (idx === state.selectedShape ? ' active' : '');
        return '<button type="button" class="' + cls + '" data-shape="' + idx + '" title="' +
          CD.escText(opt.source || '') + '">' +
          CD.escText(opt.label) + '</button>';
      }).join('');
    }

    function renderScaleOptions() {
      var row = document.getElementById('scale-options-row');
      var el = document.getElementById('scale-options');
      if (!row || !el) return;
      if (state.viewMode !== 'scale' || state.instrument === 'baixo' || !state.scaleOptions.length) {
        row.classList.remove('show');
        el.innerHTML = '';
        return;
      }
      row.classList.add('show');
      el.innerHTML = state.scaleOptions.map(function (sc, idx) {
        var cls = 'chord-chip' + (idx === state.selectedScale ? ' active' : '');
        return '<button type="button" class="' + cls + '" data-scale="' + idx + '">' + CD.escText(sc.label) + '</button>';
      }).join('');
    }

    function renderArpOptions() {
      var row = document.getElementById('arp-options-row');
      var el = document.getElementById('arp-options');
      if (!row || !el) return;
      if (state.instrument !== 'baixo' || state.viewMode !== 'chord') {
        row.classList.remove('show');
        el.innerHTML = '';
        return;
      }
      row.classList.add('show');
      state.arpPatternBass = 'root';
      el.innerHTML = '<button type="button" class="chord-chip active" data-arp="root">Fundamental</button>';
    }

    function showBodyMessage(html) {
      var body = document.getElementById('chord-modal-body-content');
      if (body) body.innerHTML = html;
    }

    function renderNotationView(chord, body, notesEl, titleEl) {
      titleEl.textContent = 'Partitura: ' + chord.display;
      notesEl.textContent = 'VexTab · posição ' + (state.selectedShape + 1);
      body.innerHTML = '<div class="diagram-loading text-center py-3"><div class="spinner-border spinner-border-sm"></div></div>';
      var sym = chord.display || chord.input || state.rawSymbol;
      CD.fetchVextab(sym, state.instrument, state.selectedShape)
        .then(function (data) {
          if (!data || !data.vextab) {
            body.innerHTML = '<div class="text-muted">Partitura indisponível.</div>';
            return;
          }
          var svgUrl = CD.renderServerSvg(sym, state.instrument, state.selectedShape);
          body.innerHTML =
            '<div class="notation-panel">' +
            '<div class="notation-svg-wrap mb-3"><object type="image/svg+xml" data="' +
            CD.escText(svgUrl) + '" class="diagram-svg-object" aria-label="Diagrama SVG"></object></div>' +
            '<details class="vextab-details"><summary class="small text-muted">VexTab (VexFlow)</summary>' +
            '<pre class="vextab-source small">' + CD.escText(data.vextab) + '</pre></details></div>';
        })
        .catch(function () {
          body.innerHTML = '<div class="alert alert-warning mb-0">Não foi possível carregar a partitura.</div>';
        });
    }

    function renderModalBody() {
      var chord = currentChord();
      if (!chord) return;

      updateShapeOptions(chord);
      updateScaleOptions(chord);
      renderViewTabs();
      syncDisplayToggles();

      var titleEl = document.getElementById('chordModalTitle');
      var notesEl = document.getElementById('chord-notes');
      var body = document.getElementById('chord-modal-body-content');
      var opts = renderOpts();

      if (state.viewMode === 'notation' && state.instrument !== 'baixo') {
        renderNotationView(chord, body, notesEl, titleEl);
      } else if (state.viewMode === 'scale' && state.instrument !== 'baixo') {
        titleEl.textContent = 'Escalas: ' + chord.display;
        var sc = state.scaleOptions[state.selectedScale];
        if (sc) {
          notesEl.innerHTML = 'Tônica: <strong>' + CD.escText(sc.root) + '</strong> · ' +
            'Notas do acorde em <span class="diagram-legend-chord-tone">●</span> destaque';
          body.innerHTML = CD.renderScaleDiagram(state.instrument, sc.root, sc.id, sc, opts);
        } else {
          notesEl.textContent = '';
          body.innerHTML = '<div class="text-muted">Nenhuma escala sugerida.</div>';
        }
      } else if (state.instrument === 'baixo') {
        titleEl.textContent = 'Acorde: ' + chord.display;
        notesEl.textContent = 'Notas: ' + (chord.notes || []).join(' · ');
        var arpToken = ++state.arpLoadToken;
        var sym = chord.display || chord.input || state.rawSymbol;
        var tuning = currentBassTuning();
        var pattern = state.arpPatternBass;
        body.innerHTML = CD.renderArpeggio(chord, tuning, pattern);
        if (CD.fetchArpeggio) {
          CD.fetchArpeggio(sym, 'baixo', pattern)
            .then(function (data) {
              if (arpToken !== state.arpLoadToken) return;
              if (!data || data.error) return;
              var apiSteps = data.fretboardSteps || [];
              if (!apiSteps.length) return;
              body.innerHTML = CD.renderArpeggio(chord, tuning, pattern, {
                steps: apiSteps,
                meta: data.arpeggioPattern,
              });
            })
            .catch(function () { /* mantém renderização local */ });
        }
      } else {
        titleEl.textContent = 'Acorde: ' + chord.display;
        notesEl.textContent = 'Notas: ' + (chord.notes || []).join(' · ');
        var shape = state.shapeOptions[state.selectedShape];
        body.innerHTML = CD.renderChordDiagram(state.instrument, chord, shape, opts);
      }

      renderChordChips();
      renderShapeOptions();
      renderScaleOptions();
      renderArpOptions();
      renderScaleNav();
      savePrefs(state);
    }

    function setViewMode(mode) {
      if (mode === 'scale') state.viewMode = 'scale';
      else if (mode === 'notation') state.viewMode = 'notation';
      else state.viewMode = 'chord';
      renderModalBody();
    }

    function loadChordsFromApi(symbol, instrument) {
      var loader = CD.fetchModalChords || fetchChordInfoLegacy;
      return loader(symbol, instrument).then(function (data) {
        if (!data || data.error || !Array.isArray(data.chords) || !data.chords.length) {
          return data;
        }
        state.chords = data.chords;
        state.selectedChord = 0;
        state.selectedShape = 0;
        state.selectedScale = 0;
        return data;
      });
    }

    function fetchChordInfoLegacy(symbol) {
      return fetch('/cifras/chord-info?symbol=' + encodeURIComponent(symbol), {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      }).then(function (r) { return r.json(); });
    }

    function setInstrument(inst) {
      state.instrument = inst;
      if (inst === 'baixo') state.viewMode = 'chord';
      document.querySelectorAll('.chord-inst-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-inst') === inst);
      });
      var bassOptions = document.getElementById('bass-options');
      if (bassOptions) bassOptions.classList.toggle('show', inst === 'baixo');
      if (state.rawSymbol && CD.fetchModalChords) {
        showBodyMessage('<div class="diagram-loading text-center py-4"><div class="spinner-border spinner-border-sm text-secondary"></div></div>');
        loadChordsFromApi(state.rawSymbol, inst)
          .then(function (data) {
            if (!data || data.error) {
              showBodyMessage('<div class="alert alert-warning mb-0">Instrumento indisponível para este acorde.</div>');
              return;
            }
            renderModalBody();
          })
          .catch(function () { renderModalBody(); });
      } else {
        renderModalBody();
      }
    }

    function setBassType(kind) {
      state.bassType = kind;
      document.querySelectorAll('.bass-opt-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-bass') === kind);
      });
      if (state.instrument === 'baixo') renderModalBody();
    }

    function fetchChordInfo(symbol) {
      if (CD.fetchModalChords) {
        return CD.fetchModalChords(symbol, state.instrument);
      }
      return fetchChordInfoLegacy(symbol);
    }

    function openChordModal(symbol) {
      var clean = CD.sanitizeChordText(symbol);
      if (!clean) return;

      state.rawSymbol = clean;
      showBodyMessage('<div class="diagram-loading text-center py-4"><div class="spinner-border spinner-border-sm text-secondary" role="status"></div><div class="text-muted mt-2" style="font-size:var(--text-sm)">Carregando acorde…</div></div>');
      document.getElementById('chord-notes').textContent = '';
      modal.show();

      fetchChordInfo(clean)
        .then(function (data) {
          if (!data || data.error || !Array.isArray(data.chords) || !data.chords.length) {
            showBodyMessage('<div class="alert alert-warning mb-0">Não foi possível analisar o acorde <strong>' +
              CD.escText(clean) + '</strong>. Verifique a notação.</div>');
            return;
          }
          state.chords = data.chords;
          state.selectedChord = 0;
          state.selectedShape = 0;
          state.selectedScale = 0;
          state.viewMode = 'chord';
          document.querySelectorAll('.chord-inst-btn').forEach(function (btn) {
            btn.classList.toggle('active', btn.getAttribute('data-inst') === state.instrument);
          });
          renderModalBody();
        })
        .catch(function () {
          showBodyMessage('<div class="alert alert-danger mb-0">Erro ao carregar o diagrama. Tente novamente.</div>');
        });
    }

    document.addEventListener('click', function (ev) {
      var target = ev.target.closest('.chord, .cj-chord, .sp-chord, .grade-chord, .grade-chord-play, .grade-visual-chord, .chord-text, .chord-sheet-chord, .cs-chord');
      if (target && target.textContent && target.textContent.trim()) {
        ev.preventDefault();
        openChordModal(target.textContent.trim());
        return;
      }

      var labelBtn = ev.target.closest('[data-label-mode]');
      if (labelBtn) {
        ev.preventDefault();
        state.labelMode = labelBtn.getAttribute('data-label-mode') || 'dedos';
        renderModalBody();
        return;
      }

      var scalePrev = ev.target.closest('[data-scale-nav="prev"]');
      if (scalePrev) {
        ev.preventDefault();
        state.scaleStart = Math.max(0, state.scaleStart - 3);
        renderModalBody();
        return;
      }
      var scaleNext = ev.target.closest('[data-scale-nav="next"]');
      if (scaleNext) {
        ev.preventDefault();
        state.scaleStart = Math.min(12, state.scaleStart + 3);
        renderModalBody();
        return;
      }

      var viewBtn = ev.target.closest('#diagram-view-tabs [data-view]');
      if (viewBtn) {
        ev.preventDefault();
        setViewMode(viewBtn.getAttribute('data-view'));
        return;
      }

      var instBtn = ev.target.closest('.chord-inst-btn');
      if (instBtn) {
        ev.preventDefault();
        setInstrument(instBtn.getAttribute('data-inst'));
        return;
      }

      var chipBtn = ev.target.closest('[data-chip]');
      if (chipBtn) {
        ev.preventDefault();
        state.selectedChord = parseInt(chipBtn.getAttribute('data-chip'), 10) || 0;
        state.selectedShape = 0;
        state.selectedScale = 0;
        renderModalBody();
        return;
      }

      var shapeBtn = ev.target.closest('[data-shape]');
      if (shapeBtn) {
        ev.preventDefault();
        state.selectedShape = parseInt(shapeBtn.getAttribute('data-shape'), 10) || 0;
        renderModalBody();
        return;
      }

      var scaleBtn = ev.target.closest('[data-scale]');
      if (scaleBtn) {
        ev.preventDefault();
        state.selectedScale = parseInt(scaleBtn.getAttribute('data-scale'), 10) || 0;
        var sc = state.scaleOptions[state.selectedScale];
        if (sc) state.scaleStart = CD.defaultScaleStart(CD.TUNINGS[state.instrument] || [], sc.root);
        renderModalBody();
        return;
      }

      var arpBtn = ev.target.closest('[data-arp]');
      if (arpBtn) {
        ev.preventDefault();
        state.arpPatternBass = arpBtn.getAttribute('data-arp') || 'root';
        renderModalBody();
        return;
      }

      var bassBtn = ev.target.closest('.bass-opt-btn');
      if (bassBtn) {
        ev.preventDefault();
        setBassType(bassBtn.getAttribute('data-bass') || '4');
      }
    });

    var lhCheck = document.getElementById('diagram-left-handed');
    if (lhCheck) {
      lhCheck.checked = state.leftHanded;
      lhCheck.addEventListener('change', function () {
        state.leftHanded = lhCheck.checked;
        renderModalBody();
      });
    }

    document.querySelectorAll('.chord-inst-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-inst') === state.instrument);
    });

    return { openChordModal: openChordModal, state: state };
  }

  CD.initChordDiagramModal = initChordDiagramModal;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChordDiagramModal);
  } else {
    initChordDiagramModal();
  }
})(typeof window !== 'undefined' ? window : globalThis);
