/**
 * Uníssono — Paleta de Comando & Busca Global Instantânea (Ctrl+K / Spotlight)
 * Compatível com navegador e Node.js (testes unitários).
 */
(function (global) {
    'use strict';

    var CACHE_KEY = 'unissono_quick_nav_v1';
    var CACHE_TTL_MS = 60 * 1000;

    var Palette = {};

    var state = {
        isOpen: false,
        activeTab: 'all',
        query: '',
        data: null,
        items: [],
        filtered: [],
        selectedIndex: 0,
        loading: false,
        quickNavUrl: '/cifras/api/quick-nav',
        lastFocusEl: null
    };

    function normalizeStr(str) {
        if (!str) return '';
        return String(str)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function escapeHtml(str) {
        return String(str == null ? '' : str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function buildFlatItems(data) {
        if (!data || typeof data !== 'object') return [];
        var out = [];

        (data.actions || []).forEach(function (a) {
            out.push({
                kind: 'actions',
                kindLabel: 'Ação',
                title: a.label || '',
                subtitle: a.subtitle || '',
                icon: a.icon || 'fa-bolt',
                url: a.url || '#',
                playUrl: null,
                tom: '',
                readiness: '',
                searchText: normalizeStr([a.label, a.subtitle, 'acao atalho'].join(' '))
            });
        });

        (data.bands || []).forEach(function (b) {
            var countLabel = (b.cifras_count || 0) + ' música' + ((b.cifras_count || 0) === 1 ? '' : 's');
            var roleLabel = b.role === 'admin' ? 'Admin' : 'Membro';
            out.push({
                kind: 'bands',
                kindLabel: 'Banda',
                title: b.name || 'Banda',
                subtitle: roleLabel + ' · ' + countLabel,
                icon: 'fa-users',
                url: b.url || '#',
                playUrl: b.play_url || null,
                tom: '',
                readiness: '',
                searchText: normalizeStr([b.name, roleLabel, 'banda'].join(' '))
            });
        });

        (data.setlists || []).forEach(function (s) {
            out.push({
                kind: 'setlists',
                kindLabel: 'Roteiro',
                title: s.name || 'Setlist',
                subtitle: s.band_name ? 'Roteiro · ' + s.band_name : 'Roteiro',
                icon: 'fa-list-ol',
                url: s.url || '#',
                playUrl: s.play_url || null,
                tom: '',
                readiness: '',
                searchText: normalizeStr([s.name, s.band_name, 'setlist roteiro'].join(' '))
            });
        });

        (data.cifras || []).forEach(function (c) {
            var subParts = [];
            if (c.artista) subParts.push(c.artista);
            if (c.scope) subParts.push(c.scope);
            out.push({
                kind: 'cifras',
                kindLabel: 'Música',
                title: c.titulo || 'Sem título',
                subtitle: subParts.join(' · ') || 'Cifra',
                icon: 'fa-music',
                url: c.url || '#',
                playUrl: c.play_url || null,
                tom: c.tom || '',
                readiness: c.readiness || '',
                searchText: normalizeStr([c.titulo, c.artista, c.scope, c.tom, c.readiness].join(' '))
            });
        });

        (data.events || []).forEach(function (e) {
            var evSub = [];
            if (e.band_name) evSub.push(e.band_name);
            if (e.starts_at) evSub.push(e.starts_at);
            out.push({
                kind: 'events',
                kindLabel: 'Agenda',
                title: e.title || 'Evento',
                subtitle: evSub.join(' · ') || 'Agenda',
                icon: e.event_type === 'show' ? 'fa-star' : 'fa-calendar-alt',
                url: e.url || '#',
                playUrl: null,
                tom: '',
                readiness: '',
                searchText: normalizeStr([e.title, e.band_name, e.starts_at, e.event_type, 'agenda'].join(' '))
            });
        });

        return out;
    }

    function filterPaletteItems(items, query, tab) {
        var activeTab = tab || 'all';
        var rawQ = (query || '').trim();
        var q = normalizeStr(rawQ);
        var keyFilter = '';

        var tomMatch = q.match(/^tom:([a-g][#b]?m?(?:7|maj7|m7|9|sus4)?)$/i);
        if (tomMatch) {
            keyFilter = normalizeStr(tomMatch[1]);
            q = '';
        }

        var pool = (items || []).filter(function (it) {
            return activeTab === 'all' || it.kind === activeTab;
        });

        if (!q && !keyFilter) {
            return pool.slice(0, 40);
        }

        var scored = [];
        pool.forEach(function (it) {
            var tomNorm = normalizeStr(it.tom);
            if (keyFilter) {
                if (tomNorm && (tomNorm === keyFilter || tomNorm.indexOf(keyFilter) === 0)) {
                    scored.push({ item: it, score: 80 });
                }
                return;
            }

            var titleNorm = normalizeStr(it.title);
            var subNorm = normalizeStr(it.subtitle);
            var matchTitle = titleNorm.indexOf(q) !== -1;
            var matchSub = subNorm.indexOf(q) !== -1;
            var matchTom = tomNorm && (tomNorm === q || tomNorm.indexOf(q) === 0);
            var matchAll = it.searchText.indexOf(q) !== -1;

            if (matchTitle || matchSub || matchTom || matchAll) {
                var score = 0;
                if (titleNorm === q) score += 120;
                else if (titleNorm.indexOf(q) === 0) score += 60;
                else if (matchTitle) score += 30;
                if (matchSub) score += 15;
                if (matchTom) score += 10;
                if (it.kind === 'cifras') score += 4;
                if (it.kind === 'setlists' || it.kind === 'bands') score += 3;
                scored.push({ item: it, score: score });
            }
        });

        scored.sort(function (a, b) {
            return b.score - a.score;
        });

        return scored.slice(0, 40).map(function (entry) {
            return entry.item;
        });
    }

    function ensureModalDom() {
        if (typeof document === 'undefined') return null;
        var existing = document.getElementById('global-command-palette');
        if (existing) return existing;

        var overlay = document.createElement('div');
        overlay.id = 'global-command-palette';
        overlay.className = 'cmd-overlay d-none';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-label', 'Busca rápida no Uníssono');

        overlay.innerHTML =
            '<div class="cmd-dialog">' +
                '<div class="cmd-search-row">' +
                    '<i class="fas fa-search cmd-search-icon" aria-hidden="true"></i>' +
                    '<input type="text" id="global-cmd-input" class="cmd-input" ' +
                           'placeholder="Ir para música, roteiro, banda, agenda ou digite tom:G…" ' +
                           'autocomplete="off" spellcheck="false">' +
                    '<button type="button" id="global-cmd-close" class="cmd-close-btn" aria-label="Fechar">' +
                        '<i class="fas fa-times"></i>' +
                    '</button>' +
                '</div>' +
                '<div class="cmd-tabs" id="global-cmd-tabs" role="tablist">' +
                    '<button type="button" class="cmd-tab active" data-cmd-tab="all">Tudo</button>' +
                    '<button type="button" class="cmd-tab" data-cmd-tab="cifras">Músicas</button>' +
                    '<button type="button" class="cmd-tab" data-cmd-tab="setlists">Roteiros</button>' +
                    '<button type="button" class="cmd-tab" data-cmd-tab="bands">Bandas</button>' +
                    '<button type="button" class="cmd-tab" data-cmd-tab="events">Agenda</button>' +
                    '<button type="button" class="cmd-tab" data-cmd-tab="actions">Ações</button>' +
                '</div>' +
                '<div class="cmd-list-wrap">' +
                    '<ul class="cmd-list" id="global-cmd-list" role="listbox"></ul>' +
                '</div>' +
                '<div class="cmd-footer">' +
                    '<span><kbd>↑</kbd> <kbd>↓</kbd> navegar · <kbd>Enter</kbd> abrir · <kbd>Shift</kbd>+<kbd>Enter</kbd> tocar no palco</span>' +
                    '<span><kbd>Esc</kbd> fechar</span>' +
                '</div>' +
            '</div>';

        document.body.appendChild(overlay);

        var input = document.getElementById('global-cmd-input');
        var closeBtn = document.getElementById('global-cmd-close');
        var tabsEl = document.getElementById('global-cmd-tabs');

        if (input) {
            input.addEventListener('input', function () {
                state.query = input.value;
                state.selectedIndex = 0;
                applyFilterAndRender();
            });
            input.addEventListener('keydown', handleKeydown);
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', function () { Palette.close(); });
        }
        if (tabsEl) {
            tabsEl.addEventListener('click', function (e) {
                var btn = e.target.closest('[data-cmd-tab]');
                if (!btn) return;
                setTab(btn.getAttribute('data-cmd-tab') || 'all');
                if (input) input.focus();
            });
        }
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) Palette.close();
        });

        return overlay;
    }

    function setTab(tab) {
        state.activeTab = tab || 'all';
        state.selectedIndex = 0;
        if (typeof document !== 'undefined') {
            document.querySelectorAll('#global-cmd-tabs .cmd-tab').forEach(function (btn) {
                btn.classList.toggle('active', btn.getAttribute('data-cmd-tab') === state.activeTab);
            });
        }
        applyFilterAndRender();
    }

    function applyFilterAndRender() {
        state.filtered = filterPaletteItems(state.items, state.query, state.activeTab);
        if (state.selectedIndex >= state.filtered.length) {
            state.selectedIndex = Math.max(0, state.filtered.length - 1);
        }
        renderResults();
    }

    function renderResults() {
        if (typeof document === 'undefined') return;
        var list = document.getElementById('global-cmd-list');
        if (!list) return;

        if (state.loading && !state.items.length) {
            list.innerHTML = '<li class="cmd-empty"><i class="fas fa-spinner fa-spin me-2"></i>Carregando seu repertório…</li>';
            return;
        }

        if (!state.filtered.length) {
            list.innerHTML = '<li class="cmd-empty">Nenhum resultado encontrado para esta busca.</li>';
            return;
        }

        var html = state.filtered.map(function (it, idx) {
            var isSel = idx === state.selectedIndex;
            var badges = '';
            if (it.readiness === 'ensaio') {
                badges += '<span class="cmd-pill cmd-pill--ensaio">Ensaio</span>';
            } else if (it.readiness === 'aprender') {
                badges += '<span class="cmd-pill cmd-pill--aprender">Aprender</span>';
            }
            if (it.tom) {
                badges += '<span class="cmd-pill cmd-pill--key">' + escapeHtml(it.tom) + '</span>';
            } else {
                badges += '<span class="cmd-pill">' + escapeHtml(it.kindLabel) + '</span>';
            }
            var playBtn = it.playUrl
                ? '<a href="' + escapeHtml(it.playUrl) + '" class="cmd-play-btn" data-cmd-play="1" title="Abrir direto no Modo Tocar">' +
                    '<i class="fas fa-play"></i><span>Palco</span>' +
                  '</a>'
                : '';

            return (
                '<li class="cmd-item' + (isSel ? ' active' : '') + '" role="option" ' +
                    'aria-selected="' + (isSel ? 'true' : 'false') + '" data-cmd-idx="' + idx + '">' +
                    '<span class="cmd-item-icon" aria-hidden="true"><i class="fas ' + escapeHtml(it.icon) + '"></i></span>' +
                    '<span class="cmd-item-body">' +
                        '<div class="cmd-item-title">' + escapeHtml(it.title) + '</div>' +
                        '<div class="cmd-item-sub">' + escapeHtml(it.subtitle) + '</div>' +
                    '</span>' +
                    '<span class="cmd-item-badges">' + badges + '</span>' +
                    playBtn +
                '</li>'
            );
        }).join('');

        list.innerHTML = html;

        list.querySelectorAll('.cmd-item').forEach(function (li) {
            li.addEventListener('click', function (e) {
                if (e.target.closest('[data-cmd-play]')) return;
                var idx = parseInt(li.getAttribute('data-cmd-idx'), 10);
                navigateTo(idx, false);
            });
        });

        var activeEl = list.querySelector('.cmd-item.active');
        if (activeEl && activeEl.scrollIntoView) {
            activeEl.scrollIntoView({ block: 'nearest' });
        }
    }

    function navigateTo(idx, preferPlay) {
        var it = state.filtered[idx];
        if (!it) return;
        var targetUrl = (preferPlay && it.playUrl) ? it.playUrl : it.url;
        if (targetUrl && targetUrl !== '#') {
            Palette.close();
            window.location.href = targetUrl;
        }
    }

    function handleKeydown(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (state.filtered.length) {
                state.selectedIndex = (state.selectedIndex + 1) % state.filtered.length;
                renderResults();
            }
            return;
        }
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (state.filtered.length) {
                state.selectedIndex = (state.selectedIndex - 1 + state.filtered.length) % state.filtered.length;
                renderResults();
            }
            return;
        }
        if (e.key === 'Enter') {
            e.preventDefault();
            navigateTo(state.selectedIndex, !!e.shiftKey);
            return;
        }
        if (e.key === 'Escape') {
            e.preventDefault();
            Palette.close();
        }
    }

    function readCache() {
        try {
            var raw = sessionStorage.getItem(CACHE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (!parsed || !parsed.data) return null;
            return parsed;
        } catch (e) {
            return null;
        }
    }

    function writeCache(data) {
        try {
            sessionStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data: data }));
        } catch (e) { /* ignore */ }
    }

    function fetchQuickNav() {
        if (typeof fetch === 'undefined') return;
        state.loading = true;
        if (!state.items.length) renderResults();

        fetch(state.quickNavUrl, {
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json' }
        })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (data) {
                state.loading = false;
                if (data && data.ok) {
                    state.data = data;
                    state.items = buildFlatItems(data);
                    writeCache(data);
                    if (state.isOpen) applyFilterAndRender();
                } else if (state.isOpen) {
                    renderResults();
                }
            })
            .catch(function () {
                state.loading = false;
                if (state.isOpen) renderResults();
            });
    }

    Palette.open = function (initialTab) {
        if (typeof document === 'undefined') return;
        if (document.body && document.body.classList.contains('play-mode')) return;

        var trigger = document.getElementById('global-cmd-trigger');
        if (trigger && trigger.getAttribute('data-quick-nav-url')) {
            state.quickNavUrl = trigger.getAttribute('data-quick-nav-url');
        }

        state.lastFocusEl = document.activeElement;
        var overlay = ensureModalDom();
        if (!overlay) return;

        var cached = readCache();
        if (cached && !state.data) {
            state.data = cached.data;
            state.items = buildFlatItems(cached.data);
        }

        state.isOpen = true;
        state.query = '';
        state.selectedIndex = 0;
        overlay.classList.remove('d-none');

        var input = document.getElementById('global-cmd-input');
        if (input) {
            input.value = '';
            setTimeout(function () { input.focus(); }, 10);
        }

        setTab(initialTab || 'all');

        if (!cached || (Date.now() - (cached.ts || 0)) > CACHE_TTL_MS) {
            fetchQuickNav();
        }
    };

    Palette.close = function () {
        if (typeof document === 'undefined') return;
        var overlay = document.getElementById('global-command-palette');
        if (overlay) overlay.classList.add('d-none');
        state.isOpen = false;
        if (state.lastFocusEl && typeof state.lastFocusEl.focus === 'function') {
            try { state.lastFocusEl.focus(); } catch (e) { /* ignore */ }
        }
    };

    Palette.init = function () {
        if (typeof document === 'undefined') return;
        document.addEventListener('click', function (e) {
            var btn = e.target.closest('#global-cmd-trigger, [data-open-command-palette]');
            if (!btn) return;
            e.preventDefault();
            Palette.open(btn.getAttribute('data-cmd-tab') || 'all');
        });

        document.addEventListener('keydown', function (e) {
            if (document.body && document.body.classList.contains('play-mode')) return;
            if ((e.ctrlKey || e.metaKey) && !e.altKey && (e.key === 'k' || e.key === 'K')) {
                var trigger = document.getElementById('global-cmd-trigger');
                if (!trigger) return;
                e.preventDefault();
                if (state.isOpen) {
                    Palette.close();
                } else {
                    Palette.open('all');
                }
            }
        });
    };

    Palette.normalizeStr = normalizeStr;
    Palette.buildFlatItems = buildFlatItems;
    Palette.filterPaletteItems = filterPaletteItems;

    global.SetSyncCommandPalette = Palette;

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', Palette.init);
        } else {
            Palette.init();
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = Palette;
    }
})(typeof window !== 'undefined' ? window : globalThis);
