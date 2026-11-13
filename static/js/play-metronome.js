/**
 * Metrônomo Profissional — Web Audio API + Flash Visual + Tap Tempo + Visual Pulse.
 * Inspirado nas melhores implementações open-source de palco (chordbook/metronome & Resonate).
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
  var onBeatCallback = null;
  var onBpmChangeCallback = null;

  var SOUND_PREF_KEY = 'setsync.metronome.sound';
  var soundEnabled = true;
  try {
    var storedSound = localStorage.getItem(SOUND_PREF_KEY);
    if (storedSound !== null) soundEnabled = storedSound === '1';
  } catch (e) {}

  // Tap tempo state
  var tapTimes = [];
  var TAP_TIMEOUT = 2500; // Reset tap after 2.5s

  function getCtx() {
    if (!audioCtx) {
      var AC = global.AudioContext || global.webkitAudioContext;
      if (AC) audioCtx = new AC();
    }
    return audioCtx;
  }

  function click(accent) {
    if (soundEnabled) {
      try {
        var ctx = getCtx();
        if (ctx) {
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
        }
      } catch (e) {}
    }

    if (flashEl) {
      flashEl.classList.add(accent ? 'metronome-flash-accent' : 'metronome-flash');
      setTimeout(function () {
        if (flashEl) flashEl.classList.remove('metronome-flash', 'metronome-flash-accent');
      }, accent ? 100 : 80);
    }

    if (typeof onBeatCallback === 'function') {
      try {
        onBeatCallback(beatInBar, beatsPerBar, accent);
      } catch (e) {}
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
    bpm = Math.max(40, Math.min(240, Number(newBpm) || bpm || 120));
    beatsPerBar = parseTimeSignature(opts.timeSignature);
    accentBeatOne = opts.accentBeatOne !== false;
    beatInBar = 0;
    active = true;
    var interval = 60000 / bpm;
    countInBeats = Math.max(0, Math.min(8, parseInt(opts.countIn, 10) || 0));
    countInRemaining = countInBeats;
    onCountInDone = opts.onCountInDone || null;

    tick();
    timer = setInterval(tick, interval);
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
    if (typeof onBeatCallback === 'function') {
      try {
        onBeatCallback(0, beatsPerBar, false);
      } catch (e) {}
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

  function getBpm() {
    return bpm;
  }

  function setBpm(val) {
    var num = Math.max(40, Math.min(240, Math.round(Number(val) || 120)));
    bpm = num;
    if (typeof onBpmChangeCallback === 'function') {
      onBpmChangeCallback(bpm);
    }
    var btn = document.getElementById('metronome-btn');
    if (btn) btn.setAttribute('data-bpm', String(bpm));
    if (active) {
      start(bpm, {
        timeSignature: String(beatsPerBar) + '/4',
        accentBeatOne: accentBeatOne,
        countIn: 0,
      });
    }
    return bpm;
  }

  function setSoundEnabled(enable) {
    soundEnabled = !!enable;
    try {
      localStorage.setItem(SOUND_PREF_KEY, soundEnabled ? '1' : '0');
    } catch (e) {}
    updateUi();
    return soundEnabled;
  }

  function isSoundEnabled() {
    return soundEnabled;
  }

  /**
   * Tap Tempo: Calcula BPM com base nos intervalos dos toques.
   * Retorna o novo BPM calculado ou null se ainda precisa de mais toques.
   */
  function tap() {
    var now = Date.now();
    if (tapTimes.length > 0 && now - tapTimes[tapTimes.length - 1] > TAP_TIMEOUT) {
      tapTimes = [];
    }
    tapTimes.push(now);
    if (tapTimes.length > 5) {
      tapTimes.shift();
    }
    if (tapTimes.length < 2) {
      return null;
    }
    var intervals = [];
    for (var i = 1; i < tapTimes.length; i++) {
      intervals.push(tapTimes[i] - tapTimes[i - 1]);
    }
    var sum = intervals.reduce(function (a, b) { return a + b; }, 0);
    var avg = sum / intervals.length;
    if (avg <= 0) return null;
    var calcBpm = Math.max(40, Math.min(240, Math.round(60000 / avg)));
    setBpm(calcBpm);
    return calcBpm;
  }

  function onBeat(fn) {
    onBeatCallback = fn;
  }

  function onBpmChange(fn) {
    onBpmChangeCallback = fn;
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
    if (song.bpm) {
      bpm = Math.max(40, Math.min(240, Number(song.bpm) || 120));
      btn.setAttribute('data-bpm', String(bpm));
    }
    if (song.time_signature) {
      btn.setAttribute('data-time-sig', song.time_signature);
      beatsPerBar = parseTimeSignature(song.time_signature);
    }
  }

  global.SetSyncMetronome = {
    start: start,
    stop: stop,
    toggle: toggle,
    isActive: isActive,
    getBpm: getBpm,
    setBpm: setBpm,
    tap: tap,
    setSoundEnabled: setSoundEnabled,
    isSoundEnabled: isSoundEnabled,
    onBeat: onBeat,
    onBpmChange: onBpmChange,
    bindUi: bindUi,
    setCountInDefault: setCountInDefault,
    updateSongContext: updateSongContext,
  };
})(window);
