/**
 * Uníssono — Filtro, Ordenação Instantânea e Atualização de Prontidão do Repertório
 */
(function (global) {
    'use strict';

    function norm(str) {
        if (!str) return '';
        return String(str)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function updateReadinessSummary(scope) {
        var summaryEl = scope.querySelector('[data-readiness-summary]');
        var rowsWrap = scope.querySelector('[data-rep-rows]');
        if (!summaryEl || !rowsWrap) return;

        var rows = Array.prototype.slice.call(rowsWrap.querySelectorAll('.row-item'));
        var total = rows.length;
        if (!total) return;

        var pronta = 0;
        var ensaio = 0;
        var aprender = 0;
        rows.forEach(function (r) {
            var st = (r.getAttribute('data-readiness') || 'pronta').toLowerCase();
            if (st === 'ensaio') ensaio += 1;
            else if (st === 'aprender') aprender += 1;
            else pronta += 1;
        });

        var pct = Math.round((pronta / total) * 100);
        var pctEl = summaryEl.querySelector('[data-rs-percent]');
        var prontaEl = summaryEl.querySelector('[data-rs-pronta]');
        var ensaioEl = summaryEl.querySelector('[data-rs-ensaio]');
        var aprenderEl = summaryEl.querySelector('[data-rs-aprender]');
        var barPronta = summaryEl.querySelector('[data-rs-bar-pronta]');
        var barEnsaio = summaryEl.querySelector('[data-rs-bar-ensaio]');
        var barAprender = summaryEl.querySelector('[data-rs-bar-aprender]');

        if (pctEl) pctEl.textContent = pct + '%';
        if (prontaEl) prontaEl.textContent = pronta;
        if (ensaioEl) ensaioEl.textContent = ensaio;
        if (aprenderEl) aprenderEl.textContent = aprender;
        if (barPronta) barPronta.style.width = Math.round((pronta / total) * 100) + '%';
        if (barEnsaio) barEnsaio.style.width = Math.round((ensaio / total) * 100) + '%';
        if (barAprender) barAprender.style.width = Math.round((aprender / total) * 100) + '%';
    }

    function initScope(scope) {
        var rowsWrap = scope.querySelector('[data-rep-rows]');
        if (!rowsWrap) return;

        var searchInput = scope.querySelector('[data-rep-search]');
        var sortSelect = scope.querySelector('[data-rep-sort]');
        var countEl = scope.querySelector('[data-rep-count]');
        var emptyEl = scope.querySelector('[data-rep-empty]');
        var chips = Array.prototype.slice.call(scope.querySelectorAll('[data-readiness-filter]'));

        var activeReadiness = 'all';
        var rows = Array.prototype.slice.call(rowsWrap.querySelectorAll('.row-item'));
        rows.forEach(function (r, idx) {
            if (!r.hasAttribute('data-orig-index')) {
                r.setAttribute('data-orig-index', String(idx));
            }
        });

        function applyFiltersAndSort() {
            var q = norm(searchInput ? searchInput.value : '');
            var sortBy = sortSelect ? sortSelect.value : 'default';
            var currentRows = Array.prototype.slice.call(rowsWrap.querySelectorAll('.row-item'));

            if (sortBy && sortBy !== 'default') {
                currentRows.sort(function (a, b) {
                    var va = '';
                    var vb = '';
                    if (sortBy === 'title') {
                        va = norm(a.getAttribute('data-title') || '');
                        vb = norm(b.getAttribute('data-title') || '');
                    } else if (sortBy === 'artist') {
                        va = norm(a.getAttribute('data-artist') || '') || norm(a.getAttribute('data-title') || '');
                        vb = norm(b.getAttribute('data-artist') || '') || norm(b.getAttribute('data-title') || '');
                    } else if (sortBy === 'tom') {
                        va = norm(a.getAttribute('data-tom') || 'zzz');
                        vb = norm(b.getAttribute('data-tom') || 'zzz');
                    }
                    return va.localeCompare(vb, 'pt-BR');
                });
            } else {
                currentRows.sort(function (a, b) {
                    return (parseInt(a.getAttribute('data-orig-index') || '0', 10)) -
                           (parseInt(b.getAttribute('data-orig-index') || '0', 10));
                });
            }

            currentRows.forEach(function (r) {
                rowsWrap.appendChild(r);
            });

            var visible = 0;
            currentRows.forEach(function (r) {
                var rReadiness = (r.getAttribute('data-readiness') || 'pronta').toLowerCase();
                var matchesReadiness = (activeReadiness === 'all' || rReadiness === activeReadiness);
                var haystack = norm([
                    r.getAttribute('data-title'),
                    r.getAttribute('data-artist'),
                    r.getAttribute('data-tom'),
                    r.textContent
                ].join(' '));
                var matchesQuery = !q || haystack.indexOf(q) !== -1;

                var show = matchesReadiness && matchesQuery;
                r.style.display = show ? '' : 'none';
                if (show) visible += 1;
            });

            if (countEl) {
                countEl.textContent = visible + ' de ' + currentRows.length + ' música' + (currentRows.length === 1 ? '' : 's');
            }
            if (emptyEl) {
                emptyEl.classList.toggle('d-none', visible > 0 || currentRows.length === 0);
            }
        }

        if (searchInput) {
            searchInput.addEventListener('input', applyFiltersAndSort);
        }
        if (sortSelect) {
            sortSelect.addEventListener('change', applyFiltersAndSort);
        }
        chips.forEach(function (btn) {
            btn.addEventListener('click', function () {
                activeReadiness = (btn.getAttribute('data-readiness-filter') || 'all').toLowerCase();
                chips.forEach(function (c) {
                    c.classList.toggle('active', c === btn);
                });
                applyFiltersAndSort();
            });
        });

        rowsWrap.addEventListener('change', function (e) {
            var sel = e.target.closest('.row-readiness-sel');
            if (!sel) return;
            var cid = sel.getAttribute('data-cifra-id');
            if (!cid) return;
            var val = sel.value;
            var row = sel.closest('.row-item');
            var prev = (row && row.getAttribute('data-readiness')) || 'pronta';

            sel.classList.remove('is-saved', 'is-error');
            sel.classList.add('is-saving');

            var fetchFn = global.ssFetch || global.fetch;
            var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
            if (global.csrfToken) headers['X-CSRFToken'] = global.csrfToken;

            fetchFn('/cifras/' + encodeURIComponent(cid) + '/readiness', {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: JSON.stringify({ readiness: val })
            })
                .then(function (r) {
                    if (!r.ok) throw new Error('http-' + r.status);
                    return r.json();
                })
                .then(function (data) {
                    if (!data || !data.ok) throw new Error('fail');
                    if (row) row.setAttribute('data-readiness', val);
                    sel.classList.add('is-saved');
                    updateReadinessSummary(scope);
                    applyFiltersAndSort();
                    setTimeout(function () { sel.classList.remove('is-saved'); }, 1800);
                })
                .catch(function () {
                    sel.value = prev;
                    sel.classList.add('is-error');
                    setTimeout(function () { sel.classList.remove('is-error'); }, 2200);
                })
                .finally(function () {
                    sel.classList.remove('is-saving');
                });
        });

        applyFiltersAndSort();
    }

    function initAll() {
        if (typeof document === 'undefined') return;
        document.querySelectorAll('[data-repertoire-scope]').forEach(initScope);
    }

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAll);
        } else {
            initAll();
        }
    }

    global.SetSyncRepertoireFilter = { initAll: initAll, initScope: initScope, norm: norm };
})(typeof window !== 'undefined' ? window : globalThis);
