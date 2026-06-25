/**
 * SSE — sincronia em tempo real por banda (Fase 1 roadmap).
 */
(function (global) {
  'use strict';

  var sources = {};

  function toast(msg) {
    if (global.SetSyncNotifications && typeof global.SetSyncNotifications.toast === 'function') {
      global.SetSyncNotifications.toast(msg);
      return;
    }
    var el = document.createElement('div');
    el.className = 'alert alert-info shadow-sm position-fixed';
    el.style.cssText = 'bottom:1rem;right:1rem;z-index:9999;max-width:320px;font-size:0.9rem';
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 4500);
  }

  function handleEvent(bandId, payload) {
    var ev = payload && payload.event;
    var data = (payload && payload.data) || {};
    if (!ev) return;
    if (ev === 'cifra_updated' || ev === 'cifra_imported') {
      toast('Cifra atualizada: ' + (data.titulo || 'música'));
    } else if (ev === 'cifra_deleted') {
      toast('Cifra removida da banda.');
    } else if (ev === 'cifra_published') {
      toast('Nova versão publicada: ' + (data.titulo || 'música'));
    }
    document.dispatchEvent(new CustomEvent('setsync:realtime', {
      detail: { bandId: bandId, event: ev, data: data },
    }));
    var cifraId = data.cifra_id;
    var onPage = document.querySelector('[data-cifra-id]');
    var pageId = onPage ? onPage.getAttribute('data-cifra-id') : '';
    if (cifraId && pageId && pageId === String(cifraId)) {
      setTimeout(function () { global.location.reload(); }, 800);
    }
  }

  function connect(bandId) {
    if (!bandId || !global.EventSource) return;
    if (sources[bandId]) return;
    var url = '/api/realtime/band/' + encodeURIComponent(bandId) + '/events';
    var es = new EventSource(url);
    sources[bandId] = es;
    es.onmessage = function (e) {
      try {
        handleEvent(bandId, JSON.parse(e.data));
      } catch (err) { /* ignore */ }
    };
    es.onerror = function () {
      es.close();
      delete sources[bandId];
      setTimeout(function () { connect(bandId); }, 8000);
    };
  }

  function init() {
    var el = document.querySelector('[data-realtime-band]');
    if (el) connect(el.getAttribute('data-realtime-band'));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  global.SetSyncRealtime = { connect: connect };
})(window);
