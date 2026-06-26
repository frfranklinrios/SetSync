/**
 * Recursos avançados do Modo Tocar (seções, culto, loop, sync, offline).
 */
(function (global) {
  'use strict';

  var STORAGE_ONBOARD = 'setsync.play.onboarding.v1';
  var STORAGE_FOLLOW = 'setsync.play.followLeader.v1';
  var STORAGE_COUNTIN = 'setsync.play.countIn.v1';
  var STORAGE_OFFLINE_AUTO = 'setsync.play.offlineAuto.v1';

  function readPref(key, def) {
    try {
      var v = localStorage.getItem(key);
      return v != null && v !== '' ? v : def;
    } catch (e) {
      return def;
    }
  }

  function writePref(key, val) {
    try { localStorage.setItem(key, val); } catch (e) {}
  }

  function install(api, cfg) {
    if (!api || !cfg) return;
    cfg = cfg || {};

    var followLeader = cfg.autoFollowLeader || readPref(STORAGE_FOLLOW, '0') === '1';
    var countInBeats = parseInt(readPref(STORAGE_COUNTIN, '4'), 10) || 0;
    var loopStart = null;
    var loopEnd = null;
    var loopActive = false;
    var lastLeaderIdx = null;
    var es = null;

    if (global.SetSyncMetronome && global.SetSyncMetronome.setCountInDefault) {
      global.SetSyncMetronome.setCountInDefault(countInBeats);
    }

    // ── Evento / modo culto ─────────────────────────────
    var eventBar = document.getElementById('play-event-bar');
    if (eventBar && cfg.event) {
      var ev = cfg.event;
      var parts = [];
      if (ev.event_type) parts.push(ev.event_type);
      if (ev.starts_at) parts.push(ev.starts_at);
      if (ev.location) parts.push(ev.location);
      eventBar.querySelector('.play-event-title').textContent = ev.title || 'Evento';
      eventBar.querySelector('.play-event-meta').textContent = parts.join(' · ');
      if (ev.notes) {
        var notesEl = eventBar.querySelector('.play-event-notes');
        if (notesEl) {
          notesEl.textContent = ev.notes;
          notesEl.classList.remove('d-none');
        }
      }
      eventBar.classList.remove('d-none');
    }

    // ── Índice de seções ────────────────────────────────
    var sectionsPanel = document.getElementById('play-sections');
    var sectionsList = document.getElementById('play-sections-list');
    var sectionsBtn = document.getElementById('sections-btn');

    function collectSections() {
      var root = document.getElementById('cifra-content');
      if (!root) return [];
      var sel = '.cifra-section, .sp-section, .grade-part-title-play, .cs-section-label';
      var nodes = root.querySelectorAll(sel);
      var out = [];
      nodes.forEach(function (node, i) {
        var label = (node.textContent || '').trim();
        if (!label || label.length > 48) label = 'Seção ' + (i + 1);
        out.push({ label: label, el: node });
      });
      return out;
    }

    function renderSectionsNav() {
      if (!sectionsList) return;
      var sections = collectSections();
      sectionsList.innerHTML = '';
      if (!sections.length) {
        sectionsList.innerHTML = '<li class="play-sections-empty">Sem seções nesta música</li>';
        return;
      }
      sections.forEach(function (sec, idx) {
        var li = document.createElement('li');
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'play-sections-item';
        btn.textContent = sec.label;
        btn.addEventListener('click', function () {
          var wrap = api.scrollWrap();
          if (!wrap || !sec.el) return;
          var top = sec.el.getBoundingClientRect().top - wrap.getBoundingClientRect().top + wrap.scrollTop - 12;
          wrap.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
          if (sectionsPanel) sectionsPanel.classList.remove('open');
        });
        li.appendChild(btn);
        sectionsList.appendChild(li);
      });
    }

    function toggleSectionsPanel() {
      if (!sectionsPanel) return;
      var open = sectionsPanel.classList.toggle('open');
      if (open) renderSectionsNav();
    }

    if (sectionsBtn) sectionsBtn.addEventListener('click', toggleSectionsPanel);

    // ── Pré-visualização próxima música ─────────────────
    var nextPeek = document.getElementById('play-next-peek');

    function updateNextPeek(idx) {
      if (!nextPeek || !api.getCifras) return;
      var list = api.getCifras();
      if (idx + 1 >= list.length) {
        nextPeek.classList.add('d-none');
        return;
      }
      var next = list[idx + 1];
      nextPeek.querySelector('.play-next-peek-title').textContent = next.titulo || '—';
      nextPeek.querySelector('.play-next-peek-artist').textContent = next.artista || '';
      nextPeek.classList.remove('d-none');
    }

    // ── Loop de trecho ──────────────────────────────────
    var loopBtn = document.getElementById('loop-btn');
    var loopBar = document.getElementById('play-loop-bar');

    function updateLoopBar() {
      if (!loopBar) return;
      var lbl = loopBar.querySelector('.play-loop-status');
      if (!lbl) return;
      if (loopStart == null) {
        lbl.textContent = 'Toque A para marcar início do loop';
      } else if (loopEnd == null) {
        lbl.textContent = 'Toque B para marcar fim do loop';
      } else {
        lbl.textContent = loopActive ? 'Loop ativo — toque para desligar' : 'Loop pronto — toque para ligar';
      }
      loopBar.classList.toggle('d-none', !loopBtn || !loopBtn.classList.contains('pb-on'));
    }

    function markLoopPoint(which) {
      var wrap = api.scrollWrap();
      if (!wrap) return;
      if (which === 'a') {
        loopStart = wrap.scrollTop;
        loopEnd = null;
        loopActive = false;
      } else {
        loopEnd = wrap.scrollTop;
        if (loopEnd < loopStart) {
          var tmp = loopStart;
          loopStart = loopEnd;
          loopEnd = tmp;
        }
        loopActive = true;
      }
      updateLoopBar();
    }

    function checkLoopScroll() {
      if (!loopActive || loopStart == null || loopEnd == null) return;
      var wrap = api.scrollWrap();
      if (!wrap) return;
      if (wrap.scrollTop >= loopEnd - 4) {
        wrap.scrollTop = loopStart;
      }
    }

    if (loopBtn) {
      loopBtn.addEventListener('click', function () {
        loopBtn.classList.toggle('pb-on');
        if (!loopBtn.classList.contains('pb-on')) {
          loopStart = loopEnd = null;
          loopActive = false;
        }
        updateLoopBar();
      });
    }
    var loopMarkA = document.getElementById('loop-mark-a');
    var loopMarkB = document.getElementById('loop-mark-b');
    if (loopMarkA) loopMarkA.addEventListener('click', function () { markLoopPoint('a'); });
    if (loopMarkB) loopMarkB.addEventListener('click', function () { markLoopPoint('b'); });
    var loopToggle = document.getElementById('loop-toggle-active');
    if (loopToggle) {
      loopToggle.addEventListener('click', function () {
        if (loopStart != null && loopEnd != null) {
          loopActive = !loopActive;
          updateLoopBar();
        }
      });
    }

    var scrollEl = api.scrollWrap();
    if (scrollEl) {
      scrollEl.addEventListener('scroll', function () {
        checkLoopScroll();
      }, { passive: true });
    }

    // ── Sincronização entre membros ─────────────────────
    var syncBtn = document.getElementById('sync-follow-btn');
    var syncBadge = document.getElementById('sync-leader-badge');

    function updateSyncUi() {
      if (syncBtn) syncBtn.classList.toggle('pb-on', followLeader);
    }

    function publishPlayState(idx) {
      if (!cfg.playStateUrl || !api.getCifras) return;
      var list = api.getCifras();
      var song = list[idx];
      if (!song) return;
      fetch(cfg.playStateUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-CSRFToken': global.csrfToken || '',
        },
        body: JSON.stringify({
          setlist_id: cfg.setlistId,
          song_index: idx,
          cifra_id: song.id,
        }),
      }).catch(function () {});
    }

    function connectRealtime() {
      if (!cfg.bandId || !global.EventSource) return;
      var url = '/api/realtime/band/' + encodeURIComponent(cfg.bandId) + '/events';
      if (es) { try { es.close(); } catch (e) {} }
      es = new EventSource(url);
      es.onmessage = function (e) {
        try {
          var payload = JSON.parse(e.data);
          if (!payload || payload.event !== 'play_sync') return;
          var data = payload.data || {};
          if (cfg.setlistId != null && data.setlist_id != null &&
              String(data.setlist_id) !== String(cfg.setlistId)) return;
          if (data.leader_id && cfg.userId && String(data.leader_id) === String(cfg.userId)) return;
          lastLeaderIdx = data.song_index;
          if (syncBadge) {
            syncBadge.textContent = 'Líder: ' + (data.leader_name || 'banda') + ' · música ' + (data.song_index + 1);
            syncBadge.classList.remove('d-none');
          }
          if (followLeader && typeof data.song_index === 'number' && api.goTo) {
            api.goTo(data.song_index, { fromSync: true });
          }
        } catch (err) { /* ignore */ }
      };
      es.onerror = function () {
        try { es.close(); } catch (e2) {}
        es = null;
        setTimeout(connectRealtime, 10000);
      };
    }

    if (cfg.autoFollowLeader) {
      writePref(STORAGE_FOLLOW, '1');
      if (syncBtn) updateSyncUi();
    }
    if (syncBtn) {
      syncBtn.addEventListener('click', function () {
        followLeader = !followLeader;
        writePref(STORAGE_FOLLOW, followLeader ? '1' : '0');
        updateSyncUi();
        if (followLeader && lastLeaderIdx != null && api.goTo) {
          api.goTo(lastLeaderIdx, { fromSync: true });
        }
      });
      updateSyncUi();
    }
    if (cfg.bandId) connectRealtime();

    // ── Offline (auto-download da setlist) ───────────────
    var offlineBanner = document.getElementById('play-offline-banner');
    var offlineBtn = document.getElementById('play-offline-download');
    var offlineStatus = document.getElementById('play-offline-status');
    var offlineAutoKey = cfg.setlistId
      ? ('sl:' + cfg.setlistId)
      : (cfg.bandId ? ('band:' + cfg.bandId) : '');

    function packIsFresh(pack) {
      if (!pack || !Array.isArray(pack.cifras)) return false;
      if (cfg.setlistId && pack.setlist_id && String(pack.setlist_id) !== String(cfg.setlistId)) {
        return false;
      }
      if (cfg.songCount && pack.cifras.length < cfg.songCount) return false;
      return pack.cifras.length > 0;
    }

    function updateOfflineStatus(pack, downloading) {
      if (!offlineStatus) return;
      if (downloading) {
        offlineStatus.textContent = 'Baixando…';
        return;
      }
      if (pack && packIsFresh(pack)) {
        offlineStatus.textContent = pack.cifras.length + '/' + (cfg.songCount || pack.cifras.length) + ' prontas';
      } else {
        offlineStatus.textContent = '';
      }
    }

    function downloadOfflinePack(silent) {
      if (!cfg.offlinePackUrl || !cfg.bandId || !global.SetSyncOfflineStore) {
        return Promise.resolve(null);
      }
      if (!SetSyncOfflineStore.isSupported()) {
        if (!silent) alert('Seu navegador não suporta armazenamento offline.');
        return Promise.resolve(null);
      }
      if (offlineBtn) offlineBtn.disabled = true;
      updateOfflineStatus(null, true);
      if (offlineBanner) {
        offlineBanner.classList.remove('d-none');
        offlineBanner.querySelector('.play-offline-msg').textContent = 'Preparando repertório offline…';
      }
      return fetch(cfg.offlinePackUrl, {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      })
        .then(function (r) {
          if (!r.ok) throw new Error('http ' + r.status);
          return r.json();
        })
        .then(function (data) {
          data.band_id = String(cfg.bandId);
          data.band_name = data.band_name || cfg.bandName || cfg.bandId;
          if (cfg.setlistId) data.setlist_id = cfg.setlistId;
          return SetSyncOfflineStore.savePack(String(cfg.bandId), data);
        })
        .then(function () {
          return SetSyncOfflineStore.getPack(String(cfg.bandId));
        })
        .then(function (pack) {
          writePref(STORAGE_OFFLINE_AUTO, offlineAutoKey);
          if (offlineBanner) {
            offlineBanner.classList.add('d-none');
          }
          updateOfflineStatus(pack, false);
          return pack;
        })
        .catch(function () {
          if (offlineBanner) {
            offlineBanner.classList.remove('d-none');
            offlineBanner.querySelector('.play-offline-msg').textContent =
              'Não foi possível baixar offline. Toque em Baixar ou verifique a conexão.';
          }
          return null;
        })
        .finally(function () {
          if (offlineBtn) offlineBtn.disabled = false;
        });
    }

    function checkOfflinePack() {
      if (!cfg.bandId || !global.SetSyncOfflineStore || !offlineBanner) return;
      if (global.navigator && global.navigator.onLine === false) {
        offlineBanner.classList.remove('d-none');
        offlineBanner.querySelector('.play-offline-msg').textContent =
          'Sem conexão — usando pacote salvo neste dispositivo.';
        SetSyncOfflineStore.getPack(String(cfg.bandId)).then(function (pack) {
          updateOfflineStatus(pack, false);
        });
        return;
      }
      SetSyncOfflineStore.getPack(String(cfg.bandId)).then(function (pack) {
        if (packIsFresh(pack)) {
          updateOfflineStatus(pack, false);
          return;
        }
        offlineBanner.classList.remove('d-none');
        offlineBanner.querySelector('.play-offline-msg').textContent =
          'Baixando repertório para o culto…';
        if (readPref(STORAGE_OFFLINE_AUTO, '') !== offlineAutoKey) {
          downloadOfflinePack(true);
        } else {
          offlineBanner.querySelector('.play-offline-msg').textContent =
            'Repertório offline desatualizado — toque em Baixar.';
        }
      }).catch(function () {});
    }

    if (offlineBtn && cfg.bandId) {
      offlineBtn.addEventListener('click', function () {
        downloadOfflinePack(false);
      });
    }
    if (cfg.bandId && cfg.offlinePackUrl) {
      SetSyncOfflineStore.getPack(String(cfg.bandId)).then(function (pack) {
        if (!packIsFresh(pack)) {
          downloadOfflinePack(true);
        } else {
          updateOfflineStatus(pack, false);
        }
      }).catch(function () {
        downloadOfflinePack(true);
      });
    }
    checkOfflinePack();
    global.addEventListener('online', checkOfflinePack);
    global.addEventListener('offline', checkOfflinePack);

    // ── Notas de palco ──────────────────────────────────
    var stageNoteEl = document.getElementById('play-stage-note');
    var stageNoteText = document.getElementById('play-stage-note-text');
    var stageNoteTimer = null;

    function showStageNote(song) {
      if (!stageNoteEl || !stageNoteText) return;
      clearTimeout(stageNoteTimer);
      var notes = song && song.play_notes ? String(song.play_notes).trim() : '';
      if (!notes) {
        stageNoteEl.classList.add('d-none');
        return;
      }
      stageNoteText.textContent = notes;
      stageNoteEl.classList.remove('d-none');
      stageNoteTimer = setTimeout(function () {
        stageNoteEl.classList.add('d-none');
      }, 5200);
    }

    function savePlayNotes(song, notes) {
      if (!cfg.playNotesUrlTpl || !song || !song.id) return Promise.resolve();
      var url = cfg.playNotesUrlTpl.replace('__ID__', encodeURIComponent(song.id));
      var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
      if (global.csrfToken) headers['X-CSRFToken'] = global.csrfToken;
      return fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: headers,
        body: JSON.stringify({ play_notes: notes }),
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!data || !data.ok) throw new Error((data && data.error) || 'Falha ao salvar');
          song.play_notes = notes;
          if (api.getCifras) {
            api.getCifras().forEach(function (c) {
              if (c.id === song.id) c.play_notes = notes;
            });
          }
          showStageNote(song);
        });
    }

    var stageNoteEdit = document.getElementById('play-stage-note-edit');
    if (stageNoteEdit && cfg.canEdit) {
      stageNoteEdit.addEventListener('click', function () {
        var song = api.getCurrent ? api.getCurrent() : null;
        if (!song) return;
        var cur = song.play_notes || '';
        var next = global.prompt('Notas de palco para esta música:', cur);
        if (next == null) return;
        savePlayNotes(song, String(next).trim()).catch(function (err) {
          alert(err.message || 'Não foi possível salvar.');
        });
      });
    }

    // ── Onboarding atalhos ──────────────────────────────
    var onboard = document.getElementById('play-onboard-overlay');
    if (onboard && readPref(STORAGE_ONBOARD, '') !== '1') {
      onboard.classList.remove('d-none');
      var dismiss = onboard.querySelector('[data-onboard-dismiss]');
      if (dismiss) {
        dismiss.addEventListener('click', function () {
          writePref(STORAGE_ONBOARD, '1');
          onboard.classList.add('d-none');
          if (global.SetSyncPedalWizard && !SetSyncPedalWizard.isDone()) {
            setTimeout(function () { SetSyncPedalWizard.show(false); }, 400);
          }
        });
      }
    } else if (global.SetSyncPedalWizard && !SetSyncPedalWizard.isDone()) {
      setTimeout(function () { SetSyncPedalWizard.show(false); }, 800);
    }

    // Count-in toggle in onboarding / settings
    var countInSel = document.getElementById('countin-select');
    if (countInSel) {
      countInSel.value = String(countInBeats);
      countInSel.addEventListener('change', function () {
        countInBeats = parseInt(countInSel.value, 10) || 0;
        writePref(STORAGE_COUNTIN, String(countInBeats));
        if (global.SetSyncMetronome && global.SetSyncMetronome.setCountInDefault) {
          global.SetSyncMetronome.setCountInDefault(countInBeats);
        }
      });
    }

    // ── Hooks na API do play mode ───────────────────────
    var origGoTo = api.goTo;
    api.goTo = function (idx, opts) {
      opts = opts || {};
      origGoTo(idx);
      if (!opts.fromSync) publishPlayState(idx);
      updateNextPeek(idx);
      setTimeout(renderSectionsNav, 120);
      loopStart = loopEnd = null;
      loopActive = false;
      updateLoopBar();
      var song = api.getCurrent ? api.getCurrent() : null;
      if (song && global.SetSyncMetronome && global.SetSyncMetronome.updateSongContext) {
        global.SetSyncMetronome.updateSongContext(song);
      }
      showStageNote(song);
    };

    var origRenderHtml = api.renderHtml;
    if (origRenderHtml) {
      api.renderHtml = function (html) {
        origRenderHtml(html);
        setTimeout(renderSectionsNav, 80);
      };
    }

    if (global.goTo) global.goTo = api.goTo;
    if (global.nextSong) {
      global.nextSong = function () { api.goTo(api.getCurrentIndex() + 1); };
    }
    if (global.prevSong) {
      global.prevSong = function () { api.goTo(api.getCurrentIndex() - 1); };
    }

    if (global.SetSyncPedalConfig) {
      global.SetSyncPedalConfig.bindHandlers({
        pageDown: global.tapScrollDown,
        pageUp: global.tapScrollUp,
        prevSong: function () { api.goTo(api.getCurrentIndex() - 1); },
        nextSong: function () { api.goTo(api.getCurrentIndex() + 1); },
        toggleScroll: global.toggleScroll,
        toggleMetronome: global.toggleMetronome,
        toggleDraw: global.toggleDraw,
        toggleFullscreen: global.toggleFullscreen,
      });
    }

    updateNextPeek(api.getCurrentIndex ? api.getCurrentIndex() : 0);

    global.SetSyncPlayFeatures = {
      renderSectionsNav: renderSectionsNav,
      toggleSectionsPanel: toggleSectionsPanel,
      onPedalConfigured: function () {
        flashPedalOk();
      },
    };

    function flashPedalOk() {
      var el = document.getElementById('kbd-hint');
      if (!el) return;
      var prev = el.textContent;
      el.textContent = 'Pedal configurado! Teste com as bordas da tela.';
      el.classList.add('show');
      setTimeout(function () {
        el.textContent = prev;
        el.classList.remove('show');
      }, 3200);
    }

    var bootSong = api.getCurrent ? api.getCurrent() : null;
    if (bootSong) showStageNote(bootSong);
  }

  function waitAndInstall() {
    var cfgEl = document.getElementById('play-features-config');
  var api = global.SetSyncPlayApi;
    if (!api || !cfgEl) {
      setTimeout(waitAndInstall, 40);
      return;
    }
    var cfg = {};
    try { cfg = JSON.parse(cfgEl.textContent || '{}'); } catch (e) {}
    install(api, cfg);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitAndInstall);
  } else {
    waitAndInstall();
  }
})(window);
