(function () {
    if (window.__ssImageLightboxInit) return;
    window.__ssImageLightboxInit = true;

    var MIN_SCALE = 0.35;
    var MAX_SCALE = 4;
    var ZOOM_STEP = 0.35;

    var dialog = document.createElement('dialog');
    dialog.className = 'ss-image-lightbox';
    dialog.setAttribute('aria-label', 'Imagem ampliada');
    dialog.innerHTML =
        '<div class="ss-image-lightbox__chrome">' +
        '<button type="button" class="ss-image-lightbox__close" aria-label="Fechar">' +
        '<i class="fas fa-times" aria-hidden="true"></i></button>' +
        '<div class="ss-image-lightbox__zoom" aria-label="Zoom">' +
        '<button type="button" class="ss-image-lightbox__zoom-btn" data-zoom="out" aria-label="Diminuir zoom">−</button>' +
        '<span class="ss-image-lightbox__zoom-label">100%</span>' +
        '<button type="button" class="ss-image-lightbox__zoom-btn" data-zoom="in" aria-label="Aumentar zoom">+</button>' +
        '<button type="button" class="ss-image-lightbox__zoom-btn ss-image-lightbox__zoom-btn--fit" data-zoom="fit" aria-label="Ajustar à tela">Ajustar</button>' +
        '</div>' +
        '</div>' +
        '<div class="ss-image-lightbox__stage" tabindex="-1">' +
        '<figure class="ss-image-lightbox__figure">' +
        '<img class="ss-image-lightbox__img" alt="" draggable="false">' +
        '</figure>' +
        '</div>' +
        '<p class="ss-image-lightbox__caption"></p>' +
        '<p class="ss-image-lightbox__hint">Arraste para mover · pinça ou +/− para zoom · duplo toque amplia</p>';
    document.body.appendChild(dialog);

    var stage = dialog.querySelector('.ss-image-lightbox__stage');
    var imgEl = dialog.querySelector('.ss-image-lightbox__img');
    var captionEl = dialog.querySelector('.ss-image-lightbox__caption');
    var zoomLabel = dialog.querySelector('.ss-image-lightbox__zoom-label');
    var closeBtn = dialog.querySelector('.ss-image-lightbox__close');
    var lastTrigger = null;

    var scale = 1;
    var panX = 0;
    var panY = 0;
    var dragging = false;
    var dragStartX = 0;
    var dragStartY = 0;
    var panStartX = 0;
    var panStartY = 0;
    var pinchStartDist = 0;
    var pinchStartScale = 1;
    var lastTap = 0;

    function clampScale(value) {
        return Math.min(MAX_SCALE, Math.max(MIN_SCALE, value));
    }

    function stageSize() {
        return { w: stage.clientWidth, h: stage.clientHeight };
    }

    function imageNatural() {
        return {
            w: imgEl.naturalWidth || 1,
            h: imgEl.naturalHeight || 1,
        };
    }

    function computeFitScale() {
        var nat = imageNatural();
        var st = stageSize();
        if (!st.w || !st.h || !nat.w || !nat.h) return 1;

        var pad = 16;
        var availW = st.w - pad;
        var availH = st.h - pad;
        var aspect = nat.w / nat.h;
        var scaleW = availW / nat.w;
        var scaleH = availH / nat.h;

        // Panorâmicas (ex.: financeiro): prioriza legibilidade — ocupa boa altura da tela.
        if (aspect >= 1.35) {
            var targetH = availH * 0.82;
            var byHeight = targetH / nat.h;
            var byWidth = availW / nat.w;
            return clampScale(Math.max(byWidth, Math.min(byHeight, byHeight * 1.35)));
        }

        // Retrato (ex.: celular): cabe na altura sem cortar.
        return clampScale(Math.min(scaleW, scaleH));
    }

    function applyTransform() {
        imgEl.style.transform =
            'translate3d(' + panX + 'px,' + panY + 'px,0) scale(' + scale + ')';
        if (zoomLabel) {
            zoomLabel.textContent = Math.round(scale * 100) + '%';
        }
    }

    function centerImage() {
        var nat = imageNatural();
        var st = stageSize();
        panX = (st.w - nat.w * scale) / 2;
        panY = (st.h - nat.h * scale) / 2;
        applyTransform();
    }

    function setScale(next, focalX, focalY) {
        var prev = scale;
        scale = clampScale(next);
        if (focalX == null || focalY == null) {
            var st = stageSize();
            focalX = st.w / 2;
            focalY = st.h / 2;
        }
        var ratio = scale / prev;
        panX = focalX - (focalX - panX) * ratio;
        panY = focalY - (focalY - panY) * ratio;
        applyTransform();
    }

    function resetView(fit) {
        scale = fit ? computeFitScale() : 1;
        centerImage();
    }

    function open(trigger) {
        var src = trigger.getAttribute('data-lightbox-src');
        if (!src) return;
        lastTrigger = trigger;
        var alt = trigger.getAttribute('data-lightbox-alt') || '';
        var caption = trigger.getAttribute('data-lightbox-caption') || '';
        imgEl.alt = alt;
        captionEl.textContent = caption;
        captionEl.hidden = !caption;

        function onReady() {
            resetView(true);
            if (typeof dialog.showModal === 'function') {
                dialog.showModal();
            }
            stage.focus({ preventScroll: true });
        }

        imgEl.onload = onReady;
        imgEl.src = src;
        if (imgEl.complete && imgEl.naturalWidth) onReady();
    }

    function close() {
        if (!dialog.open) return;
        dialog.close();
        imgEl.removeAttribute('src');
        imgEl.onload = null;
        scale = 1;
        panX = 0;
        panY = 0;
        if (lastTrigger && typeof lastTrigger.focus === 'function') {
            lastTrigger.focus();
        }
        lastTrigger = null;
    }

    function pointerDown(clientX, clientY) {
        dragging = true;
        dragStartX = clientX;
        dragStartY = clientY;
        panStartX = panX;
        panStartY = panY;
        stage.classList.add('is-dragging');
    }

    function pointerMove(clientX, clientY) {
        if (!dragging) return;
        panX = panStartX + (clientX - dragStartX);
        panY = panStartY + (clientY - dragStartY);
        applyTransform();
    }

    function pointerUp() {
        dragging = false;
        stage.classList.remove('is-dragging');
    }

    function touchDistance(touches) {
        var dx = touches[0].clientX - touches[1].clientX;
        var dy = touches[0].clientY - touches[1].clientY;
        return Math.hypot(dx, dy);
    }

    document.addEventListener('click', function (event) {
        var trigger = event.target.closest('[data-lightbox-src]');
        if (!trigger) return;
        event.preventDefault();
        open(trigger);
    });

    closeBtn.addEventListener('click', close);

    dialog.addEventListener('click', function (event) {
        if (event.target === dialog) close();
    });

    dialog.addEventListener('cancel', function (event) {
        event.preventDefault();
        close();
    });

    dialog.querySelectorAll('[data-zoom]').forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            event.stopPropagation();
            var action = btn.getAttribute('data-zoom');
            if (action === 'in') setScale(scale + ZOOM_STEP);
            else if (action === 'out') setScale(scale - ZOOM_STEP);
            else resetView(true);
        });
    });

    stage.addEventListener('mousedown', function (event) {
        if (event.button !== 0) return;
        event.preventDefault();
        pointerDown(event.clientX, event.clientY);
    });

    window.addEventListener('mousemove', function (event) {
        pointerMove(event.clientX, event.clientY);
    });

    window.addEventListener('mouseup', pointerUp);

    stage.addEventListener(
        'wheel',
        function (event) {
            if (!dialog.open) return;
            event.preventDefault();
            var delta = event.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP;
            setScale(scale + delta, event.offsetX, event.offsetY);
        },
        { passive: false }
    );

    stage.addEventListener(
        'touchstart',
        function (event) {
            if (!dialog.open) return;
            if (event.touches.length === 2) {
                pinchStartDist = touchDistance(event.touches);
                pinchStartScale = scale;
                dragging = false;
                return;
            }
            if (event.touches.length === 1) {
                var now = Date.now();
                if (now - lastTap < 300) {
                    event.preventDefault();
                    if (scale < computeFitScale() * 1.4) {
                        setScale(computeFitScale() * 2, event.touches[0].clientX, event.touches[0].clientY);
                    } else {
                        resetView(true);
                    }
                    lastTap = 0;
                    return;
                }
                lastTap = now;
                pointerDown(event.touches[0].clientX, event.touches[0].clientY);
            }
        },
        { passive: false }
    );

    stage.addEventListener(
        'touchmove',
        function (event) {
            if (!dialog.open) return;
            if (event.touches.length === 2) {
                event.preventDefault();
                var dist = touchDistance(event.touches);
                if (pinchStartDist > 0) {
                    setScale(pinchStartScale * (dist / pinchStartDist));
                }
                return;
            }
            if (event.touches.length === 1 && dragging) {
                event.preventDefault();
                pointerMove(event.touches[0].clientX, event.touches[0].clientY);
            }
        },
        { passive: false }
    );

    stage.addEventListener('touchend', pointerUp);

    imgEl.addEventListener('dblclick', function (event) {
        if (scale < computeFitScale() * 1.4) {
            setScale(computeFitScale() * 2, event.offsetX, event.offsetY);
        } else {
            resetView(true);
        }
    });

    window.addEventListener('resize', function () {
        if (dialog.open) resetView(true);
    });

    document.addEventListener('keydown', function (event) {
        if (!dialog.open) return;
        if (event.key === 'Escape') close();
        else if (event.key === '+' || event.key === '=') setScale(scale + ZOOM_STEP);
        else if (event.key === '-') setScale(scale - ZOOM_STEP);
        else if (event.key === '0') resetView(true);
    });
})();
