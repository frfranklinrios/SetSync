import { useEffect, useMemo, useState } from "react";
import CheckoutDrawer from "./CheckoutDrawer.jsx";
import ProductCard from "./ProductCard.jsx";
import { CONTA_URL, LOGIN_URL, LOGOUT_URL, carregarSessao } from "./lib/auth.js";
import { aplicarTema, lerTema } from "./theme.js";

const API_URL = "/api/loja/produtos";
const CART_KEY = "unissono-loja-carrinho";
const ORDEM_CATEGORIAS = [
  "Transmissores",
  "Pedais",
  "Encordoamentos",
  "Palhetas",
  "Correias",
  "Cabos",
  "Afinadores",
  "Capotrastes",
  "Capas e bags",
  "Suportes",
  "Percussão",
  "Acessórios",
];

function SkeletonCard() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-brand-card">
      <div className="mb-3 aspect-square animate-pulse rounded-md bg-slate-100 dark:bg-slate-800" />
      <div className="mb-2 h-3 w-16 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
      <div className="mb-3 h-8 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
      <div className="h-10 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
    </div>
  );
}

function lerCarrinho() {
  try {
    const raw = JSON.parse(localStorage.getItem(CART_KEY) || "[]");
    return Array.isArray(raw) ? raw : [];
  } catch {
    return [];
  }
}

