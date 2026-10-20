export function formatarMoeda(valor) {
  return `R$ ${Math.abs(valor).toFixed(2)}`;
}

export function classificarSaldo(saldoDevedor) {
  if (saldoDevedor > 0) return "devedor";
  if (saldoDevedor < 0) return "credito";
  return "quitado";
}
