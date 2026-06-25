/**
 * Assistente de configuração de pedal Bluetooth no Modo Tocar.
 */
(function (global) {
  'use strict';

  var STORAGE_KEY = 'setsync.play.pedalWizard.v1';
  var step = 0;
  var captured = { pageDown: null, pageUp: null, nextSong: null, prevSong: null };
  var modalEl = null;
  var keyHandler = null;

  function readDone() {
    try { return localStorage.getItem(STORAGE_KEY) === '1'; } catch (e) { return false; }
  }

  function writeDone() {
    try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
  }

  function stepLabels() {
    return [
      'Conecte o pedal via Bluetooth nas configurações do tablet/celular.',
      'Pressione o pedal da DIREITA (próxima página).',
      'Pressione o pedal da ESQUERDA (página anterior).',
      'Pressione o pedal para PRÓXIMA música (opcional — Enter para pular).',
      'Pressione o pedal para MÚSICA ANTERIOR (opcional — Enter para pular).',
      'Pronto! Teste com as setas ou pedais.',
    ];
  }

  function renderStep() {
    if (!modalEl) return;
    var title = modalEl.querySelector('.play-pedal-wizard-title');
    var body = modalEl.querySelector('.play-pedal-wizard-body');
    var prog = modalEl.querySelector('.play-pedal-wizard-progress');
    var labels = stepLabels();
    if (title) title.textContent = 'Configurar pedal (' + (Math.min(step, labels.length - 1) + 1) + '/' + labels.length + ')';
    if (body) body.textContent = labels[Math.min(step, labels.length - 1)] || '';
    if (prog) {
      var pct = Math.round(((Math.min(step, labels.length - 1) + 1) / labels.length) * 100);
      prog.style.width = pct + '%';
    }
    var skipBtn = modalEl.querySelector('[data-pedal-wizard-skip]');
    if (skipBtn) skipBtn.style.display = (step >= 3 && step <= 4) ? 'inline-block' : 'none';
  }

  function saveAndClose() {
    if (!global.SetSyncPedalConfig) return;
    var map = SetSyncPedalConfig.loadMap();
    if (captured.pageDown) map.pageDown = [captured.pageDown];
    if (captured.pageUp) map.pageUp = [captured.pageUp];
    if (captured.nextSong) map.nextSong = [captured.nextSong];
    if (captured.prevSong) map.prevSong = [captured.prevSong];
    SetSyncPedalConfig.saveMap(map);
    writeDone();
    hide();
    if (global.SetSyncPlayFeatures && typeof global.SetSyncPlayFeatures.onPedalConfigured === 'function') {
      global.SetSyncPlayFeatures.onPedalConfigured();
    }
  }

  function onKey(e) {
    if (!modalEl || modalEl.classList.contains('d-none')) return;
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      writeDone();
      hide();
      return;
    }
    if (step >= 3 && step <= 4 && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      step += 1;
      if (step >= stepLabels().length - 1) saveAndClose();
      else renderStep();
      return;
    }
    if (step === 1) {
      e.preventDefault();
      captured.pageDown = e.key;
      step = 2;
      renderStep();
      return;
    }
    if (step === 2) {
      e.preventDefault();
      captured.pageUp = e.key;
      step = 3;
      renderStep();
      return;
    }
    if (step === 3) {
      e.preventDefault();
      captured.nextSong = e.key;
      step = 4;
      renderStep();
      return;
    }
    if (step === 4) {
      e.preventDefault();
      captured.prevSong = e.key;
      step = 5;
      renderStep();
      return;
    }
    if (step === 5) {
      e.preventDefault();
      saveAndClose();
    }
  }

  function show(force) {
    modalEl = document.getElementById('play-pedal-wizard');
    if (!modalEl) return;
    if (!force && readDone()) return;
    step = 0;
    captured = { pageDown: null, pageUp: null, nextSong: null, prevSong: null };
    modalEl.classList.remove('d-none');
    renderStep();
    if (!keyHandler) {
      keyHandler = onKey;
      document.addEventListener('keydown', keyHandler, true);
    }
  }

  function hide() {
    if (!modalEl) return;
    modalEl.classList.add('d-none');
    if (keyHandler) {
      document.removeEventListener('keydown', keyHandler, true);
      keyHandler = null;
    }
  }

  function bindUi() {
    modalEl = document.getElementById('play-pedal-wizard');
    if (!modalEl) return;
    var startBtn = document.getElementById('pedal-wizard-open-btn');
    if (startBtn) {
      startBtn.addEventListener('click', function () { show(true); });
    }
    var nextBtn = modalEl.querySelector('[data-pedal-wizard-next]');
    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        if (step === 0) {
          step = 1;
          renderStep();
          return;
        }
        if (step >= stepLabels().length - 1) saveAndClose();
      });
    }
    var skipBtn = modalEl.querySelector('[data-pedal-wizard-skip]');
    if (skipBtn) {
      skipBtn.addEventListener('click', function () {
        step += 1;
        if (step >= stepLabels().length - 1) saveAndClose();
        else renderStep();
      });
    }
    var dismissBtn = modalEl.querySelector('[data-pedal-wizard-dismiss]');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', function () {
        writeDone();
        hide();
      });
    }
  }

  global.SetSyncPedalWizard = {
    show: show,
    hide: hide,
    bindUi: bindUi,
    isDone: readDone,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindUi);
  } else {
    bindUi();
  }
})(window);
