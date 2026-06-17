/**
 * Detecção de tablatura, seções em colchetes e preview alinhado ao backend (chordpro.py / util.py).
 */
(function (global) {
  "use strict";

  var CHORD_TOKEN =
    /^[A-G][#b]?(?:(?:maj7?|min|m7b5|m7|M7?|m|dim7?|aug|sus[24]?|add9?|\d+|[+\-°º]|[b#]\d))*(?:\/[A-G][#b]?)?$/;

  function isChord(token) {
    return CHORD_TOKEN.test(String(token || "").replace(/[()]/g, ""));
  }

  function isChordLine(line) {
    var tokens = String(line || "")
      .trim()
      .split(/\s+/)
      .filter(function (t) {
        return t.length > 0;
      });
    return tokens.length > 0 && tokens.every(isChord);
  }

  function isBracketChord(token) {
    var t = String(token || "").trim();
    if (!t) return false;
    if (t === "%" || t === "%%" || /^%?\d+$/.test(t)) return true;
    return isChord(t);
  }

  function isTabLine(line) {
    var s = String(line || "").trim();
    if (!s) return false;
    if (/^[EBGDAeFH]\s*\|/i.test(s)) return true;
    if (s.indexOf("|") !== -1 && (s.match(/-/g) || []).length >= 5) return true;
    return false;
  }

  function isTabHeader(line) {
    var s = String(line || "").trim();
    return /^(?:\[(?:Tab|TAB)[^\]]*\]|(?:Tab|TABlatura)\b)/i.test(s);
  }

  function isTabMeta(line) {
    var s = String(line || "").trim();
    if (!s) return false;
    if (/^Parte\s+\d+\s+de\s+\d+$/i.test(s)) return true;
    if (/^Riff\b/i.test(s)) return true;
    return false;
  }

  function isTabRelated(line) {
    return isTabLine(line) || isTabHeader(line) || isTabMeta(line);
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function parseConteudo(text) {
    if (
      global.SetSyncCifraClubPaste &&
      global.SetSyncCifraClubPaste.normalizarColagem
    ) {
      text = global.SetSyncCifraClubPaste.normalizarColagem(text);
    }
    var lines = String(text || "").split("\n");
    var result = [];
    var seq = 0;
    var group = 0;
    var i = 0;

    while (i < lines.length) {
      var line = lines[i];

      if (line.trim() === "") {
        group++;
        i++;
        continue;
      }

      if (isTabRelated(line)) {
        while (i < lines.length && isTabRelated(lines[i])) {
          result.push({
            segundo: seq++,
            texto_letra: lines[i].replace(/\s+$/, ""),
            acorde: "",
            group: group,
          });
          i++;
        }
        group++;
        continue;
      }

      if (/\[([^\]]+)\]/.test(line)) {
        var re = /\[([^\]]+)\]([^\[]*)/g;
        var m;
        var lastIndex = 0;

        while ((m = re.exec(line)) !== null) {
          if (m.index > lastIndex) {
            var prefixo = line.slice(lastIndex, m.index);
            if (prefixo.length) {
              result.push({
                segundo: seq++,
                texto_letra: prefixo,
                acorde: "",
                group: group,
              });
            }
          }

          var token = m[1].trim();
          var texto = String(m[2] || "");
          if (isBracketChord(token)) {
            result.push({
              segundo: seq++,
              texto_letra: texto,
              acorde: token,
              group: group,
            });
          } else {
            var extra = texto.trim();
            result.push({
              segundo: seq++,
              texto_letra: "[" + token + "]" + (extra ? extra : ""),
              acorde: "",
              group: group,
              section: token,
            });
          }
          lastIndex = re.lastIndex;
        }

        if (lastIndex < line.length) {
          var sufixo = line.slice(lastIndex);
          if (sufixo.length) {
            result.push({
              segundo: seq++,
              texto_letra: sufixo,
              acorde: "",
              group: group,
            });
          }
        }

        group++;
        i++;
        continue;
      }

      result.push({
        segundo: seq++,
        texto_letra: line.trim(),
        acorde: "",
        group: group,
      });
      group++;
      i++;
    }

    return result;
  }

  function renderPreview(data, boxEl, countEl) {
    if (!boxEl) return;
    if (!Array.isArray(data) || !data.length) {
      boxEl.innerHTML = '<span class="pv-empty">Digite a cifra ao lado…</span>';
      if (countEl) countEl.textContent = "0 blocos";
      return;
    }

    var hasGroup = data.some(function (item) {
      return item && item.group != null;
    });
    var groups = {};
    var order = [];

    data.forEach(function (item, idx) {
      var key =
        hasGroup && item && item.group != null ? String(item.group) : String(idx);
      if (!groups[key]) {
        groups[key] = [];
        order.push(key);
      }
      groups[key].push(item || {});
    });

    if (countEl) {
      countEl.textContent =
        order.length + " bloco" + (order.length === 1 ? "" : "s");
    }

    boxEl.innerHTML = order
      .map(function (key) {
        var items = groups[key];
        var allTabs = items.every(function (it) {
          return isTabRelated(it.texto_letra || "");
        });

        if (allTabs) {
          return (
            '<pre class="sp-tab-block">' +
            items
              .map(function (it) {
                return escHtml(it.texto_letra || "");
              })
              .join("\n") +
            "</pre>"
          );
        }

        var line = items
          .map(function (item, idx) {
            if (item.section && !item.acorde) {
              return (
                '<span class="sp-section">' + escHtml(item.section) + "</span>"
              );
            }

            if (isTabRelated(item.texto_letra || "")) {
              return (
                '<pre class="sp-tab-line">' +
                escHtml(item.texto_letra || "") +
                "</pre>"
              );
            }

            var next = idx + 1 < items.length ? items[idx + 1] : null;
            var chord = item.acorde ? escHtml(item.acorde) : "";
            var lyric =
              item.texto_letra != null && String(item.texto_letra).length
                ? escHtml(String(item.texto_letra))
                : "&nbsp;";
            var noGap = false;
            if (next) {
              var thisLyric = String(item.texto_letra || "");
              var nextLyric = String(next.texto_letra || "");
              if (
                thisLyric &&
                nextLyric &&
                !/\s$/.test(thisLyric) &&
                !/^\s/.test(nextLyric)
              ) {
                noGap = true;
              }
            }
            return (
              '<span class="sp-item' +
              (noGap ? " sp-no-gap" : "") +
              '"><span class="sp-chord">' +
              (chord || "&nbsp;") +
              '</span><span class="sp-word">' +
              lyric +
              "</span></span>"
            );
          })
          .join("");

        return '<div class="sp-line">' + line + "</div>";
      })
      .join("");
  }

  global.SetSyncCifraLineParse = {
    isChord: isChord,
    isChordLine: isChordLine,
    isBracketChord: isBracketChord,
    isTabLine: isTabLine,
    isTabHeader: isTabHeader,
    isTabMeta: isTabMeta,
    isTabRelated: isTabRelated,
    parseConteudo: parseConteudo,
    renderPreview: renderPreview,
    escHtml: escHtml,
  };
})(typeof window !== "undefined" ? window : this);
