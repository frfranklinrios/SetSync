/**
 * Uníssono — Motor Universal de Ordenação por Colunas
 * Suporta:
 *  1) Todas as tabelas <table class="table"> com <thead> e <tbody> (exceto [data-no-sort], .no-sort, .help-table)
 *  2) Listas declarativas (.row-card, .list-group, .bands-grid) via .row-sort-header + [data-sortable-list]
 * Compatível com navegador e Node.js (testes unitários).
 */
(function (global) {
    'use strict';

    function normalizeText(str) {
        if (str == null) return '';
        return String(str)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function isEmptyVal(raw) {
        var s = normalizeText(raw);
        return !s || s === '—' || s === '-' || s === '–';
    }

    function parseCurrency(raw) {
        var s = String(raw || '').trim();
        if (!/r\$|^-?\s*[\d.]+,\d{2}/i.test(s)) return null;
        var neg = s.indexOf('-') !== -1 || s.indexOf('−') !== -1;
        var cleaned = s.replace(/[^\d.,]/g, '');
        if (!cleaned) return null;
        if (cleaned.indexOf(',') !== -1) {
            cleaned = cleaned.replace(/\./g, '').replace(',', '.');
        }
        var num = parseFloat(cleaned);
        if (!Number.isFinite(num)) return null;
        return neg ? -Math.abs(num) : num;
    }

    function parseDateValue(raw) {
        var s = String(raw || '').trim();
        if (!s) return null;

        // ISO: YYYY-MM-DD[ HH:MM[:SS]]
        var iso = s.match(/^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?/);
        if (iso) {
            return Date.UTC(
                parseInt(iso[1], 10),
                parseInt(iso[2], 10) - 1,
                parseInt(iso[3], 10),
                parseInt(iso[4] || '0', 10),
                parseInt(iso[5] || '0', 10),
                parseInt(iso[6] || '0', 10)
            );
        }

        // BR: DD/MM/YYYY[ às HH:MM] or DD/MM/YYYY[ HH:MM]
        var br = s.match(/^(\d{2})\/(\d{2})\/(\d{4})(?:\s*(?:às|as)?\s*(\d{2}):(\d{2}))?/i);
        if (br) {
            return Date.UTC(
                parseInt(br[3], 10),
                parseInt(br[2], 10) - 1,
                parseInt(br[1], 10),
                parseInt(br[4] || '0', 10),
                parseInt(br[5] || '0', 10),
                0
            );
        }

        return null;
    }

    function parseNumberValue(raw) {
        var s = String(raw || '').trim().replace('%', '').replace(/\s+/g, '');
        if (!s) return null;
        if (/^-?\d+(?:\.\d{3})*,\d+$/.test(s)) {
            s = s.replace(/\./g, '').replace(',', '.');
        } else if (/^-?\d+,\d+$/.test(s)) {
            s = s.replace(',', '.');
        }
        if (!/^-?\d+(?:\.\d+)?$/.test(s)) return null;
        var num = parseFloat(s);
        return Number.isFinite(num) ? num : null;
    }

    function parseSortValue(raw, typeHint) {
        if (isEmptyVal(raw)) {
            return { empty: true, kind: 'empty', val: '' };
        }
        var s = String(raw).trim();
        var hint = (typeHint || 'auto').toLowerCase();

        if (hint === 'currency') {
            var c = parseCurrency(s);
            if (c !== null) return { empty: false, kind: 'number', val: c };
        }
        if (hint === 'date') {
            var d = parseDateValue(s);
            if (d !== null) return { empty: false, kind: 'number', val: d };
        }
        if (hint === 'number') {
            var n = parseNumberValue(s);
            if (n !== null) return { empty: false, kind: 'number', val: n };
        }

        if (hint === 'auto') {
            var autoCur = parseCurrency(s);
            if (autoCur !== null) return { empty: false, kind: 'number', val: autoCur };

            var autoDate = parseDateValue(s);
            if (autoDate !== null) return { empty: false, kind: 'number', val: autoDate };

            var autoNum = parseNumberValue(s);
            if (autoNum !== null) return { empty: false, kind: 'number', val: autoNum };
        }

        return { empty: false, kind: 'text', val: normalizeText(s).toLowerCase() };
    }

    function compareValues(rawA, rawB, direction, typeHint) {
        var dir = direction === 'desc' ? -1 : 1;
        var a = parseSortValue(rawA, typeHint);
        var b = parseSortValue(rawB, typeHint);

        if (a.empty && b.empty) return 0;
        if (a.empty) return 1;
        if (b.empty) return -1;

        if (a.kind === 'number' && b.kind === 'number') {
            if (a.val < b.val) return -1 * dir;
            if (a.val > b.val) return 1 * dir;
            return 0;
        }

        var cmp = String(a.val).localeCompare(String(b.val), 'pt-BR', {
            sensitivity: 'base',
            numeric: true
        });
        return cmp * dir;
    }

    function indicatorGlyph(dir) {
        if (dir === 'asc') return '↑';
        if (dir === 'desc') return '↓';
        return '⇅';
    }

    function updateTableIndicators(ths, activeIdx, dir) {
        ths.forEach(function (th, idx) {
            if (!th.classList.contains('ss-sortable')) return;
            var ind = th.querySelector('.ss-sort-ind');
            if (idx === activeIdx) {
                th.setAttribute('aria-sort', dir === 'desc' ? 'descending' : 'ascending');
                if (ind) ind.textContent = indicatorGlyph(dir);
            } else {
                th.setAttribute('aria-sort', 'none');
                if (ind) ind.textContent = indicatorGlyph('');
            }
        });
    }

    function groupTableRows(tbody) {
        var rows = Array.prototype.slice.call(tbody.children).filter(function (el) {
            return el.tagName === 'TR';
        });
        var groups = [];
        rows.forEach(function (tr) {
            if (tr.classList.contains('collapse') && groups.length > 0) {
                groups[groups.length - 1].companions.push(tr);
            } else {
                groups.push({ row: tr, companions: [] });
            }
        });
        return groups;
    }

    function sortTable(table, colIdx, forcedDir) {
        if (!table || !table.tBodies || !table.tBodies.length) return;
        var tbody = table.tBodies[0];
        var thead = table.tHead;
        if (!thead || !thead.rows.length) return;

        var ths = Array.prototype.slice.call(thead.rows[0].cells);
        var th = ths[colIdx];
        if (!th || !th.classList.contains('ss-sortable')) return;

        var currentSort = th.getAttribute('aria-sort');
        var nextDir = forcedDir || (currentSort === 'ascending' ? 'desc' : 'asc');
        var typeHint = th.getAttribute('data-sort-type') || 'auto';

        var groups = groupTableRows(tbody);
        groups.forEach(function (g, idx) {
            if (!g.row.hasAttribute('data-orig-index')) {
                g.row.setAttribute('data-orig-index', String(idx));
            }
        });

        groups.sort(function (ga, gb) {
            var cellA = ga.row.cells[colIdx];
            var cellB = gb.row.cells[colIdx];
            var valA = cellA ? (cellA.getAttribute('data-sort-value') || cellA.textContent) : '';
            var valB = cellB ? (cellB.getAttribute('data-sort-value') || cellB.textContent) : '';
            var cmp = compareValues(valA, valB, nextDir, typeHint);
            if (cmp !== 0) return cmp;
            return parseInt(ga.row.getAttribute('data-orig-index') || '0', 10) -
                   parseInt(gb.row.getAttribute('data-orig-index') || '0', 10);
        });

        groups.forEach(function (g) {
            tbody.appendChild(g.row);
            g.companions.forEach(function (comp) {
                tbody.appendChild(comp);
            });
        });

        updateTableIndicators(ths, colIdx, nextDir);
    }

    function initTable(table) {
        if (!table || table.getAttribute('data-ss-sort-init') === '1') return;
        if (table.hasAttribute('data-no-sort') || table.classList.contains('no-sort') || table.classList.contains('help-table')) {
            return;
        }
        var thead = table.tHead;
        if (!thead || !thead.rows.length || !table.tBodies.length) return;

        var headerRow = thead.rows[0];
        var ths = Array.prototype.slice.call(headerRow.cells);
        var anySortable = false;

        ths.forEach(function (th, idx) {
            if (th.hasAttribute('data-no-sort')) return;
            var label = normalizeText(th.textContent);
            if (!label) return;
            anySortable = true;
            th.classList.add('ss-sortable');
            th.setAttribute('tabindex', '0');
            th.setAttribute('role', 'button');
            th.setAttribute('aria-sort', 'none');
            if (!th.querySelector('.ss-sort-ind')) {
                var span = document.createElement('span');
                span.className = 'ss-sort-ind';
                span.setAttribute('aria-hidden', 'true');
                span.textContent = '⇅';
                th.appendChild(span);
            }
            th.addEventListener('click', function () {
                sortTable(table, idx);
            });
            th.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    sortTable(table, idx);
                }
            });
        });

        if (anySortable) {
            table.setAttribute('data-ss-sort-init', '1');
        }
    }

    function resolveListItemsContainer(targetEl) {
        if (!targetEl) return null;
        if (targetEl.id === 'setlist-card') {
            var inner = targetEl.querySelector('#sortable-cifras');
            if (inner) return inner;
        }
        return targetEl;
    }

    function sortListContainer(headerEl, btn) {
        if (!headerEl || !btn) return;
        var targetSelector = headerEl.getAttribute('data-sort-target');
        var listRoot = targetSelector ? document.querySelector(targetSelector) : headerEl.parentElement;
        if (!listRoot) return;

        var itemsWrap = resolveListItemsContainer(listRoot);
        if (!itemsWrap) return;

        var col = btn.getAttribute('data-sort-col');
        var typeHint = btn.getAttribute('data-sort-type') || 'auto';
        if (!col) return;

        var currentSort = btn.getAttribute('aria-sort');
        var defaultDir = btn.getAttribute('data-default-dir') || 'asc';
        var nextDir = (currentSort === 'ascending') ? 'desc' : (currentSort === 'descending' ? 'asc' : defaultDir);

        var items = Array.prototype.slice.call(itemsWrap.children).filter(function (el) {
            return el.classList.contains('row-item') ||
                   el.classList.contains('list-group-item') ||
                   el.classList.contains('band-tile') ||
                   el.hasAttribute('data-sort-item');
        });

        items.forEach(function (el, idx) {
            if (!el.hasAttribute('data-orig-index')) {
                el.setAttribute('data-orig-index', String(idx));
            }
        });

        items.sort(function (a, b) {
            if (col === 'orig-index') {
                var ia = parseInt(a.getAttribute('data-orig-index') || '0', 10);
                var ib = parseInt(b.getAttribute('data-orig-index') || '0', 10);
                return nextDir === 'desc' ? (ib - ia) : (ia - ib);
            }
            var attrName = 'data-' + col;
            var valA = a.getAttribute(attrName);
            var valB = b.getAttribute(attrName);
            if (valA == null) valA = a.textContent;
            if (valB == null) valB = b.textContent;
            var cmp = compareValues(valA, valB, nextDir, typeHint);
            if (cmp !== 0) return cmp;
            return parseInt(a.getAttribute('data-orig-index') || '0', 10) -
                   parseInt(b.getAttribute('data-orig-index') || '0', 10);
        });

        var isManualSetlistOrder = itemsWrap.id === 'sortable-cifras';
        var visibleNum = 0;
        items.forEach(function (el) {
            itemsWrap.appendChild(el);
            if (!isManualSetlistOrder && el.style.display !== 'none') {
                var numEl = el.querySelector('.row-num');
                if (numEl) {
                    visibleNum += 1;
                    numEl.textContent = String(visibleNum);
                }
            }
        });

        headerEl.querySelectorAll('.row-sort-btn').forEach(function (other) {
            var ind = other.querySelector('.ss-sort-ind');
            if (other === btn) {
                other.setAttribute('aria-sort', nextDir === 'desc' ? 'descending' : 'ascending');
                if (ind) ind.textContent = indicatorGlyph(nextDir);
            } else {
                other.setAttribute('aria-sort', 'none');
                if (ind) ind.textContent = indicatorGlyph('');
            }
        });
    }

    function initListHeader(headerEl) {
        if (!headerEl || headerEl.getAttribute('data-ss-sort-init') === '1') return;
        var buttons = Array.prototype.slice.call(headerEl.querySelectorAll('.row-sort-btn'));
        if (!buttons.length) return;

        var targetSelector = headerEl.getAttribute('data-sort-target');
        var listRoot = targetSelector ? document.querySelector(targetSelector) : headerEl.parentElement;
        var itemsWrap = resolveListItemsContainer(listRoot);
        if (itemsWrap) {
            var items = Array.prototype.slice.call(itemsWrap.children).filter(function (el) {
                return el.classList.contains('row-item') ||
                       el.classList.contains('list-group-item') ||
                       el.classList.contains('band-tile') ||
                       el.hasAttribute('data-sort-item');
            });
            items.forEach(function (el, idx) {
                if (!el.hasAttribute('data-orig-index')) {
                    el.setAttribute('data-orig-index', String(idx));
                }
            });
        }

        buttons.forEach(function (btn) {
            if (!btn.hasAttribute('aria-sort')) {
                btn.setAttribute('aria-sort', 'none');
            }
            if (!btn.querySelector('.ss-sort-ind')) {
                var span = document.createElement('span');
                span.className = 'ss-sort-ind';
                span.setAttribute('aria-hidden', 'true');
                var current = btn.getAttribute('aria-sort');
                span.textContent = indicatorGlyph(current === 'ascending' ? 'asc' : (current === 'descending' ? 'desc' : ''));
                btn.appendChild(span);
            }
            btn.addEventListener('click', function () {
                sortListContainer(headerEl, btn);
            });
        });

        headerEl.setAttribute('data-ss-sort-init', '1');
    }

    function initAll() {
        if (typeof document === 'undefined') return;
        document.querySelectorAll('table.table').forEach(initTable);
        document.querySelectorAll('.row-sort-header').forEach(initListHeader);
    }

    var API = {
        parseSortValue: parseSortValue,
        compareValues: compareValues,
        sortTable: sortTable,
        sortListContainer: sortListContainer,
        initAll: initAll
    };

    global.SetSyncUniversalSort = API;

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAll);
        } else {
            initAll();
        }
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = API;
    }
})(typeof window !== 'undefined' ? window : globalThis);
