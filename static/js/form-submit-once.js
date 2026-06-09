/**
 * Evita envio duplicado de formulários (duplo clique em Salvar).
 */
(function () {
    'use strict';

    function lockForm(form) {
        if (form.dataset.submitLocked === '1') return false;
        form.dataset.submitLocked = '1';
        form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (btn) {
            if (btn.disabled) return;
            btn.disabled = true;
            if (!btn.dataset.submitLabel) {
                btn.dataset.submitLabel = (btn.tagName === 'INPUT' ? btn.value : btn.textContent) || '';
            }
            var label = btn.dataset.submitLabel;
            if (btn.tagName === 'INPUT') {
                btn.value = 'Salvando…';
            } else if (label) {
                btn.textContent = 'Salvando…';
            }
        });
        return true;
    }

    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form || form.tagName !== 'FORM') return;
        if (form.dataset.allowMultiSubmit === '1') return;
        if (!lockForm(form)) {
            e.preventDefault();
        }
    }, true);
})();
