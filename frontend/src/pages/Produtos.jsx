import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { ESPECIES, FASES_VIDA } from "../constants.js";

export default function Produtos() {
  const [produtos, setProdutos] = useState([]);
  const [filtros, setFiltros] = useState({ especie: "", fase_vida: "" });
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
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtros]);

  async function excluir(id) {
    if (!confirm("Excluir esta ração do estoque?")) return;
    await api.excluirProduto(id);
    carregar();
  }

  return (
    <div>
      <h2>Estoque de Rações</h2>

      <div className="filtros">
        <select
          value={filtros.especie}
          onChange={(e) => setFiltros((f) => ({ ...f, especie: e.target.value }))}
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
          onChange={(e) => setFiltros((f) => ({ ...f, fase_vida: e.target.value }))}
        >
          <option value="">Todas as fases</option>
          {FASES_VIDA.map((op) => (
            <option key={op.value} value={op.value}>
              {op.label}
            </option>
          ))}
        </select>
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
