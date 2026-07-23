const BASE_URL = `http://${window.location.hostname}:8000`;

let aoDeslogar = () => {};

export function definirAoDeslogar(fn) {
  aoDeslogar = fn;
}

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });
  if (res.status === 401 && token) {
    localStorage.removeItem("token");
    aoDeslogar();
    throw new Error("Sessão expirada. Faça login novamente.");
  }
  if (!res.ok) {
    const erro = await res.json().catch(() => ({}));
    throw new Error(erro.detail || "Erro na requisição");
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  login: (usuario, senha) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ usuario, senha }) }),
  logout: () => request("/auth/logout", { method: "POST" }),

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
  obterProduto: (id) => request(`/produtos/${id}`),
  criarProduto: (produto) => request("/produtos/", { method: "POST", body: JSON.stringify(produto) }),
  atualizarProduto: (id, produto) =>
    request(`/produtos/${id}`, { method: "PUT", body: JSON.stringify(produto) }),
  excluirProduto: (id) => request(`/produtos/${id}`, { method: "DELETE" }),

  listarMovimentacoes: () => request("/movimentacoes/"),
  criarMovimentacao: (mov) => request("/movimentacoes/", { method: "POST", body: JSON.stringify(mov) }),
  estornarMovimentacao: (id) => request(`/movimentacoes/${id}/estornar`, { method: "POST" }),

  listarClientes: () => request("/clientes/"),
  criarCliente: (nome) => request("/clientes/", { method: "POST", body: JSON.stringify({ nome }) }),
  excluirCliente: (id) => request(`/clientes/${id}`, { method: "DELETE" }),
  obterResumoCliente: (id) => request(`/clientes/${id}/resumo`),
  criarCompra: (clienteId, compra) =>
    request(`/clientes/${clienteId}/compras`, { method: "POST", body: JSON.stringify(compra) }),
  estornarCompra: (clienteId, compraId) =>
    request(`/clientes/${clienteId}/compras/${compraId}/estornar`, { method: "POST" }),
  criarPagamento: (clienteId, pagamento) =>
    request(`/clientes/${clienteId}/pagamentos`, { method: "POST", body: JSON.stringify(pagamento) }),
};
