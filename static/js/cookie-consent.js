(function () {
    'use strict';

    var banner = document.getElementById('ss-cookie-banner');
    if (!banner) return;

    var url = banner.getAttribute('data-consent-url');
    if (!url) return;

    function postChoice(choice) {
        var fetchFn = window.ssFetch || window.fetch;
        fetchFn(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ choice: choice }),
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (!data || !data.ok) return;
                banner.remove();
                if (choice === 'accept') {
                    window.location.reload();
                }
            })
            .catch(function () { /* silencioso — usuário pode tentar de novo */ });
    }

    banner.querySelectorAll('[data-choice]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            postChoice(btn.getAttribute('data-choice'));
        });
    });
})();
