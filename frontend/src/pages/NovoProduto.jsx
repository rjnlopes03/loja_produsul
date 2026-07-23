import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client.js";
import { ESPECIES, FASES_VIDA } from "../constants.js";

const vazio = {
  nome: "",
  marca_id: "",
  especie: "",
  fase_vida: "",
  castrado: "",
  peso_kg: "",
  preco: "",
  quantidade_estoque: 0,
};

export default function NovoProduto() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();

  const [marcas, setMarcas] = useState([]);
  const [form, setForm] = useState(vazio);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.listarMarcas().then(setMarcas);
  }, []);

  useEffect(() => {
    if (editando) {
      api.listarProdutos().then((produtos) => {
        const produto = produtos.find((p) => String(p.id) === id);
        if (produto) {
          setForm({
            nome: produto.nome,
            marca_id: produto.marca_id,
            especie: produto.especie,
            fase_vida: produto.fase_vida,
            castrado: produto.castrado === null || produto.castrado === undefined ? "" : String(produto.castrado),
            peso_kg: produto.peso_kg,
            preco: produto.preco,
            quantidade_estoque: produto.quantidade_estoque,
          });
        }
      });
    }
  }, [editando, id]);

  function atualizarCampo(campo, valor) {
    setForm((f) => {
      const novo = { ...f, [campo]: valor };
      if (campo === "especie" && valor !== "gato") {
        novo.castrado = "";
      }
      return novo;
    });
  }

  async function salvar(e) {
    e.preventDefault();
    setErro("");
    const payload = {
      ...form,
      marca_id: Number(form.marca_id),
      castrado: form.especie === "gato" && form.castrado !== "" ? form.castrado === "true" : null,
      peso_kg: Number(form.peso_kg),
      preco: Number(form.preco),
      quantidade_estoque: Number(form.quantidade_estoque),
    };
    try {
      if (editando) {
        await api.atualizarProduto(id, payload);
      } else {
        await api.criarProduto(payload);
      }
      navigate("/");
    } catch (e2) {
      setErro(e2.message);
    }
  }

  return (
    <div>
      <div className="hero">
        <div className="hero-top">
          <div>
            <h2>{editando ? "Editar Ração" : "Cadastrar Nova Ração"}</h2>
            <p>{editando ? "Atualize os dados desta ração." : "Preencha os dados para adicionar uma ração ao estoque."}</p>
          </div>
        </div>
      </div>

      <form className="form" onSubmit={salvar}>
        <label>
          Nome da ração
          <input
            required
            value={form.nome}
            onChange={(e) => atualizarCampo("nome", e.target.value)}
          />
        </label>

        <label>
          Marca
          <select
            required
            value={form.marca_id}
            onChange={(e) => atualizarCampo("marca_id", e.target.value)}
          >
            <option value="">Selecione</option>
            {marcas.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nome}
              </option>
            ))}
          </select>
        </label>

        <label>
          Destinada a qual animal
          <select
            required
            value={form.especie}
            onChange={(e) => atualizarCampo("especie", e.target.value)}
          >
            <option value="">Selecione</option>
            {ESPECIES.map((op) => (
              <option key={op.value} value={op.value}>
                {op.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Fase de vida
          <select
            required
            value={form.fase_vida}
            onChange={(e) => atualizarCampo("fase_vida", e.target.value)}
          >
            <option value="">Selecione</option>
            {FASES_VIDA.map((op) => (
              <option key={op.value} value={op.value}>
                {op.label}
              </option>
            ))}
          </select>
        </label>

        {form.especie === "gato" && (
          <label>
            Castrado
            <select
              value={form.castrado}
              onChange={(e) => atualizarCampo("castrado", e.target.value)}
            >
              <option value="">Não especificado</option>
              <option value="true">Castrado</option>
              <option value="false">Não castrado</option>
            </select>
          </label>
        )}

        <label>
          Peso (kg)
          <input
            required
            type="number"
            step="0.1"
            min="0.1"
            value={form.peso_kg}
            onChange={(e) => atualizarCampo("peso_kg", e.target.value)}
          />
        </label>

        <label>
          Preço (R$)
          <input
            required
            type="number"
            step="0.01"
            min="0.01"
            value={form.preco}
            onChange={(e) => atualizarCampo("preco", e.target.value)}
          />
        </label>

        <label>
          Quantidade em estoque
          <input
            required
            type="number"
            min="0"
            value={form.quantidade_estoque}
            onChange={(e) => atualizarCampo("quantidade_estoque", e.target.value)}
          />
        </label>

        {erro && <p className="erro">{erro}</p>}

        <button type="submit">{editando ? "Salvar alterações" : "Cadastrar ração"}</button>
      </form>
    </div>
  );
}
