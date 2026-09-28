import { useEffect, useMemo, useState } from "react";
import { LOGIN_URL } from "./lib/auth.js";
import { formatarBRL } from "./lib/money.js";

const VAZIO = {
  nome: "",
  email: "",
  telefone: "",
  cpf: "",
  cep: "",
  endereco: "",
  numero: "",
  complemento: "",
  bairro: "",
  cidade: "",
  uf: "CE",
};

export default function CheckoutDrawer({
  aberto,
  itens,
  sessao,
  onFechar,
  onAlterarQtd,
  onRemover,
}) {
  const [cliente, setCliente] = useState(VAZIO);
  const [pagamento, setPagamento] = useState("pix");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!aberto || !sessao?.autenticado) return;
    let cancelado = false;
    async function preencher() {
      const headers = {};
      if (sessao.token) headers.Authorization = `Bearer ${sessao.token}`;
      try {
        const res = await fetch("/api/loja/endereco", { credentials: "include", headers });
        const data = res.ok ? await res.json() : {};
        const salvo = data.endereco || {};
        if (cancelado) return;
        setCliente((c) => ({
          ...c,
          ...Object.fromEntries(Object.entries(salvo).filter(([, v]) => v)),
          nome: sessao.usuario?.nome || salvo.nome || c.nome,
          email: sessao.usuario?.email || salvo.email || c.email,
          telefone: sessao.usuario?.telefone || salvo.telefone || c.telefone,
        }));
      } catch {
        if (!cancelado) {
          setCliente((c) => ({
            ...c,
            nome: sessao.usuario?.nome || c.nome,
            email: sessao.usuario?.email || c.email,
            telefone: sessao.usuario?.telefone || c.telefone,
          }));
        }
      }
    }
    preencher();
    return () => {
      cancelado = true;
    };
  }, [aberto, sessao]);

  const total = useMemo(
    () => itens.reduce((acc, i) => acc + Number(i.preco_venda) * i.quantidade, 0),
    [itens],
  );

  function setCampo(campo, valor) {
    setCliente((c) => ({ ...c, [campo]: valor }));
  }

  async function buscarCep(cepBruto) {
    const cep = String(cepBruto || "").replace(/\D/g, "");
    if (cep.length !== 8) return;
    try {
      const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      const data = await res.json();
      if (data.erro) return;
      setCliente((c) => ({
        ...c,
        cep,
        endereco: data.logradouro || c.endereco,
        bairro: data.bairro || c.bairro,
        cidade: data.localidade || c.cidade,
        uf: (data.uf || c.uf).toUpperCase(),
      }));
    } catch {
      /* ViaCEP opcional */
    }
  }

  async function finalizar(e) {
    e.preventDefault();
    if (!itens.length) return;
    setEnviando(true);
    setErro("");
    try {
      const headers = { "Content-Type": "application/json" };
      if (sessao?.token) headers.Authorization = `Bearer ${sessao.token}`;
      const res = await fetch("/api/loja/pedidos", {
        method: "POST",
        credentials: "include",
        headers,
        body: JSON.stringify({
          pagamento,
          cliente,
          itens: itens.map((i) => ({ produto_id: i.id, quantidade: i.quantidade })),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.status === 401) {
        window.location.href = LOGIN_URL;
        return;
      }
      const detalhe = typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg;
      if (!res.ok) throw new Error(detalhe || "Não foi possível iniciar o pagamento.");
      if (!data.checkout_url) throw new Error("Mercado Pago não retornou o checkout.");
      window.location.href = data.checkout_url;
    } catch (err) {
      setErro(err.message || "Falha no checkout.");
      setEnviando(false);
    }
  }

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50">
      <button type="button" className="h-full flex-1" aria-label="Fechar" onClick={onFechar} />
      <aside className="flex h-full w-full max-w-md flex-col overflow-y-auto bg-white shadow-2xl dark:bg-brand-card">
        <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-700">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Carrinho</h2>
          <button type="button" onClick={onFechar} className="text-sm font-semibold text-slate-500">
            Fechar
          </button>
        </header>

        <div className="space-y-3 px-4 py-4">
          {!itens.length && <p className="text-sm text-slate-500">Seu carrinho está vazio.</p>}
          {itens.map((item) => (
            <div key={item.id} className="flex gap-3 border-b border-slate-100 pb-3 dark:border-slate-800">
              <img src={item.imagem_url} alt="" className="h-16 w-16 rounded object-contain" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{item.nome}</p>
                <p className="text-sm font-bold">{formatarBRL(item.preco_venda)}</p>
                <div className="mt-1 flex items-center gap-2 text-sm">
                  <button type="button" onClick={() => onAlterarQtd(item.id, item.quantidade - 1)}>
                    −
                  </button>
                  <span>{item.quantidade}</span>
                  <button type="button" onClick={() => onAlterarQtd(item.id, item.quantidade + 1)}>
                    +
                  </button>
                  <button type="button" className="ml-auto text-xs text-red-600" onClick={() => onRemover(item.id)}>
                    Remover
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {!!itens.length && !sessao?.autenticado && (
          <div className="px-4 pb-6">
            <p className="mb-3 text-sm text-slate-600 dark:text-slate-300">
              Use a mesma conta do app Uníssono para finalizar a compra.
            </p>
            <a
              href={LOGIN_URL}
              className="block w-full rounded bg-brand py-3 text-center font-bold text-slate-950"
            >
              Entrar para comprar
            </a>
          </div>
        )}

        {!!itens.length && sessao?.autenticado && (
          <form className="space-y-3 px-4 pb-6" onSubmit={finalizar}>
            <p className="text-sm text-slate-500">
              Conta Uníssono: <strong>{sessao.usuario?.nome || sessao.usuario?.email}</strong>
            </p>
            <p className="text-right text-lg font-bold">{formatarBRL(total)}</p>
            <div className="grid grid-cols-3 gap-2 text-sm">
              {["pix", "cartao", "boleto"].map((meio) => (
                <button
                  key={meio}
                  type="button"
                  onClick={() => setPagamento(meio)}
                  className={`rounded border px-2 py-2 font-semibold capitalize ${
                    pagamento === meio ? "border-brand bg-brand/15" : "border-slate-300 dark:border-slate-600"
                  }`}
                >
                  {meio === "cartao" ? "Cartão" : meio === "boleto" ? "Boleto" : "Pix"}
                </button>
              ))}
            </div>
            {[
              ["nome", "Nome completo", "text"],
              ["email", "E-mail", "email"],
              ["telefone", "Celular com DDD", "tel"],
              ["cpf", "CPF", "text"],
              ["cep", "CEP", "text"],
              ["endereco", "Endereço", "text"],
              ["numero", "Número", "text"],
              ["complemento", "Complemento", "text"],
              ["bairro", "Bairro", "text"],
              ["cidade", "Cidade", "text"],
              ["uf", "UF", "text"],
            ].map(([campo, label, tipo]) => (
              <label key={campo} className="block text-sm">
                <span className="mb-1 block text-slate-500">{label}</span>
                <input
                  required={campo !== "complemento"}
                  type={tipo}
                  inputMode={campo === "cep" || campo === "cpf" || campo === "telefone" ? "numeric" : undefined}
                  maxLength={campo === "uf" ? 2 : campo === "cep" ? 9 : campo === "cpf" ? 14 : undefined}
                  value={cliente[campo]}
                  onChange={(e) => setCampo(campo, campo === "uf" ? e.target.value.toUpperCase() : e.target.value)}
                  onBlur={campo === "cep" ? (e) => buscarCep(e.target.value) : undefined}
                  className="w-full rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
                />
              </label>
            ))}
            {erro && <p className="text-sm text-red-600">{erro}</p>}
            <button
              type="submit"
              disabled={enviando}
              className="w-full rounded bg-brand py-3 font-bold text-slate-950 disabled:opacity-60"
            >
              {enviando ? "Abrindo Mercado Pago…" : "Pagar agora"}
            </button>
          </form>
        )}
      </aside>
    </div>
  );
}
