/**
 * Intercepta respostas HTTP 402 (limite de plano) e exibe modal de upgrade.
 */
(function () {
    const UPGRADE_URL = '/assinatura/planos';

    function showUpgradeModal(payload) {
        const msg = payload.mensagem || payload.erro || 'Limite do plano grátis atingido.';
        const url = payload.upgrade_url || UPGRADE_URL;
        let el = document.getElementById('planoLimiteModal');
        if (!el) {
            el = document.createElement('div');
            el.id = 'planoLimiteModal';
            el.className = 'modal fade';
            el.innerHTML =
                '<div class="modal-dialog modal-dialog-centered">' +
                '<div class="modal-content">' +
                '<div class="modal-header"><h5 class="modal-title">Upgrade necessário</h5>' +
                '<button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>' +
                '<div class="modal-body"><p id="planoLimiteMsg"></p></div>' +
                '<div class="modal-footer">' +
                '<a href="' + url + '" class="btn btn-primary">Ver planos</a>' +
                '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>' +
                '</div></div></div>';
            document.body.appendChild(el);
        }
        document.getElementById('planoLimiteMsg').textContent = msg;
        if (typeof bootstrap !== 'undefined') {
            new bootstrap.Modal(el).show();
        } else {
            alert(msg + '\n\n' + url);
        }
    }

    function showToast(msg, isError) {
        let t = document.getElementById('planoLimiteToast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'planoLimiteToast';
            t.className = 'position-fixed bottom-0 end-0 p-3';
            t.style.zIndex = '1080';
            document.body.appendChild(t);
        }
        t.innerHTML =
            '<div class="toast show align-items-center text-white border-0 ' +
            (isError ? 'bg-danger' : 'bg-success') +
            '" role="alert"><div class="d-flex"><div class="toast-body"></div></div></div>';
        t.querySelector('.toast-body').textContent = msg;
        setTimeout(function () { t.innerHTML = ''; }, 5000);
    }

    window.setSyncShowUpgrade = showUpgradeModal;
    window.setSyncShowToast = showToast;

    const origFetch = window.fetch;
    window.fetch = async function (...args) {
        const res = await origFetch.apply(this, args);
        if (res.status === 402) {
            try {
                const data = await res.clone().json();
                if (data.erro === 'limite_plano' || data.erro === 'plano_necessario') {
                    showUpgradeModal(data);
                }
            } catch (e) { /* ignore */ }
        }
        return res;
    };
})();
