/**
 * Mapeamento de teclas/pedais Bluetooth no Modo Tocar.
 */
(function (global) {
  'use strict';

  var STORAGE_KEY = 'setsync.pedalMap.v1';

  var ACTION_LABELS = {
    pageDown: 'Próxima página',
    pageUp: 'Página anterior',
    prevSong: 'Música anterior',
    nextSong: 'Próxima música',
    toggleScroll: 'Auto-scroll',
    toggleMetronome: 'Metrônomo',
    toggleDraw: 'Desenhar',
    toggleFullscreen: 'Tela cheia',
  };

  var DEFAULT_MAP = {
    pageDown: ['PageDown', 'ArrowRight'],
    pageUp: ['PageUp', 'ArrowLeft'],
    prevSong: ['ArrowUp'],
    nextSong: ['ArrowDown'],
    toggleScroll: [' '],
    toggleMetronome: ['m', 'M'],
    toggleDraw: ['d', 'D'],
    toggleFullscreen: ['f', 'F'],
  };

  var handlers = {};

  function cloneDefault() {
    var out = {};
    Object.keys(DEFAULT_MAP).forEach(function (k) {
      out[k] = DEFAULT_MAP[k].slice();
    });
    return out;
  }

  function loadMap() {
    try {
      var raw = global.localStorage.getItem(STORAGE_KEY);
      if (!raw) return cloneDefault();
      var parsed = JSON.parse(raw);
      var base = cloneDefault();
      Object.keys(base).forEach(function (action) {
        if (Array.isArray(parsed[action])) {
          base[action] = parsed[action].filter(function (k) { return typeof k === 'string' && k; });
        }
      });
      return base;
    } catch (e) {
      return cloneDefault();
    }
  }

  function saveMap(map) {
    try {
      global.localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
    } catch (e) { /* quota */ }
  }

  function normalizeKeyInput(val) {
    val = String(val || '').trim();
    if (!val) return '';
    var aliases = {
      space: ' ',
      espaço: ' ',
      esc: 'Escape',
      enter: 'Enter',
      pgup: 'PageUp',
      pgdn: 'PageDown',
      pageup: 'PageUp',
      pagedown: 'PageDown',
    };
    var low = val.toLowerCase();
    if (aliases[low]) return aliases[low];
    if (val.length === 1) return val;
    if (val === ' ') return ' ';
    if (/^arrow(up|down|left|right)$/i.test(val)) {
      return val.charAt(0).toUpperCase() + val.slice(1).toLowerCase();
    }
    if (/^page(up|down)$/i.test(val)) {
      return 'Page' + val.slice(4, 5).toUpperCase() + val.slice(5).toLowerCase();
    }
    return val;
  }

  function keyLabel(key) {
    if (key === ' ') return 'Espaço';
    return key;
  }

  function bindHandlers(mapHandlers) {
    handlers = mapHandlers || {};
  }

  function handleKeydown(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return false;
    var tag = e.target && e.target.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return false;
    var map = loadMap();
    var key = e.key;
    var actions = Object.keys(map);
    for (var i = 0; i < actions.length; i++) {
      var action = actions[i];
      var keys = map[action];
      if (!keys || !keys.length) continue;
      if (keys.indexOf(key) === -1) continue;
      var fn = handlers[action];
      if (typeof fn === 'function') {
        e.preventDefault();
        fn();
        return true;
      }
    }
    return false;
  }

  function renderModal(container) {
    if (!container) return;
    var map = loadMap();
    var html = '<div class="play-pedal-modal-inner">';
    html += '<p class="text-muted small mb-3">Associe teclas do pedal Bluetooth (ou do teclado) a cada ação. Separe várias teclas com vírgula.</p>';
    Object.keys(ACTION_LABELS).forEach(function (action) {
      html += '<div class="play-pedal-row">';
      html += '<label class="play-pedal-label">' + ACTION_LABELS[action] + '</label>';
      html += '<input type="text" class="form-control form-control-sm play-pedal-input" data-action="' + action + '" value="' +
        (map[action] || []).map(keyLabel).join(', ') + '">';
      html += '</div>';
    });
    html += '<div class="d-flex gap-2 mt-3 flex-wrap">';
    html += '<button type="button" class="btn btn-primary btn-sm" data-pedal-save>Salvar</button>';
    html += '<button type="button" class="btn btn-outline-secondary btn-sm" data-pedal-reset>Restaurar padrão</button>';
    html += '</div></div>';
    container.innerHTML = html;

    container.querySelector('[data-pedal-save]').addEventListener('click', function () {
      var next = cloneDefault();
      container.querySelectorAll('.play-pedal-input').forEach(function (inp) {
        var action = inp.getAttribute('data-action');
        var parts = String(inp.value || '').split(/[,;]+/).map(normalizeKeyInput).filter(Boolean);
        next[action] = parts;
      });
      saveMap(next);
      if (global.bootstrap && container.closest('.modal')) {
        var modalEl = container.closest('.modal');
        var inst = bootstrap.Modal.getInstance(modalEl);
        if (inst) inst.hide();
      }
    });

    container.querySelector('[data-pedal-reset]').addEventListener('click', function () {
      saveMap(cloneDefault());
      renderModal(container);
    });
  }

  global.SetSyncPedalConfig = {
    loadMap: loadMap,
    saveMap: saveMap,
    bindHandlers: bindHandlers,
    handleKeydown: handleKeydown,
    renderModal: renderModal,
    ACTION_LABELS: ACTION_LABELS,
  };
})(window);
