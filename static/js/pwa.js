/**
 * SetSync PWA — registro do service worker, instalação (Android/desktop) e guia iOS.
 */
(function () {
    'use strict';

    var deferredPrompt = null;
    var installBtn = null;
    var iosModal = null;

    function isIOS() {
        var ua = navigator.userAgent || '';
        if (/iPad|iPhone|iPod/.test(ua)) return true;
        return navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1;
    }

    function isStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches
            || window.navigator.standalone === true;
    }

    function isInAppBrowser() {
        var ua = (navigator.userAgent || '').toLowerCase();
        return /(fban|fbav|instagram|line\/|twitter|linkedinapp|snapchat|whatsapp)/i.test(ua);
    }

    function canRegisterSW() {
        return 'serviceWorker' in navigator
            && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1');
    }

    function registerServiceWorker() {
        if (!canRegisterSW()) return;

        navigator.serviceWorker.register('/sw.js', { scope: '/' })
            .then(function (reg) {
                reg.addEventListener('updatefound', function () {
                    var nw = reg.installing;
                    if (!nw) return;
                    nw.addEventListener('statechange', function () {
                        if (nw.state === 'installed' && navigator.serviceWorker.controller) {
                            nw.postMessage('skipWaiting');
                        }
                    });
                });
            })
            .catch(function (err) {
                console.warn('SetSync SW:', err);
            });

        navigator.serviceWorker.addEventListener('controllerchange', function () {
            if (window.__setsyncSwReloading) return;
            window.__setsyncSwReloading = true;
            window.location.reload();
        });
    }

    function showInstallButton() {
        if (installBtn) installBtn.classList.add('show');
    }

    function hideInstallButton() {
        if (installBtn) installBtn.classList.remove('show');
    }

    function openIosModal() {
        if (!iosModal && window.bootstrap) {
            iosModal = new bootstrap.Modal(document.getElementById('pwa-ios-modal'));
        }
        if (iosModal) iosModal.show();
        else {
            alert(
                'No iPhone/iPad (Safari):\n\n'
                + '1. Toque em Compartilhar (ícone com seta para cima)\n'
                + '2. Role e escolha "Adicionar à Tela de Início"\n'
                + '3. Confirme em Adicionar\n\n'
                + 'Use o Safari — no Chrome do iOS a instalação não funciona como app.'
            );
        }
    }

    function updateInstallVisibility() {
        if (isStandalone()) {
            hideInstallButton();
            return;
        }
        if (deferredPrompt) {
            showInstallButton();
            return;
        }
        if (isIOS() && !isInAppBrowser()) {
            showInstallButton();
        }
    }

    window.installPWA = function () {
        if (isStandalone()) return;

        if (isInAppBrowser()) {
            alert('Abra este site no Safari (Compartilhar → Abrir no Safari) para instalar o SetSync na tela inicial.');
            return;
        }

        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(function () {
                deferredPrompt = null;
                hideInstallButton();
            });
            return;
        }

        if (isIOS()) {
            openIosModal();
            return;
        }

        alert('Use o menu do navegador e escolha "Instalar aplicativo" ou "Adicionar à tela inicial".');
    };

    document.addEventListener('DOMContentLoaded', function () {
        installBtn = document.getElementById('install-btn');
        registerServiceWorker();
        updateInstallVisibility();
    });

    window.addEventListener('beforeinstallprompt', function (e) {
        e.preventDefault();
        deferredPrompt = e;
        updateInstallVisibility();
    });

    window.addEventListener('appinstalled', function () {
        deferredPrompt = null;
        hideInstallButton();
    });
})();
