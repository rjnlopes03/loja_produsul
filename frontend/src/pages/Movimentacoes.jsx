import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { useApiData } from "../hooks/useApiData.js";

const vazio = { produto_id: "", tipo: "entrada", quantidade: "" };

export default function Movimentacoes() {
  const [produtos, setProdutos] = useState([]);
  const [form, setForm] = useState(vazio);
  const {
    dados: movimentacoes,
    carregando,
    erro,
    setErro,
    carregar,
  } = useApiData(() => api.listarMovimentacoes(), [], []);

  useEffect(() => {
    api.listarProdutos().then(setProdutos).catch((e) => setErro(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function atualizarCampo(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function registrar(e) {
    e.preventDefault();
    setErro("");
    try {
      await api.criarMovimentacao({
        produto_id: Number(form.produto_id),
        tipo: form.tipo,
        quantidade: Number(form.quantidade),
      });
      setForm(vazio);
      carregar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  const totalEntradas = movimentacoes.filter((m) => m.tipo === "entrada").length;
  const totalSaidas = movimentacoes.filter((m) => m.tipo === "saida").length;

  return (
    <div>
      <div className="hero">
        <div className="hero-top">
          <div>
            <h2>Movimentações de Estoque</h2>
            <p>Histórico de entradas e saídas de rações, com registro manual de reposição ou ajuste.</p>
          </div>

          <div className="hero-stats">
            <div className="stat-chip">
              <div className="stat-icon">
                <IconArrowDown />
              </div>
              <div>
                <strong>{totalEntradas}</strong>
                <span>entradas</span>
              </div>
            </div>
            <div className="stat-chip">
              <div className="stat-icon">
                <IconArrowUp />
              </div>
              <div>
                <strong>{totalSaidas}</strong>
                <span>saídas</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <form className="form" onSubmit={registrar}>
        <label>
          Ração
          <select
            required
            value={form.produto_id}
            onChange={(e) => atualizarCampo("produto_id", e.target.value)}
          >
            <option value="">Selecione</option>
            {produtos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nome} ({p.marca.nome})
              </option>
            ))}
          </select>
        </label>

        <label>
          Tipo
          <select value={form.tipo} onChange={(e) => atualizarCampo("tipo", e.target.value)}>
            <option value="entrada">Entrada (reposição)</option>
            <option value="saida">Saída (baixa manual)</option>
          </select>
        </label>

        <label>
          Quantidade
          <input
            required
            type="number"
            min="1"
            value={form.quantidade}
            onChange={(e) => atualizarCampo("quantidade", e.target.value)}
          />
        </label>

        {erro && <p className="erro">{erro}</p>}

        <button type="submit">Registrar movimentação</button>
      </form>

      {carregando ? (
        <p className="carregando">Carregando...</p>
      ) : (
        <div className="tabela-wrap tabela-espacada">
          <table className="tabela">
            <thead>
              <tr>
                <th>Data</th>
                <th>Ração</th>
                <th>Marca</th>
                <th>Tipo</th>
                <th>Quantidade</th>
              </tr>
            </thead>
            <tbody>
              {movimentacoes.map((m) => (
                <tr key={m.id}>
                  <td>{new Date(m.criado_em).toLocaleString("pt-BR")}</td>
                  <td className="nome-produto">{m.produto.nome}</td>
                  <td>{m.produto.marca.nome}</td>
                  <td>
                    <span className={`badge ${m.tipo === "entrada" ? "badge-ok" : "badge-rust"}`}>
                      {m.tipo === "entrada" ? "Entrada" : "Saída"}
                    </span>
                  </td>
                  <td>{m.quantidade}</td>
                </tr>
              ))}
              {movimentacoes.length === 0 && (
                <tr>
                  <td className="vazio" colSpan={5}>
                    Nenhuma movimentação registrada.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function IconArrowDown() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14M5 12l7 7 7-7" />
    </svg>
  );
}

function IconArrowUp() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 19V5M5 12l7-7 7 7" />
    </svg>
  );
}
