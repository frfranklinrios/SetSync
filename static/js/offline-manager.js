/**
 * UI e download de pacotes offline (Fase 1 roadmap).
 */
(function (global) {
  'use strict';

  var store = global.SetSyncOfflineStore;

  function fmtBytes(n) {
    n = Number(n) || 0;
    if (n < 1024) return n + ' B';
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
    return (n / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function fmtDate(iso) {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('pt-BR');
    } catch (e) {
      return iso;
    }
  }

  function setProgress(panel, pct, label) {
    var bar = panel.querySelector('.offline-progress-bar');
    var txt = panel.querySelector('.offline-progress-text');
    if (bar) bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
    if (txt) txt.textContent = label || '';
  }

  function renderList(panel) {
    var listEl = panel.querySelector('.offline-pack-list');
    if (!listEl || !store) return;
    store.listPacks().then(function (packs) {
      if (!packs || !packs.length) {
        listEl.innerHTML = '<p class="text-muted small mb-0">Nenhum repertório salvo neste dispositivo.</p>';
        return;
      }
      listEl.innerHTML = packs.map(function (p) {
        var size = new Blob([JSON.stringify(p)]).size;
        return (
          '<div class="offline-pack-item">' +
          '<div><strong>' + (p.band_name || p.band_id) + '</strong>' +
          '<div class="text-muted" style="font-size:var(--text-sm)">' +
          (p.cifras ? p.cifras.length : 0) + ' músicas · ' + fmtBytes(size) +
          ' · ' + fmtDate(p.saved_at) + '</div></div>' +
          '<button type="button" class="btn btn-sm btn-outline-danger offline-del" data-band-id="' +
          p.band_id + '">Remover</button></div>'
        );
      }).join('');
      listEl.querySelectorAll('.offline-del').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var bid = btn.getAttribute('data-band-id');
          if (!bid || !confirm('Remover pacote offline desta banda?')) return;
          store.deletePack(bid).then(function () { renderList(panel); });
        });
      });
    });
  }

  function downloadBand(bandId, bandName, panel) {
    if (!store || !store.isSupported()) {
      alert('Seu navegador não suporta armazenamento offline (IndexedDB).');
      return Promise.reject(new Error('no-idb'));
    }
    setProgress(panel, 5, 'Baixando repertório…');
    return fetch('/cifras/band/' + encodeURIComponent(bandId) + '/offline-pack.json', {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Falha ao baixar (' + res.status + ')');
        setProgress(panel, 45, 'Processando…');
        return res.json();
      })
      .then(function (data) {
        data.band_name = data.band_name || bandName || bandId;
        setProgress(panel, 70, 'Salvando no dispositivo…');
        return store.savePack(bandId, data);
      })
      .then(function () {
        setProgress(panel, 100, 'Pronto para uso offline.');
        renderList(panel);
        if (global.navigator && global.navigator.serviceWorker && global.navigator.serviceWorker.controller) {
          global.navigator.serviceWorker.controller.postMessage({
            type: 'offline-pack-saved',
            bandId: String(bandId),
          });
        }
      })
      .catch(function (err) {
        setProgress(panel, 0, 'Erro: ' + (err.message || String(err)));
        throw err;
      });
  }

  function bindPanel(panel) {
    if (!panel || panel.dataset.offlineBound) return;
    panel.dataset.offlineBound = '1';
    var bandId = panel.getAttribute('data-band-id');
    var bandName = panel.getAttribute('data-band-name') || '';
    var btn = panel.querySelector('[data-offline-download]');
    if (btn) {
      btn.addEventListener('click', function () {
        btn.disabled = true;
        downloadBand(bandId, bandName, panel).finally(function () {
          btn.disabled = false;
        });
      });
    }
    renderList(panel);
  }

  function init() {
    document.querySelectorAll('[data-offline-panel]').forEach(bindPanel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  global.SetSyncOffline = {
    downloadBand: downloadBand,
    getPack: store ? store.getPack : function () { return Promise.resolve(null); },
    listPacks: store ? store.listPacks : function () { return Promise.resolve([]); },
  };
})(window);
