(function () {
  const form = document.getElementById("form");
  const status = document.getElementById("status");
  const resultado = document.getElementById("resultado");
  const btn = document.getElementById("btn-gerar");
  const apiUrl =
    document.body.dataset.processarUrl || "/cifras/import/api/processar";
  let ultimoPayload = null;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;
    resultado.classList.add("hidden");
    status.className = "";
    status.innerHTML =
      '<span class="loader"></span>Processando… (pode levar alguns minutos)';

    try {
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          url_cifra: document.getElementById("url_cifra").value.trim(),
          url_youtube: document.getElementById("url_youtube").value.trim(),
          embed: true,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        const det = data.detail;
        const msg =
          typeof det === "string"
            ? det
            : Array.isArray(det)
              ? det.map((d) => d.msg || d).join(", ")
              : "Erro ao processar";
        throw new Error(msg);
      }

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

      document.getElementById("meta").innerHTML = [
        ["Música", data.titulo + " — " + data.artista],
        ["Tom", data.tom],
        ["Compasso", data.compasso],
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
      status.textContent = "Pronto. Clique em «Usar no formulário SetSync».";
    } catch (err) {
      status.className = "erro";
      status.textContent = err.message || String(err);
    } finally {
      btn.disabled = false;
    }
  });

  document.getElementById("btn-aplicar").addEventListener("click", () => {
    if (!ultimoPayload) return;
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(ultimoPayload, "*");
      status.textContent = "Dados enviados ao SetSync.";
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
