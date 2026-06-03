(function () {
    'use strict';

    var wrap = document.getElementById('ss-notif-wrap');
    if (!wrap) return;

    var btn = document.getElementById('ss-notif-btn');
    var panel = document.getElementById('ss-notif-panel');
    var list = document.getElementById('ss-notif-list');
    var badge = document.getElementById('ss-notif-badge');
    var markAllBtn = document.getElementById('ss-notif-mark-all');
    var listUrl = wrap.getAttribute('data-list-url');
    var readUrlTpl = wrap.getAttribute('data-read-url');
    var readAllUrl = wrap.getAttribute('data-read-all-url');

    function fmtTime(iso) {
        if (!iso) return '';
        var d = new Date(iso.replace(' ', 'T') + (iso.includes('Z') ? '' : 'Z'));
        if (isNaN(d.getTime())) {
            d = new Date(iso.replace(' ', 'T'));
        }
        if (isNaN(d.getTime())) return '';
        var diff = (Date.now() - d.getTime()) / 1000;
        if (diff < 60) return 'agora';
        if (diff < 3600) return 'há ' + Math.floor(diff / 60) + ' min';
        if (diff < 86400) return 'há ' + Math.floor(diff / 3600) + ' h';
        return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    }

    function setBadge(n) {
        if (!badge) return;
        n = parseInt(n, 10) || 0;
        if (n > 0) {
            badge.textContent = n > 99 ? '99+' : String(n);
            badge.hidden = false;
        } else {
            badge.hidden = true;
        }
    }

    function readUrl(id) {
        return readUrlTpl.replace('__ID__', encodeURIComponent(id));
    }

    function renderItems(items) {
        if (!list) return;
        if (!items || !items.length) {
            list.innerHTML = '<div class="ss-notif-empty">Nenhuma notificação ainda.</div>';
            return;
        }
        list.innerHTML = items.map(function (n) {
            var cls = 'ss-notif-item' + (n.read ? '' : ' unread');
            var isAdmin = (n.type || '').indexOf('admin_') === 0;
            var tag = isAdmin ? '<span class="ss-notif-tag">Admin</span> ' : '';
            var meta = '';
            if (n.band_name) {
                meta = '<span class="ss-notif-band">' + escapeHtml(n.band_name) + '</span> · ';
            }
            return (
                '<button type="button" class="' + cls + '" data-id="' + n.id + '" data-url="' + (n.url || '') + '">' +
                '<div class="ss-notif-item-title">' + tag + escapeHtml(n.title) + '</div>' +
                '<p class="ss-notif-item-body">' + escapeHtml(n.body) + '</p>' +
                '<div class="ss-notif-item-time">' + meta + escapeHtml(fmtTime(n.created_at)) + '</div>' +
                '</button>'
            );
        }).join('');
    }

    function escapeHtml(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function loadNotifications() {
        return ssFetch(listUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                setBadge(data.unread);
                renderItems(data.items || []);
            })
            .catch(function () {});
    }

    function closePanel() {
        panel.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
    }

    function openPanel() {
        panel.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        loadNotifications();
    }

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (panel.classList.contains('open')) {
            closePanel();
        } else {
            openPanel();
        }
    });

    document.addEventListener('click', function (e) {
        if (!wrap.contains(e.target)) closePanel();
    });

    if (list) {
        list.addEventListener('click', function (e) {
            var item = e.target.closest('.ss-notif-item');
            if (!item) return;
            var id = item.getAttribute('data-id');
            var url = item.getAttribute('data-url') || '';
            ssFetch(readUrl(id), { method: 'POST' })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    setBadge(data.unread);
                    item.classList.remove('unread');
                })
                .catch(function () {});
            if (url && url.charAt(0) === '/' && url.indexOf('//') !== 0) {
                window.location.href = url;
            }
        });
    }

    if (markAllBtn) {
        markAllBtn.addEventListener('click', function (e) {
            e.preventDefault();
            ssFetch(readAllUrl, { method: 'POST' })
                .then(function () { return loadNotifications(); })
                .catch(function () {});
        });
    }

    setBadge(wrap.getAttribute('data-unread') || 0);
    loadNotifications();
    setInterval(loadNotifications, 60000);
})();
