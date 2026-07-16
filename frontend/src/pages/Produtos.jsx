import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { ESPECIES, FASES_VIDA } from "../constants.js";

export default function Produtos() {
  const [produtos, setProdutos] = useState([]);
  const [marcas, setMarcas] = useState([]);
  const [filtros, setFiltros] = useState({ especie: "", fase_vida: "", marca_id: "", castrado: "" });
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  async function carregar() {
    setCarregando(true);
    try {
      const dados = await api.listarProdutos(filtros);
      setProdutos(dados);
      setErro("");
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    api.listarMarcas().then(setMarcas).catch(() => {});
  }, []);

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtros]);

  function atualizarFiltro(campo, valor) {
    setFiltros((f) => {
      const novo = { ...f, [campo]: valor };
      if (campo === "especie" && valor !== "gato") {
        novo.castrado = "";
      }
      return novo;
    });
  }

  async function excluir(id) {
    if (!confirm("Excluir esta ração do estoque?")) return;
    try {
      await api.excluirProduto(id);
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  return (
    <div>
      <h2>Estoque de Rações</h2>

      <div className="filtros">
        <select
          value={filtros.especie}
          onChange={(e) => atualizarFiltro("especie", e.target.value)}
        >
          <option value="">Todos os animais</option>
          {ESPECIES.map((op) => (
            <option key={op.value} value={op.value}>
              {op.label}
            </option>
          ))}
        </select>

        <select
          value={filtros.fase_vida}
          onChange={(e) => atualizarFiltro("fase_vida", e.target.value)}
        >
          <option value="">Todas as fases</option>
          {FASES_VIDA.map((op) => (
            <option key={op.value} value={op.value}>
              {op.label}
            </option>
          ))}
        </select>

        <select
          value={filtros.marca_id}
          onChange={(e) => atualizarFiltro("marca_id", e.target.value)}
        >
          <option value="">Todas as marcas</option>
          {marcas.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nome}
            </option>
          ))}
        </select>

        {filtros.especie === "gato" && (
          <select
            value={filtros.castrado}
            onChange={(e) => atualizarFiltro("castrado", e.target.value)}
          >
            <option value="">Castrado</option>
            <option value="true">Sim</option>
            <option value="false">Não</option>
          </select>
        )}
      </div>

      {erro && <p className="erro">{erro}</p>}
      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <table className="tabela">
          <thead>
            <tr>
              <th>Ração</th>
              <th>Marca</th>
              <th>Animal</th>
              <th>Fase</th>
              <th>Peso (kg)</th>
              <th>Preço</th>
              <th>Estoque</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {produtos.map((p) => (
              <tr key={p.id}>
                <td>{p.nome}</td>
                <td>{p.marca.nome}</td>
                <td className="capitalize">{p.especie}</td>
                <td className="capitalize">
                  {p.fase_vida}
                  {p.especie === "gato" && p.castrado !== null && p.castrado !== undefined
                    ? ` · ${p.castrado ? "castrado" : "não castrado"}`
                    : ""}
                </td>
                <td>{p.peso_kg}</td>
                <td>R$ {p.preco.toFixed(2)}</td>
                <td className={p.quantidade_estoque <= 5 ? "estoque-baixo" : ""}>
                  {p.quantidade_estoque}
                </td>
                <td className="acoes">
                  <Link to={`/produtos/${p.id}/editar`}>Editar</Link>
                  <button onClick={() => excluir(p.id)}>Excluir</button>
                </td>
              </tr>
            ))}
            {produtos.length === 0 && (
              <tr>
                <td colSpan={8}>Nenhuma ração encontrada.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
