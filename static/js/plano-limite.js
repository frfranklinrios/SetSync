/**
 * Compat: toasts + delegação do 402 para modal-upgrade.js (fonte única de upgrade).
 */
(function () {
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

    window.setSyncShowToast = showToast;

    // Se modal-upgrade ainda não carregou, fallback mínimo
    if (typeof window.setSyncShowUpgrade !== 'function') {
        window.setSyncShowUpgrade = function (payload) {
            const msg = (payload && (payload.mensagem || payload.erro)) || 'Limite do plano grátis atingido.';
            const url = (payload && payload.upgrade_url) || '/assinatura/planos';
            if (confirm(msg + '\n\nAbrir planos?')) {
                window.location.href = url;
            }
        };
    }
})();
