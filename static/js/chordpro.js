/**
 * Conversão para ChordPro no envio do formulário (espelha chordpro.py).
 */
(function (global) {
  "use strict";

  var META = {
    title: 1,
    t: 1,
    artist: 1,
    subtitle: 1,
    st: 1,
    key: 1,
    capo: 1,
    tempo: 1,
    time: 1,
  };

  var DIRECTIVE_RE = /^\{\s*([^}:]+?)(?:\s*:\s*(.*?))?\s*\}\s*$/i;

  function parseDirective(line) {
    var m = String(line || "").trim().match(DIRECTIVE_RE);
    if (!m) return null;
    return { name: m[1].toLowerCase(), value: (m[2] || "").trim() };
  }

  function isSectionLabel(text) {
    var s = String(text || "").trim();
    if (!s || s.indexOf("[") >= 0) return false;
    if (s.length > 72 || (s.match(/ /g) || []).length > 10) return false;
    return true;
  }

  function directive(name, value) {
    var v = String(value || "").replace(/\n/g, " ").trim();
    return v ? "{" + name + ": " + v + "}" : "{" + name + "}";
  }

  function groupByField(data) {
    if (!data.length) return [];
    if (data[0].group == null) return [data];
    var groups = [];
    var cur = null;
    var bucket = [];
    data.forEach(function (item) {
      var g = item.group;
      if (cur === null) cur = g;
      if (g !== cur && bucket.length) {
        groups.push(bucket);
        bucket = [];
        cur = g;
      }
      bucket.push(item);
    });
    if (bucket.length) groups.push(bucket);
    return groups;
  }

  function mergeGroup(items) {
    var parts = [];
    items.forEach(function (item) {
      var chord = (item.acorde || "").trim();
      var lyric = item.texto_letra != null ? String(item.texto_letra) : "";
      if (chord) parts.push("[" + chord + "]" + lyric);
      else parts.push(lyric);
    });
    return parts.join("");
  }

  function stripMetaFromBody(text) {
    var lines = String(text || "").split("\n");
    var out = [];
    lines.forEach(function (ln) {
      var d = parseDirective(ln.trim());
      if (d && META[d.name]) return;
      out.push(ln);
    });
    return out.join("\n").trim();
  }

  function toChordPro(text, meta) {
    meta = meta || {};
    var body = stripMetaFromBody(text);
    var data =
      typeof global.parseConteudo === "function"
        ? global.parseConteudo(body)
        : [];
    var groups = groupByField(data);
    var out = [];

    if (meta.titulo) out.push(directive("title", meta.titulo));
    if (meta.artista) out.push(directive("artist", meta.artista));
    if (meta.key) out.push(directive("key", meta.key));
    if (out.length) out.push("");

    groups.forEach(function (items, idx) {
      var hasChord = items.some(function (it) {
        return (it.acorde || "").trim();
      });
      var merged = mergeGroup(items);
      if (!merged.trim()) return;
      if (!hasChord && isSectionLabel(merged)) {
        if (idx > 0 && out.length && out[out.length - 1] !== "") out.push("");
        out.push(directive("comment", merged.trim()));
        return;
      }
      if (idx > 0 && out.length && out[out.length - 1] !== "") out.push("");
      out.push(merged.replace(/\s+$/, ""));
    });

    while (out.length && out[out.length - 1] === "") out.pop();
    return out.length ? out.join("\n") + "\n" : "";
  }

  function attachFormChordProSave(formId) {
    var form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener("submit", function () {
      var ta = document.getElementById("conteudo");
      if (!ta || !ta.value.trim()) return;
      var meta = {
        titulo:
          (form.querySelector('[name="titulo"]') || {}).value || "",
        artista:
          (form.querySelector('[name="artista"]') || {}).value || "",
        key:
          (form.querySelector('[name="tom_original"]') || {}).value || "",
      };
      ta.value = toChordPro(ta.value, meta);
    });
  }

  global.SetSyncChordPro = {
    toChordPro: toChordPro,
    attachFormChordProSave: attachFormChordProSave,
  };
})(window);
