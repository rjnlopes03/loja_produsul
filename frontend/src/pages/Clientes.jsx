import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

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
            <p>Contas de clientes: compras registradas na conta e pagamentos recebidos.</p>
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
                  </td>
                  <td>
                    <span className={`badge ${c.saldo_devedor > 0 ? "badge-danger" : "badge-ok"}`}>
                      R$ {c.saldo_devedor.toFixed(2)}
                    </span>
                  </td>
                  <td className="acoes">
                    <button className="btn-danger" onClick={() => excluir(c.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
              {clientes.length === 0 && (
                <tr>
                  <td className="vazio" colSpan={3}>
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