export default function Storefront() {
  const [produtos, setProdutos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [busca, setBusca] = useState("");
  const [categoria, setCategoria] = useState("Todos");
  const [tema, setTema] = useState(() => lerTema());
  const [carrinho, setCarrinho] = useState(() => lerCarrinho());
  const [checkoutAberto, setCheckoutAberto] = useState(false);
  const [aviso, setAviso] = useState("");
  const [sessao, setSessao] = useState(null);

  useEffect(() => {
    aplicarTema(tema);
  }, [tema]);

  useEffect(() => {
    try {
      localStorage.setItem(CART_KEY, JSON.stringify(carrinho));
    } catch {
      /* ignore */
    }
  }, [carrinho]);

  useEffect(() => {
    carregarSessao().then(setSessao);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const pg = params.get("pagamento");
    if (pg === "sucesso") setAviso("Pagamento aprovado. Você vai receber a confirmação no e-mail.");
    if (pg === "pendente") setAviso("Pagamento em análise. Assim que cair, o pedido segue.");
    if (pg === "falha") setAviso("Pagamento não concluído. Você pode tentar de novo pelo carrinho.");
  }, []);

  useEffect(() => {
    let cancelado = false;
    async function carregar() {
      setCarregando(true);
      setErro("");
      try {
        const res = await fetch(API_URL, { cache: "no-store" });
        if (!res.ok) throw new Error(`Falha ao carregar o catálogo (${res.status})`);
        const data = await res.json();
        if (!cancelado) {
          const lista = Array.isArray(data) ? data.filter((p) => p && p.id) : [];
          setProdutos(lista);
          if (!lista.length) setErro("Catálogo ainda sem produtos.");
        }
      } catch (e) {
        if (!cancelado) setErro(e.message || "Não foi possível carregar o catálogo.");
      } finally {
        if (!cancelado) setCarregando(false);
      }
    }
    carregar();
    return () => {
      cancelado = true;
    };
  }, []);

  const categorias = useMemo(() => {
    const extra = [...new Set(produtos.map((p) => p.categoria).filter(Boolean))];
    const ordenadas = [
      ...ORDEM_CATEGORIAS.filter((c) => extra.includes(c)),
      ...extra.filter((c) => !ORDEM_CATEGORIAS.includes(c)),
    ];
    return ["Todos", ...ordenadas];
  }, [produtos]);

  const filtrados = useMemo(() => {
    const q = busca.trim().toLowerCase();
    return produtos.filter((p) => {
      const catOk = categoria === "Todos" || p.categoria === categoria;
      const buscaOk =
        !q || p.nome.toLowerCase().includes(q) || (p.marca || "").toLowerCase().includes(q);
      return catOk && buscaOk;
    });
  }, [produtos, busca, categoria]);

  const qtdCarrinho = carrinho.reduce((acc, i) => acc + i.quantidade, 0);
  const escuro = tema === "dark";

  function adicionar(produto) {
    if (sessao && !sessao.autenticado) {
      window.location.href = LOGIN_URL;
      return;
    }
    setCarrinho((atual) => {
      const i = atual.findIndex((x) => x.id === produto.id);
      if (i >= 0) {
        const copia = [...atual];
        copia[i] = { ...copia[i], quantidade: copia[i].quantidade + 1 };
        return copia;
      }
      return [...atual, { ...produto, quantidade: 1 }];
    });
    setCheckoutAberto(true);
  }

  function alterarQtd(id, qtd) {
    if (qtd < 1) {
      setCarrinho((atual) => atual.filter((i) => i.id !== id));
      return;
    }
    setCarrinho((atual) => atual.map((i) => (i.id === id ? { ...i, quantidade: qtd } : i)));
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800 dark:bg-brand-dark dark:text-slate-100">
      <div className="bg-slate-900 text-xs text-slate-300">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-2">
          <p>Loja Uníssono · Pix, cartão e boleto via Mercado Pago</p>
          <a href="https://unissono.app" className="hover:text-white">
            Voltar ao app
          </a>
        </div>
      </div>

      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-brand-card">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center">
          <a href="/" className="shrink-0">
            <img
              src={escuro ? "/logo-unissono.png" : "/logo-unissono-color.png"}
              alt="Uníssono"
              className="h-11 w-auto max-w-[220px] object-contain"
            />
          </a>
          <form
            className="flex min-w-0 flex-1 overflow-hidden rounded-md border border-slate-300 bg-white focus-within:border-brand"
            onSubmit={(e) => e.preventDefault()}
          >
            <input
              type="search"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              placeholder="Busque palheta, cabo, pedal, afinador, correia..."
              className="min-w-0 flex-1 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none"
            />
            <button type="submit" className="bg-brand px-4 text-sm font-bold text-slate-950">
              Buscar
            </button>
          </form>
          <div className="flex items-center gap-3 text-sm sm:gap-4">
            <button
              type="button"
              onClick={() => setTema(escuro ? "light" : "dark")}
              className="rounded-md border border-slate-300 px-2.5 py-1.5 font-semibold text-slate-700 dark:border-slate-600 dark:text-slate-200"
            >
              {escuro ? "Claro" : "Escuro"}
            </button>
            {sessao?.autenticado ? (
              <>
                {sessao.usuario?.is_superadmin && (
                  <a href="/admin" className="hidden font-semibold text-brand sm:inline">
                    Admin
                  </a>
                )}
                <a href={CONTA_URL} className="hidden font-semibold sm:inline">
                  {sessao.usuario?.nome || sessao.usuario?.username || "Minha conta"}
                </a>
                <a href={LOGOUT_URL} className="text-slate-500 hover:text-slate-800 dark:hover:text-white">
                  Sair
                </a>
              </>
            ) : (
              <a href={LOGIN_URL} className="font-semibold">
                Entrar
              </a>
            )}
            <button
              type="button"
              onClick={() => setCheckoutAberto(true)}
              className="rounded-md bg-slate-900 px-3 py-1.5 font-semibold text-white dark:bg-brand dark:text-slate-950"
            >
              Carrinho ({qtdCarrinho})
            </button>
          </div>
        </div>
        <nav className="bg-slate-900">
          <div className="no-scrollbar mx-auto flex max-w-6xl gap-1 overflow-x-auto px-2">
            {categorias.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setCategoria(cat)}
                className={`whitespace-nowrap px-4 py-3 text-sm font-semibold ${
                  categoria === cat ? "bg-brand text-slate-950" : "text-white hover:bg-white/10"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <section className="mb-6 rounded-lg bg-gradient-to-br from-slate-900 to-slate-800 p-6 text-white">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-ink">Loja</p>
          <h1 className="mt-2 text-3xl font-bold leading-tight sm:text-4xl">
            Acessórios para músicos
          </h1>
          <p className="mt-2 text-sm text-slate-300">
            Palhetas, cabos, pedais, correias, encordoamentos e mais. Compra no site, envio pelo fornecedor.
          </p>
        </section>

        {aviso && (
          <p className="mb-4 rounded-md border border-brand/40 bg-brand/10 px-4 py-3 text-sm">{aviso}</p>
        )}
        {erro && (
          <p className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-500/40 dark:bg-red-500/10 dark:text-red-200">
            {erro}
          </p>
        )}

        <div className="mb-4 flex items-end justify-between">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {categoria === "Todos" ? "Destaques" : categoria}
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {carregando ? "…" : `${filtrados.length} produtos`}
          </p>
        </div>

        {carregando && (
          <section className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </section>
        )}

        {!carregando && !erro && filtrados.length === 0 && (
          <p className="rounded-lg bg-white p-8 text-center text-slate-500 dark:bg-brand-card dark:text-slate-400">
            Nenhum produto encontrado.
          </p>
        )}

        {!carregando && !erro && filtrados.length > 0 && (
          <section className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
            {filtrados.map((produto) => (
              <ProductCard key={produto.id} produto={produto} onComprar={adicionar} />
            ))}
          </section>
        )}
      </main>

      <footer className="mt-10 bg-slate-900 text-slate-300">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <img src="/logo-unissono.png" alt="Uníssono" className="mb-3 h-8 w-auto" />
            <p className="text-sm text-slate-400">Artigos musicais para palco e ensaio.</p>
          </div>
          <div>
            <p className="mb-2 text-sm font-bold text-white">Pagamento</p>
            <p className="text-sm">Pix, cartão e boleto pelo Mercado Pago</p>
          </div>
          <div>
            <p className="mb-2 text-sm font-bold text-white">Atendimento</p>
            <p className="text-sm">contato@unissono.app</p>
          </div>
        </div>
      </footer>

      <CheckoutDrawer
        aberto={checkoutAberto}
        itens={carrinho}
        sessao={sessao}
        onFechar={() => setCheckoutAberto(false)}
        onAlterarQtd={alterarQtd}
        onRemover={(id) => setCarrinho((atual) => atual.filter((i) => i.id !== id))}
      />
    </div>
  );
}
