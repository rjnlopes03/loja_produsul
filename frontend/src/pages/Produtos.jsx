import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { ESPECIES, FASES_VIDA, ESPECIE_COR } from "../constants.js";
import { useApiData } from "../hooks/useApiData.js";

function IconBox() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 8 12 3 3 8l9 5 9-5Z" />
      <path d="M3 8v8l9 5 9-5V8" />
      <path d="M12 13v8" />
    </svg>
  );
}

function IconTag() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.6 12.6 12.7 20.5a1.9 1.9 0 0 1-2.7 0L3.5 14a1.9 1.9 0 0 1 0-2.7L11.4 3.4A1.9 1.9 0 0 1 12.8 3H19a2 2 0 0 1 2 2v6.2a1.9 1.9 0 0 1-.4 1.4Z" />
      <circle cx="15.5" cy="8.5" r="1.5" />
    </svg>
  );
}

function IconAlert() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.3 3.9 1.9 18a2 2 0 0 0 1.7 3h16.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
      <path d="M12 9v4M12 17h.01" />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

export default function Produtos() {
  const [marcas, setMarcas] = useState([]);
  const [filtros, setFiltros] = useState({ especie: "", fase_vida: "", marca_id: "", castrado: "" });
  const {
    dados: produtos,
    carregando,
    erro,
    setErro,
    carregar,
  } = useApiData(() => api.listarProdutos(filtros), [filtros], []);

  useEffect(() => {
    api.listarMarcas().then(setMarcas).catch(() => {});
  }, []);

  function atualizarFiltro(campo, valor) {
    setFiltros((f) => {
      const novo = { ...f, [campo]: valor === f[campo] ? "" : valor };
      if (campo === "especie" && novo.especie !== "gato") {
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
      if (e.message.includes("movimentações de estoque registradas")) {
        if (
          confirm(
            `${e.message}\n\nDeseja excluir mesmo assim? O histórico de movimentações deste produto será perdido.`
          )
        ) {
          try {
            await api.excluirProduto(id, { forcar: true });
            carregar();
          } catch (e2) {
            setErro(e2.message);
          }
        }
        return;
      }
      setErro(e.message);
    }
  }

  const estoqueBaixo = produtos.filter((p) => p.quantidade_estoque <= 5).length;

  return (
    <div>
      <div className="hero">
        <div className="hero-top">
          <div>
            <h2>Estoque de Rações</h2>
            <p>Acompanhe o saldo e os dados de cada ração cadastrada na Produsul.</p>
          </div>

          <div className="hero-stats">
            <div className="stat-chip">
              <div className="stat-icon">
                <IconBox />
              </div>
              <div>
                <strong>{produtos.length}</strong>
                <span>rações listadas</span>
              </div>
            </div>
            <div className="stat-chip">
              <div className="stat-icon">
                <IconTag />
              </div>
              <div>
                <strong>{marcas.length}</strong>
                <span>marcas</span>
              </div>
            </div>
            <div className={`stat-chip ${estoqueBaixo > 0 ? "stat-alert" : ""}`}>
              <div className="stat-icon">{estoqueBaixo > 0 ? <IconAlert /> : <IconCheck />}</div>
              <div>
                <strong>{estoqueBaixo}</strong>
                <span>estoque baixo</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="filtros">
        <div className="filtro-grupo">
          <span className="filtro-label">Animal</span>
          <button
            type="button"
            className={`pill pill-sm ${filtros.especie === "" ? "active" : ""}`}
            onClick={() => atualizarFiltro("especie", "")}
          >
            Todos
          </button>
          {ESPECIES.map((op) => (
            <button
              key={op.value}
              type="button"
              className={`pill pill-sm ${filtros.especie === op.value ? "active" : ""}`}
              onClick={() => atualizarFiltro("especie", op.value)}
            >
              {op.label}
            </button>
          ))}
        </div>
      </div>

      <div className="filtros">
        <div className="filtro-grupo">
          <span className="filtro-label">Fase</span>
          <button
            type="button"
            className={`pill pill-sm ${filtros.fase_vida === "" ? "active" : ""}`}
            onClick={() => atualizarFiltro("fase_vida", "")}
          >
            Todas
          </button>
          {FASES_VIDA.map((op) => (
            <button
              key={op.value}
              type="button"
              className={`pill pill-sm ${filtros.fase_vida === op.value ? "active" : ""}`}
              onClick={() => atualizarFiltro("fase_vida", op.value)}
            >
              {op.label}
            </button>
          ))}
        </div>

        {filtros.especie === "gato" && (
          <div className="filtro-grupo">
            <span className="filtro-label">Castrado</span>
            <button
              type="button"
              className={`pill pill-sm ${filtros.castrado === "" ? "active" : ""}`}
              onClick={() => atualizarFiltro("castrado", "")}
            >
              Todos
            </button>
            <button
              type="button"
              className={`pill pill-sm ${filtros.castrado === "true" ? "active" : ""}`}
              onClick={() => atualizarFiltro("castrado", "true")}
            >
              Sim
            </button>
            <button
              type="button"
              className={`pill pill-sm ${filtros.castrado === "false" ? "active" : ""}`}
              onClick={() => atualizarFiltro("castrado", "false")}
            >
              Não
            </button>
          </div>
        )}

        <div className="filtro-grupo">
          <span className="filtro-label">Marca</span>
          <select
            className="filtro-select"
            value={filtros.marca_id}
            onChange={(e) => atualizarFiltro("marca_id", e.target.value)}
          >
            <option value="">Todas</option>
            {marcas.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nome}
              </option>
            ))}
          </select>
        </div>
      </div>

      {erro && <p className="erro">{erro}</p>}
      {carregando ? (
        <p className="carregando">Carregando...</p>
      ) : (
        <div className="tabela-wrap">
          <table className="tabela">
            <thead>
              <tr>
                <th>Ração</th>
                <th>Marca</th>
                <th>Animal</th>
                <th>Fase</th>
                <th>Castrado</th>
                <th>Peso (kg)</th>
                <th>Preço</th>
                <th>Estoque</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {produtos.map((p) => (
                <tr key={p.id}>
                  <td className="nome-produto">{p.nome}</td>
                  <td>{p.marca.nome}</td>
                  <td>
                    <div className="especie-cell">
                      <span
                        className="especie-avatar"
                        style={{
                          background: (ESPECIE_COR[p.especie] ?? ESPECIE_COR.vaca).bg,
                          color: (ESPECIE_COR[p.especie] ?? ESPECIE_COR.vaca).fg,
                        }}
                      >
                        {(ESPECIE_COR[p.especie] ?? ESPECIE_COR.vaca).sigla}
                      </span>
                      <span className="capitalize">{p.especie}</span>
                    </div>
                  </td>
                  <td className="capitalize">{p.fase_vida}</td>
                  <td>
                    {p.especie === "gato" && p.castrado !== null && p.castrado !== undefined ? (
                      <span className={`badge ${p.castrado ? "badge-ok" : "badge-muted"}`}>
                        {p.castrado ? "Sim" : "Não"}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>{p.peso_kg}</td>
                  <td>R$ {p.preco.toFixed(2)}</td>
                  <td>
                    {p.quantidade_estoque <= 5 ? (
                      <span className="badge badge-danger">{p.quantidade_estoque} un.</span>
                    ) : (
                      <span className="badge badge-rust">{p.quantidade_estoque} un.</span>
                    )}
                  </td>
                  <td className="acoes">
                    <Link className="link-editar" to={`/produtos/${p.id}/editar`}>
                      Editar
                    </Link>
                    <button className="btn-danger" onClick={() => excluir(p.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
              {produtos.length === 0 && (
                <tr>
                  <td className="vazio" colSpan={9}>
                    Nenhuma ração encontrada.
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
