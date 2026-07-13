/**
 * Modal de upgrade ao atingir limite do plano Grátis (HTTP 402).
 * Fonte única — plano-limite.js delega para cá.
 */
(function () {
    const UPGRADE_URL = '/assinatura/planos';
    const PRO_FEATURES = [
        'Músicas, setlists e integrantes ilimitados',
        'Exportar setlist em PDF para o ensaio',
        'Sem anúncios no Modo Tocar',
        'Cancele quando quiser · Mercado Pago',
    ];

    function buildModal() {
        let el = document.getElementById('upgradeModal');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'upgradeModal';
        el.className = 'modal fade';
        el.setAttribute('tabindex', '-1');
        el.setAttribute('aria-labelledby', 'upgradeModalTitle');
        el.innerHTML =
            '<div class="modal-dialog modal-dialog-centered">' +
            '<div class="modal-content">' +
            '<div class="modal-header border-0 pb-0">' +
            '<h5 class="modal-title fw-bold" id="upgradeModalTitle">Continue com o Pro</h5>' +
            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>' +
            '</div>' +
            '<div class="modal-body">' +
            '<p id="upgradeModalMsg" class="text-muted mb-2"></p>' +
            '<p class="small mb-3"><strong>Pro — R$ 29/mês</strong> por banda · anual sai ~R$ 21/mês</p>' +
            '<p class="fw-semibold mb-2">No Pro você libera:</p>' +
            '<ul id="upgradeModalFeatures" class="list-unstyled mb-0"></ul>' +
            '</div>' +
            '<div class="modal-footer border-0 flex-column flex-sm-row gap-2">' +
            '<a id="upgradeModalCta" href="' + UPGRADE_URL + '" class="btn btn-primary w-100 w-sm-auto">' +
            'Assinar Pro — R$ 29/mês</a>' +
            '<button type="button" class="btn btn-outline-secondary w-100 w-sm-auto" data-bs-dismiss="modal">' +
            'Agora não</button>' +
            '</div></div></div>';
        document.body.appendChild(el);
        const ul = el.querySelector('#upgradeModalFeatures');
        PRO_FEATURES.forEach(function (f) {
            const li = document.createElement('li');
            li.className = 'mb-1';
            li.textContent = '✓ ' + f;
            ul.appendChild(li);
        });
        return el;
    }

    function showUpgradeModal(payload) {
        payload = payload || {};
        const el = buildModal();
        const recurso = payload.recurso || 'recursos';
        const limite = payload.limite != null ? payload.limite : '';
        const msg = payload.mensagem || (
            'Você atingiu o limite de ' + limite + ' ' + recurso + ' no plano Grátis.'
        );
        document.getElementById('upgradeModalMsg').textContent = msg;
        const url = payload.upgrade_url || UPGRADE_URL;
        const cta = document.getElementById('upgradeModalCta');
        cta.href = url;
        cta.textContent = payload.cta_label || 'Assinar Pro — R$ 29/mês';
        if (typeof bootstrap !== 'undefined') {
            bootstrap.Modal.getOrCreateInstance(el).show();
        } else {
            alert(msg + '\n\n' + url);
        }
    }

    window.setSyncShowUpgrade = showUpgradeModal;

    const origFetch = window.fetch;
    window.fetch = async function (...args) {
        const res = await origFetch.apply(this, args);
        if (res.status === 402) {
            try {
                const data = await res.clone().json();
                if (
                    data.status === 'limite_atingido' ||
                    data.erro === 'limite_plano' ||
                    data.erro === 'plano_necessario'
                ) {
                    showUpgradeModal(data);
                }
            } catch (e) { /* ignore */ }
        }
        return res;
    };
})();
