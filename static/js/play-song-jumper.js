/**
 * Uníssono (SetSync) - Quick Song Jumper (Paleta de Busca de Músicas no Modo Tocar)
 * Permite encontrar e pular imediatamente para qualquer música do setlist sem sair da tela.
 */
(function (global) {
    'use strict';

    var Jumper = {};

    var state = {
        cifras: [],
        filtered: [],
        selectedIndex: 0,
        isOpen: false,
        onSelect: null,
        getCurrentIndex: null
    };

    function normalizeStr(str) {
        if (!str) return '';
        return String(str)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function buildModalHtml() {
        if (typeof document === 'undefined') return;
        if (document.getElementById('play-song-jumper-modal')) return;

        var overlay = document.createElement('div');
        overlay.id = 'play-song-jumper-modal';
        overlay.className = 'play-jumper-overlay d-none';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-label', 'Busca rápida de músicas');

        overlay.innerHTML =
            '<div class="play-jumper-dialog">' +
                '<div class="play-jumper-search-box">' +
                    '<i class="fas fa-search play-jumper-search-icon" aria-hidden="true"></i>' +
                    '<input type="text" id="play-jumper-input" class="play-jumper-input" ' +
                           'placeholder="Pular para música… (número, título, artista ou tom)" ' +
                           'autocomplete="off" spellcheck="false">' +
                    '<button type="button" class="play-jumper-close-btn" id="play-jumper-close-btn" aria-label="Fechar">✕</button>' +
                '</div>' +
                '<div class="play-jumper-list-wrap">' +
                    '<ul id="play-jumper-list" class="play-jumper-list" role="listbox"></ul>' +
                '</div>' +
                '<div class="play-jumper-footer">' +
                    '<span><kbd>↑</kbd> <kbd>↓</kbd> navegar</span>' +
                    '<span><kbd>Enter</kbd> tocar agora</span>' +
                    '<span><kbd>Esc</kbd> fechar</span>' +
                '</div>' +
            '</div>';

        document.body.appendChild(overlay);

        var input = document.getElementById('play-jumper-input');
        var closeBtn = document.getElementById('play-jumper-close-btn');

        if (input) {
            input.addEventListener('input', function () {
                filterSongs(input.value);
            });
            input.addEventListener('keydown', handleInputKeydown);
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                Jumper.close();
            });
        }

        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                Jumper.close();
            }
        });
    }

    function filterSongs(query) {
        var rawQ = (query || '').trim();
        var q = normalizeStr(rawQ);
        var currentIdx = state.getCurrentIndex ? state.getCurrentIndex() : 0;

        if (!q) {
            state.filtered = state.cifras.map(function (c, idx) {
                return { cifra: c, originalIndex: idx };
            });
        } else {
            var numMatch = /^\d+$/.test(q) ? parseInt(q, 10) : null;
            state.filtered = [];

            state.cifras.forEach(function (c, idx) {
                var order = idx + 1;
                var titleNorm = normalizeStr(c.titulo || c.title);
                var artistNorm = normalizeStr(c.artista || c.artist);
                var tomNorm = normalizeStr(c.tom || c.tom_original || c.tom_root);

                var matchesNumber = (numMatch !== null && order === numMatch);
                var matchesTitle = titleNorm.indexOf(q) !== -1;
                var matchesArtist = artistNorm.indexOf(q) !== -1;
                var matchesTom = tomNorm === q || tomNorm.indexOf(q) !== -1;

                if (matchesNumber || matchesTitle || matchesArtist || matchesTom) {
                    var score = 0;
                    if (matchesNumber) score += 100;
                    if (titleNorm.indexOf(q) === 0) score += 50;
                    else if (matchesTitle) score += 20;
                    if (artistNorm.indexOf(q) === 0) score += 15;
                    else if (matchesArtist) score += 10;
                    if (matchesTom) score += 5;

                    state.filtered.push({
                        cifra: c,
                        originalIndex: idx,
                        score: score
                    });
                }
            });

            state.filtered.sort(function (a, b) {
                return b.score - a.score;
            });
        }

        // Seleciona preferencialmente o atual se na lista, senão o primeiro
        state.selectedIndex = 0;
        if (!q && currentIdx >= 0) {
            for (var i = 0; i < state.filtered.length; i++) {
                if (state.filtered[i].originalIndex === currentIdx) {
                    state.selectedIndex = i;
                    break;
                }
            }
        }

        renderList();
    }

    function renderList() {
        if (typeof document === 'undefined') return;
        var listEl = document.getElementById('play-jumper-list');
        if (!listEl) return;

        listEl.innerHTML = '';
        var currentIdx = state.getCurrentIndex ? state.getCurrentIndex() : 0;

        if (state.filtered.length === 0) {
            listEl.innerHTML = '<li class="play-jumper-empty">Nenhuma música encontrada no setlist</li>';
            return;
        }

        state.filtered.forEach(function (item, idx) {
            var c = item.cifra;
            var isCurrent = (item.originalIndex === currentIdx);
            var isSelected = (idx === state.selectedIndex);

            var li = document.createElement('li');
            li.className = 'play-jumper-item' +
                (isSelected ? ' is-selected' : '') +
                (isCurrent ? ' is-current' : '');
            li.setAttribute('role', 'option');
            li.setAttribute('aria-selected', isSelected ? 'true' : 'false');
            li.setAttribute('data-target-idx', String(item.originalIndex));

            var num = item.originalIndex + 1;
            var title = c.titulo || c.title || 'Sem título';
            var artist = c.artista || c.artist || '';
            var key = c.tom || c.tom_original || c.tom_root || '';

            var badgesHtml = '';
            if (isCurrent) {
                badgesHtml += '<span class="play-jumper-badge-now">Tocando agora</span>';
            }
            if (c.has_personal_draft) {
                badgesHtml += '<span class="play-jumper-badge-mine">Minha</span>';
            }
            if (key) {
                badgesHtml += '<span class="play-jumper-badge-key">' + key + '</span>';
            }

            li.innerHTML =
                '<span class="play-jumper-item-num">#' + num + '</span>' +
                '<div class="play-jumper-item-info">' +
                    '<div class="play-jumper-item-title">' + escapeHtml(title) + '</div>' +
                    (artist ? '<div class="play-jumper-item-artist">' + escapeHtml(artist) + '</div>' : '') +
                '</div>' +
                '<div class="play-jumper-item-badges">' + badgesHtml + '</div>';

            li.addEventListener('click', function () {
                Jumper.select(item.originalIndex);
            });

            listEl.appendChild(li);
        });

        scrollSelectedIntoView();
    }

    function scrollSelectedIntoView() {
        if (typeof document === 'undefined') return;
        var listEl = document.getElementById('play-jumper-list');
        if (!listEl) return;
        var selectedEl = listEl.querySelector('.play-jumper-item.is-selected');
        if (selectedEl && selectedEl.scrollIntoView) {
            selectedEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    function handleInputKeydown(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (state.filtered.length > 0) {
                state.selectedIndex = (state.selectedIndex + 1) % state.filtered.length;
                renderList();
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (state.filtered.length > 0) {
                state.selectedIndex = (state.selectedIndex - 1 + state.filtered.length) % state.filtered.length;
                renderList();
            }
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (state.filtered.length > 0 && state.filtered[state.selectedIndex]) {
                Jumper.select(state.filtered[state.selectedIndex].originalIndex);
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            Jumper.close();
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    Jumper.init = function (options) {
        options = options || {};
        state.cifras = options.cifras || [];
        state.onSelect = options.onSelect || null;
        state.getCurrentIndex = options.getCurrentIndex || null;

        buildModalHtml();
    };

    Jumper.open = function () {
        buildModalHtml();
        var overlay = document.getElementById('play-song-jumper-modal');
        var input = document.getElementById('play-jumper-input');
        if (!overlay || !input) return;

        state.isOpen = true;
        overlay.classList.remove('d-none');
        input.value = '';
        filterSongs('');

        setTimeout(function () {
            input.focus();
            input.select();
        }, 50);
    };

    Jumper.close = function () {
        var overlay = document.getElementById('play-song-jumper-modal');
        if (overlay) {
            overlay.classList.add('d-none');
        }
        state.isOpen = false;
    };

    Jumper.toggle = function () {
        if (state.isOpen) {
            Jumper.close();
        } else {
            Jumper.open();
        }
    };

    Jumper.select = function (index) {
        Jumper.close();
        if (typeof state.onSelect === 'function') {
            state.onSelect(index);
        }
    };

    Jumper.isOpen = function () {
        return state.isOpen;
    };

    Jumper.filterSongsForTest = function (cifras, query) {
        state.cifras = cifras;
        filterSongs(query);
        return state.filtered;
    };

    global.SetSyncSongJumper = Jumper;

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = Jumper;
    }
})(typeof window !== 'undefined' ? window : globalThis);
