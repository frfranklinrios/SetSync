/**
 * Editor Chord Sheet (formato chordsheet.com) — integrado ao SetSync.
 * Salvamento automático no servidor + desfazer para o último estado salvo.
 */
(function () {
    "use strict";

    var CFG = window.CHORDSHEET_EDITOR;
    if (!CFG) return;

    var RENDER_DEBOUNCE_MS = 280;
    var AUTOSAVE_DEBOUNCE_MS = 2500;
    var AUTOSAVE_RETRY_MS = 12000;

    var debounceTimer = null;
    var autosaveTimer = null;
    var autosaveRetryTimer = null;
    var busy = false;
    var saving = false;
    var savedBaseline = null;
    var dirty = false;
    var saveFailed = false;

    function $(id) { return document.getElementById(id); }

    function clonePayload(data) {
        return JSON.parse(JSON.stringify(data || {}));
    }

    function mainMetaField(name) {
        var el = document.querySelector('[name="' + name + '"]');
        return el ? String(el.value || "").trim() : "";
    }

    function setMainMetaField(name, value) {
        var el = document.querySelector('[name="' + name + '"]');
        if (el) el.value = value || "";
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
        return {
            source: ($("source") && $("source").value) || "",
            meta: metaFromForm(),
            prefs: prefsFromForm()
        };
    }

    function payloadSignature(payload) {
        var p = payload || {};
        return JSON.stringify({
            source: p.source || "",
            meta: p.meta || {},
            prefs: p.prefs || {}
        });
    }

    function isDirtyAgainstBaseline() {
        if (!savedBaseline) return false;
        return payloadSignature(payloadFromForm()) !== payloadSignature(savedBaseline);
    }

    function updateDirtyState() {
        dirty = isDirtyAgainstBaseline();
        updateUndoButton();
        if (dirty) {
            if (!saving && !saveFailed) {
                setStatus("Alterações pendentes…", false, "pending");
            }
        } else if (!saving && !saveFailed) {
            setStatus("Salvo", false, "saved");
        }
    }

    function updateUndoButton() {
        var disabled = !dirty || busy || saving;
        ["btn-undo", "btn-undo-top"].forEach(function (id) {
            var btn = $(id);
            if (btn) btn.disabled = disabled;
        });
    }

    function setStatus(msg, isErr, kind) {
        var el = $("status");
        if (!el) return;
        if (!msg) {
            el.hidden = true;
            el.textContent = "";
            el.classList.remove("err", "pending", "saved", "saving");
            return;
        }
        el.hidden = false;
        el.textContent = msg;
        el.classList.toggle("err", !!isErr);
        el.classList.remove("pending", "saved", "saving");
        if (kind) el.classList.add(kind);
    }

    function applyInitial(data, options) {
        options = options || {};
        if (!data) return;
        var meta = data.meta || {};
        if (!CFG.embedMode) {
            if ($("meta-title")) $("meta-title").value = meta.title || "";
            if ($("meta-artist")) $("meta-artist").value = meta.artist || "";
            if ($("meta-key")) $("meta-key").value = meta.key || "";
            if ($("meta-bpm")) $("meta-bpm").value = meta.bpm || "";
        } else if (options.syncEmbedMeta) {
            setMainMetaField("titulo", meta.title || "");
            setMainMetaField("artista", meta.artist || "");
            setMainMetaField("tom_original", meta.key || "");
            setMainMetaField("bpm", meta.bpm || "");
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

    function saveDraftLocal() {
        try {
            var payload = payloadFromForm();
            payload._draftAt = Date.now();
            payload._serverSavedAt = (savedBaseline && savedBaseline.saved_at) || (CFG.initial && CFG.initial.saved_at) || "";
            localStorage.setItem(CFG.draftKey, JSON.stringify(payload));
        } catch (e) { /* ignore */ }
    }

    function loadDraftLocal() {
        try {
            var raw = localStorage.getItem(CFG.draftKey);
            if (raw) return JSON.parse(raw);
        } catch (e) { /* ignore */ }
        return null;
    }

    function clearDraftLocal() {
        try { localStorage.removeItem(CFG.draftKey); } catch (e) { /* ignore */ }
    }

    function shouldRestoreLocalDraft(draft, baseline) {
        if (!draft) return false;
        if (payloadSignature(draft) === payloadSignature(baseline)) return false;
        var serverAt = String(baseline.saved_at || "");
        var draftServerAt = String(draft._serverSavedAt || "");
        if (serverAt && draftServerAt && serverAt !== draftServerAt) {
            return true;
        }
        return true;
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
        updateUndoButton();
        apiFetch(CFG.urls.render, payloadFromForm())
            .then(function (res) {
                busy = false;
                if (res.ok && res.data && res.data.ok) {
                    $("preview").innerHTML = res.data.html || "";
                    if (!saving && !saveFailed) {
                        if (dirty) {
                            setStatus("Alterações pendentes…", false, "pending");
                        } else {
                            var extra = res.data.bar_count ? res.data.bar_count + " compassos · " : "";
                            setStatus(extra + "Salvo", false, "saved");
                        }
                    }
                    saveDraftLocal();
                } else if (res.status === 302 || res.status === 401 || res.status === 403) {
                    setStatus("Sessão expirada — recarregue a página", true);
                } else {
                    setStatus((res.data && res.data.error) || "Erro na prévia", true);
                }
                updateUndoButton();
            })
            .catch(function () {
                busy = false;
                setStatus("Falha de rede na prévia", true);
                updateUndoButton();
            });
    }

    function scheduleRender() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(renderPreview, RENDER_DEBOUNCE_MS);
    }

    function scheduleAutosave() {
        updateDirtyState();
        if (!dirty) {
            clearTimeout(autosaveTimer);
            return;
        }
        saveDraftLocal();
        clearTimeout(autosaveTimer);
        autosaveTimer = setTimeout(function () {
            saveToServer(true);
        }, AUTOSAVE_DEBOUNCE_MS);
    }

    function scheduleAutosaveRetry() {
        clearTimeout(autosaveRetryTimer);
        if (!dirty && !saveFailed) return;
        autosaveRetryTimer = setTimeout(function () {
            if (dirty || saveFailed) saveToServer(true);
        }, AUTOSAVE_RETRY_MS);
    }

    function onEditorChange() {
        scheduleRender();
        scheduleAutosave();
    }

    function saveToServer(isAutosave) {
        if (saving) return;
        if (!isAutosave && !dirty) return;
        if (isAutosave && !dirty) return;

        saving = true;
        saveFailed = false;
        updateUndoButton();
        setStatus("Salvando…", false, "saving");

        var body = payloadFromForm();
        body.autosave = true;
        if (CFG.embedMode) body.redirect_to = "edit";

        apiFetch(CFG.urls.save, body)
            .then(function (res) {
                saving = false;
                if (res.ok && res.data && res.data.ok) {
                    var current = payloadFromForm();
                    savedBaseline = clonePayload(current);
                    if (res.data.saved_at) savedBaseline.saved_at = res.data.saved_at;
                    clearDraftLocal();
                    dirty = false;
                    saveFailed = false;
                    clearTimeout(autosaveRetryTimer);
                    setStatus("Salvo", false, "saved");
                } else if (res.status === 302 || res.status === 401 || res.status === 403) {
                    saveFailed = true;
                    setStatus("Sessão expirada — recarregue a página", true);
                    scheduleAutosaveRetry();
                } else {
                    saveFailed = true;
                    setStatus((res.data && res.data.error) || "Erro ao salvar — tentando de novo…", true);
                    scheduleAutosaveRetry();
                }
                updateUndoButton();
            })
            .catch(function () {
                saving = false;
                saveFailed = true;
                setStatus("Sem conexão — tentando salvar de novo…", true);
                scheduleAutosaveRetry();
                updateUndoButton();
            });
    }

    function undoChanges() {
        if (!savedBaseline || !dirty) return;
        if (!window.confirm("Descartar alterações e voltar ao último estado salvo?")) return;
        applyInitial(clonePayload(savedBaseline), { syncEmbedMeta: true });
        dirty = false;
        saveFailed = false;
        clearDraftLocal();
        clearTimeout(autosaveTimer);
        clearTimeout(autosaveRetryTimer);
        setStatus("Alterações desfeitas", false, "saved");
        updateUndoButton();
        scheduleRender();
    }

    function transpose(delta) {
        if (busy || saving) return;
        busy = true;
        updateUndoButton();
        setStatus("Transpondo…", false, "saving");
        var body = payloadFromForm();
        body.semitones = delta;
        apiFetch(CFG.urls.transpose, body)
            .then(function (res) {
                busy = false;
                if (res.ok && res.data && res.data.ok) {
                    if ($("source")) $("source").value = res.data.source || "";
                    if (res.data.meta) {
                        if ($("meta-key") && res.data.meta.key) $("meta-key").value = res.data.meta.key;
                        if (CFG.embedMode) setMainMetaField("tom_original", res.data.meta.key || "");
                    }
                    onEditorChange();
                } else {
                    setStatus((res.data && res.data.error) || "Erro ao transpor", true);
                }
                updateUndoButton();
            })
            .catch(function () {
                busy = false;
                setStatus("Falha de rede ao transpor", true);
                updateUndoButton();
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
        onEditorChange();
    }

    function bindEvents() {
        var metaIds = CFG.embedMode
            ? ["meta-ts", "meta-capo", "source"]
            : ["meta-title", "meta-artist", "meta-key", "meta-bpm", "meta-ts", "meta-capo", "source"];
        metaIds.forEach(function (id) {
            var el = $(id);
            if (el) {
                el.addEventListener("input", onEditorChange);
                el.addEventListener("change", onEditorChange);
            }
        });
        if (CFG.embedMode) {
            ["titulo", "artista", "tom_original", "bpm"].forEach(function (name) {
                var el = document.querySelector('[name="' + name + '"]');
                if (el) {
                    el.addEventListener("input", onEditorChange);
                    el.addEventListener("change", onEditorChange);
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
                    onEditorChange();
                });
            }
        });

        if ($("btn-undo")) $("btn-undo").addEventListener("click", undoChanges);
        if ($("btn-undo-top")) $("btn-undo-top").addEventListener("click", undoChanges);
        if ($("btn-transpose-down")) $("btn-transpose-down").addEventListener("click", function () { transpose(-1); });
        if ($("btn-transpose-up")) $("btn-transpose-up").addEventListener("click", function () { transpose(1); });
        if ($("btn-print")) $("btn-print").addEventListener("click", function () { window.print(); });
        if ($("btn-print-top")) $("btn-print-top").addEventListener("click", function () { window.print(); });
        if ($("examples")) {
            $("examples").addEventListener("change", function () {
                loadExample(this.value);
                this.value = "";
            });
        }

        window.addEventListener("beforeunload", function (e) {
            if (dirty || saving) {
                e.preventDefault();
                e.returnValue = "";
            }
        });
    }

    function initWhenVisible() {
        if (CFG._inited) return;
        CFG._inited = true;

        var baseline = clonePayload(CFG.initial || {});
        savedBaseline = clonePayload(baseline);
        var draft = loadDraftLocal();
        if (shouldRestoreLocalDraft(draft, baseline)) {
            applyInitial(draft);
            dirty = true;
            setStatus("Rascunho local restaurado — salvando…", false, "pending");
            scheduleAutosave();
        } else {
            applyInitial(baseline);
            dirty = false;
            setStatus("Salvo", false, "saved");
        }

        bindEvents();
        updateUndoButton();
        scheduleRender();
        if (dirty) scheduleAutosave();
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
