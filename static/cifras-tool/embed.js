(function () {
  const body = document.body;
  const youtubeNoServer = body.dataset.youtubeNoServer === "1";
  const urls = {
    youtube: body.dataset.processarUrl || "/cifras/import/api/processar",
    audio: body.dataset.processarAudioUrl || "/cifras/import/api/processar-audio",
    cifra: body.dataset.processarCifraUrl || "/cifras/import/api/processar-cifra",
  };

  const resultado = document.getElementById("resultado");
  let ultimoPayload = null;

  function setStatus(el, msg, isError) {
    if (!el) return;
    el.className = "status-line" + (isError ? " erro" : "");
    el.innerHTML = msg;
  }

  function showResult(data) {
    ultimoPayload = {
      type: "setsync-cifras-apply",
      titulo: data.titulo,
      artista: data.artista,
      tom_original: data.tom,
      conteudo: data.cifra,
      cifra_json: data.setsync_cifra,
      grade_json: data.setsync_grade,
      bpm: data.bpm,
      duracao_seg: data.duracao_seg,
      compasso: data.compasso,
    };

    const bpmLabel = data.bpm != null ? data.bpm + " BPM" : "—";
    const durLabel = data.duracao_seg != null ? data.duracao_seg + " s" : "—";

    document.getElementById("meta").innerHTML = [
      ["Música", data.titulo + " — " + data.artista],
      ["Tom", data.tom],
      ["Compasso", data.compasso],
      ["BPM", bpmLabel],
      ["Duração", durLabel],
    ]
      .map(
        ([k, v]) =>
          `<span>${k}: <strong>${CifrasGradeRender.esc(v)}</strong></span>`
      )
      .join("");

    document.getElementById("dl-cifra").href = data.downloads.setsync_cifra;
    document.getElementById("dl-grade").href = data.downloads.setsync_grade;
    document.getElementById("out-cifra").value = data.cifra;
    document.getElementById("out-grade").value = data.grade;
    CifrasGradeRender.renderGradeView(
      document.getElementById("grade-view"),
      data.grade_partes || [],
      data.compasso
    );
    resultado.classList.remove("hidden");
  }

  async function parseError(res) {
    const data = await res.json().catch(() => ({}));
    const det = data.detail;
    if (typeof det === "string") return det;
    if (Array.isArray(det)) return det.map((d) => d.msg || d).join(", ");
    return "Erro ao processar";
  }

  document.querySelectorAll(".tabs .tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const name = tab.dataset.tab;
      document.querySelectorAll(".tabs .tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
      const panel = document.querySelector(".panel-" + name);
      if (panel) panel.classList.remove("hidden");
    });
  });

  if (youtubeNoServer) {
    document.querySelector('.tab[data-tab="audio"]')?.click();
  }

  const formAudio = document.getElementById("form-audio");
  if (formAudio) {
    formAudio.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = document.getElementById("btn-audio");
      const status = document.getElementById("status-audio");
      const file = document.getElementById("audio_file").files[0];
      if (!file) {
        setStatus(status, "Selecione um arquivo de áudio.", true);
        return;
      }

      btn.disabled = true;
      resultado.classList.add("hidden");
      setStatus(status, '<span class="loader"></span>Processando áudio…');

      const fd = new FormData();
      fd.append("url_cifra", document.getElementById("url_cifra_audio").value.trim());
      fd.append("audio", file);
      const ytRef = document.getElementById("url_youtube_ref").value.trim();
      if (ytRef) fd.append("url_youtube", ytRef);
      fd.append("embed", "true");

      try {
        const res = await fetch(urls.audio, {
          method: "POST",
          credentials: "same-origin",
          body: fd,
        });
        if (!res.ok) throw new Error(await parseError(res));
        showResult(await res.json());
        setStatus(status, "Pronto. Clique em «Usar no formulário SetSync».");
      } catch (err) {
        setStatus(status, err.message || String(err), true);
      } finally {
        btn.disabled = false;
      }
    });
  }

  const formCifra = document.getElementById("form-cifra");
  if (formCifra) {
    formCifra.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = document.getElementById("btn-cifra");
      const status = document.getElementById("status-cifra");
      btn.disabled = true;
      resultado.classList.add("hidden");
      setStatus(status, '<span class="loader"></span>Importando cifra…');

      try {
        const res = await fetch(urls.cifra, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
          body: JSON.stringify({
            url_cifra: document.getElementById("url_cifra_only").value.trim(),
            url_youtube: document.getElementById("url_youtube_cifra").value.trim(),
            embed: true,
          }),
        });
        if (!res.ok) throw new Error(await parseError(res));
        showResult(await res.json());
        setStatus(status, "Pronto. Clique em «Usar no formulário SetSync».");
      } catch (err) {
        setStatus(status, err.message || String(err), true);
      } finally {
        btn.disabled = false;
      }
    });
  }

  const formYoutube = document.getElementById("form-youtube");
  if (formYoutube) {
    formYoutube.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = document.getElementById("btn-youtube");
      const status = document.getElementById("status-youtube");
      btn.disabled = true;
      resultado.classList.add("hidden");
      setStatus(status, '<span class="loader"></span>Processando… (pode levar alguns minutos)');

      try {
        const res = await fetch(urls.youtube, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
          body: JSON.stringify({
            url_cifra: document.getElementById("url_cifra_yt").value.trim(),
            url_youtube: document.getElementById("url_youtube_yt").value.trim(),
            embed: true,
          }),
        });
        if (!res.ok) throw new Error(await parseError(res));
        showResult(await res.json());
        setStatus(status, "Pronto. Clique em «Usar no formulário SetSync».");
      } catch (err) {
        setStatus(status, err.message || String(err), true);
      } finally {
        btn.disabled = false;
      }
    });
  }

  document.getElementById("btn-aplicar")?.addEventListener("click", () => {
    if (!ultimoPayload) return;
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(ultimoPayload, "*");
    }
  });

  document.querySelectorAll("[data-copy]").forEach((btnCopy) => {
    btnCopy.addEventListener("click", () => {
      const id = btnCopy.dataset.copy === "cifra" ? "out-cifra" : "out-grade";
      const ta = document.getElementById(id);
      ta.select();
      navigator.clipboard.writeText(ta.value);
    });
  });
})();
