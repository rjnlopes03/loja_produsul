// Em produção, VITE_API_URL aponta para o backend (lida no build). Sem ela, usa o backend local.
const BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const TOKEN_KEY = "produsul_token";

export function obterToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || "";
  } catch {
    return "";
  }
}

export function salvarToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Sem localStorage (ex.: janela anônima restrita), o login vale só até recarregar.
  }
}

async function request(path, options = {}) {
  const token = obterToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (res.status === 401 && path !== "/auth/login") {
    salvarToken("");
    window.dispatchEvent(new Event("sessao-expirada"));
  }
  if (!res.ok) {
    const erro = await res.json().catch(() => ({}));
    throw new Error(erro.detail || "Erro na requisição");
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  statusLogin: () => request("/auth/status"),
  login: (senha) => request("/auth/login", { method: "POST", body: JSON.stringify({ senha }) }),

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

  listarClientes: () => request("/clientes/"),
  criarCliente: (nome) => request("/clientes/", { method: "POST", body: JSON.stringify({ nome }) }),
  atualizarCliente: (id, dados) => request(`/clientes/${id}`, { method: "PUT", body: JSON.stringify(dados) }),
  excluirCliente: (id) => request(`/clientes/${id}`, { method: "DELETE" }),
  obterResumoCliente: (id) => request(`/clientes/${id}/resumo`),
  criarCompra: (clienteId, compra) =>
    request(`/clientes/${clienteId}/compras`, { method: "POST", body: JSON.stringify(compra) }),
  atualizarCompra: (clienteId, compraId, compra) =>
    request(`/clientes/${clienteId}/compras/${compraId}`, { method: "PUT", body: JSON.stringify(compra) }),
  excluirCompra: (clienteId, compraId) =>
    request(`/clientes/${clienteId}/compras/${compraId}`, { method: "DELETE" }),
  criarPagamento: (clienteId, pagamento) =>
    request(`/clientes/${clienteId}/pagamentos`, { method: "POST", body: JSON.stringify(pagamento) }),
  atualizarPagamento: (clienteId, pagamentoId, pagamento) =>
    request(`/clientes/${clienteId}/pagamentos/${pagamentoId}`, { method: "PUT", body: JSON.stringify(pagamento) }),
  excluirPagamento: (clienteId, pagamentoId) =>
    request(`/clientes/${clienteId}/pagamentos/${pagamentoId}`, { method: "DELETE" }),
};
