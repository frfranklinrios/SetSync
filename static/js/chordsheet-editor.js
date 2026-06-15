/**
 * Editor Chord Sheet (formato chordsheet.com) — integrado ao SetSync.
 */
(function () {
    "use strict";

    var CFG = window.CHORDSHEET_EDITOR;
    if (!CFG) return;

    var debounceTimer = null;
    var busy = false;

    function $(id) { return document.getElementById(id); }

    function mainMetaField(name) {
        var el = document.querySelector('[name="' + name + '"]');
        return el ? String(el.value || "").trim() : "";
    }

    function metaFromForm() {
        if (CFG.embedMode) {
            return {
                title: mainMetaField("titulo"),
                artist: mainMetaField("artista"),
                key: mainMetaField("tom_original"),
                bpm: mainMetaField("bpm"),
                time_signature: ($("meta-ts") && $("meta-ts").value) || "4/4",
                capo: ($("meta-capo") && $("meta-capo").value || "").trim(),
                style: ""
            };
        }
        return {
            title: ($("meta-title") && $("meta-title").value || "").trim(),
            artist: ($("meta-artist") && $("meta-artist").value || "").trim(),
            key: ($("meta-key") && $("meta-key").value || "").trim(),
            bpm: ($("meta-bpm") && $("meta-bpm").value || "").trim(),
            time_signature: ($("meta-ts") && $("meta-ts").value) || "4/4",
            capo: ($("meta-capo") && $("meta-capo").value || "").trim(),
            style: ""
        };
    }

    function prefsFromForm() {
        return {
            bars_per_row: parseInt($("pref-bars-per-row").value, 10) || 4,
            font_size: $("pref-font-size").value || "M",
            line_spacing: $("pref-line-spacing").value || "normal",
            align_chords: $("pref-align-chords").value || "auto",
            notation_style: $("pref-notation-style").value || "br",
            notation_style_chosen: true,
            maj7_style: $("pref-maj7").value || "delta",
            dim_style: $("pref-dim").value || "circle",
            half_dim_style: $("pref-half-dim").value || "oslash",
            show_footer: $("pref-show-footer").checked,
            bar_line_style: $("pref-bar-line-style").value || "tab",
            tab_lines: parseInt($("pref-tab-lines").value, 10) || 6,
            tab_show_barlines: $("pref-tab-barlines").checked
        };
    }

    function payloadFromForm() {
        var payload = {
            source: ($("source") && $("source").value) || "",
            meta: metaFromForm(),
            prefs: prefsFromForm()
        };
        if (CFG.embedMode) payload.redirect_to = "edit";
        return payload;
    }

    function setStatus(msg, isErr) {
        var el = $("status");
        if (!el) return;
        if (!msg) {
            el.hidden = true;
            el.textContent = "";
            el.classList.remove("err");
            return;
        }
        el.hidden = false;
        el.textContent = msg;
        el.classList.toggle("err", !!isErr);
    }

    function applyInitial(data) {
        if (!data) return;
        var meta = data.meta || {};
        if (!CFG.embedMode) {
            if ($("meta-title")) $("meta-title").value = meta.title || "";
            if ($("meta-artist")) $("meta-artist").value = meta.artist || "";
            if ($("meta-key")) $("meta-key").value = meta.key || "";
            if ($("meta-bpm")) $("meta-bpm").value = meta.bpm || "";
        }
        if ($("meta-ts")) $("meta-ts").value = meta.time_signature || "4/4";
        if ($("meta-capo")) $("meta-capo").value = meta.capo || "";
        if ($("source")) $("source").value = data.source || "";

        var prefs = data.prefs || {};
        if (prefs.bars_per_row && $("pref-bars-per-row")) $("pref-bars-per-row").value = String(prefs.bars_per_row);
        if (prefs.font_size && $("pref-font-size")) $("pref-font-size").value = prefs.font_size;
        if (prefs.line_spacing && $("pref-line-spacing")) $("pref-line-spacing").value = prefs.line_spacing;
        if (prefs.align_chords && $("pref-align-chords")) $("pref-align-chords").value = prefs.align_chords;
        if ($("pref-notation-style")) {
            var ns = prefs.notation_style || "br";
            if (ns === "intl" && !prefs.notation_style_chosen) ns = "br";
            $("pref-notation-style").value = ns;
        }
        if (prefs.maj7_style && $("pref-maj7")) $("pref-maj7").value = prefs.maj7_style;
        if (prefs.dim_style && $("pref-dim")) $("pref-dim").value = prefs.dim_style;
        if (prefs.half_dim_style && $("pref-half-dim")) $("pref-half-dim").value = prefs.half_dim_style;
        if ($("pref-show-footer")) $("pref-show-footer").checked = prefs.show_footer !== false;
        if ($("pref-bar-line-style")) {
            $("pref-bar-line-style").value = prefs.bar_line_style || "tab";
        }
        if (prefs.tab_lines && $("pref-tab-lines")) $("pref-tab-lines").value = String(prefs.tab_lines);
        if ($("pref-tab-barlines")) $("pref-tab-barlines").checked = prefs.tab_show_barlines !== false;
        syncTabPrefsVisibility();
        syncNotationPrefsVisibility();
    }

    function syncNotationPrefsVisibility() {
        var intl = $("pref-notation-style") && $("pref-notation-style").value === "intl";
        document.querySelectorAll(".pref-notation-detail").forEach(function (el) {
            el.hidden = !intl;
        });
    }

    function syncTabPrefsVisibility() {
        var tab = $("pref-bar-line-style") && $("pref-bar-line-style").value === "tab";
        document.querySelectorAll(".pref-tab-only").forEach(function (el) {
            el.hidden = !tab;
        });
    }

    function saveDraft() {
        try {
            localStorage.setItem(CFG.draftKey, JSON.stringify(payloadFromForm()));
        } catch (e) { /* ignore */ }
    }

    function loadDraft() {
        try {
            var raw = localStorage.getItem(CFG.draftKey);
            if (raw) return JSON.parse(raw);
        } catch (e) { /* ignore */ }
        return null;
    }

    function clearDraft() {
        try { localStorage.removeItem(CFG.draftKey); } catch (e) { /* ignore */ }
    }

    function apiFetch(url, body) {
        var headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        };
        if (window.ssCsrfToken) headers["X-CSRFToken"] = window.ssCsrfToken();
        var req = window.ssFetch || fetch;
        return req(url, {
            method: "POST",
            credentials: "same-origin",
            headers: headers,
            body: JSON.stringify(body)
        }).then(function (r) {
            return r.text().then(function (text) {
                var data = null;
                try { data = text ? JSON.parse(text) : null; } catch (e) { /* HTML/redirect */ }
                return { ok: r.ok, status: r.status, data: data };
            });
        });
    }

    function renderPreview() {
        if (busy) return;
        busy = true;
        setStatus("Renderizando…", false);
        apiFetch(CFG.urls.render, payloadFromForm())
            .then(function (res) {
                busy = false;
                if (res.ok && res.data && res.data.ok) {
                    $("preview").innerHTML = res.data.html || "";
                    setStatus(res.data.bar_count ? res.data.bar_count + " compassos" : "OK", false);
                    saveDraft();
                } else if (res.status === 302 || res.status === 401 || res.status === 403) {
                    setStatus("Sessão expirada — recarregue a página e tente de novo", true);
                } else {
                    setStatus((res.data && res.data.error) || "Erro ao renderizar", true);
                }
            })
            .catch(function () {
                busy = false;
                setStatus("Falha de rede ao renderizar", true);
            });
    }

    function scheduleRender() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(renderPreview, 280);
    }

    function transpose(delta) {
        if (busy) return;
        busy = true;
        setStatus("Transpondo…", false);
        var body = payloadFromForm();
        body.semitones = delta;
        apiFetch(CFG.urls.transpose, body)
            .then(function (res) {
                busy = false;
                if (res.ok && res.data && res.data.ok) {
                    if ($("source")) $("source").value = res.data.source || "";
                    if (res.data.meta) {
                        if ($("meta-key") && res.data.meta.key) $("meta-key").value = res.data.meta.key;
                    }
                    scheduleRender();
                } else {
                    setStatus((res.data && res.data.error) || "Erro ao transpor", true);
                }
            })
            .catch(function () {
                busy = false;
                setStatus("Falha de rede ao transpor", true);
            });
    }

    function saveChart() {
        if (busy) return;
        busy = true;
        setStatus("Salvando…", false);
        apiFetch(CFG.urls.save, payloadFromForm())
            .then(function (res) {
                busy = false;
                if (res.ok && res.data && res.data.ok) {
                    clearDraft();
                    setStatus("Salvo!", false);
                    if (res.data.redirect) {
                        window.location.href = res.data.redirect;
                    }
                } else {
                    setStatus((res.data && res.data.error) || "Erro ao salvar", true);
                }
            })
            .catch(function () {
                busy = false;
                setStatus("Falha de rede ao salvar", true);
            });
    }

    function loadExample(key) {
        if (!key || !CFG.examples || !CFG.examples[key]) return;
        var ex = CFG.examples[key];
        applyInitial({
            source: ex.source || "",
            meta: ex.meta || {},
            prefs: payloadFromForm().prefs
        });
        scheduleRender();
    }

    function bindEvents() {
        var metaIds = CFG.embedMode
            ? ["meta-ts", "meta-capo", "source"]
            : ["meta-title", "meta-artist", "meta-key", "meta-bpm", "meta-ts", "meta-capo", "source"];
        metaIds.forEach(function (id) {
            var el = $(id);
            if (el) {
                el.addEventListener("input", scheduleRender);
                el.addEventListener("change", scheduleRender);
            }
        });
        if (CFG.embedMode) {
            ["titulo", "artista", "tom_original", "bpm"].forEach(function (name) {
                var el = document.querySelector('[name="' + name + '"]');
                if (el) {
                    el.addEventListener("input", scheduleRender);
                    el.addEventListener("change", scheduleRender);
                }
            });
        }
        ["pref-notation-style", "pref-bars-per-row", "pref-font-size", "pref-line-spacing", "pref-align-chords",
            "pref-maj7", "pref-dim", "pref-half-dim", "pref-bar-line-style",
            "pref-tab-lines", "pref-show-footer", "pref-tab-barlines"].forEach(function (id) {
            var el = $(id);
            if (el) {
                el.addEventListener("change", function () {
                    syncTabPrefsVisibility();
                    syncNotationPrefsVisibility();
                    scheduleRender();
                });
            }
        });

        if ($("btn-render")) $("btn-render").addEventListener("click", renderPreview);
        if ($("btn-transpose-down")) $("btn-transpose-down").addEventListener("click", function () { transpose(-1); });
        if ($("btn-transpose-up")) $("btn-transpose-up").addEventListener("click", function () { transpose(1); });
        if ($("btn-save")) $("btn-save").addEventListener("click", saveChart);
        if ($("btn-save-top")) $("btn-save-top").addEventListener("click", saveChart);
        if ($("btn-print")) $("btn-print").addEventListener("click", function () { window.print(); });
        if ($("btn-print-top")) $("btn-print-top").addEventListener("click", function () { window.print(); });
        if ($("examples")) {
            $("examples").addEventListener("change", function () {
                loadExample(this.value);
                this.value = "";
            });
        }
    }

    function initWhenVisible() {
        if (CFG._inited) return;
        CFG._inited = true;
        var draft = loadDraft();
        applyInitial(draft || CFG.initial || {});
        bindEvents();
        scheduleRender();
    }

    function init() {
        if (CFG.lazyInit) {
            var tab = document.getElementById("tab-chordsheet");
            if (tab && tab.classList.contains("show")) {
                initWhenVisible();
                return;
            }
            var trigger = document.querySelector('[data-bs-target="#tab-chordsheet"], [href="#tab-chordsheet"]');
            if (trigger) {
                trigger.addEventListener("shown.bs.tab", initWhenVisible, { once: true });
            }
            return;
        }
        initWhenVisible();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
