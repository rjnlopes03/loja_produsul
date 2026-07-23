import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client.js";
import { classificarSaldo, formatarMoeda } from "../format.js";
import { useApiData } from "../hooks/useApiData.js";

export default function ClienteDetalhe() {
  const { id } = useParams();
  const [produtos, setProdutos] = useState([]);
  const [compraForm, setCompraForm] = useState({ produto_id: "", quantidade: "" });
  const [valorPagamento, setValorPagamento] = useState("");
  const {
    dados: resumo,
    carregando,
    erro,
    setErro,
    carregar,
  } = useApiData(() => api.obterResumoCliente(id), [id], null);

  useEffect(() => {
    api.listarProdutos().then(setProdutos).catch((e) => setErro(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function registrarCompra(e) {
    e.preventDefault();
    setErro("");
    try {
      await api.criarCompra(id, {
        produto_id: Number(compraForm.produto_id),
        quantidade: Number(compraForm.quantidade),
      });
      setCompraForm({ produto_id: "", quantidade: "" });
      carregar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  async function registrarPagamento(e) {
    e.preventDefault();
    setErro("");
    try {
      await api.criarPagamento(id, { valor: Number(valorPagamento) });
      setValorPagamento("");
      carregar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  if (carregando) return <p className="carregando">Carregando...</p>;
  if (!resumo) return erro ? <p className="erro">{erro}</p> : null;

  const { cliente, compras, pagamentos, saldo_devedor } = resumo;
  const situacaoSaldo = classificarSaldo(saldo_devedor);

  return (
    <div>
      <div className="hero">
        <div className="hero-top">
          <div>
            <Link className="hero-voltar" to="/clientes">
              ← Clientes
            </Link>
            <h2>{cliente.nome}</h2>
            <p>Compras registradas na conta e pagamentos recebidos.</p>
          </div>

          <div className="hero-stats">
            <div
              className={`stat-chip ${
                situacaoSaldo === "devedor" ? "stat-alert" : situacaoSaldo === "credito" ? "stat-credit" : ""
              }`}
            >
              <div className="stat-icon">R$</div>
              <div>
                <strong>{formatarMoeda(saldo_devedor)}</strong>
                <span>{situacaoSaldo === "credito" ? "crédito do cliente" : "saldo devedor"}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {erro && <p className="erro">{erro}</p>}

      <div className="duas-colunas">
        <form className="form" onSubmit={registrarCompra}>
          <strong>Registrar compra</strong>
          <label>
            Ração
            <select
              required
              value={compraForm.produto_id}
              onChange={(e) => setCompraForm((f) => ({ ...f, produto_id: e.target.value }))}
            >
              <option value="">Selecione</option>
              {produtos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nome} — R$ {p.preco.toFixed(2)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Quantidade
            <input
              required
              type="number"
              min="1"
              value={compraForm.quantidade}
              onChange={(e) => setCompraForm((f) => ({ ...f, quantidade: e.target.value }))}
            />
          </label>
          <button type="submit">Adicionar à conta</button>
        </form>

        <form className="form" onSubmit={registrarPagamento}>
          <strong>Registrar pagamento</strong>
          <label>
            Valor (R$)
            <input
              required
              type="number"
              step="0.01"
              min="0.01"
              value={valorPagamento}
              onChange={(e) => setValorPagamento(e.target.value)}
            />
          </label>
          <button className="btn-primary" type="submit">
            Registrar pagamento
          </button>
        </form>
      </div>

      <h3 className="subtitulo">Compras</h3>
      <div className="tabela-wrap">
        <table className="tabela">
          <thead>
            <tr>
              <th>Data</th>
              <th>Ração</th>
              <th>Quantidade</th>
              <th>Preço unit.</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {compras.map((c) => (
              <tr key={c.id}>
                <td>{new Date(c.criado_em).toLocaleDateString("pt-BR")}</td>
                <td className="nome-produto">{c.produto.nome}</td>
                <td>{c.quantidade}</td>
                <td>R$ {c.preco_unitario.toFixed(2)}</td>
                <td>R$ {c.valor_total.toFixed(2)}</td>
              </tr>
            ))}
            {compras.length === 0 && (
              <tr>
                <td className="vazio" colSpan={5}>
                  Nenhuma compra registrada.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <h3 className="subtitulo">Pagamentos</h3>
      <div className="tabela-wrap">
        <table className="tabela">
          <thead>
            <tr>
              <th>Data</th>
              <th>Valor</th>
            </tr>
          </thead>
          <tbody>
            {pagamentos.map((p) => (
              <tr key={p.id}>
                <td>{new Date(p.criado_em).toLocaleDateString("pt-BR")}</td>
                <td>R$ {p.valor.toFixed(2)}</td>
              </tr>
            ))}
            {pagamentos.length === 0 && (
              <tr>
                <td className="vazio" colSpan={2}>
                  Nenhum pagamento registrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
