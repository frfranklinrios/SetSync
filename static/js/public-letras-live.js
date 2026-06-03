/**
 * Atualização em tempo real da página pública (lista de músicas).
 */
(function () {
  "use strict";

  var cfg = window.PUBLIC_LETRAS;
  if (!cfg || !cfg.token) return;

  var POLL_MS = 4000;
  var revision = cfg.revision || "";
  var mainEl = document.getElementById("pl-songs-root");
  var hintEl = document.getElementById("pl-hint");
  var titleEl = document.querySelector(".pl-title");
  var descEl = document.querySelector(".pl-desc");
  var bandEl = document.querySelector(".pl-eyebrow");
  var statusEl = document.getElementById("pl-live-status");
  var pollTimer = null;
  var inFlight = false;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function songCountLabel(n) {
    return n + " música" + (n === 1 ? "" : "s");
  }

  function renderSong(song) {
    var art = song.artista
      ? '<span class="pl-artist">' + esc(song.artista) + "</span>"
      : "";
    var meta = "";
    if (song.display_key) {
      meta +=
        '<span class="pl-key" title="Tom">Tom ' + esc(song.display_key) + "</span>";
    }
    if (song.vocalist_name) {
      meta += '<span class="pl-vox">' + esc(song.vocalist_name) + "</span>";
    }

    return (
      '<li class="pl-setlist-item" id="musica-' +
      song.index +
      '">' +
      '<span class="pl-num">' +
      song.index +
      "</span>" +
      '<div class="pl-song-titles">' +
      '<span class="pl-song-title">' +
      esc(song.titulo) +
      "</span>" +
      art +
      "</div>" +
      '<div class="pl-song-meta">' +
      meta +
      "</div>" +
      "</li>"
    );
  }

  function applyPayload(data) {
    if (bandEl && data.band && data.band.name) {
      bandEl.textContent = data.band.name;
    }
    if (titleEl && data.setlist) {
      titleEl.textContent = data.setlist.name || "";
      document.title = (data.setlist.name || "Setlist") + " — Setlist";
    }
    if (descEl && data.setlist) {
      var d = (data.setlist.description || "").trim();
      if (d) {
        descEl.textContent = d;
        descEl.style.display = "";
      } else {
        descEl.textContent = "";
        descEl.style.display = "none";
      }
    }
    if (hintEl) {
      var n = (data.songs && data.songs.length) || 0;
      hintEl.textContent =
        "Programação do show · " +
        songCountLabel(n) +
        " · atualiza automaticamente";
    }
    if (!mainEl) return;

    if (!data.songs || !data.songs.length) {
      mainEl.innerHTML =
        '<div class="pl-empty">' +
        "<p>Nenhuma música na setlist no momento.</p>" +
        '<p class="pl-empty-sub">A lista aparece aqui quando a banda adicionar músicas.</p>' +
        "</div>";
      return;
    }

    mainEl.innerHTML =
      '<ol class="pl-setlist">' +
      data.songs.map(renderSong).join("") +
      "</ol>";
  }

  function flashUpdated() {
    if (!statusEl) return;
    statusEl.classList.add("is-visible");
    clearTimeout(flashUpdated._t);
    flashUpdated._t = setTimeout(function () {
      statusEl.classList.remove("is-visible");
    }, 2200);
  }

  function poll() {
    if (inFlight || document.hidden) return;
    inFlight = true;
    var url =
      "/setlists/letras/" +
      encodeURIComponent(cfg.token) +
      "/dados.json?r=" +
      encodeURIComponent(revision || "");

    fetch(url, { credentials: "omit", cache: "no-store" })
      .then(function (res) {
        if (res.status === 404) {
          if (mainEl) {
            mainEl.innerHTML =
              '<div class="pl-empty pl-empty-error">' +
              "<p>Link indisponível ou desativado.</p>" +
              "</div>";
          }
          if (pollTimer) clearInterval(pollTimer);
          return null;
        }
        if (!res.ok) return null;
        return res.json();
      })
      .then(function (data) {
        if (!data || !data.ok) return;
        if (data.revision && data.revision !== revision) {
          revision = data.revision;
          applyPayload(data);
          flashUpdated();
        }
      })
      .catch(function () {})
      .finally(function () {
        inFlight = false;
      });
  }

  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) poll();
  });

  pollTimer = setInterval(poll, POLL_MS);
  setTimeout(poll, 1500);
})();
