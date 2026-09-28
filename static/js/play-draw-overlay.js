/**
 * Anotações livres (draw-over) — local + conta (versão pessoal de palco).
 * Canvas cobre o conteúdo integral de #cifra-scroll (não só a viewport).
 */
(function (global) {
  'use strict';

  var canvas = null;
  var ctx = null;
  var drawing = false;
  var strokes = [];
  var current = null;
  var cifraId = null;
  var enabled = false;
  var tool = 'pen';
  var saveTimer = null;
  var apiUrl = null;
  var remoteLoaded = false;
  var wrapEl = null;
  var resizeObserver = null;

  var PEN_WIDTH = 2.5;
  var ERASER_WIDTH = 20;
  var PEN_COLOR = 'rgba(251, 146, 60, 0.9)';

  function resolvePenColor() {
    var light = document.documentElement.getAttribute('data-theme') === 'light';
    return light ? 'rgba(37, 99, 235, 0.9)' : 'rgba(251, 146, 60, 0.9)';
  }

  function syncPenColor() {
    PEN_COLOR = resolvePenColor();
    redraw();
  }

  function storageKey(id) {
    return 'setsync-draw:' + String(id || 'unknown');
  }

  function loadLocal(id) {
    try {
      var raw = global.localStorage.getItem(storageKey(id));
      strokes = raw ? JSON.parse(raw) : [];
      strokes.forEach(function (s) {
        if (!s.tool) s.tool = 'pen';
      });
    } catch (e) {
      strokes = [];
    }
  }

  function saveLocal() {
    if (!cifraId) return;
    try {
      global.localStorage.setItem(storageKey(cifraId), JSON.stringify(strokes));
    } catch (e) { /* quota */ }
  }

  function scheduleRemoteSave() {
    if (!apiUrl || !cifraId) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
      var body = JSON.stringify({ strokes: strokes });
      fetch(apiUrl, {
        method: 'PUT',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: body,
      }).catch(function () { /* offline */ });
    }, 600);
  }

  function save() {
    saveLocal();
    scheduleRemoteSave();
  }

  function loadRemote(id) {
    if (!apiUrl) return Promise.resolve();
    var requestId = id;
    return fetch(apiUrl, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
      .then(function (r) {
        if (!r.ok) return null;
        return r.json();
      })
      .then(function (data) {
        if (String(requestId) !== String(cifraId)) return;
        if (!data || !Array.isArray(data.strokes)) return;
        // Não apagar traços locais com [] remoto (race com PUT ou ainda não syncado).
        if (data.strokes.length === 0 && strokes.length > 0) {
          scheduleRemoteSave();
          return;
        }
        strokes = data.strokes;
        strokes.forEach(function (s) {
          if (!s.tool) s.tool = 'pen';
        });
        saveLocal();
        redraw();
      })
      .catch(function () { /* offline */ });
  }

  function resize() {
    if (!canvas) return;
    var parent = wrapEl || canvas.parentElement;
    if (!parent) return;
    // Cobrir o conteúdo rolável inteiro — inset:0 sozinho fica só na viewport.
    var w = Math.max(parent.scrollWidth || 0, parent.clientWidth || 0, 1);
    var h = Math.max(parent.scrollHeight || 0, parent.clientHeight || 0, 1);
    var changed = canvas.width !== w || canvas.height !== h;
    if (changed) {
      canvas.width = w;
      canvas.height = h;
    }
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    if (changed) redraw();
  }

  function applyStrokeStyle(stroke) {
    var isEraser = stroke.tool === 'eraser';
    ctx.globalCompositeOperation = isEraser ? 'destination-out' : 'source-over';
    ctx.strokeStyle = isEraser ? 'rgba(0,0,0,1)' : PEN_COLOR;
    ctx.lineWidth = stroke.width || (isEraser ? ERASER_WIDTH : PEN_WIDTH);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  }

  function drawStrokePath(stroke) {
    if (!stroke.points || stroke.points.length < 2) return;
    applyStrokeStyle(stroke);
    ctx.beginPath();
    ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
    for (var i = 1; i < stroke.points.length; i++) {
      ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
    }
    ctx.stroke();
  }

  function redraw() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokes.forEach(drawStrokePath);
    if (current && current.points && current.points.length > 1) {
      drawStrokePath(current);
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  function pos(ev) {
    var r = canvas.getBoundingClientRect();
    var t = ev.touches && ev.touches[0] ? ev.touches[0] : ev;
    var sx = canvas.width / Math.max(r.width, 1);
    var sy = canvas.height / Math.max(r.height, 1);
    return {
      x: (t.clientX - r.left) * sx,
      y: (t.clientY - r.top) * sy,
    };
  }

  function onStart(ev) {
    if (!enabled) return;
    ev.preventDefault();
    drawing = true;
    current = {
      points: [pos(ev)],
      tool: tool,
      width: tool === 'eraser' ? ERASER_WIDTH : PEN_WIDTH,
    };
  }

  function onMove(ev) {
    if (!drawing || !enabled) return;
    ev.preventDefault();
    current.points.push(pos(ev));
    redraw();
  }

  function onEnd() {
    if (!drawing) return;
    drawing = false;
    if (current && current.points.length > 1) {
      strokes.push(current);
      save();
    }
    current = null;
    redraw();
  }

  function clear() {
    if (strokes.length && !global.confirm('Limpar todas as anotações desta música?')) {
      return false;
    }
    strokes = [];
    current = null;
    save();
    redraw();
    return true;
  }

  function setTool(next) {
    tool = next === 'eraser' ? 'eraser' : 'pen';
    syncToolbar();
    return tool;
  }

  function syncChrome() {
    try {
      document.body.classList.toggle('play-drawing', enabled);
    } catch (e) { /* */ }
  }

  function syncToolbar() {
    var wrap = document.getElementById('draw-tools');
    if (wrap) wrap.classList.toggle('draw-tools-visible', enabled);
    var penBtn = document.getElementById('draw-pen-btn');
    var eraserBtn = document.getElementById('draw-eraser-btn');
    if (penBtn) penBtn.classList.toggle('pb-on', enabled && tool === 'pen');
    if (eraserBtn) eraserBtn.classList.toggle('pb-on', enabled && tool === 'eraser');
    if (canvas) {
      canvas.classList.toggle('play-draw-eraser', enabled && tool === 'eraser');
      canvas.classList.toggle('play-draw-pen', enabled && tool === 'pen');
    }
  }

  function mount(wrapId, id) {
    cifraId = id;
    loadLocal(id);
    remoteLoaded = false;
    wrapEl = document.getElementById(wrapId);
    if (!wrapEl) return;
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.className = 'play-draw-canvas';
      canvas.setAttribute('aria-hidden', 'true');
      wrapEl.appendChild(canvas);
      ctx = canvas.getContext('2d');
      canvas.addEventListener('mousedown', onStart);
      canvas.addEventListener('mousemove', onMove);
      global.addEventListener('mouseup', onEnd);
      canvas.addEventListener('touchstart', onStart, { passive: false });
      canvas.addEventListener('touchmove', onMove, { passive: false });
      canvas.addEventListener('touchend', onEnd);
      global.addEventListener('resize', resize);
      if (global.ResizeObserver) {
        resizeObserver = new ResizeObserver(function () {
          resize();
        });
        resizeObserver.observe(wrapEl);
      }
    } else if (canvas.parentElement !== wrapEl) {
      wrapEl.appendChild(canvas);
      if (resizeObserver) {
        try { resizeObserver.disconnect(); } catch (e) { /* */ }
        resizeObserver.observe(wrapEl);
      }
    }
    resize();
    loadRemote(id).finally(function () {
      remoteLoaded = true;
      resize();
      redraw();
    });
  }

  function setEnabled(on) {
    enabled = !!on;
    if (!enabled) tool = 'pen';
    if (canvas) {
      canvas.style.pointerEvents = enabled ? 'auto' : 'none';
      canvas.classList.toggle('play-draw-active', enabled);
    }
    var btn = document.getElementById('draw-btn');
    if (btn) btn.classList.toggle('pb-on', enabled);
    syncToolbar();
    syncChrome();
    if (enabled) resize();
  }

  function toggle() {
    setEnabled(!enabled);
    return enabled;
  }

  function onCifraChange(id) {
    // Mesma música (ex.: cifra → grade): só redimensiona; mantém lápis e traços.
    if (id != null && cifraId != null && String(id) === String(cifraId)) {
      requestAnimationFrame(function () {
        resize();
        redraw();
      });
      return;
    }
    cifraId = id;
    loadLocal(id);
    remoteLoaded = false;
    redraw();
    if (enabled) setEnabled(false);
    resize();
    loadRemote(id).finally(function () {
      remoteLoaded = true;
      resize();
      redraw();
    });
  }

  function configure(opts) {
    opts = opts || {};
    if (opts.apiUrl) apiUrl = opts.apiUrl;
  }

  syncPenColor();
  document.addEventListener('setsync-themechange', syncPenColor);

  global.SetSyncDrawOverlay = {
    mount: mount,
    toggle: toggle,
    clear: clear,
    setTool: setTool,
    getTool: function () { return tool; },
    onCifraChange: onCifraChange,
    setEnabled: setEnabled,
    configure: configure,
    resize: resize,
    isEnabled: function () { return enabled; },
  };
})(window);
