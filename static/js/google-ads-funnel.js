(function () {
    'use strict';

    var cfg = window.__setsyncGoogleAds;
    if (!cfg || !cfg.events || !cfg.events.length) return;

    function fireGtagConversion(sendTo, value, currency) {
        if (typeof gtag !== 'function' || !sendTo) return;
        gtag('event', 'conversion', {
            send_to: sendTo,
            value: value,
            currency: currency || 'BRL',
        });
        if (cfg.debug) console.info('[SetSync] Ads conversion', sendTo);
    }

    function fireGtagEvent(name, params) {
        if (typeof gtag !== 'function') return;
        gtag('event', name, params || {});
        if (cfg.debug) console.info('[SetSync] gtag event', name, params);
    }

    function fireDataLayer(event, extra) {
        window.dataLayer = window.dataLayer || [];
        var payload = Object.assign({ event: event }, extra || {});
        window.dataLayer.push(payload);
        if (cfg.debug) console.info('[SetSync] dataLayer', payload);
    }

    cfg.events.forEach(function (ev) {
        var value = (cfg.funnelValues && cfg.funnelValues[ev]) || 1;
        var currency = cfg.currency || 'BRL';
        if (cfg.useGtm) {
            fireDataLayer('setsync_' + ev, { conversion_value: value, conversion_currency: currency });
            return;
        }
        var sendTo = cfg.funnelLabels && cfg.funnelLabels[ev];
        if (sendTo) {
            fireGtagConversion(sendTo, value, currency);
        } else {
            fireGtagEvent('setsync_' + ev, { value: value, currency: currency });
        }
    });
})();
