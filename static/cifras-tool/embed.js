(function () {
  const body = document.body;
  const processarCifraUrl =
    body.dataset.processarCifraUrl || "/cifras/import/api/processar-cifra";

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
        const res = await fetch(processarCifraUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
          body: JSON.stringify({
            url_cifra: document.getElementById("url_cifra_only").value.trim(),
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
