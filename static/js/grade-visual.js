/**
 * Grade harmônica visual + conversão texto ↔ JSON (formato SetSync).
 */
(function (global) {
  function escHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function flatToPartes(flat) {
    if (!Array.isArray(flat) || !flat.length) return [];
    var hasParte = flat.some(function (c) {
      return c && c.parte != null && String(c.parte).trim() !== "";
    });
    var map = {};
    var order = [];

    flat.forEach(function (item) {
      var key =
        hasParte && item.parte ? String(item.parte).toUpperCase() : "__UNICO__";
      if (!map[key]) {
        map[key] = {
          nome: key === "__UNICO__" ? "Progressão" : "Parte " + key,
          compassos: [],
        };
        order.push(key);
      }
      map[key].compassos.push({
        secao: item.secao || null,
        acordes: (item.acordes || []).slice(),
      });
    });

    return order.map(function (k) {
      return map[k];
    });
  }

  function renderBar(acordes) {
    var cells = (acordes || []).map(function (a) {
      var t = String(a || "").trim();
      if (t === "%") return '<span class="grade-visual-chord repeat">%</span>';
      return '<span class="grade-visual-chord">' + escHtml(t) + "</span>";
    });
    return (
      '<span class="grade-visual-bar">' +
      cells.join('<span class="grade-visual-sep">·</span>') +
      "</span>"
    );
  }

  function renderBloco(compassos) {
    return (
      '<div class="grade-visual-bloco">' +
      compassos.map(function (c) {
        return renderBar(c.acordes);
      }).join("") +
      "</div>"
    );
  }

  function render(el, data, opts) {
    if (!el) return;
    opts = opts || {};
    var partes = Array.isArray(data) && data[0] && data[0].compassos
      ? data
      : flatToPartes(data);

    if (!partes.length) {
      el.innerHTML = '<div class="grade-visual-header">Sem grade.</div>';
      return;
    }

    var header = opts.title || "Grade Harmônica";
    if (opts.compasso) header += " · Compasso " + escHtml(opts.compasso);
    var html = '<div class="grade-visual-root">';
    html += '<div class="grade-visual-header">' + header + "</div>";

    partes.forEach(function (parte) {
      html +=
        '<div class="grade-visual-parte"><div class="grade-visual-parte-nome">' +
        escHtml(parte.nome) +
        "</div>";
      var bloco = [];
      (parte.compassos || []).forEach(function (c) {
        if (c.secao) {
          if (bloco.length) {
            html += renderBloco(bloco);
            bloco = [];
          }
          html += '<div class="grade-visual-secao">' + escHtml(c.secao) + "</div>";
        }
        bloco.push(c);
      });
      if (bloco.length) html += renderBloco(bloco);
      html += "</div>";
    });
    html += "</div>";
    el.innerHTML = html;
  }

  function jsonToText(data) {
    if (!Array.isArray(data) || !data.length) return "";
    var partes = flatToPartes(data);
    var lines = [];
    partes.forEach(function (parte) {
      if (parte.nome && parte.nome !== "Progressão") {
        lines.push(parte.nome);
      }
      (parte.compassos || []).forEach(function (c) {
        if (c.secao) lines.push("  ▸ " + c.secao);
        var ac = (c.acordes || []).length ? c.acordes : ["%"];
        lines.push(ac.join(" "));
      });
      lines.push("");
    });
    return lines.join("\n").trim();
  }

  function parseGradeTextToJson(text) {
    var lines = String(text || "").split("\n");
    var out = [];
    var compasso = 1;
    var currentParte = "";
    var pendingSecao = null;

    lines.forEach(function (raw) {
      var line = String(raw || "").trim();
      if (!line) return;
      if (/^Partes\s+detectadas/i.test(line)) return;
      if (/^Grade\s+Harmonica/i.test(line)) return;
      if (/^Compasso:/i.test(line)) return;
      if (/^Pulsos:/i.test(line)) return;

      var parteMatch = line.match(/^Parte\s+([A-Za-z0-9_-]+)/i);
      if (parteMatch) {
        currentParte = String(parteMatch[1] || "").toUpperCase();
        pendingSecao = null;
        return;
      }

      var secaoMatch = line.match(/^▸\s*(.+)$/);
      if (secaoMatch) {
        pendingSecao = secaoMatch[1].trim();
        return;
      }

      function pushBar(acordes) {
        if (!acordes.length) return;
        var item = { compasso: compasso++, acordes: acordes };
        if (currentParte) item.parte = currentParte;
        if (pendingSecao) {
          item.secao = pendingSecao;
          pendingSecao = null;
        }
        out.push(item);
      }

      if (line.indexOf("|") !== -1) {
        line
          .split("|")
          .map(function (s) {
            return s.trim();
          })
          .filter(function (s) {
            return s.length > 0;
          })
          .forEach(function (bar) {
            var acordes = bar.split(/\s+/).filter(Boolean);
            pushBar(acordes);
          });
        return;
      }

      var acordes = line.split(/\s+/).filter(Boolean);
      if (acordes.length) pushBar(acordes);
    });

    return out.length ? out : null;
  }

  global.SetSyncGradeVisual = {
    escHtml: escHtml,
    flatToPartes: flatToPartes,
    render: render,
    jsonToText: jsonToText,
    parseGradeTextToJson: parseGradeTextToJson,
  };
})(window);
