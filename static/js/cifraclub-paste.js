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

  var RE_TAG_SPAN_CHORD = /<span\s+data-chord="([^"]+)"[^>]*>[\s\S]*?<\/span>/gi;
  var RE_TAG_B = /<b>([^<]*)<\/b>/gi;
  var RE_TAG_I = /<i>([\s\S]*?)<\/i>/gi;
  var RE_TAG_ANY = /<[^>]+>/gi;
  var RE_TOKEN = /\S+/g;
  var RE_CHORD_TOKEN =
    /^(?:[A-G]#|[A-G]b|[A-G])(?:maj7|maj|min|m7b5|m7|M7|m|M|dim7|dim|aug|sus2|sus4|sus|add9|add|7|9|11|13|6|5|4|2|[+\-°º]|[b#]\d{1,2}|\d{1,2}\+|\([^)]*\))*(?:\/(?:[A-G]#|[A-G]b|[A-G]))?$/i;

  function isChordToken(token, allowBareRoot) {
    var t = String(token || "").trim();
    if (!RE_CHORD_TOKEN.test(t)) return false;
    if (!allowBareRoot && /^[A-G][#b]?$/i.test(t)) return false;
    return true;
  }

  function layoutTemLetra(layout) {
    var m;
    RE_TOKEN.lastIndex = 0;
    while ((m = RE_TOKEN.exec(layout || "")) !== null) {
      var tok = m[0];
      if (/^\[[^\]]+\]$/.test(tok)) continue;
      if (!isChordToken(tok, true)) return true;
    }
    return false;
  }

  function snapInicioPalavra(letra, pos) {
    pos = Math.min(Math.max(0, pos), letra.length);
    if (pos >= letra.length || /\s/.test(letra.charAt(pos))) return pos;
    while (pos > 0 && !/\s/.test(letra.charAt(pos - 1))) pos -= 1;
    return pos;
  }

  function htmlParaLayout(linhaHtml) {
    var s = String(linhaHtml || "")
      .replace(/&nbsp;/g, " ")
      .replace(/&#160;/g, " ");
    var partes = [];
    var pos = 0;
    while (pos < s.length) {
      RE_TAG_SPAN_CHORD.lastIndex = pos;
      var mSpan = RE_TAG_SPAN_CHORD.exec(s);
      if (mSpan && mSpan.index === pos) {
        partes.push(mSpan[1].trim());
        pos = RE_TAG_SPAN_CHORD.lastIndex;
        continue;
      }
      RE_TAG_B.lastIndex = pos;
      var mB = RE_TAG_B.exec(s);
      if (mB && mB.index === pos) {
        partes.push(mB[1].trim());
        pos = RE_TAG_B.lastIndex;
        continue;
      }
      RE_TAG_I.lastIndex = pos;
      var mI = RE_TAG_I.exec(s);
      if (mI && mI.index === pos) {
        partes.push(mI[1]);
        pos = RE_TAG_I.lastIndex;
        continue;
      }
      RE_TAG_ANY.lastIndex = pos;
      var mT = RE_TAG_ANY.exec(s);
      if (mT && mT.index === pos) {
        pos = RE_TAG_ANY.lastIndex;
        continue;
      }
      partes.push(s.charAt(pos));
      pos += 1;
    }
    return partes.join("");
  }

  function extrairAcordesLayout(layout) {
    var temLetra = layoutTemLetra(layout);
    var posicoes = [];
    var m;
    RE_TOKEN.lastIndex = 0;
    while ((m = RE_TOKEN.exec(layout || "")) !== null) {
      var tok = m[0];
      if (tok.charAt(0) === "[" && tok.charAt(tok.length - 1) === "]") continue;
      if (!isChordToken(tok, true)) continue;
      if (/^[A-G][#b]?$/i.test(tok) && temLetra) continue;
      posicoes.push([m.index, tok]);
    }
    return posicoes;
  }

  function analisarLinhaHtml(linhaHtml) {
    var layout = htmlParaLayout(linhaHtml);
    var acordes = extrairAcordesLayout(layout);
    var resto = layout;
    acordes
      .slice()
      .sort(function (a, b) {
        return b[0] - a[0];
      })
      .forEach(function (pair) {
        var ac = pair[1];
        resto =
          resto.slice(0, pair[0]) +
          " ".repeat(ac.length) +
          resto.slice(pair[0] + ac.length);
      });
    var lyric = resto.replace(/\s+/g, " ").trim();
    return {
      layout: layout,
      acordes: acordes,
      lyric_text: lyric,
      tem_acordes: acordes.length > 0,
      somente_acordes: acordes.length > 0 && !lyric,
      somente_letra: acordes.length === 0 && !!lyric,
    };
  }

  function mesclarAcordesInline(acordes, letra, larguraLayout, deslocamento) {
    letra = String(letra || "").replace(/\s+$/, "");
    var resultado = letra;
    var tamanho = letra.length;
    var ref =
      larguraLayout && larguraLayout > 0 ? larguraLayout : tamanho;
    var desloc = deslocamento || 0;
    if (ref < tamanho * 0.6 && acordes.length) {
      var prefixo = acordes
        .slice()
        .sort(function (a, b) {
          return a[0] - b[0];
        })
        .map(function (pair) {
          return "[" + pair[1] + "]";
        })
        .join(" ");
      return prefixo + " " + letra;
    }
    acordes
      .slice()
      .sort(function (a, b) {
        return b[0] - a[0];
      })
      .forEach(function (pair) {
        var p = pair[0];
        if (ref > tamanho * 1.12 && tamanho > 0) {
          p = Math.round((p * tamanho) / ref);
        }
        if (desloc) p = p - desloc;
        p = snapInicioPalavra(letra, Math.min(Math.max(0, p), tamanho));
        resultado =
          resultado.slice(0, p) + "[" + pair[1] + "]" + resultado.slice(p);
      });
    return resultado;
  }

  function formatarLinhaAcordesBrackets(layout, acordes) {
    var linha = layout;
    acordes
      .slice()
      .sort(function (a, b) {
        return b[0] - a[0];
      })
      .forEach(function (pair) {
        var ac = pair[1];
        linha =
          linha.slice(0, pair[0]) +
          "[" +
          ac +
          "]" +
          linha.slice(pair[0] + ac.length);
      });
    return linha.replace(/ +/g, " ").trim();
  }

  function converterHtmlParaInline(html) {
    html = extrairTablaturasDoHtml(html);
    html = html.replace(/<br\s*\/?>/gi, "\n");
    var linhasHtml = html.split(/\r\n?|\n/);
    var saida = [];
    var indice = 0;
    var total = linhasHtml.length;

    while (indice < total) {
      if (!linhasHtml[indice].trim()) {
        indice += 1;
        continue;
      }

      var atual = analisarLinhaHtml(linhasHtml[indice]);

      if (atual.somente_letra && indice + 2 < total) {
        var meio = analisarLinhaHtml(linhasHtml[indice + 1]);
        var prox = analisarLinhaHtml(linhasHtml[indice + 2]);
        if (meio.somente_acordes && prox.somente_letra) {
          saida.push(atual.lyric_text);
          var letra2 =
            prox.lyric_text || htmlParaLayout(linhasHtml[indice + 2]).trim();
          var deslocSand = atual.lyric_text.length - letra2.length;
          saida.push(
            mesclarAcordesInline(
              meio.acordes,
              letra2,
              meio.layout.length,
              deslocSand > 0 ? deslocSand : 0
            )
          );
          indice += 3;
          continue;
        }
      }

      if (atual.somente_acordes) {
        if (indice + 1 < total) {
          var prox2 = analisarLinhaHtml(linhasHtml[indice + 1]);
          if (prox2.somente_letra) {
            var letra =
              prox2.lyric_text ||
              htmlParaLayout(linhasHtml[indice + 1]).trim();
            saida.push(
              mesclarAcordesInline(
                atual.acordes,
                letra,
                atual.layout.length
              )
            );
            indice += 2;
            continue;
          }
        }
        saida.push(formatarLinhaAcordesBrackets(atual.layout, atual.acordes));
        indice += 1;
        continue;
      }

      if (atual.somente_letra) {
        saida.push(atual.lyric_text);
        indice += 1;
        continue;
      }

      if (atual.tem_acordes) {
        if (
          atual.lyric_text &&
          /^\[[^\]]+\]$/.test(atual.lyric_text.trim())
        ) {
          saida.push(formatarLinhaAcordesBrackets(atual.layout, atual.acordes));
        } else if (atual.lyric_text) {
          saida.push(
            mesclarAcordesInline(
              atual.acordes,
              atual.lyric_text,
              atual.layout.length
            )
          );
        } else {
          saida.push(formatarLinhaAcordesBrackets(atual.layout, atual.acordes));
        }
        indice += 1;
        continue;
      }

      var texto = htmlParaLayout(linhasHtml[indice]).trim();
      if (texto) saida.push(texto);
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
      if (looksLikeCifraClubPlain(plain)) return true;
    }
    return false;
  }

  function looksLikeCifraClubPlain(plain) {
    var lines = String(plain || "")
      .split(/\r?\n/)
      .filter(function (ln) {
        return ln.trim().length > 0;
      });
    if (lines.length < 3) return false;
    if (/^\{[\w]+:/m.test(plain)) return false;
    var somenteAcordes = 0;
    for (var i = 0; i < lines.length; i++) {
      var info = analisarLinhaHtml(lines[i]);
      if (info.somente_acordes) somenteAcordes++;
    }
    return somenteAcordes >= 2;
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
    looksLikeCifraClubPlain: looksLikeCifraClubPlain,
    normalizarColagem: function (text) {
      if (!looksLikeCifraClubPlain(text)) return text;
      return converterHtmlParaInline(text);
    },
  };
})(window);
