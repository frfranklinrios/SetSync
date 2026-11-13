/**
 * Uníssono (SetSync) - Relógio de Palco & Cronômetro de Apresentação (Show Clock & Live Timer)
 * Exibe a hora local com precisão e fornece um cronômetro progressivo de show para músicos ao vivo.
 */
(function (global) {
    'use strict';

    var StageClock = {};

    var STORAGE_KEY = 'setsync_stage_timer_state';

    var state = {
        mode: 'clock', // 'clock' | 'timer'
        timerRunning: false,
        timerStartedAt: 0,
        timerElapsedMs: 0,
        intervalId: null,
        elements: {}
    };

    function loadSavedState() {
        if (typeof sessionStorage === 'undefined') return;
        try {
            var raw = sessionStorage.getItem(STORAGE_KEY);
            if (!raw) return;
            var data = JSON.parse(raw);
            state.mode = data.mode || 'clock';
            state.timerElapsedMs = Number(data.timerElapsedMs) || 0;
            state.timerRunning = !!data.timerRunning;
            if (state.timerRunning && data.timerStartedAt) {
                var now = Date.now();
                var diff = Math.max(0, now - data.timerStartedAt);
                state.timerElapsedMs += diff;
                state.timerStartedAt = now;
            }
        } catch (e) {
            /* ignore */
        }
    }

    function saveState() {
        if (typeof sessionStorage === 'undefined') return;
        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
                mode: state.mode,
                timerRunning: state.timerRunning,
                timerStartedAt: state.timerStartedAt,
                timerElapsedMs: state.timerElapsedMs
            }));
        } catch (e) {
            /* ignore */
        }
    }

    function pad2(n) {
        return (n < 10 ? '0' : '') + n;
    }

    StageClock.formatTime = function (d) {
        d = d || new Date();
        var h = pad2(d.getHours());
        var m = pad2(d.getMinutes());
        return h + ':' + m;
    };

    StageClock.formatTimeWithSec = function (d) {
        d = d || new Date();
        var h = pad2(d.getHours());
        var m = pad2(d.getMinutes());
        var s = pad2(d.getSeconds());
        return h + ':' + m + ':' + s;
    };

    StageClock.formatDuration = function (totalSeconds) {
        totalSeconds = Math.max(0, Math.floor(totalSeconds));
        var hours = Math.floor(totalSeconds / 3600);
        var minutes = Math.floor((totalSeconds % 3600) / 60);
        var seconds = totalSeconds % 60;

        if (hours > 0) {
            return hours + ':' + pad2(minutes) + ':' + pad2(seconds);
        }
        return pad2(minutes) + ':' + pad2(seconds);
    };

    function currentTimerSeconds() {
        var ms = state.timerElapsedMs;
        if (state.timerRunning && state.timerStartedAt) {
            ms += (Date.now() - state.timerStartedAt);
        }
        return Math.floor(ms / 1000);
    }

    function updateDisplay() {
        var elTime = state.elements.time;
        var elIcon = state.elements.icon;
        var elControls = state.elements.controls;
        var elPlayIcon = state.elements.playIcon;
        var elWidget = state.elements.widget;

        if (!elTime) return;

        if (state.mode === 'clock') {
            var now = new Date();
            elTime.textContent = StageClock.formatTime(now);
            if (elIcon) {
                elIcon.className = 'fas fa-clock stage-clock-icon text-info';
            }
            if (elControls) elControls.classList.add('d-none');
            if (elWidget) {
                elWidget.classList.remove('is-timer-mode', 'is-timer-active');
            }
        } else {
            // Timer mode
            var secs = currentTimerSeconds();
            elTime.textContent = StageClock.formatDuration(secs);
            if (elIcon) {
                elIcon.className = 'fas fa-stopwatch stage-clock-icon ' +
                    (state.timerRunning ? 'text-success' : 'text-warning');
            }
            if (elControls) elControls.classList.remove('d-none');
            if (elPlayIcon) {
                elPlayIcon.className = state.timerRunning ? 'fas fa-pause' : 'fas fa-play';
            }
            if (elWidget) {
                elWidget.classList.add('is-timer-mode');
                elWidget.classList.toggle('is-timer-active', state.timerRunning);
            }
        }
    }

    StageClock.init = function (container, options) {
        options = options || {};
        loadSavedState();

        if (typeof container === 'string') {
            container = document.getElementById(container);
        }
        if (!container && typeof document !== 'undefined') {
            container = document.getElementById('stage-clock-widget');
        }

        if (container) {
            state.elements.widget = container;
            state.elements.display = container.querySelector('#stage-clock-display') || container;
            state.elements.time = container.querySelector('#stage-clock-time');
            state.elements.icon = container.querySelector('#stage-clock-icon');
            state.elements.controls = container.querySelector('#stage-timer-ctrls');
            state.elements.playIcon = container.querySelector('#stage-timer-play-icon');

            if (state.elements.display) {
                state.elements.display.addEventListener('click', function (e) {
                    if (e.target.closest('#stage-timer-ctrls')) return;
                    StageClock.toggleMode();
                });
            }

            var toggleBtn = container.querySelector('#stage-timer-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', function (e) {
                    e.stopPropagation();
                    StageClock.toggleTimer();
                });
            }

            var resetBtn = container.querySelector('#stage-timer-reset');
            if (resetBtn) {
                resetBtn.addEventListener('click', function (e) {
                    e.stopPropagation();
                    StageClock.resetTimer();
                });
            }
        }

        if (state.intervalId) clearInterval(state.intervalId);
        state.intervalId = setInterval(updateDisplay, 1000);
        updateDisplay();
    };

    StageClock.setMode = function (mode) {
        if (mode !== 'clock' && mode !== 'timer') return;
        state.mode = mode;
        saveState();
        updateDisplay();
    };

    StageClock.toggleMode = function () {
        StageClock.setMode(state.mode === 'clock' ? 'timer' : 'clock');
    };

    StageClock.startTimer = function () {
        if (state.timerRunning) return;
        state.timerRunning = true;
        state.timerStartedAt = Date.now();
        state.mode = 'timer';
        saveState();
        updateDisplay();
    };

    StageClock.pauseTimer = function () {
        if (!state.timerRunning) return;
        state.timerElapsedMs += (Date.now() - state.timerStartedAt);
        state.timerRunning = false;
        state.timerStartedAt = 0;
        saveState();
        updateDisplay();
    };

    StageClock.toggleTimer = function () {
        if (state.timerRunning) {
            StageClock.pauseTimer();
        } else {
            StageClock.startTimer();
        }
    };

    StageClock.resetTimer = function () {
        state.timerRunning = false;
        state.timerStartedAt = 0;
        state.timerElapsedMs = 0;
        saveState();
        updateDisplay();
    };

    StageClock.getState = function () {
        return {
            mode: state.mode,
            timerRunning: state.timerRunning,
            elapsedSeconds: currentTimerSeconds(),
            currentTime: StageClock.formatTime()
        };
    };

    StageClock.destroy = function () {
        if (state.intervalId) {
            clearInterval(state.intervalId);
            state.intervalId = null;
        }
    };

    global.SetSyncStageClock = StageClock;

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = StageClock;
    }
})(typeof window !== 'undefined' ? window : globalThis);
