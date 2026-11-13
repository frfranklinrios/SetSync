/**
 * Anotações Pessoais de Palco (Personal Musician Cues) — Uníssono.
 * Inspirado em open-setlist & stage-binder.
 * Permite que cada músico salve colas privadas por música (ex: "Entrar no 2º refrão", "Solo em Am", "Dedilhado").
 */
(function (global) {
  'use strict';

  var STORAGE_PREFIX = 'setsync.cue.';

  function getStorageKey(cifraId) {
    var uid = (global.CURRENT_USER_ID || 'anon');
    return STORAGE_PREFIX + uid + '.' + String(cifraId);
  }

  function getCue(cifraId) {
    if (!cifraId) return '';
    try {
      return (localStorage.getItem(getStorageKey(cifraId)) || '').trim();
    } catch (e) {
      return '';
    }
  }

  function saveCue(cifraId, text) {
    if (!cifraId) return false;
    try {
      var clean = (text || '').trim();
      var key = getStorageKey(cifraId);
      if (clean) {
        localStorage.setItem(key, clean);
      } else {
        localStorage.removeItem(key);
      }
      renderCueBanner(cifraId);
      return true;
    } catch (e) {
      return false;
    }
  }

  function renderCueBanner(cifraId) {
    var banner = document.getElementById('play-personal-cue-banner');
    var textEl = document.getElementById('play-personal-cue-text');
    if (!banner || !textEl) return;

    var text = getCue(cifraId);
    if (text) {
      textEl.textContent = text;
      banner.classList.remove('d-none');
    } else {
      banner.classList.add('d-none');
    }
  }

  function promptEdit(cifraId, currentTitle) {
    var existing = getCue(cifraId);
    var modal = document.getElementById('play-cue-modal');
    var input = document.getElementById('play-cue-input');
    var titleEl = document.getElementById('play-cue-modal-title');

    if (modal && input) {
      if (titleEl && currentTitle) titleEl.textContent = currentTitle;
      input.value = existing;
      modal.classList.remove('d-none');
      input.focus();
    } else {
      var novo = window.prompt('Sua cola pessoal para esta música (ex: "Solo em Am", "Começar no chimbal"):', existing);
      if (novo !== null) {
        saveCue(cifraId, novo);
      }
    }
  }

  global.SetSyncPersonalCues = {
    getCue: getCue,
    saveCue: saveCue,
    renderCueBanner: renderCueBanner,
    promptEdit: promptEdit,
  };
})(window);
