/**
 * Pós-Modo Tocar: micro-CSAT → (opcional) share/convidar.
 * CSAT: 1× por conta (servidor). Share: cooldown local 7d após ~45s no palco.
 * API: SetSyncPlayShare.tryExit(url)
 */
(function (global) {
  'use strict';

  var STORAGE_KEY = 'setsync.play.sharePrompt.v1';
  var MIN_MS = 45 * 1000;
  var COOLDOWN_MS = 7 * 24 * 60 * 60 * 1000;
  var started = Date.now();
  var pendingExit = null;
  var csatDone = false;

  function readBoot() {
    if (global.SetSyncPlayBoot && global.SetSyncPlayBoot.readBootConfig) {
      return global.SetSyncPlayBoot.readBootConfig('play-boot-config') || {};
    }
    var el = document.getElementById('play-boot-config');
    if (!el) return {};
    try {
      return JSON.parse(el.textContent || '{}') || {};
    } catch (e) {
      return {};
    }
  }

  function canShowShare() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return true;
      var t = parseInt(raw, 10);
      if (!t) return true;
      return Date.now() - t > COOLDOWN_MS;
    } catch (e) {
      return true;
    }
  }

  function markShareShown() {
    try {
      localStorage.setItem(STORAGE_KEY, String(Date.now()));
    } catch (e) {}
  }

  function waUrl(text) {
    return 'https://wa.me/?text=' + encodeURIComponent(text);
  }

  function postJson(url, body) {
    var headers = { 'Content-Type': 'application/json', Accept: 'application/json' };
    if (global.csrfToken) headers['X-CSRFToken'] = global.csrfToken;
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: headers,
      body: JSON.stringify(body || {}),
    }).catch(function () {});
  }

  function buildCsatOverlay(boot) {
    var existing = document.getElementById('play-csat-prompt');
    if (existing) return existing;

    var root = document.createElement('div');
    root.id = 'play-csat-prompt';
    root.className = 'play-share-prompt';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-labelledby', 'play-csat-title');
    root.innerHTML =
      '<div class="play-share-card">' +
      '<button type="button" class="play-share-close" aria-label="Fechar" data-csat-skip>&times;</button>' +
      '<p class="play-share-kicker">Feedback rápido</p>' +
      '<h2 id="play-csat-title">Como foi o ensaio com o Uníssono hoje?</h2>' +
      '<p class="play-share-lead">Uma resposta — leva 2 segundos.</p>' +
      '<div class="play-share-actions">' +
      '<button type="button" class="btn btn-primary" data-csat="excelente">Excelente</button>' +
      '<button type="button" class="btn btn-outline-secondary" data-csat="problemas">Teve problemas</button>' +
      '<button type="button" class="btn btn-outline-secondary" data-csat="nao_usei">Não usei de verdade</button>' +
      '</div>' +
      '<button type="button" class="play-share-skip" data-csat-skip>Pular</button>' +
      '</div>';

    document.body.appendChild(root);

    function finishCsat(answer) {
      csatDone = true;
      var url = boot.playCsatUrl || '/ajuda/play-csat';
      if (answer) postJson(url, { answer: answer });
      root.classList.remove('is-open');
      continueExitFlow(boot);
    }

    root.addEventListener('click', function (e) {
      var ansBtn = e.target.closest && e.target.closest('[data-csat]');
      if (ansBtn) {
        e.preventDefault();
        finishCsat(ansBtn.getAttribute('data-csat'));
        return;
      }
      if (e.target === root || (e.target.closest && e.target.closest('[data-csat-skip]'))) {
        e.preventDefault();
        finishCsat(null);
      }
    });

    return root;
  }

  function buildShareOverlay(boot) {
    var existing = document.getElementById('play-share-prompt');
    if (existing) return existing;

    var bandName = boot.bandName || 'minha banda';
    var membersUrl = boot.membersUrl || '';
    var inviteUrl = boot.bandInviteUrl || membersUrl || '';
    var indicarUrl = boot.indicarUrl || '/assinatura/voucher/indicar';
    var siteUrl = boot.siteUrl || 'https://unissono.app';
    var canInvite = !!inviteUrl && !!boot.canEdit;

    var inviteMsg =
      'Bora usar o Uníssono no ensaio da banda "' +
      bandName +
      '"? Cifras no tom certo + Modo Tocar offline. Entra por este link: ' +
      (inviteUrl || siteUrl);
    var referMsg =
      'App de cifras/setlist pro ensaio — Modo Tocar offline. Grátis + 30 dias Pro sem cartão: ' +
      siteUrl;

    var root = document.createElement('div');
    root.id = 'play-share-prompt';
    root.className = 'play-share-prompt';
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-labelledby', 'play-share-title');
    root.innerHTML =
      '<div class="play-share-card">' +
      '<button type="button" class="play-share-close" aria-label="Fechar" data-share-skip>&times;</button>' +
      '<p class="play-share-kicker">Ensaio bom de espalhar</p>' +
      '<h2 id="play-share-title">Leve a banda (ou indique outra)</h2>' +
      '<p class="play-share-lead">Você não precisa vender o app — um toque no WhatsApp basta.</p>' +
      '<div class="play-share-actions">' +
      (canInvite
        ? '<a class="btn btn-primary" data-share-go href="' +
          waUrl(inviteMsg) +
          '" target="_blank" rel="noopener">' +
          '<i class="fab fa-whatsapp me-1" aria-hidden="true"></i>Convidar no WhatsApp</a>' +
          '<a class="btn btn-outline-secondary" data-share-go href="' +
          (membersUrl || inviteUrl) +
          '">Abrir link de convite</a>'
        : '') +
      '<a class="btn btn-outline-success" data-share-go href="' +
      indicarUrl +
      '"><i class="fas fa-gift me-1" aria-hidden="true"></i>Indicar e ganhar 3 meses Pro</a>' +
      '<a class="btn btn-outline-secondary btn-sm" data-share-go href="' +
      waUrl(referMsg) +
      '" target="_blank" rel="noopener">Mandar o app no WhatsApp</a>' +
      '</div>' +
      '<button type="button" class="play-share-skip" data-share-skip>Agora não · sair</button>' +
      '</div>';

    document.body.appendChild(root);

    root.addEventListener('click', function (e) {
      if (e.target === root || (e.target.closest && e.target.closest('[data-share-skip]'))) {
        e.preventDefault();
        closeAndExit();
        return;
      }
      if (e.target.closest && e.target.closest('[data-share-go]')) {
        markShareShown();
      }
    });

    return root;
  }

  function goExit(url) {
    window.location.href = url || '/';
  }

  function closeAndExit() {
    var root = document.getElementById('play-share-prompt');
    if (root) root.classList.remove('is-open');
    goExit(pendingExit);
  }

  function continueExitFlow(boot) {
    if (canShowShare() && Date.now() - started >= MIN_MS) {
      var share = buildShareOverlay(boot);
      share.classList.add('is-open');
      markShareShown();
      return;
    }
    goExit(pendingExit);
  }

  function tryExit(exitHref) {
    var boot = readBoot();
    var dest = exitHref || boot.exitUrl || '/';
    pendingExit = dest;

    if (boot.showPlayCsat && !csatDone) {
      var csat = buildCsatOverlay(boot);
      csat.classList.add('is-open');
      return true;
    }

    if (!canShowShare() || Date.now() - started < MIN_MS) {
      goExit(dest);
      return true;
    }
    var root = buildShareOverlay(boot);
    root.classList.add('is-open');
    markShareShown();
    return true;
  }

  function install() {
    document.addEventListener('click', function (e) {
      var exitBtn = e.target.closest && e.target.closest('a.pb-exit');
      if (!exitBtn) return;
      e.preventDefault();
      tryExit(exitBtn.getAttribute('href'));
    });
  }

  global.SetSyncPlayShare = { tryExit: tryExit };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install);
  } else {
    install();
  }
})(window);
