/**
 * Preferências e utilitários puros do Modo Tocar (sem Jinja).
 */
(function (global) {
  'use strict';

  function decodeBase64Utf8(b64) {
    var bin = atob(b64);
    if (typeof TextDecoder !== 'undefined') {
      var bytes = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      return new TextDecoder('utf-8').decode(bytes);
    }
    try {
      return decodeURIComponent(escape(bin));
    } catch (e) {
      return bin;
    }
  }

  function decodeCifrasPayload(elId) {
    var el = document.getElementById(elId || 'cifras-data');
    if (!el) return [];
    var raw = (el.textContent || '').trim();
    if (!raw) return [];
    try {
      return JSON.parse(decodeBase64Utf8(raw));
    } catch (b64Err) {
      try {
        return JSON.parse(raw);
      } catch (jsonErr) {
        console.error('Uníssono: falha ao ler cifras do modo tocar', b64Err, jsonErr);
        return [];
      }
    }
  }

  function showPlayBootError(msg) {
    var el = document.getElementById('cifra-content');
    if (!el) return;
    if (el.innerHTML && el.innerHTML.trim()) return;
    var safe = String(msg || '')
      .replace(/&/g, '\u0026amp;')
      .replace(/</g, '\u003c')
      .replace(/>/g, '\u003e');
    el.innerHTML =
      '<div class="grade-empty-play" style="padding:2rem 4vw;color:#94a3b8;font-size:var(--text-base);">' +
      safe +
      '</div>';
  }

  function readPlayPref(key) {
    try {
      var localVal = localStorage.getItem(key);
      if (localVal) return localVal;
    } catch (e) {}
    try {
      return sessionStorage.getItem(key) || '';
    } catch (e2) {
      return '';
    }
  }

  function writePlayPref(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (e) {}
    try {
      sessionStorage.setItem(key, val);
    } catch (e2) {}
  }

  function clearPlayPref(key) {
    try {
      localStorage.removeItem(key);
    } catch (e) {}
    try {
      sessionStorage.removeItem(key);
    } catch (e2) {}
  }

  function readSessionPref(key, def) {
    try {
      var val = sessionStorage.getItem(key);
      return val != null && val !== '' ? val : def !== undefined ? def : '';
    } catch (e) {
      return def !== undefined ? def : '';
    }
  }

  function writeSessionPref(key, val) {
    try {
      sessionStorage.setItem(key, val);
    } catch (e) {}
  }

  function removeSessionPref(key) {
    try {
      sessionStorage.removeItem(key);
    } catch (e) {}
  }

  function readBootConfig(elId) {
    var el = document.getElementById(elId || 'play-boot-config');
    if (!el) return {};
    try {
      return JSON.parse(el.textContent || '{}') || {};
    } catch (e) {
      return {};
    }
  }

  function tplUrl(tpl, id) {
    if (!tpl) return '';
    return String(tpl).replace('__ID__', encodeURIComponent(id));
  }

  global.SetSyncPlayBoot = {
    decodeBase64Utf8: decodeBase64Utf8,
    decodeCifrasPayload: decodeCifrasPayload,
    showPlayBootError: showPlayBootError,
    readPlayPref: readPlayPref,
    writePlayPref: writePlayPref,
    clearPlayPref: clearPlayPref,
    readSessionPref: readSessionPref,
    writeSessionPref: writeSessionPref,
    removeSessionPref: removeSessionPref,
    readBootConfig: readBootConfig,
    tplUrl: tplUrl,
  };
})(window);
