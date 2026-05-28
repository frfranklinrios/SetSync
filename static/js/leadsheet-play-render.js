/**
 * Renderização read-only do Lead Sheet (modo tocar / preview).
 */
(function (global) {
  var STAFF_BAR_WIDTH_MAX = 232;
  var STAFF_BAR_WIDTH_MIN = 68;

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
   * Quantos compassos por linha e largura alvo, conforme a área útil.
   */
  function computeLayout(wrapWidth) {
    var w = Math.max(160, Number(wrapWidth) || 360);
    var padding = 16;
    var avail = w - padding;
    var barsPerLine;

    /* Sempre cabe na largura real — evita scroll horizontal */
    if (avail < 300) {
      barsPerLine = 1;
    } else if (avail < 460) {
      barsPerLine = 2;
    } else if (avail < 640) {
      barsPerLine = 3;
    } else if (avail < 860) {
      barsPerLine = 4;
    } else {
      barsPerLine = Math.max(1, Math.floor(avail / STAFF_BAR_WIDTH_MAX));
    }

    var barWidth = Math.floor(avail / barsPerLine);
    barWidth = Math.max(STAFF_BAR_WIDTH_MIN, Math.min(STAFF_BAR_WIDTH_MAX, barWidth));

    /* Se ainda não couber, reduz compassos por linha */
    while (barsPerLine > 1 && barsPerLine * barWidth > avail + 2) {
      barsPerLine -= 1;
      barWidth = Math.floor(avail / barsPerLine);
      barWidth = Math.max(STAFF_BAR_WIDTH_MIN, Math.min(STAFF_BAR_WIDTH_MAX, barWidth));
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

  function chordSizeClass(chord) {
    var len = String(chord || "").length;
    if (len > 6) return "chord-sm";
    if (len > 4) return "chord-md";
    return "chord-lg";
  }

  function renderBarHtml(pulseRow, barIndex, isLastInLine, parts) {
    var cells = pulseRow
      .map(function (pulse) {
        var isPercent = pulse === "%";
        var content = isPercent
          ? '<span class="pulse-empty">%</span>'
          : '<span class="chord-text ' +
            chordSizeClass(pulse) +
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
              parts
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
    if (!wrapWidth && typeof document !== "undefined") {
      var wrap = document.getElementById("cifra-wrap");
      var content = document.getElementById("cifra-content");
      wrapWidth =
        (wrap && wrap.clientWidth) ||
        (content && content.clientWidth) ||
        (typeof window !== "undefined" ? window.innerWidth : 360);
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
      '">' +
      header +
      '<div class="leadsheet-play-body"><div class="leadsheet-systems" data-fluid="1" style="--bar-width-max:' +
      layout.barWidth +
      'px">' +
      systemsHtml +
      "</div></div></div>"
    );
  }

  function getPlayAreaWidth() {
    if (typeof document === "undefined") return 360;
    var content = document.getElementById("cifra-content");
    var wrap = document.getElementById("cifra-wrap");
    if (content && content.clientWidth > 0) return content.clientWidth;
    if (wrap && wrap.clientWidth > 0) return wrap.clientWidth;
    return window.innerWidth || 360;
  }

  global.LeadsheetPlayRender = {
    isLeadsheet: isLeadsheet,
    barsFromLeadsheet: barsFromLeadsheet,
    computeLayout: computeLayout,
    getPlayAreaWidth: getPlayAreaWidth,
    renderHtml: renderHtml,
    STAFF_BAR_WIDTH_MAX: STAFF_BAR_WIDTH_MAX,
  };
})(typeof window !== "undefined" ? window : this);
