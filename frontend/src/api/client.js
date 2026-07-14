const BASE_URL = "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const erro = await res.json().catch(() => ({}));
    throw new Error(erro.detail || "Erro na requisição");
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listarMarcas: () => request("/marcas/"),
  criarMarca: (nome) => request("/marcas/", { method: "POST", body: JSON.stringify({ nome }) }),
  excluirMarca: (id) => request(`/marcas/${id}`, { method: "DELETE" }),

  listarProdutos: (filtros = {}) => {
    const params = new URLSearchParams(
      Object.fromEntries(Object.entries(filtros).filter(([, v]) => v))
    );
    const qs = params.toString();
    return request(`/produtos/${qs ? `?${qs}` : ""}`);
  },
  criarProduto: (produto) => request("/produtos/", { method: "POST", body: JSON.stringify(produto) }),
  atualizarProduto: (id, produto) =>
    request(`/produtos/${id}`, { method: "PUT", body: JSON.stringify(produto) }),
  excluirProduto: (id) => request(`/produtos/${id}`, { method: "DELETE" }),

  listarMovimentacoes: () => request("/movimentacoes/"),
  criarMovimentacao: (mov) => request("/movimentacoes/", { method: "POST", body: JSON.stringify(mov) }),
};
