/**
 * SetSync — Web Push (Android PWA + iOS 16.4+ standalone).
 */
(function () {
    'use strict';

    var API_BASE = '/notifications/api/push';

    function supportsPush() {
        return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
    }

    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent || '')
            || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    }

    function isStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches
            || window.navigator.standalone === true;
    }

    function urlBase64ToUint8Array(base64String) {
        var padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        var base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        var raw = window.atob(base64);
        var arr = new Uint8Array(raw.length);
        for (var i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
        return arr;
    }

    function swRegistration() {
        return navigator.serviceWorker.ready;
    }

    function fetchVapidKey() {
        return fetch(API_BASE + '/vapid-key', { credentials: 'same-origin' })
            .then(function (r) { return r.json(); });
    }

    function getStatus() {
        return fetch(API_BASE + '/status', { credentials: 'same-origin' })
            .then(function (r) { return r.json(); });
    }

    function subscribeOnServer(subscription) {
        var json = subscription.toJSON();
        return fetch(API_BASE + '/subscribe', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(json),
        }).then(function (r) { return r.json(); });
    }

    function unsubscribeOnServer(endpoint) {
        return fetch(API_BASE + '/unsubscribe', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(endpoint ? { endpoint: endpoint } : {}),
        }).then(function (r) { return r.json(); });
    }

    function enablePush() {
        if (!supportsPush()) {
            alert('Seu navegador não suporta notificações push.');
            return Promise.reject(new Error('unsupported'));
        }
        if (isIOS() && !isStandalone()) {
            alert(
                'No iPhone/iPad, instale o SetSync na Tela de Início (Safari → Compartilhar → '
                + 'Adicionar à Tela de Início) e abra o app de lá para ativar push.'
            );
            return Promise.reject(new Error('ios_not_standalone'));
        }
        return Notification.requestPermission().then(function (perm) {
            if (perm !== 'granted') {
                throw new Error('permission_denied');
            }
            return fetchVapidKey();
        }).then(function (data) {
            if (!data.ok || !data.publicKey) throw new Error('no_vapid');
            return swRegistration().then(function (reg) {
                return reg.pushManager.getSubscription().then(function (existing) {
                    if (existing) return existing;
                    return reg.pushManager.subscribe({
                        userVisibleOnly: true,
                        applicationServerKey: urlBase64ToUint8Array(data.publicKey),
                    });
                });
            });
        }).then(function (subscription) {
            return subscribeOnServer(subscription);
        });
    }

    function updatePerfilUi(status) {
        var label = document.getElementById('push-device-label');
        var btn = document.getElementById('push-enable-btn');
        var master = document.getElementById('push_notify');
        if (!label) return;

        if (!supportsPush()) {
            label.textContent = 'Push não suportado neste navegador.';
            if (btn) btn.hidden = true;
            return;
        }
        if (isIOS() && !isStandalone()) {
            label.textContent = 'No iPhone, instale o app na Tela de Início para receber push.';
            if (btn) btn.hidden = true;
            return;
        }
        if (!status || !status.configured) {
            label.textContent = 'Push indisponível no servidor.';
            if (btn) btn.hidden = true;
            return;
        }

        var perm = Notification.permission;
        if (status.subscriptions > 0 && perm === 'granted') {
            label.textContent = 'Push ativo neste dispositivo (' + status.subscriptions + ' inscrição' + (status.subscriptions > 1 ? 'ões' : '') + ').';
            if (btn) {
                btn.hidden = false;
                btn.textContent = 'Reativar push';
            }
        } else if (perm === 'denied') {
            label.textContent = 'Permissão bloqueada — libere nas configurações do navegador/celular.';
            if (btn) btn.hidden = true;
        } else {
            label.textContent = 'Push ainda não ativado neste dispositivo.';
            if (btn) {
                btn.hidden = false;
                btn.innerHTML = '<i class="fas fa-bell me-1"></i> Ativar neste dispositivo';
            }
        }
        if (master && status.push_notify && perm === 'granted' && status.subscriptions === 0) {
            enablePush().catch(function () {});
        }
    }

    function bindPerfilPage() {
        var btn = document.getElementById('push-enable-btn');
        if (btn) {
            btn.addEventListener('click', function () {
                btn.disabled = true;
                enablePush()
                    .then(function () { return getStatus(); })
                    .then(updatePerfilUi)
                    .catch(function () {})
                    .finally(function () { btn.disabled = false; });
            });
        }
        getStatus().then(updatePerfilUi).catch(function () {});
    }

    function syncIfLoggedIn() {
        if (!supportsPush() || Notification.permission !== 'granted') return;
        getStatus().then(function (status) {
            if (!status.ok || !status.configured || !status.push_notify) return;
            if (status.subscriptions > 0) return;
            enablePush().catch(function () {});
        }).catch(function () {});
    }

    document.addEventListener('DOMContentLoaded', function () {
        if (document.getElementById('push-device-status')) bindPerfilPage();
        else syncIfLoggedIn();
    });

    window.SetSyncPush = {
        enable: enablePush,
        getStatus: getStatus,
    };
})();
