/**
 * Ícones e clique do botão de tema (toggle em index.html <head>).
 */
(function () {
  "use strict";

  function syncThemeIcons() {
    var dark = document.documentElement.getAttribute("data-theme") !== "light";
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.innerHTML = dark
        ? '<i class="fas fa-sun" aria-hidden="true"></i>'
        : '<i class="fas fa-moon" aria-hidden="true"></i>';
      btn.setAttribute(
        "aria-label",
        dark ? "Ativar tema claro" : "Ativar tema escuro"
      );
      btn.setAttribute("title", dark ? "Tema claro" : "Tema escuro");
    });
  }

  window.__setSyncSyncThemeIcons = syncThemeIcons;

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    if (typeof window.toggleTheme === "function") {
      window.toggleTheme();
    }
  });

  document.addEventListener("setsync-themechange", syncThemeIcons);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", syncThemeIcons);
  } else {
    syncThemeIcons();
  }
})();
