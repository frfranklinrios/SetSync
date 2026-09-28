export function formatarBRL(valor) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(valor);
}

export function parcela(valor, n = 12) {
  return valor / n;
}

export function precoPix(valor) {
  return valor * 0.95;
}
