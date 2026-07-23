import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function Marcas() {
  const [marcas, setMarcas] = useState([]);
  const [nome, setNome] = useState("");
  const [erro, setErro] = useState("");

  function carregar() {
    api.listarMarcas().then(setMarcas).catch((e) => setErro(e.message));
  }

  useEffect(carregar, []);

  async function adicionar(e) {
    e.preventDefault();
    setErro("");
    try {
      await api.criarMarca(nome);
      setNome("");
      carregar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  async function excluir(id) {
    if (!confirm("Excluir esta marca?")) return;
    try {
      await api.excluirMarca(id);
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
            <h2>Marcas</h2>
            <p>Gerencie as marcas de ração disponíveis para cadastro.</p>
          </div>
        </div>
      </div>

      <form className="form-inline" onSubmit={adicionar}>
        <input
          placeholder="Nome da marca"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
        />
        <button className="btn-primary" type="submit">
          Adicionar
        </button>
      </form>

      {erro && <p className="erro">{erro}</p>}

      <ul className="lista-marcas">
        {marcas.map((m) => (
          <li key={m.id}>
            {m.nome}
            <button className="btn-danger" onClick={() => excluir(m.id)}>
              Excluir
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
