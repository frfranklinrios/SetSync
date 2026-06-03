/**
 * Converte colagem do Cifra Club (HTML ou texto com marcação) para o formato SetSync.
 */
(function (global) {
  "use strict";

  var CIFRACLUB_URL_RE =
    /^https?:\/\/(?:www\.)?cifraclub\.com\.br\/[a-z0-9\-]+\/[a-z0-9\-]+\/?/i;

  function normalizeClipboardHtml(html) {
    if (!html) return "";
    html = html.replace(/<script[\s\S]*?<\/script>/gi, "");
    html = html.replace(/<style[\s\S]*?<\/style>/gi, "");
    try {
      var doc = new DOMParser().parseFromString(html, "text/html");
      var pre =
        doc.querySelector("#cifra pre") ||
        doc.querySelector(".cifra_cnt pre") ||
        doc.querySelector("pre");
      if (pre) return pre.innerHTML;
      var cnt = doc.querySelector(".cifra_cnt") || doc.querySelector("#cifra");
      if (cnt) return cnt.innerHTML;
    } catch (e) {
      /* usa html bruto */
    }
    return html;
  }

  function textoBlocoTablatura(inner) {
    var texto = String(inner || "");
    texto = texto.replace(/<span\s+class=["']cnt["'][^>]*>/gi, "");
    texto = texto.replace(/<\/span>/gi, "");
    texto = texto.replace(/<[^>]+>/g, "");
    texto = texto.replace(/&nbsp;/g, " ").replace(/&#160;/g, " ");
    return texto
      .split("\n")
      .map(function (ln) {
        return ln.replace(/\s+$/, "");
      })
      .filter(function (ln) {
        return ln.trim().length > 0;
      })
      .join("\n");
  }

  function extrairTablaturasDoHtml(html) {
    return html.replace(
      /<span\s+class=["']tablatura["'][^>]*>([\s\S]*?)<\/span>/gi,
      function (_, inner) {
        var bloco = textoBlocoTablatura(inner);
        return bloco ? "\n" + bloco + "\n" : "";
      }
    );
  }

  function parseLinhaHtml(linhaHtml) {
    var posicoes = [];
    var texto = "";
    var temAcordes = false;
    var re =
      /<span\s+data-chord="([^"]+)"[^>]*>[\s\S]*?<\/span>|<b>([^<]+)<\/b>|<i>([\s\S]*?)<\/i>|([^<]+)/gi;
    var m;
    while ((m = re.exec(linhaHtml)) !== null) {
      if (m[1]) {
        temAcordes = true;
        posicoes.push([texto.length, m[1]]);
        texto += m[1];
      } else if (m[2]) {
        temAcordes = true;
        var acorde = m[2].trim();
        posicoes.push([texto.length, acorde]);
        texto += acorde;
      } else if (m[3] !== undefined) {
        texto += m[3];
      } else if (m[4]) {
        texto += m[4];
      }
    }
    return { posicoes: posicoes, texto: texto.replace(/\s+$/, ""), temAcordes: temAcordes };
  }

  function mesclarAcordesInline(acordes, letra) {
    letra = String(letra || "").replace(/\s+$/, "");
    var resultado = letra;
    var tamanho = letra.length;
    acordes
      .slice()
      .sort(function (a, b) {
        return b[0] - a[0];
      })
      .forEach(function (pair) {
        var pos = Math.min(pair[0], tamanho);
        resultado =
          resultado.slice(0, pos) + "[" + pair[1] + "]" + resultado.slice(pos);
      });
    return resultado;
  }

  function converterHtmlParaInline(html) {
    html = extrairTablaturasDoHtml(html);
    html = html.replace(/<br\s*\/?>/gi, "\n");
    var linhasHtml = html.split(/\r\n?|\n/);
    var saida = [];
    var indice = 0;

    while (indice < linhasHtml.length) {
      if (!linhasHtml[indice].trim()) {
        indice += 1;
        continue;
      }

      var parsed = parseLinhaHtml(linhasHtml[indice]);
      var acordes = parsed.posicoes;
      var texto = parsed.texto;
      var temAcordes = parsed.temAcordes;

      if (temAcordes) {
        if (indice + 1 < linhasHtml.length) {
          var prox = parseLinhaHtml(linhasHtml[indice + 1]);
          if (!prox.temAcordes && prox.texto.trim()) {
            saida.push(mesclarAcordesInline(acordes, prox.texto));
            indice += 2;
            continue;
          }
        }

        var linha = texto;
        acordes
          .slice()
          .sort(function (a, b) {
            return b[0] - a[0];
          })
          .forEach(function (pair) {
            var pos = pair[0];
            var ac = pair[1];
            linha =
              linha.slice(0, pos) +
              "[" +
              ac +
              "]" +
              linha.slice(pos + ac.length);
          });
        saida.push(linha.trim());
        indice += 1;
        continue;
      }

      if (texto.trim()) {
        saida.push(texto.trim());
      }
      indice += 1;
    }

    return saida.join("\n");
  }

  function looksLikeCifraClub(html, plain) {
    if (html) {
      if (/cifraclub\.com/i.test(html)) return true;
      if (/data-chord\s*=/i.test(html)) return true;
      if (/class\s*=\s*["'][^"']*tablatura/i.test(html)) return true;
      if (
        /<span[^>]*class\s*=\s*["']cnt["']/i.test(html) &&
        /<b>/i.test(html)
      ) {
        return true;
      }
    }
    if (plain) {
      if (/span\s+class\s*=\s*["']tablatura/i.test(plain)) return true;
      if (/data-chord\s*=/i.test(plain)) return true;
      if (/<\/?b>/i.test(plain) && /<i>/i.test(plain)) return true;
    }
    return false;
  }

  function isCifraClubUrl(text) {
    var t = String(text || "").trim();
    return t.length > 10 && t.length < 600 && CIFRACLUB_URL_RE.test(t);
  }

  function csrfHeaders() {
    var headers = { "Content-Type": "application/json" };
    if (typeof global.ssCsrfToken === "function") {
      headers["X-CSRFToken"] = global.ssCsrfToken();
    }
    return headers;
  }

  function importFromCifraClubUrl(url) {
    return fetch("/cifras/import/api/processar-cifra", {
      method: "POST",
      headers: csrfHeaders(),
      credentials: "same-origin",
      body: JSON.stringify({ url_cifra: url, embed: true }),
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) {
          throw new Error(
            (data && data.detail) || "Não foi possível importar a cifra."
          );
        }
        return data;
      });
    });
  }

  function showPasteHint(textarea, message) {
    var hint = textarea.parentElement && textarea.parentElement.querySelector(".cifraclub-paste-hint");
    if (!hint) {
      hint = document.createElement("div");
      hint.className = "cifraclub-paste-hint form-text text-success";
      hint.setAttribute("role", "status");
      textarea.parentElement.appendChild(hint);
    }
    hint.textContent = message;
    global.setTimeout(function () {
      if (hint.textContent === message) hint.textContent = "";
    }, 4500);
  }

  function insertAtCursor(textarea, text) {
    var start = textarea.selectionStart;
    var end = textarea.selectionEnd;
    var before = textarea.value.slice(0, start);
    var after = textarea.value.slice(end);
    textarea.value = before + text + after;
    var pos = before.length + text.length;
    textarea.selectionStart = textarea.selectionEnd = pos;
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function attach(textarea, options) {
    if (!textarea) return;
    options = options || {};

    textarea.addEventListener("paste", function (ev) {
      var cd = ev.clipboardData;
      if (!cd) return;

      var html = cd.getData("text/html") || "";
      var plain = cd.getData("text/plain") || "";

      if (isCifraClubUrl(plain)) {
        ev.preventDefault();
        showPasteHint(textarea, "Importando do Cifra Club…");
        importFromCifraClubUrl(plain.trim())
          .then(function (data) {
            var payload = {
              type: "setsync-cifras-apply",
              titulo: data.titulo,
              artista: data.artista,
              tom_original: data.tom,
              conteudo: data.cifra,
              cifra_json: data.setsync_cifra,
              grade_json: data.setsync_grade,
              bpm: data.bpm,
              duracao_seg: data.duracao_seg,
            };
            if (typeof global.applyCifrasToolResult === "function") {
              global.applyCifrasToolResult(payload);
            } else {
              textarea.value = data.cifra || "";
              textarea.dispatchEvent(new Event("input", { bubbles: true }));
            }
            showPasteHint(textarea, "Cifra importada do Cifra Club.");
          })
          .catch(function (err) {
            alert(err.message || "Falha ao importar URL do Cifra Club.");
          });
        return;
      }

      if (!looksLikeCifraClub(html, plain)) return;

      var rawHtml = normalizeClipboardHtml(html || plain);
      var converted = converterHtmlParaInline(rawHtml);
      if (!converted || !converted.trim()) return;

      ev.preventDefault();
      insertAtCursor(textarea, converted);
      if (options.onConverted) options.onConverted(converted);
      showPasteHint(
        textarea,
        "Colagem do Cifra Club convertida para o formato SetSync."
      );
    });
  }

  global.SetSyncCifraClubPaste = {
    attach: attach,
    converterHtmlParaInline: converterHtmlParaInline,
    looksLikeCifraClub: looksLikeCifraClub,
  };
})(window);
