import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client.js";
import { STATUS_PAGAMENTO } from "../constants.js";

const pad = (n) => String(n).padStart(2, "0");

// Data local no formato do <input type="date">.
function dataISO(valor = new Date()) {
  const d = new Date(valor);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// "2026-11-10" -> "10/11/2026", sem passar por Date (evita deslocar o dia pelo fuso).
function formatarDia(iso) {
  const [ano, mes, dia] = iso.split("-");
  return `${dia}/${mes}/${ano}`;
}

function dadosDoCliente(cliente) {
  return {
    nome: cliente.nome,
    telefone: (cliente.telefone || "").replace(/\D/g, ""),
    observacoes: cliente.observacoes || "",
    limite_credito: cliente.limite_credito ?? "",
    dia_vencimento: cliente.dia_vencimento ?? "",
    status_manual: cliente.status_manual || "",
  };
}

function LinhaCompra({ compra, onSalvar, onExcluir }) {
  const [editando, setEditando] = useState(false);
  const [form, setForm] = useState({});

  function editar() {
    setForm({
      quantidade: compra.quantidade,
      preco_unitario: compra.preco_unitario,
      data: dataISO(compra.criado_em),
    });
    setEditando(true);
  }

  async function salvar() {
    const ok = await onSalvar(compra.id, {
      quantidade: Number(form.quantidade),
      preco_unitario: Number(form.preco_unitario),
      data: form.data,
    });
    if (ok) setEditando(false);
  }

  if (!editando) {
    return (
      <tr>
        <td>{new Date(compra.criado_em).toLocaleDateString("pt-BR")}</td>
        <td className="nome-produto">{compra.produto.nome}</td>
        <td>{compra.quantidade}</td>
        <td>R$ {compra.preco_unitario.toFixed(2)}</td>
        <td>R$ {compra.valor_total.toFixed(2)}</td>
        <td className="acoes">
          <button className="btn-sec" onClick={editar}>
            Editar
          </button>
          <button className="btn-danger" onClick={() => onExcluir(compra.id)}>
            Excluir
          </button>
        </td>
      </tr>
    );
  }

  const muda = (campo) => (e) => setForm((f) => ({ ...f, [campo]: e.target.value }));
  return (
    <tr>
      <td>
        <input type="date" required value={form.data} onChange={muda("data")} />
      </td>
      <td className="nome-produto">{compra.produto.nome}</td>
      <td>
        <input type="number" min="1" value={form.quantidade} onChange={muda("quantidade")} />
      </td>
      <td>
        <input type="number" min="0" step="0.01" value={form.preco_unitario} onChange={muda("preco_unitario")} />
      </td>
      <td>R$ {(Number(form.quantidade) * Number(form.preco_unitario) || 0).toFixed(2)}</td>
      <td className="acoes">
        <button onClick={salvar}>Salvar</button>
        <button className="btn-sec" onClick={() => setEditando(false)}>
          Cancelar
        </button>
      </td>
    </tr>
  );
}

function LinhaPagamento({ pagamento, onSalvar, onExcluir }) {
  const [editando, setEditando] = useState(false);
  const [form, setForm] = useState({});

  function editar() {
    setForm({ valor: pagamento.valor, data: dataISO(pagamento.criado_em) });
    setEditando(true);
  }

  async function salvar() {
    const ok = await onSalvar(pagamento.id, { valor: Number(form.valor), data: form.data });
    if (ok) setEditando(false);
  }

  if (!editando) {
    return (
      <tr>
        <td>{new Date(pagamento.criado_em).toLocaleDateString("pt-BR")}</td>
        <td>R$ {pagamento.valor.toFixed(2)}</td>
        <td className="acoes">
          <button className="btn-sec" onClick={editar}>
            Editar
          </button>
          <button className="btn-danger" onClick={() => onExcluir(pagamento.id)}>
            Excluir
          </button>
        </td>
      </tr>
    );
  }

  const muda = (campo) => (e) => setForm((f) => ({ ...f, [campo]: e.target.value }));
  return (
    <tr>
      <td>
        <input type="date" required value={form.data} onChange={muda("data")} />
      </td>
      <td>
        <input type="number" min="0.01" step="0.01" value={form.valor} onChange={muda("valor")} />
      </td>
      <td className="acoes">
        <button onClick={salvar}>Salvar</button>
        <button className="btn-sec" onClick={() => setEditando(false)}>
          Cancelar
        </button>
      </td>
    </tr>
  );
}

export default function ClienteDetalhe() {
  const { id } = useParams();
  const [resumo, setResumo] = useState(null);
  const [produtos, setProdutos] = useState([]);
  const [compraForm, setCompraForm] = useState({ produto_id: "", quantidade: "", data: dataISO() });
  const [pagamentoForm, setPagamentoForm] = useState({ valor: "", data: dataISO() });
  const [dadosForm, setDadosForm] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  function carregar() {
    return api
      .obterResumoCliente(id)
      .then((dados) => {
        setResumo(dados);
        setErro("");
      })
      .catch((e) => setErro(e.message))
      .finally(() => setCarregando(false));
  }

  function carregarProdutos() {
    api.listarProdutos().then(setProdutos).catch(() => {});
  }

  useEffect(() => {
    setCarregando(true);
    carregar();
    carregarProdutos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Executa uma alteração, recarrega a conta e devolve se deu certo.
  async function executar(acao, { estoque = false } = {}) {
    setErro("");
    try {
      await acao();
      await carregar();
      if (estoque) carregarProdutos();
      return true;
    } catch (e) {
      setErro(e.message);
      return false;
    }
  }

  async function registrarCompra(e) {
    e.preventDefault();
    const ok = await executar(
      () =>
        api.criarCompra(id, {
          produto_id: Number(compraForm.produto_id),
          quantidade: Number(compraForm.quantidade),
          data: compraForm.data,
        }),
      { estoque: true }
    );
    if (ok) setCompraForm((f) => ({ ...f, produto_id: "", quantidade: "" }));
  }

  async function registrarPagamento(e) {
    e.preventDefault();
    const ok = await executar(() =>
      api.criarPagamento(id, { valor: Number(pagamentoForm.valor), data: pagamentoForm.data })
    );
    if (ok) setPagamentoForm((f) => ({ ...f, valor: "" }));
  }

  async function salvarDados(e) {
    e.preventDefault();
    const ok = await executar(() =>
      api.atualizarCliente(id, {
        nome: dadosForm.nome,
        telefone: dadosForm.telefone,
        observacoes: dadosForm.observacoes,
        limite_credito: dadosForm.limite_credito === "" ? null : Number(dadosForm.limite_credito),
        dia_vencimento: dadosForm.dia_vencimento === "" ? null : Number(dadosForm.dia_vencimento),
        status_manual: dadosForm.status_manual || null,
      })
    );
    if (ok) setDadosForm(null);
  }

  const salvarCompra = (compraId, dados) =>
    executar(() => api.atualizarCompra(id, compraId, dados), { estoque: true });

  function excluirCompra(compraId) {
    if (!confirm("Excluir esta compra? A ração volta para o estoque.")) return;
    executar(() => api.excluirCompra(id, compraId), { estoque: true });
  }

  const salvarPagamento = (pagamentoId, dados) => executar(() => api.atualizarPagamento(id, pagamentoId, dados));

  function excluirPagamento(pagamentoId) {
    if (!confirm("Excluir este pagamento?")) return;
    executar(() => api.excluirPagamento(id, pagamentoId));
  }

  if (carregando) return <p className="carregando">Carregando...</p>;
  if (!resumo) return erro ? <p className="erro">{erro}</p> : null;

  const { cliente, compras, pagamentos, saldo_devedor, valor_vencido, proximo_vencimento, status, acima_do_limite } =
    resumo;
  const statusInfo = STATUS_PAGAMENTO[status];
  const mudaDados = (campo) => (e) => setDadosForm((f) => ({ ...f, [campo]: e.target.value }));

  return (
    <div>
      <div className="hero">
        <div className="hero-top">
          <div>
            <Link className="hero-voltar" to="/clientes">
              ← Clientes
            </Link>
            <h2>{cliente.nome}</h2>
            <p>
              {[cliente.telefone, cliente.observacoes].filter(Boolean).join(" · ") ||
                "Compras registradas na conta e pagamentos recebidos."}
            </p>
          </div>

          <div className="hero-stats">
            <div
              className={`stat-chip ${
                saldo_devedor > 0 ? "stat-alert" : saldo_devedor < 0 ? "stat-credit" : ""
              }`}
            >
              <div className="stat-icon">R$</div>
              <div>
                <strong>R$ {Math.abs(saldo_devedor).toFixed(2)}</strong>
                <span>
                  {saldo_devedor < 0 ? "crédito do cliente" : "saldo devedor"}
                  {acima_do_limite && " · acima do limite"}
                </span>
              </div>
            </div>
            <div className={`stat-chip ${status === "atrasado" ? "stat-alert" : ""}`}>
              <div className="stat-icon">{status === "atrasado" ? "!" : "✓"}</div>
              <div>
                <strong>{statusInfo.label}</strong>
                <span>
                  {cliente.status_manual
                    ? "definido manualmente"
                    : valor_vencido > 0
                      ? `R$ ${valor_vencido.toFixed(2)} vencido`
                      : proximo_vencimento
                        ? `vence em ${formatarDia(proximo_vencimento)}`
                        : cliente.dia_vencimento
                          ? `vencimento todo dia ${cliente.dia_vencimento}`
                          : "sem dia de vencimento"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {erro && <p className="erro">{erro}</p>}

      {dadosForm ? (
        <form className="form form-larga" onSubmit={salvarDados}>
          <strong>Dados do cliente</strong>
          <div className="form-grade">
            <label>
              Nome
              <input required value={dadosForm.nome} onChange={mudaDados("nome")} />
            </label>
            <label>
              Telefone
              <input
                type="tel"
                inputMode="numeric"
                maxLength={11}
                placeholder="Ex.: 51999998888"
                value={dadosForm.telefone}
                onChange={(e) => setDadosForm((f) => ({ ...f, telefone: e.target.value.replace(/\D/g, "") }))}
              />
              <span className="dica">Somente números, com DDD.</span>
            </label>
            <label>
              Limite de crédito (R$)
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="Sem limite"
                value={dadosForm.limite_credito}
                onChange={mudaDados("limite_credito")}
              />
            </label>
            <label>
              Dia de vencimento
              <input
                type="number"
                min="1"
                max="28"
                placeholder="Sem vencimento"
                value={dadosForm.dia_vencimento}
                onChange={mudaDados("dia_vencimento")}
              />
              <span className="dica">As compras do mês vencem nesse dia do mês seguinte (1 a 28).</span>
            </label>
            <label>
              Status do pagamento
              <select value={dadosForm.status_manual} onChange={mudaDados("status_manual")}>
                <option value="">Automático (pelo vencimento)</option>
                <option value="em_dia">Em dia (manual)</option>
                <option value="atrasado">Atrasado (manual)</option>
              </select>
              <span className="dica">
                Hoje, pelo vencimento: {STATUS_PAGAMENTO[resumo.status_automatico].label.toLowerCase()}.
              </span>
            </label>
          </div>
          <label>
            Observações
            <textarea value={dadosForm.observacoes} onChange={mudaDados("observacoes")} />
          </label>
          <div className="form-acoes">
            <button type="submit">Salvar dados</button>
            <button type="button" className="btn-sec" onClick={() => setDadosForm(null)}>
              Cancelar
            </button>
          </div>
        </form>
      ) : (
        <div className="form-acoes" style={{ marginBottom: "1.5rem" }}>
          <button className="btn-sec" onClick={() => setDadosForm(dadosDoCliente(cliente))}>
            Editar dados do cliente
          </button>
        </div>
      )}

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
                  {p.nome} — R$ {p.preco.toFixed(2)} ({p.quantidade_estoque} em estoque)
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
          <label>
            Data
            <input
              required
              type="date"
              value={compraForm.data}
              onChange={(e) => setCompraForm((f) => ({ ...f, data: e.target.value }))}
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
              value={pagamentoForm.valor}
              onChange={(e) => setPagamentoForm((f) => ({ ...f, valor: e.target.value }))}
            />
          </label>
          <label>
            Data
            <input
              required
              type="date"
              value={pagamentoForm.data}
              onChange={(e) => setPagamentoForm((f) => ({ ...f, data: e.target.value }))}
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
              <th></th>
            </tr>
          </thead>
          <tbody>
            {compras.map((c) => (
              <LinhaCompra key={c.id} compra={c} onSalvar={salvarCompra} onExcluir={excluirCompra} />
            ))}
            {compras.length === 0 && (
              <tr>
                <td className="vazio" colSpan={6}>
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
              <th></th>
            </tr>
          </thead>
          <tbody>
            {pagamentos.map((p) => (
              <LinhaPagamento key={p.id} pagamento={p} onSalvar={salvarPagamento} onExcluir={excluirPagamento} />
            ))}
            {pagamentos.length === 0 && (
              <tr>
                <td className="vazio" colSpan={3}>
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
