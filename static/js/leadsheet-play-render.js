/**
 * Renderização read-only do Lead Sheet (modo tocar / preview).
 */
(function (global) {
  var STAFF_BAR_WIDTH_MAX = 220;
  var STAFF_BAR_WIDTH_MIN = 96;

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function styleChord(chord) {
    var safe = escapeHtml(String(chord || "").trim());
    var withAccidentals = safe
      .replace(/([A-G])b/g, "$1<span class=\"accidental\">♭</span>")
      .replace(/([A-G])#/g, "$1<span class=\"accidental\">♯</span>");
    return withAccidentals.replace(
      /(maj7|maj9|m7|m6|m|sus4|sus2|add9|dim|aug|7|6|9|11|13)/gi,
      '<span class="chord-quality">$1</span>'
    );
  }

  function isLeadsheet(doc) {
    return doc && typeof doc === "object" && Array.isArray(doc.events);
  }

  function parseBeatsPerMeasure(timeSignature) {
    var sig = String(timeSignature || "4/4").trim();
    var beats = parseInt(sig.split("/")[0], 10);
    return Number.isFinite(beats) && beats > 0 ? beats : 4;
  }

  /**
   * Largura útil no modo tocar (desconta zonas de toque e padding).
   */
  function getPlayAreaWidth() {
    if (typeof document === "undefined") return 360;
    var scroll = document.getElementById("cifra-scroll");
    var wrap = document.getElementById("cifra-wrap");
    var content = document.getElementById("cifra-content");
    var base =
      (scroll && scroll.clientWidth > 0 ? scroll.clientWidth : 0) ||
      (wrap && wrap.clientWidth > 0 ? wrap.clientWidth : 0) ||
      (typeof window !== "undefined" ? window.innerWidth : 360);

    var deduct = 0;
    if (!scroll) {
      var tapL = document.getElementById("tap-prev");
      var tapR = document.getElementById("tap-next");
      if (tapL && tapR) {
        deduct = (tapL.offsetWidth || 0) + (tapR.offsetWidth || 0);
      } else {
        deduct = Math.min(Math.round(base * 0.24), 240);
      }
    }

    var pad = 12;
    if (content && content.classList.contains("grade-mode")) {
      try {
        var cs = window.getComputedStyle(content);
        pad +=
          (parseFloat(cs.paddingLeft) || 0) + (parseFloat(cs.paddingRight) || 0);
      } catch (e) {}
    }

    return Math.max(140, Math.floor(base - deduct - pad));
  }

  /**
   * Quantos compassos por linha — prioriza leitura em telas estreitas.
   */
  function computeLayout(wrapWidth) {
    var avail = Math.max(140, Number(wrapWidth) || getPlayAreaWidth());
    var barsPerLine;

    if (avail < 200) {
      barsPerLine = 1;
    } else if (avail < 320) {
      barsPerLine = 2;
    } else if (avail < 440) {
      barsPerLine = 2;
    } else if (avail < 580) {
      barsPerLine = 3;
    } else if (avail < 760) {
      barsPerLine = 4;
    } else {
      barsPerLine = Math.max(1, Math.floor(avail / STAFF_BAR_WIDTH_MAX));
      barsPerLine = Math.min(barsPerLine, 6);
    }

    var barWidth = Math.floor(avail / barsPerLine);
    barWidth = Math.max(
      STAFF_BAR_WIDTH_MIN,
      Math.min(STAFF_BAR_WIDTH_MAX, barWidth)
    );

    while (barsPerLine > 1 && barsPerLine * barWidth > avail + 1) {
      barsPerLine -= 1;
      barWidth = Math.floor(avail / barsPerLine);
      barWidth = Math.max(
        STAFF_BAR_WIDTH_MIN,
        Math.min(STAFF_BAR_WIDTH_MAX, barWidth)
      );
    }

    return { barsPerLine: barsPerLine, barWidth: barWidth, availWidth: avail };
  }

  function barsFromLeadsheet(doc) {
    var song = doc.song || {};
    var bpm = Number(song.tempo_bpm) || 120;
    var beats = parseBeatsPerMeasure(song.time_signature);
    var beatDur = 60 / bpm;
    var bars = [];

    (doc.events || [])
      .filter(function (e) {
        return e && e.type === "chord";
      })
      .forEach(function (evt) {
        var t = Number(evt.time_seconds) || 0;
        var absoluteBeat = Math.round(t / beatDur);
        var bar = Math.floor(absoluteBeat / beats);
        var beat = absoluteBeat % beats;
        while (bars.length <= bar) {
          bars.push(Array(beats).fill("%"));
        }
        bars[bar][beat] = evt.value || "%";
      });

    var parts = [];
    (doc.events || []).forEach(function (evt) {
      if (!evt || (evt.type !== "marker" && evt.type !== "lyric")) return;
      var bar = Math.min(
        bars.length ? bars.length - 1 : 0,
        Math.max(0, Math.round(Number(evt.time_seconds) / beatDur / beats))
      );
      if (evt.type === "marker") {
        parts = parts.filter(function (p) {
          return p.barIndex !== bar;
        });
        parts.push({ name: evt.value, barIndex: bar });
      } else if (evt.type === "lyric") {
        var part = parts.find(function (p) {
          return p.barIndex === bar;
        });
        if (part) part.lyric = evt.value;
        else parts.push({ name: "Parte", barIndex: bar, lyric: evt.value });
      }
    });
    parts.sort(function (a, b) {
      return a.barIndex - b.barIndex;
    });

    return {
      bars: bars,
      parts: parts,
      meta: {
        title: song.title || "",
        artist: song.artist || "",
        bpm: song.tempo_bpm,
        timeSignature: song.time_signature || "4/4",
        key: song.key || "",
      },
    };
  }

  function partAtBar(parts, barIndex) {
    return parts.find(function (p) {
      return p.barIndex === barIndex;
    });
  }

  function formatPartLabelText(part) {
    if (!part) return "";
    var lyric = (part.lyric || "").trim();
    if (!lyric) return part.name;
    return part.name + " - " + lyric;
  }

  function chordSizeClass(chord, barsPerLine) {
    var len = String(chord || "").length;
    var narrow = (barsPerLine || 1) >= 3;
    if (len > 7 || (narrow && len > 5)) return "chord-sm";
    if (len > 4 || narrow) return "chord-md";
    return "chord-lg";
  }

  function renderBarHtml(pulseRow, barIndex, isLastInLine, parts, barsPerLine) {
    var cells = pulseRow
      .map(function (pulse) {
        var isPercent = pulse === "%";
        var content = isPercent
          ? '<span class="pulse-empty">%</span>'
          : '<span class="chord-text ' +
            chordSizeClass(pulse, barsPerLine) +
            '" title="' +
            escapeHtml(pulse) +
            '">' +
            styleChord(pulse) +
            "</span>";
        return '<div class="pulse-cell">' + content + "</div>";
      })
      .join("");
    var lastClass = isLastInLine ? " staff-bar-last" : "";
    var part = partAtBar(parts, barIndex);
    var labelClass = part
      ? "staff-part-label" + (part.lyric ? " has-lyric" : "")
      : "staff-part-label is-empty";
    var labelText = formatPartLabelText(part);
    var labelHtml = part
      ? '<span title="' + escapeHtml(labelText) + '">' + escapeHtml(labelText) + "</span>"
      : "&nbsp;";
    return (
      '<div class="staff-bar-col' +
      lastClass +
      '"><div class="' +
      labelClass +
      '">' +
      labelHtml +
      '</div><div class="staff-bar"><div class="pulse-grid" style="grid-template-columns:repeat(' +
      pulseRow.length +
      ', minmax(0, 1fr))">' +
      cells +
      "</div></div></div>"
    );
  }

  function splitBarsIntoLines(allBars, barsPerLine) {
    var perLine = Math.max(1, barsPerLine || 1);
    var lines = [];
    for (var i = 0; i < allBars.length; i += perLine) {
      lines.push(allBars.slice(i, i + perLine));
    }
    return lines;
  }

  function buildStaffSystemsHtml(bars, parts, layout, maxBars) {
    var slice = bars.slice(0, maxBars || 64);
    var lines = splitBarsIntoLines(slice, layout.barsPerLine);
    var globalBarIndex = 0;
    return lines
      .map(function (lineBars) {
        var count = lineBars.length;
        var barsHtml = lineBars
          .map(function (pulseRow, i) {
            var html = renderBarHtml(
              pulseRow,
              globalBarIndex,
              i === lineBars.length - 1,
              parts,
              layout.barsPerLine
            );
            globalBarIndex += 1;
            return html;
          })
          .join("");
        return (
          '<div class="staff-system" style="--bars-in-line:' +
          count +
          '"><div class="staff-line"><div class="staff-bars">' +
          barsHtml +
          "</div></div></div>"
        );
      })
      .join("");
  }

  function buildMetaHtml(meta, songTitle, songArtist, opts) {
    opts = opts || {};
    if (opts.hideHeader) return "";

    var title = (songTitle || meta.title || "").trim() || "Lead Sheet";
    var metaParts = [];
    var artist = (songArtist || meta.artist || "").trim();
    if (artist && !opts.skipArtist) metaParts.push(escapeHtml(artist));
    if (meta.bpm) metaParts.push(escapeHtml(meta.bpm) + " BPM");
    if (meta.timeSignature) metaParts.push("Compasso " + escapeHtml(meta.timeSignature));
    if (meta.key) metaParts.push("Tom " + escapeHtml(meta.key));

    if (opts.hideTitle) {
      if (!metaParts.length) return "";
      return (
        '<div class="leadsheet-play-header leadsheet-play-header--meta-only">' +
        '<div class="leadsheet-play-meta">' +
        metaParts.join(" · ") +
        "</div></div>"
      );
    }

    return (
      '<div class="leadsheet-play-header">' +
      '<div class="leadsheet-play-title">' +
      escapeHtml(title) +
      "</div>" +
      (metaParts.length
        ? '<div class="leadsheet-play-meta">' + metaParts.join(" · ") + "</div>"
        : "") +
      "</div>"
    );
  }

  function renderHtml(doc, opts) {
    opts = opts || {};
    if (!isLeadsheet(doc)) {
      return '<div class="leadsheet-play-empty">Sem Lead Sheet cadastrado.</div>';
    }
    var parsed = barsFromLeadsheet(doc);
    if (!parsed.bars.length) {
      return '<div class="leadsheet-play-empty">Lead Sheet vazio.</div>';
    }
    var wrapWidth = opts.wrapWidth;
    if (!wrapWidth) {
      wrapWidth = getPlayAreaWidth();
    }
    var layout = computeLayout(wrapWidth);
    var systemsHtml = buildStaffSystemsHtml(
      parsed.bars,
      parsed.parts,
      layout,
      opts.maxBars
    );
    var header = buildMetaHtml(parsed.meta, opts.title, opts.artist, opts);
    return (
      '<div class="leadsheet-play-wrap" data-layout-width="' +
      Math.round(wrapWidth) +
      '" data-bars-per-line="' +
      layout.barsPerLine +
      '">' +
      header +
      '<div class="leadsheet-play-body"><div class="leadsheet-systems" data-fluid="1" data-bars-per-line="' +
      layout.barsPerLine +
      '" style="--bar-width-max:' +
      layout.barWidth +
      "px;--bars-per-line:" +
      layout.barsPerLine +
      '">' +
      systemsHtml +
      "</div></div></div>"
    );
  }

  function flatGradeToPartes(flat) {
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

  function renderLegacyGradeHtml(gradeData) {
    var partes =
      Array.isArray(gradeData) && gradeData[0] && gradeData[0].compassos
        ? gradeData
        : flatGradeToPartes(gradeData);
    if (!partes.length) {
      return '<div class="leadsheet-play-empty">Grade vazia.</div>';
    }
    var html =
      '<div class="leadsheet-play-wrap leadsheet-play-wrap--legacy" data-layout-width="' +
      Math.round(getPlayAreaWidth()) +
      '"><div class="leadsheet-play-body"><div class="grade-bars-play">';
    partes.forEach(function (parte) {
      html += '<div class="grade-part-play">';
      if (parte.nome && parte.nome !== "Progressão") {
        html +=
          '<span class="grade-part-title-play">' +
          escapeHtml(parte.nome) +
          "</span>";
      }
      var bloco = [];
      (parte.compassos || []).forEach(function (c) {
        if (c.secao) {
          if (bloco.length) {
            html += '<div class="grade-line-play">';
            bloco.forEach(function (bar) {
              var cells = (bar.acordes || [])
                .map(function (a) {
                  var t = String(a || "").trim();
                  if (t === "%") {
                    return '<span class="grade-chord-play grade-repeat-play">%</span>';
                  }
                  return (
                    '<span class="grade-chord-play">' + escapeHtml(t) + "</span>"
                  );
                })
                .join('<span class="grade-sep-play">·</span>');
              html += '<span class="grade-inline-play">' + cells + "</span>";
            });
            html += "</div>";
            bloco = [];
          }
          html +=
            '<div class="grade-secao-play">' + escapeHtml(c.secao) + "</div>";
        }
        bloco.push(c);
      });
      if (bloco.length) {
        html += '<div class="grade-line-play">';
        bloco.forEach(function (bar) {
          var cells = (bar.acordes || [])
            .map(function (a) {
              var t = String(a || "").trim();
              if (t === "%") {
                return '<span class="grade-chord-play grade-repeat-play">%</span>';
              }
              return (
                '<span class="grade-chord-play">' + escapeHtml(t) + "</span>"
              );
            })
            .join('<span class="grade-sep-play">·</span>');
          html += '<span class="grade-inline-play">' + cells + "</span>";
        });
        html += "</div>";
      }
      html += "</div>";
    });
    html += "</div></div></div>";
    return html;
  }

  global.LeadsheetPlayRender = {
    isLeadsheet: isLeadsheet,
    barsFromLeadsheet: barsFromLeadsheet,
    computeLayout: computeLayout,
    getPlayAreaWidth: getPlayAreaWidth,
    renderHtml: renderHtml,
    renderLegacyGradeHtml: renderLegacyGradeHtml,
    STAFF_BAR_WIDTH_MAX: STAFF_BAR_WIDTH_MAX,
  };
})(typeof window !== "undefined" ? window : this);
