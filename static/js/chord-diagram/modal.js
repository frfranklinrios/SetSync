/** Modal de diagramas — acordes reais e escalas */
(function (global) {
  var CD = (global.SetSyncChordDiagram = global.SetSyncChordDiagram || {});

  function initChordDiagramModal() {
    var modalEl = document.getElementById('chordModal');
    if (!modalEl || typeof bootstrap === 'undefined') return null;

    var modal = new bootstrap.Modal(modalEl);
    var state = {
      instrument: 'violao',
      viewMode: 'chord',
      rawSymbol: '',
      chords: [],
      selectedChord: 0,
      bassType: '4',
      shapeOptions: [],
      selectedShape: 0,
      scaleOptions: [],
      selectedScale: 0,
      arpPatternBass: 'root',
    };

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
      state.shapeOptions = CD.buildShapeOptions(state.instrument, chord);
      if (state.selectedShape >= state.shapeOptions.length) state.selectedShape = 0;
    }

    function updateScaleOptions(chord) {
      state.scaleOptions = CD.suggestScalesForChord(chord);
      if (state.selectedScale >= state.scaleOptions.length) state.selectedScale = 0;
    }

    function renderViewTabs() {
      var tabs = document.getElementById('diagram-view-tabs');
      if (!tabs) return;
      tabs.querySelectorAll('[data-view]').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-view') === state.viewMode);
      });
      tabs.style.display = state.instrument === 'baixo' ? 'none' : 'flex';
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
        return '<button type="button" class="' + cls + '" data-shape="' + idx + '">' +
          CD.escText(opt.label) + ' · ' + CD.fretsLabel(opt.frets) + '</button>';
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
      var title = row ? row.querySelector('.modal-option-title') : null;
      var chord = currentChord();
      if (!row || !el) return;

      if (state.instrument !== 'baixo' || state.viewMode !== 'chord') {
        row.classList.remove('show');
        el.innerHTML = '';
        return;
      }

      row.classList.add('show');
      var list = CD.availableBassPatterns(chord);
      if (!list.some(function (p) { return p.id === state.arpPatternBass; })) {
        state.arpPatternBass = 'root';
      }
      if (title) title.textContent = 'Arpejo e inversões';
      el.innerHTML = list.map(function (p) {
        var cls = 'chord-chip' + (p.id === state.arpPatternBass ? ' active' : '');
        return '<button type="button" class="' + cls + '" data-arp="' + p.id + '">' + p.label + '</button>';
      }).join('');
    }

    function renderModalBody() {
      var chord = currentChord();
      if (!chord) return;

      updateShapeOptions(chord);
      updateScaleOptions(chord);
      renderViewTabs();

      var titleEl = document.getElementById('chordModalTitle');
      var notesEl = document.getElementById('chord-notes');
      var body = document.getElementById('chord-modal-body-content');

      if (state.viewMode === 'scale' && state.instrument !== 'baixo') {
        titleEl.textContent = 'Escalas: ' + chord.display;
        var sc = state.scaleOptions[state.selectedScale];
        if (sc) {
          notesEl.textContent = 'Tônica: ' + sc.root + ' · Notas: ' + (sc.notes || []).join(' · ');
          body.innerHTML = CD.renderScaleDiagram(state.instrument, sc.root, sc.id, sc);
        } else {
          notesEl.textContent = '';
          body.innerHTML = '<div class="text-muted">Nenhuma escala sugerida.</div>';
        }
      } else if (state.instrument === 'baixo') {
        titleEl.textContent = 'Acorde: ' + chord.display;
        notesEl.textContent = 'Notas: ' + (chord.notes || []).join(' · ');
        body.innerHTML = CD.renderArpeggio(chord, currentBassTuning(), state.arpPatternBass);
      } else {
        titleEl.textContent = 'Acorde: ' + chord.display;
        notesEl.textContent = 'Notas: ' + (chord.notes || []).join(' · ');
        var shape = state.shapeOptions[state.selectedShape];
        body.innerHTML = CD.renderChordDiagram(state.instrument, chord, shape);
      }

      renderChordChips();
      renderShapeOptions();
      renderScaleOptions();
      renderArpOptions();
    }

    function setViewMode(mode) {
      state.viewMode = mode === 'scale' ? 'scale' : 'chord';
      renderModalBody();
    }

    function setInstrument(inst) {
      state.instrument = inst;
      if (inst === 'baixo') state.viewMode = 'chord';
      document.querySelectorAll('.chord-inst-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-inst') === inst);
      });
      var bassOptions = document.getElementById('bass-options');
      if (bassOptions) bassOptions.classList.toggle('show', inst === 'baixo');
      renderModalBody();
    }

    function setBassType(kind) {
      state.bassType = kind;
      document.querySelectorAll('.bass-opt-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-bass') === kind);
      });
      if (state.instrument === 'baixo') renderModalBody();
    }

    function fetchChordInfo(symbol) {
      return fetch('/cifras/chord-info?symbol=' + encodeURIComponent(symbol), {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      }).then(function (r) { return r.json(); });
    }

    function openChordModal(symbol) {
      var clean = CD.sanitizeChordText(symbol);
      if (!clean) return;
      state.rawSymbol = clean;
      fetchChordInfo(clean)
        .then(function (data) {
          if (!data || !Array.isArray(data.chords) || !data.chords.length) return;
          state.chords = data.chords;
          state.selectedChord = 0;
          state.selectedShape = 0;
          state.selectedScale = 0;
          state.viewMode = 'chord';
          setInstrument(state.instrument || 'violao');
          modal.show();
        })
        .catch(function () {});
    }

    document.addEventListener('click', function (ev) {
      var target = ev.target.closest('.chord, .cj-chord, .sp-chord, .grade-chord, .grade-chord-play');
      if (target && target.textContent && target.textContent.trim()) {
        ev.preventDefault();
        openChordModal(target.textContent.trim());
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

    return { openChordModal: openChordModal, state: state };
  }

  CD.initChordDiagramModal = initChordDiagramModal;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChordDiagramModal);
  } else {
    initChordDiagramModal();
  }
})(typeof window !== 'undefined' ? window : globalThis);
