/**
 * Página pública de letras: menu + músicas, atualização em tempo real.
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

  function pollUrl() {
    if (cfg.pollUrl) return cfg.pollUrl;
    return (
      "/setlists/letras/" +
      encodeURIComponent(cfg.token) +
      "/dados.json"
    );
  }

  function renderMenu(songs) {
    var items = songs
      .map(function (song) {
        var artist = song.artista
          ? '<span class="pl-menu-artist">' + esc(song.artista) + "</span>"
          : "";
        var vox = song.vocalist_name
          ? '<span class="pl-menu-vox">' + esc(song.vocalist_name) + "</span>"
          : "";
        var key = song.display_key
          ? '<span class="pl-menu-key">' + esc(song.display_key) + "</span>"
          : "";
        return (
          '<li class="pl-menu-item">' +
          '<a href="#musica-' +
          song.index +
          '" class="pl-menu-link">' +
          '<span class="pl-menu-num">' +
          song.index +
          "</span>" +
          '<span class="pl-menu-text">' +
          '<span class="pl-menu-song">' +
          esc(song.titulo) +
          "</span>" +
          artist +
          vox +
          "</span>" +
          key +
          "</a></li>"
        );
      })
      .join("");

    return (
      '<nav class="pl-menu" id="menu" aria-label="Músicas da setlist">' +
      '<h2 class="pl-menu-title">Músicas</h2>' +
      '<ol class="pl-menu-list">' +
      items +
      "</ol></nav>"
    );
  }

  function renderSong(song) {
    var art = song.artista
      ? '<p class="pl-artist">' + esc(song.artista) + "</p>"
      : "";
    var meta = "";
    if (song.display_key) {
      meta +=
        '<span class="pl-key" title="Tom">Tom ' + esc(song.display_key) + "</span>";
    }
    if (song.vocalist_name) {
      meta += '<span class="pl-vox">' + esc(song.vocalist_name) + "</span>";
    }
    var body = song.lyrics
      ? '<pre class="pl-lyrics">' + esc(song.lyrics) + "</pre>"
      : '<p class="pl-empty-song">Letra não disponível para esta música.</p>';

    return (
      '<article class="pl-song" id="musica-' +
      song.index +
      '">' +
      '<header class="pl-song-hd">' +
      '<span class="pl-num">' +
      song.index +
      "</span>" +
      '<div class="pl-song-titles">' +
      "<h2>" +
      esc(song.titulo) +
      "</h2>" +
      art +
      "</div>" +
      '<div class="pl-song-meta">' +
      meta +
      "</div>" +
      "</header>" +
      '<p class="pl-back">' +
      '<a href="#menu" class="pl-back-link">' +
      '<i class="pl-back-icon" aria-hidden="true">↑</i> Voltar ao menu</a></p>' +
      body +
      "</article>"
    );
  }

  function renderMain(songs) {
    return renderMenu(songs) + songs.map(renderSong).join("");
  }

  function applyPayload(data) {
    if (bandEl && data.band && data.band.name) {
      bandEl.textContent = data.band.name;
    }
    if (titleEl && data.setlist) {
      titleEl.textContent = data.setlist.name || "";
      document.title = (data.setlist.name || "Setlist") + " — Letras";
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
        "Letras · " + songCountLabel(n) + " · atualiza automaticamente";
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

    var hash = window.location.hash;
    mainEl.innerHTML = renderMain(data.songs);
    if (hash) {
      var target = document.querySelector(hash);
      if (target) {
        target.scrollIntoView({ behavior: "instant", block: "start" });
      }
    }
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
      pollUrl() + "?r=" + encodeURIComponent(revision || "");

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
