/**
 * Metrônomo — Web Audio + flash visual, acento no tempo 1, count-in e compassos.
 */
(function (global) {
  'use strict';

  var active = false;
  var bpm = 120;
  var timer = null;
  var audioCtx = null;
  var flashEl = null;
  var beatInBar = 0;
  var beatsPerBar = 4;
  var accentBeatOne = true;
  var countInBeats = 0;
  var countInRemaining = 0;
  var onCountInDone = null;

  function getCtx() {
    if (!audioCtx) {
      var AC = global.AudioContext || global.webkitAudioContext;
      if (AC) audioCtx = new AC();
    }
    return audioCtx;
  }

  function click(accent) {
    var ctx = getCtx();
    if (!ctx) return;
    if (ctx.state === 'suspended') ctx.resume();
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = 'square';
    o.frequency.value = accent ? 1400 : 1000;
    g.gain.value = accent ? 0.12 : 0.08;
    o.connect(g);
    g.connect(ctx.destination);
    var t = ctx.currentTime;
    o.start(t);
    g.gain.exponentialRampToValueAtTime(0.001, t + (accent ? 0.07 : 0.05));
    o.stop(t + (accent ? 0.08 : 0.06));
    if (flashEl) {
      flashEl.classList.add(accent ? 'metronome-flash-accent' : 'metronome-flash');
      setTimeout(function () {
        flashEl.classList.remove('metronome-flash', 'metronome-flash-accent');
      }, accent ? 100 : 80);
    }
  }

  function parseTimeSignature(ts) {
    if (!ts || typeof ts !== 'string') return 4;
    var parts = ts.split('/');
    var n = parseInt(parts[0], 10);
    return n > 0 && n <= 12 ? n : 4;
  }

  function tick() {
    if (countInRemaining > 0) {
      var beatNum = countInBeats - countInRemaining + 1;
      click(beatNum === 1);
      countInRemaining -= 1;
      if (countInRemaining === 0 && typeof onCountInDone === 'function') {
        var fn = onCountInDone;
        onCountInDone = null;
        fn();
      }
      return;
    }
    beatInBar = (beatInBar % beatsPerBar) + 1;
    click(accentBeatOne && beatInBar === 1);
  }

  function start(newBpm, opts) {
    stop(false);
    opts = opts || {};
    bpm = Math.max(40, Math.min(240, Number(newBpm) || 120));
    beatsPerBar = parseTimeSignature(opts.timeSignature);
    accentBeatOne = opts.accentBeatOne !== false;
    beatInBar = 0;
    active = true;
    var interval = 60000 / bpm;
    countInBeats = Math.max(0, Math.min(8, parseInt(opts.countIn, 10) || 0));
    countInRemaining = countInBeats;
    onCountInDone = opts.onCountInDone || null;
    if (countInRemaining > 0) {
      tick();
      timer = setInterval(tick, interval);
    } else {
      tick();
      timer = setInterval(tick, interval);
    }
    updateUi();
  }

  function stop(clearCountIn) {
    if (clearCountIn !== false) {
      countInRemaining = 0;
      onCountInDone = null;
    }
    active = false;
    beatInBar = 0;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    updateUi();
  }

  function toggle(newBpm, opts) {
    if (active) stop();
    else start(newBpm, opts);
    return active;
  }

  function isActive() {
    return active;
  }

  function bindUi(btnId, flashTargetId) {
    flashEl = flashTargetId ? document.getElementById(flashTargetId) : null;
    var btn = btnId ? document.getElementById(btnId) : null;
    if (btn) {
      btn.addEventListener('click', function () {
        var countIn = btn.getAttribute('data-count-in');
        toggle(btn.getAttribute('data-bpm') || bpm, {
          timeSignature: btn.getAttribute('data-time-sig') || '4/4',
          countIn: countIn ? parseInt(countIn, 10) : 0,
        });
      });
    }
  }

  function updateUi() {
    var btn = document.getElementById('metronome-btn');
    if (btn) btn.classList.toggle('pb-on', active);
    var badge = document.getElementById('countin-badge');
    if (badge) {
      badge.style.display = countInRemaining > 0 ? 'block' : 'none';
      if (countInRemaining > 0) {
        badge.textContent = countInBeats - countInRemaining + 1 + '…';
      }
    }
  }

  function setCountInDefault(beats) {
    var btn = document.getElementById('metronome-btn');
    if (btn) btn.setAttribute('data-count-in', String(Math.max(0, beats || 0)));
  }

  function updateSongContext(song) {
    var btn = document.getElementById('metronome-btn');
    if (!btn || !song) return;
    if (song.bpm) btn.setAttribute('data-bpm', String(song.bpm));
    if (song.time_signature) btn.setAttribute('data-time-sig', song.time_signature);
  }

  global.SetSyncMetronome = {
    start: start,
    stop: stop,
    toggle: toggle,
    isActive: isActive,
    bindUi: bindUi,
    setCountInDefault: setCountInDefault,
    updateSongContext: updateSongContext,
  };
})(window);
