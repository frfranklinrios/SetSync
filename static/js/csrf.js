(function () {
    'use strict';

    window.ssCsrfToken = function () {
        var m = document.querySelector('meta[name=csrf-token]');
        return m ? m.getAttribute('content') : '';
    };

    window.ssFetch = function (url, opts) {
        opts = opts || {};
        var headers = Object.assign({}, opts.headers || {});
        var method = (opts.method || 'GET').toUpperCase();
        if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
            headers['X-CSRFToken'] = ssCsrfToken();
        }
        opts.headers = headers;
        opts.credentials = opts.credentials || 'same-origin';
        return fetch(url, opts);
    };

    (function patchFetch() {
        var nativeFetch = window.fetch.bind(window);
        window.fetch = function (url, opts) {
            opts = opts || {};
            var method = (opts.method || 'GET').toUpperCase();
            if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
                opts.headers = Object.assign({}, opts.headers || {}, {
                    'X-CSRFToken': ssCsrfToken(),
                });
            }
            if (!opts.credentials) {
                opts.credentials = 'same-origin';
            }
            return nativeFetch(url, opts);
        };
    })();

    function injectCsrfIntoForms() {
        var token = ssCsrfToken();
        if (!token) return;
        document.querySelectorAll('form').forEach(function (form) {
            var method = (form.getAttribute('method') || 'GET').toUpperCase();
            if (method === 'GET') return;
            if (form.querySelector('input[name=csrf_token]')) return;
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = token;
            form.appendChild(input);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectCsrfIntoForms);
    } else {
        injectCsrfIntoForms();
    }
})();
