/**
 * Calendário mensal da agenda da banda.
 * Espera #band-agenda-calendar e #band-agenda-events-json no DOM.
 */
(function () {
    'use strict';

    var MONTHS = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
    ];
    var WEEKDAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    var MAX_VISIBLE = 3;

    function pad(n) {
        return n < 10 ? '0' + n : String(n);
    }

    function dateKey(y, m, d) {
        return y + '-' + pad(m + 1) + '-' + pad(d);
    }

    function parseEventDate(value) {
        if (!value) return '';
        return String(value).slice(0, 10);
    }

    function formatTime(value) {
        if (!value) return '';
        var t = String(value).slice(11, 16);
        return t || '';
    }

    function formatDayLabel(dateStr) {
        if (!dateStr) return '';
        var p = dateStr.split('-');
        if (p.length !== 3) return dateStr;
        return p[2] + '/' + p[1] + '/' + p[0];
    }

    function groupByDate(events) {
        var map = {};
        (events || []).forEach(function (ev) {
            var d = parseEventDate(ev.starts_at);
            if (!d) return;
            if (!map[d]) map[d] = [];
            map[d].push(ev);
        });
        Object.keys(map).forEach(function (k) {
            map[k].sort(function (a, b) {
                return String(a.starts_at).localeCompare(String(b.starts_at));
            });
        });
        return map;
    }

    function BandAgendaCalendar(root, events) {
        this.root = root;
        this.events = events || [];
        this.byDate = groupByDate(this.events);
        var now = new Date();
        this.year = now.getFullYear();
        this.month = now.getMonth();
        this.selectedDate = null;
        this._bind();
        this.render();
    }

    BandAgendaCalendar.prototype._bind = function () {
        var self = this;
        this.root.addEventListener('click', function (e) {
            var prev = e.target.closest('[data-cal-prev]');
            var next = e.target.closest('[data-cal-next]');
            var today = e.target.closest('[data-cal-today]');
            var more = e.target.closest('[data-cal-more]');
            var cell = e.target.closest('[data-cal-date]');

            if (prev) {
                e.preventDefault();
                self._shiftMonth(-1);
            } else if (next) {
                e.preventDefault();
                self._shiftMonth(1);
            } else if (today) {
                e.preventDefault();
                var n = new Date();
                self.year = n.getFullYear();
                self.month = n.getMonth();
                self.selectedDate = dateKey(self.year, self.month, n.getDate());
                self.render();
            } else if (more) {
                e.preventDefault();
                self.selectedDate = more.getAttribute('data-cal-more');
                self.render();
            } else if (cell && !e.target.closest('a.agenda-cal-event')) {
                self.selectedDate = cell.getAttribute('data-cal-date');
                self.render();
            }
        });
    };

    BandAgendaCalendar.prototype._shiftMonth = function (delta) {
        this.month += delta;
        if (this.month < 0) {
            this.month = 11;
            this.year -= 1;
        } else if (this.month > 11) {
            this.month = 0;
            this.year += 1;
        }
        this.render();
    };

    BandAgendaCalendar.prototype._renderDayDetail = function () {
        var panel = this.root.querySelector('[data-cal-day-detail]');
        if (!panel) return;
        if (!this.selectedDate || !this.byDate[this.selectedDate]) {
            panel.classList.remove('is-open');
            panel.innerHTML = '';
            return;
        }
        var items = this.byDate[this.selectedDate];
        var html = '<h4>' + formatDayLabel(this.selectedDate) + '</h4><ul>';
        items.forEach(function (ev) {
            var tipo = ev.event_type === 'show' ? 'Show' : 'Ensaio';
            var time = formatTime(ev.starts_at);
            html += '<li><a href="' + ev.url + '">';
            html += '<strong>' + escapeHtml(ev.title) + '</strong>';
            html += ' <span class="meta">· ' + tipo;
            if (time) html += ' às ' + time;
            if (ev.location) html += ' · ' + escapeHtml(ev.location);
            if (ev.scale_preview) html += ' · ' + escapeHtml(ev.scale_preview);
            html += '</span></a></li>';
        });
        html += '</ul>';
        panel.innerHTML = html;
        panel.classList.add('is-open');
    };

    BandAgendaCalendar.prototype.render = function () {
        var self = this;
        var today = new Date();
        var todayKey = dateKey(today.getFullYear(), today.getMonth(), today.getDate());

        var first = new Date(this.year, this.month, 1);
        var startPad = first.getDay();
        var daysInMonth = new Date(this.year, this.month + 1, 0).getDate();
        var daysInPrev = new Date(this.year, this.month, 0).getDate();

        var cells = [];
        var i;
        for (i = 0; i < startPad; i++) {
            var d = daysInPrev - startPad + i + 1;
            var pm = this.month === 0 ? 11 : this.month - 1;
            var py = this.month === 0 ? this.year - 1 : this.year;
            cells.push({ y: py, m: pm, d: d, outside: true });
        }
        for (i = 1; i <= daysInMonth; i++) {
            cells.push({ y: this.year, m: this.month, d: i, outside: false });
        }
        var tail = cells.length % 7;
        if (tail !== 0) {
            var need = 7 - tail;
            var nm = this.month === 11 ? 0 : this.month + 1;
            var ny = this.month === 11 ? this.year + 1 : this.year;
            for (i = 1; i <= need; i++) {
                cells.push({ y: ny, m: nm, d: i, outside: true });
            }
        }

        var weekdaysHtml = WEEKDAYS.map(function (w) {
            return '<div class="agenda-cal-weekday">' + w + '</div>';
        }).join('');

        var cellsHtml = cells.map(function (c) {
            var key = dateKey(c.y, c.m, c.d);
            var dayEvents = self.byDate[key] || [];
            var cls = 'agenda-cal-cell';
            if (c.outside) cls += ' is-outside';
            if (key === todayKey) cls += ' is-today';
            if (key === self.selectedDate) cls += ' is-selected';

            var evHtml = '';
            var visible = dayEvents.slice(0, MAX_VISIBLE);
            visible.forEach(function (ev) {
                var typeCls = ev.event_type === 'show' ? 'type-show' : 'type-ensaio';
                var time = formatTime(ev.starts_at);
                var label = (time ? time + ' ' : '') + ev.title;
                var tip = label;
                if (ev.scale_preview) tip += ' — ' + ev.scale_preview;
                evHtml += '<a class="agenda-cal-event ' + typeCls + '" href="' + ev.url + '" title="' + escapeAttr(tip) + '">' + escapeHtml(label) + '</a>';
            });
            if (dayEvents.length > MAX_VISIBLE) {
                evHtml += '<button type="button" class="agenda-cal-more" data-cal-more="' + key + '">+' + (dayEvents.length - MAX_VISIBLE) + ' mais</button>';
            }

            return (
                '<div class="' + cls + '" data-cal-date="' + key + '">' +
                '<div class="agenda-cal-daynum">' + c.d + '</div>' +
                '<div class="agenda-cal-events">' + evHtml + '</div>' +
                '</div>'
            );
        }).join('');

        this.root.innerHTML =
            '<div class="agenda-cal-toolbar">' +
            '<h3 class="agenda-cal-title">' + MONTHS[this.month] + ' ' + this.year + '</h3>' +
            '<div class="agenda-cal-nav">' +
            '<button type="button" class="btn btn-outline-secondary btn-sm" data-cal-today title="Ir para hoje">Hoje</button>' +
            '<button type="button" class="btn btn-outline-secondary btn-sm" data-cal-prev aria-label="Mês anterior"><i class="fas fa-chevron-left"></i></button>' +
            '<button type="button" class="btn btn-outline-secondary btn-sm" data-cal-next aria-label="Próximo mês"><i class="fas fa-chevron-right"></i></button>' +
            '</div></div>' +
            '<div class="agenda-cal-weekdays">' + weekdaysHtml + '</div>' +
            '<div class="agenda-cal-grid">' + cellsHtml + '</div>' +
            '<div class="agenda-cal-legend">' +
            '<span><i class="lg-ensaio"></i> Ensaio</span>' +
            '<span><i class="lg-show"></i> Show</span>' +
            '</div>' +
            '<div class="agenda-cal-day-detail" data-cal-day-detail></div>';

        this._renderDayDetail();
    };

    function escapeHtml(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function escapeAttr(s) {
        return escapeHtml(s);
    }

    function init() {
        var mount = document.getElementById('band-agenda-calendar');
        var dataEl = document.getElementById('band-agenda-events-json');
        if (!mount || !dataEl) return;
        var events;
        try {
            events = JSON.parse(dataEl.textContent || '[]');
        } catch (e) {
            events = [];
        }
        new BandAgendaCalendar(mount, events);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
