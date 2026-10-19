import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { STATUS_PAGAMENTO } from "../constants.js";

export default function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [nome, setNome] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  function carregar() {
    setCarregando(true);
    api
      .listarClientes()
      .then((dados) => {
        setClientes(dados);
        setErro("");
      })
      .catch((e) => setErro(e.message))
      .finally(() => setCarregando(false));
  }

  useEffect(carregar, []);

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
              {clientes.map((c) => (
                <tr key={c.id}>
                  <td className="nome-produto">
                    <Link className="link-nome" to={`/clientes/${c.id}`}>
                      {c.nome}
                    </Link>
                    {c.telefone && <div className="dica">{c.telefone}</div>}
                  </td>
                  <td>
                    <span className={`badge ${STATUS_PAGAMENTO[c.status].badge}`}>
                      {STATUS_PAGAMENTO[c.status].label}
                    </span>
                    {c.valor_vencido > 0 && (
                      <div className="dica">R$ {c.valor_vencido.toFixed(2)} vencido</div>
                    )}
                  </td>
                  <td>
                    {c.saldo_devedor > 0 ? (
                      <span className="badge badge-danger">R$ {c.saldo_devedor.toFixed(2)}</span>
                    ) : c.saldo_devedor < 0 ? (
                      <span className="badge badge-credit">Crédito de R$ {Math.abs(c.saldo_devedor).toFixed(2)}</span>
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
              ))}
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
