import { useEffect, useState } from "react";
import { ADMIN_LOGIN_URL, carregarSessao } from "./lib/auth.js";
import { formatarBRL } from "./lib/money.js";

const VAZIO = {
  id: "",
  sku: "",
  titulo: "",
  categoria: "Acessórios",
  marca: "Uníssono",
  imagem_url: "",
  url: "",
  preco_base_usd: "",
  frete_usd: "0",
  estoque: "0",
};

function headers(sessao) {
  const h = { "Content-Type": "application/json" };
  if (sessao?.token) h.Authorization = `Bearer ${sessao.token}`;
  return h;
}

export default function Admin() {
  const [sessao, setSessao] = useState(null);
  const [aba, setAba] = useState("resumo");
  const [resumo, setResumo] = useState(null);
  const [produtos, setProdutos] = useState([]);
  const [pedidos, setPedidos] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [importTexto, setImportTexto] = useState("");
  const [importCategoria, setImportCategoria] = useState("");
  const [importPreco, setImportPreco] = useState("");
  const [importFrete, setImportFrete] = useState("7.5");
  const [buscaCj, setBuscaCj] = useState("");
  const [resultadosCj, setResultadosCj] = useState([]);
  const [erro, setErro] = useState("");
  const [aviso, setAviso] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    carregarSessao().then(setSessao);
  }, []);

  useEffect(() => {
    if (!sessao?.usuario?.is_superadmin) return;
    recarregar();
  }, [sessao, aba]);

  async function api(path, opts = {}) {
    const ctrl = new AbortController();
    const t = window.setTimeout(() => ctrl.abort(), 20000);
    let res;
    try {
      res = await fetch(path, {
        credentials: "include",
        headers: headers(sessao),
        signal: ctrl.signal,
        ...opts,
      });
    } catch (e) {
      if (e.name === "AbortError") throw new Error("O painel demorou demais. Atualize a página.");
      throw e;
    } finally {
      window.clearTimeout(t);
    }
    const data = await res.json().catch(() => ({}));
    if (res.status === 401) {
      window.location.href = ADMIN_LOGIN_URL;
      throw new Error("Faça login.");
    }
    if (!res.ok) {
      const detalhe = typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg;
      throw new Error(detalhe || `Erro ${res.status}`);
    }
    return data;
  }

  async function recarregar() {
    setErro("");
    setBusy(true);
    try {
      if (aba === "resumo") setResumo(await api("/api/loja/admin/resumo"));
      if (aba === "produtos") setProdutos(await api("/api/loja/admin/produtos"));
      if (aba === "pedidos") setPedidos(await api("/api/loja/admin/pedidos"));
    } catch (e) {
      setErro(e.message || "Falha ao carregar o painel.");
    } finally {
      setBusy(false);
    }
  }

  async function acao(fn, okMsg) {
    setBusy(true);
    setErro("");
    setAviso("");
    try {
      await fn();
      if (okMsg) setAviso(okMsg);
      await recarregar();
    } catch (e) {
      setErro(e.message || "Não foi possível concluir.");
    } finally {
      setBusy(false);
    }
  }

  function editar(p) {
    setForm({
      id: p.id,
      sku: p.sku || "",
      titulo: p.titulo || "",
      categoria: p.categoria || "Acessórios",
      marca: p.marca || "Uníssono",
      imagem_url: p.imagem_url || "",
      url: p.url || "",
      preco_base_usd: String(p.preco_base_usd ?? ""),
      frete_usd: String(p.frete_usd ?? "0"),
      estoque: String(p.estoque ?? "0"),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (!sessao) {
    return <p className="p-8 text-slate-500">Carregando…</p>;
  }

  if (!sessao.autenticado) {
    return (
      <div className="mx-auto max-w-lg p-8">
        <h1 className="text-2xl font-bold">Painel da loja</h1>
        <p className="mt-2 text-slate-600">Entre com a conta Uníssono de administrador.</p>
        <a href={ADMIN_LOGIN_URL} className="mt-4 inline-block rounded bg-brand px-4 py-2 font-bold text-slate-950">
          Entrar
        </a>
      </div>
    );
  }

  if (!sessao.usuario?.is_superadmin) {
    return (
      <div className="mx-auto max-w-lg p-8">
        <h1 className="text-2xl font-bold">Área restrita</h1>
        <p className="mt-2 text-slate-600">Esta página é só para o administrador da loja.</p>
        <a href="/" className="mt-4 inline-block font-semibold text-brand">
          Voltar à loja
        </a>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Uníssono</p>
            <h1 className="text-xl font-bold">Painel da loja</h1>
          </div>
          <a href="/" className="text-sm font-semibold text-slate-600 hover:text-slate-900">
            Ver vitrine
          </a>
        </div>
        <nav className="mx-auto flex max-w-6xl gap-1 px-4">
          {[
            ["resumo", "Resumo"],
            ["produtos", "Produtos"],
            ["pedidos", "Pedidos"],
          ].map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => setAba(id)}
              className={`px-4 py-2 text-sm font-semibold ${
                aba === id ? "border-b-2 border-brand text-slate-900" : "text-slate-500"
              }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl space-y-4 px-4 py-6">
        {erro && <p className="rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{erro}</p>}
        {aviso && <p className="rounded border border-brand/40 bg-brand/10 px-4 py-3 text-sm">{aviso}</p>}

        {aba === "resumo" && !resumo && !erro && (
          <p className="rounded-lg border border-slate-200 bg-white px-4 py-8 text-center text-slate-500">
            {busy ? "Carregando o resumo…" : "Clique em Resumo de novo se a página ficar vazia."}
          </p>
        )}

        {aba === "resumo" && resumo && (
          <section className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["USD/BRL", Number(resumo.usd_brl || 0).toFixed(4)],
                ["Vendas no mês", String(resumo.qtd_vendas || 0)],
                ["Faturamento", formatarBRL(resumo.valor_venda || 0)],
                ["Lucro líquido", formatarBRL(resumo.lucro_liquido || 0)],
              ].map(([label, valor]) => (
                <div key={label} className="rounded-lg border border-slate-200 bg-white p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
                  <p className="mt-1 text-2xl font-bold">{valor}</p>
                </div>
              ))}
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
              <p>
                Competência {resumo.competencia} · custo {formatarBRL(resumo.custo_aquisicao || 0)} ·
                taxa MP {formatarBRL(resumo.taxa_mp || 0)} · {resumo.quantidade} produtos no catálogo
                {resumo.ultimo_scrape ? ` · scrape ${resumo.ultimo_scrape}` : ""}
              </p>
              <p className="mt-2">
                Fornecedor CJ:{" "}
                <strong>{resumo.cj_configurada ? "conectado — envio automático no pagamento" : "aguardando API Key (conta PF, sem CNPJ)"}</strong>
              </p>
              {!resumo.cj_configurada && (
                <p className="mt-1 text-slate-500">
                  Crie a conta em cjdropshipping.com → Apps → API → cole CJ_API_KEY no servidor e coloque saldo na carteira.
                  Aí o catálogo entra sozinho e, no Pix aprovado, o CJ despacha para o cliente.
                </p>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() =>
                    acao(async () => {
                      const r = await api("/api/loja/admin/cambio", { method: "POST" });
                      setAviso(`Câmbio atualizado: ${Number(r.usd_brl).toFixed(4)}`);
                    })
                  }
                  className="rounded bg-slate-900 px-3 py-2 font-semibold text-white disabled:opacity-60"
                >
                  Atualizar câmbio
                </button>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() =>
                    acao(
                      () => api("/api/loja/admin/scraper", { method: "POST" }),
                      resumo.cj_configurada
                        ? "Catálogo do fornecedor atualizado."
                        : "Scraper concluído. Preços recalculados.",
                    )
                  }
                  className="rounded bg-brand px-3 py-2 font-bold text-slate-950 disabled:opacity-60"
                >
                  {resumo.cj_configurada ? "Sincronizar fornecedor" : "Rodar scraper"}
                </button>
              </div>
            </div>
          </section>
        )}

        {aba === "produtos" && (
          <section className="space-y-4">
            <form
              className="space-y-3 rounded-lg border border-brand/40 bg-white p-4"
              onSubmit={(e) => {
                e.preventDefault();
                acao(async () => {
                  const r = await api(`/api/loja/admin/cj/buscar?q=${encodeURIComponent(buscaCj)}&tamanho=12`);
                  setResultadosCj(r.itens || []);
                  if (!(r.itens || []).length) setAviso("Nenhum produto no CJ para essa busca.");
                });
              }}
            >
              <h2 className="text-lg font-bold">Escolher no fornecedor (CJ)</h2>
              <p className="text-sm text-slate-600">
                Busque em inglês e clique em Disponibilizar para publicar na vitrine.
              </p>
              <div className="flex flex-col gap-2 sm:flex-row">
                <input
                  value={buscaCj}
                  onChange={(e) => setBuscaCj(e.target.value)}
                  placeholder="Ex.: guitar pick, capo, tuner, cable, pedal, strap"
                  className="min-w-0 flex-1 rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
                />
                <button
                  type="submit"
                  disabled={busy}
                  className="rounded bg-brand px-4 py-2 font-bold text-slate-950 disabled:opacity-60"
                >
                  {busy ? "Buscando…" : "Buscar no CJ"}
                </button>
              </div>
              {!!resultadosCj.length && (
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {resultadosCj.map((p) => (
                    <article key={p.pid} className="flex flex-col rounded-lg border border-slate-200 p-3">
                      {p.imagem_url ? (
                        <img src={p.imagem_url} alt="" className="mb-2 h-28 w-full object-contain" />
                      ) : (
                        <div className="mb-2 h-28 bg-slate-100" />
                      )}
                      <p className="min-h-[40px] text-sm font-medium">{p.titulo}</p>
                      <p className="mt-1 text-sm text-slate-500">
                        USD {Number(p.preco_base_usd || 0).toFixed(2)}
                      </p>
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() =>
                          acao(async () => {
                            await api("/api/loja/admin/cj/disponibilizar", {
                              method: "POST",
                              body: JSON.stringify({ pid: p.pid, categoria: importCategoria }),
                            });
                            setAviso("Produto na vitrine.");
                          }, "Produto disponibilizado na loja.")
                        }
                        className="mt-2 rounded bg-slate-900 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
                      >
                        Disponibilizar
                      </button>
                    </article>
                  ))}
                </div>
              )}
            </form>

            <form
              className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"
              onSubmit={(e) => {
                e.preventDefault();
                const urls = importTexto
                  .split(/[\n,]+/)
                  .map((u) => u.trim())
                  .filter((u) => /^https?:\/\//i.test(u));
                if (!urls.length) {
                  setErro("Cole o link do produto no AliExpress ou Shopee.");
                  return;
                }
                acao(async () => {
                  const resultados = [];
                  for (const url of urls) {
                    const r = await api("/api/loja/admin/importar", {
                      method: "POST",
                      body: JSON.stringify({
                        url,
                        publicar: true,
                        categoria: importCategoria,
                        preco_base_usd: importPreco ? Number(importPreco) : null,
                        frete_usd: importFrete ? Number(importFrete) : null,
                      }),
                    });
                    resultados.push(r);
                    if (!r.publicado && r.produto) {
                      const p = r.produto;
                      setForm({
                        id: p.id || "",
                        sku: p.sku || "",
                        titulo: p.titulo || "",
                        categoria: p.categoria || "Acessórios",
                        marca: p.marca || "Uníssono",
                        imagem_url: p.imagem_url || "",
                        url: p.url || url,
                        preco_base_usd: String(p.preco_base_usd || ""),
                        frete_usd: String(p.frete_usd || "7.5"),
                        estoque: String(p.estoque || "12"),
                      });
                    }
                  }
                  const ok = resultados.filter((r) => r.publicado).length;
                  const pendente = resultados.length - ok;
                  setAviso(
                    ok
                      ? `${ok} produto(s) já na vitrine.${pendente ? ` ${pendente} sem preço — complete o USD e salve.` : ""}`
                      : resultados[0]?.aviso || "Não foi possível publicar. Complete o preço e salve.",
                  );
                  if (ok) setImportTexto("");
                });
              }}
            >
              <h2 className="text-lg font-bold">Disponibilizar automaticamente</h2>
              <p className="text-sm text-slate-600">
                Cole o link do produto. A loja tenta buscar título, foto e preço. Se o fornecedor bloquear a leitura,
                informe o USD abaixo — um clique e o item já aparece na vitrine.
              </p>
              <textarea
                required
                rows={3}
                value={importTexto}
                onChange={(e) => setImportTexto(e.target.value)}
                placeholder="https://www.aliexpress.com/item/100500….html"
                className="w-full rounded border border-slate-300 bg-white px-3 py-2 font-mono text-sm text-slate-900"
              />
              <div className="grid gap-3 sm:grid-cols-3">
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-500">Preço USD (se a página não trouxer)</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={importPreco}
                    onChange={(e) => setImportPreco(e.target.value)}
                    placeholder="24.90"
                    className="w-full rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-500">Frete USD</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={importFrete}
                    onChange={(e) => setImportFrete(e.target.value)}
                    className="w-full rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-500">Categoria</span>
                  <select
                    value={importCategoria}
                    onChange={(e) => setImportCategoria(e.target.value)}
                    className="w-full rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
                  >
                    <option value="">Detectar pelo título</option>
                    <option>Transmissores</option>
                    <option>Pedais</option>
                    <option>Encordoamentos</option>
                    <option>Palhetas</option>
                    <option>Correias</option>
                    <option>Cabos</option>
                    <option>Afinadores</option>
                    <option>Capotrastes</option>
                    <option>Capas e bags</option>
                    <option>Suportes</option>
                    <option>Percussão</option>
                    <option>Acessórios</option>
                  </select>
                </label>
              </div>
              <button
                type="submit"
                disabled={busy}
                className="rounded bg-brand px-4 py-2 font-bold text-slate-950 disabled:opacity-60"
              >
                {busy ? "Importando…" : "Importar e disponibilizar"}
              </button>
            </form>

            <form
              className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 sm:grid-cols-2"
              onSubmit={(e) => {
                e.preventDefault();
                acao(async () => {
                  await api("/api/loja/admin/produtos", {
                    method: "POST",
                    body: JSON.stringify({
                      ...form,
                      preco_base_usd: Number(form.preco_base_usd),
                      frete_usd: Number(form.frete_usd || 0),
                      estoque: Number(form.estoque || 0),
                    }),
                  });
                  setForm(VAZIO);
                }, "Produto salvo. Preço de venda recalculado.");
              }}
            >
              <h2 className="sm:col-span-2 text-lg font-bold">
                {form.id && produtos.some((p) => p.id === form.id) ? "Editar produto" : "Novo produto"}
              </h2>
              {[
                ["id", "ID interno"],
                ["sku", "SKU"],
                ["titulo", "Título"],
                ["categoria", "Categoria"],
                ["marca", "Marca"],
                ["imagem_url", "Imagem (URL ou /produtos/…)"],
                ["url", "URL do fornecedor"],
                ["preco_base_usd", "Preço USD"],
                ["frete_usd", "Frete USD"],
                ["estoque", "Estoque"],
              ].map(([campo, label]) => (
                <label key={campo} className="block text-sm">
                  <span className="mb-1 block text-slate-500">{label}</span>
                  <input
                    required={["id", "titulo", "preco_base_usd"].includes(campo)}
                    value={form[campo]}
                    onChange={(e) => setForm((f) => ({ ...f, [campo]: e.target.value }))}
                    className="w-full rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
                  />
                </label>
              ))}
              <div className="sm:col-span-2 flex gap-2">
                <button
                  type="submit"
                  disabled={busy}
                  className="rounded bg-brand px-4 py-2 font-bold text-slate-950 disabled:opacity-60"
                >
                  Salvar
                </button>
                <button type="button" onClick={() => setForm(VAZIO)} className="rounded border px-4 py-2">
                  Limpar
                </button>
              </div>
            </form>

            <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-2">Produto</th>
                    <th className="px-3 py-2">USD + frete</th>
                    <th className="px-3 py-2">Venda</th>
                    <th className="px-3 py-2">Estoque</th>
                    <th className="px-3 py-2" />
                  </tr>
                </thead>
                <tbody>
                  {produtos.map((p) => (
                    <tr key={p.id} className="border-t border-slate-100">
                      <td className="px-3 py-2">
                        <p className="font-semibold">{p.titulo}</p>
                        <p className="text-xs text-slate-500">
                          {p.id} · {p.categoria} · {p.fonte}
                        </p>
                      </td>
                      <td className="px-3 py-2">
                        {Number(p.preco_base_usd || 0).toFixed(2)} + {Number(p.frete_usd || 0).toFixed(2)}
                      </td>
                      <td className="px-3 py-2 font-semibold">{formatarBRL(p.preco_venda || 0)}</td>
                      <td className="px-3 py-2">{p.estoque}</td>
                      <td className="px-3 py-2 text-right">
                        <button type="button" className="mr-2 font-semibold" onClick={() => editar(p)}>
                          Editar
                        </button>
                        <button
                          type="button"
                          className="text-red-600"
                          onClick={() => {
                            if (!window.confirm(`Remover ${p.titulo}?`)) return;
                            acao(
                              () => api(`/api/loja/admin/produtos/${encodeURIComponent(p.id)}`, { method: "DELETE" }),
                              "Produto removido.",
                            );
                          }}
                        >
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {aba === "pedidos" && (
          <section className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Pedido</th>
                  <th className="px-3 py-2">Cliente</th>
                  <th className="px-3 py-2">Itens</th>
                  <th className="px-3 py-2">Total</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Fornecedor</th>
                </tr>
              </thead>
              <tbody>
                {!pedidos.length && (
                  <tr>
                    <td colSpan={6} className="px-3 py-8 text-center text-slate-500">
                      Nenhum pedido ainda.
                    </td>
                  </tr>
                )}
                {pedidos.map((p) => (
                  <tr key={p.id} className="border-t border-slate-100 align-top">
                    <td className="px-3 py-2">
                      <p className="font-semibold">{p.id}</p>
                      <p className="text-xs text-slate-500">{p.criado_em}</p>
                    </td>
                    <td className="px-3 py-2">
                      <p>{p.cliente?.nome}</p>
                      <p className="text-xs text-slate-500">
                        {p.cliente?.cidade}/{p.cliente?.uf} · {p.cliente?.cep}
                      </p>
                    </td>
                    <td className="px-3 py-2 text-xs">
                      {(p.itens || []).map((i) => (
                        <p key={`${p.id}-${i.produto_id}`}>
                          {i.quantidade}× {i.nome}
                        </p>
                      ))}
                    </td>
                    <td className="px-3 py-2 font-semibold">{formatarBRL(p.total || 0)}</td>
                    <td className="px-3 py-2 capitalize">
                      {p.status} · {p.pagamento}
                    </td>
                    <td className="px-3 py-2 text-xs">
                      {p.fulfillment?.ok
                        ? `CJ ${p.fulfillment.cj_order_id || "enviado"}`
                        : p.fulfillment?.erro || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  );
}
