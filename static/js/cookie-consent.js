(function () {
    'use strict';

    var banner = document.getElementById('ss-cookie-banner');
    if (!banner) return;

    var url = banner.getAttribute('data-consent-url');
    if (!url) return;

    var STORAGE_KEY = 'ss_cookie_consent';

    function readStoredChoice() {
        try {
            var v = window.localStorage.getItem(STORAGE_KEY);
            return (v === 'accept' || v === 'essential') ? v : null;
        } catch (e) {
            return null;
        }
    }

    function writeStoredChoice(choice) {
        try {
            window.localStorage.setItem(STORAGE_KEY, choice === 'accept' ? 'accept' : 'essential');
        } catch (e) {}
    }

    function setButtonsDisabled(disabled) {
        banner.querySelectorAll('[data-choice]').forEach(function (btn) {
            btn.disabled = disabled;
        });
    }

    function postChoice(choice, opts) {
        opts = opts || {};
        var normalized = choice === 'accept' ? 'accept' : 'essential';
        if (!opts.silent) {
            setButtonsDisabled(true);
            writeStoredChoice(normalized);
        }
        var fetchFn = window.ssFetch || window.fetch;
        var headers = { 'Content-Type': 'application/json' };
        if (window.csrfToken) headers['X-CSRFToken'] = window.csrfToken;
        fetchFn(url, {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin',
            keepalive: true,
            body: JSON.stringify({ choice: choice }),
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (!data || !data.ok) {
                    setButtonsDisabled(false);
                    return;
                }
                if (banner.parentNode) banner.remove();
                if (!opts.silent && choice === 'accept') {
                    window.location.reload();
                }
            })
            .catch(function () {
                if (!opts.silent && readStoredChoice()) {
                    if (banner.parentNode) banner.remove();
                } else {
                    setButtonsDisabled(false);
                }
            });
    }

    // Se o usuário já escolheu antes (ex.: página servida do cache PWA ou sessão expirada),
    // oculta o banner na hora e resincroniza o cookie de 1 ano silenciosamente.
    var saved = readStoredChoice();
    if (saved) {
        banner.remove();
        postChoice(saved, { silent: true });
        return;
    }

    banner.querySelectorAll('[data-choice]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            postChoice(btn.getAttribute('data-choice'));
        });
    });
})();
