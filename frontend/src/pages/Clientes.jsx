import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { classificarSaldo, formatarMoeda } from "../format.js";
import { useApiData } from "../hooks/useApiData.js";
import { STATUS_PAGAMENTO } from "../constants.js";

export default function Clientes() {
  const [nome, setNome] = useState("");
  const {
    dados: clientes,
    carregando,
    erro,
    setErro,
    carregar,
  } = useApiData(() => api.listarClientes(), [], []);

  async function adicionar(e) {
    e.preventDefault();
    setErro("");
    try {
      await api.criarCliente(nome);
      setNome("");
      carregar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  async function excluir(id) {
    if (!confirm("Excluir este cliente?")) return;
    try {
      await api.excluirCliente(id);
      carregar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  return (
    <div>
      <div className="hero">
        <div className="hero-top">
          <div>
            <h2>Clientes</h2>
            <p>Contas de clientes: clique em "Abrir conta" para lançar compras, pagamentos e editar os dados.</p>
          </div>
        </div>
      </div>

      <form className="form-inline" onSubmit={adicionar}>
        <input
          placeholder="Nome do cliente"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
        />
        <button className="btn-primary" type="submit">
          Adicionar
        </button>
      </form>

      {erro && <p className="erro">{erro}</p>}

      {carregando ? (
        <p className="carregando">Carregando...</p>
      ) : (
        <div className="tabela-wrap">
          <table className="tabela">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Status</th>
                <th>Saldo devedor</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {clientes.map((c) => {
                const situacao = classificarSaldo(c.saldo_devedor);
                return (
                <tr key={c.id}>
                  <td className="nome-produto">
                    <Link className="link-nome" to={`/clientes/${c.id}`}>
                      {c.nome}
                    </Link>
                    {c.telefone && <div className="dica">{c.telefone}</div>}
                  </td>
                  <td data-label="Status">
                    <span className={`badge ${STATUS_PAGAMENTO[c.status].badge}`}>
                      {STATUS_PAGAMENTO[c.status].label}
                    </span>
                    {c.valor_vencido > 0 && (
                      <div className="dica">{formatarMoeda(c.valor_vencido)} vencido</div>
                    )}
                  </td>
                  <td data-label="Saldo devedor">
                    {situacao === "devedor" ? (
                      <span className="badge badge-danger">{formatarMoeda(c.saldo_devedor)}</span>
                    ) : situacao === "credito" ? (
                      <span className="badge badge-credit">Crédito de {formatarMoeda(c.saldo_devedor)}</span>
                    ) : (
                      <span className="badge badge-ok">R$ 0.00</span>
                    )}
                    {c.acima_do_limite && <div className="dica">Acima do limite</div>}
                  </td>
                  <td className="acoes">
                    <Link className="link-editar" to={`/clientes/${c.id}`}>
                      Abrir conta
                    </Link>
                    <button className="btn-danger" onClick={() => excluir(c.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
                );
              })}
              {clientes.length === 0 && (
                <tr>
                  <td className="vazio" colSpan={4}>
                    Nenhum cliente cadastrado.
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
