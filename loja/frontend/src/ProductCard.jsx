import { formatarBRL } from "./lib/money.js";

export default function ProductCard({ produto, onComprar }) {
  const esgotado = Number(produto.estoque) <= 0;
  return (
    <article className="group flex h-full flex-col rounded-lg border border-slate-200 bg-white p-3 shadow-sm transition hover:border-brand/40 hover:shadow-md dark:border-slate-700 dark:bg-brand-card dark:hover:border-brand/50">
      <div className="relative mb-3 aspect-square overflow-hidden rounded-md bg-white">
        <img
          src={produto.imagem_url}
          alt={produto.nome}
          className="h-full w-full object-contain p-2 transition duration-300 group-hover:scale-[1.03]"
          loading="lazy"
        />
        {esgotado && (
          <span className="absolute left-2 top-2 rounded bg-slate-900/85 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
            Sem estoque
          </span>
        )}
      </div>
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
        {produto.categoria} · {produto.marca}
      </p>
      <h3 className="mt-1 min-h-[44px] text-sm font-medium leading-snug text-slate-800 dark:text-slate-100">
        {produto.nome}
      </h3>
      <p className="mt-2 text-xl font-bold text-slate-900 dark:text-white">{formatarBRL(produto.preco_venda)}</p>
      <p className="text-xs text-slate-500 dark:text-slate-400">Pix, cartão ou boleto</p>
      <button
        type="button"
        disabled={esgotado}
        onClick={() => onComprar?.(produto)}
        className="mt-3 w-full rounded bg-brand py-2 text-sm font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {esgotado ? "Indisponível" : "Comprar"}
      </button>
    </article>
  );
}
