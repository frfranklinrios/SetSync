/**
 * Modal de upgrade ao atingir limite do plano Grátis (HTTP 402).
 */
(function () {
    const UPGRADE_URL = '/assinatura/planos';
    const PRO_FEATURES = [
        'Músicas, setlists e integrantes ilimitados',
        'Exportar setlist em PDF',
        'Sem anúncios',
        'Suporte prioritário',
    ];

    function buildModal() {
        let el = document.getElementById('upgradeModal');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'upgradeModal';
        el.className = 'modal fade';
        el.setAttribute('tabindex', '-1');
        el.innerHTML =
            '<div class="modal-dialog modal-dialog-centered">' +
            '<div class="modal-content">' +
            '<div class="modal-header border-0 pb-0">' +
            '<h5 class="modal-title fw-bold">Você chegou no limite do plano Grátis</h5>' +
            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>' +
            '</div>' +
            '<div class="modal-body">' +
            '<p id="upgradeModalMsg" class="text-muted mb-3"></p>' +
            '<p class="fw-semibold mb-2">No Pro você ganha:</p>' +
            '<ul id="upgradeModalFeatures" class="list-unstyled mb-0"></ul>' +
            '</div>' +
            '<div class="modal-footer border-0 flex-column flex-sm-row gap-2">' +
            '<a id="upgradeModalCta" href="' + UPGRADE_URL + '" class="btn btn-primary w-100 w-sm-auto">' +
            'Fazer upgrade para Pro — R$29/mês</a>' +
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
        const el = buildModal();
        const recurso = payload.recurso || 'recursos';
        const limite = payload.limite != null ? payload.limite : '';
        const msg = payload.mensagem || (
            'Você atingiu o limite de ' + limite + ' ' + recurso + ' no plano Grátis.'
        );
        document.getElementById('upgradeModalMsg').textContent = msg;
        const url = payload.upgrade_url || UPGRADE_URL;
        document.getElementById('upgradeModalCta').href = url;
        if (typeof bootstrap !== 'undefined') {
            const modal = bootstrap.Modal.getOrCreateInstance(el);
            modal.show();
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

    document.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape') {
            const el = document.getElementById('upgradeModal');
            if (el && typeof bootstrap !== 'undefined') {
                bootstrap.Modal.getInstance(el)?.hide();
            }
        }
    });
})();
