import { Routes, Route, NavLink } from "react-router-dom";
import Produtos from "./pages/Produtos.jsx";
import NovoProduto from "./pages/NovoProduto.jsx";
import Marcas from "./pages/Marcas.jsx";
import Movimentacoes from "./pages/Movimentacoes.jsx";
import Clientes from "./pages/Clientes.jsx";
import ClienteDetalhe from "./pages/ClienteDetalhe.jsx";

function IconEstoque() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 8 12 3 3 8l9 5 9-5Z" />
      <path d="M3 8v8l9 5 9-5V8" />
      <path d="M12 13v8" />
    </svg>
  );
}

function IconNovo() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

function IconMarcas() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.6 12.6 12.7 20.5a1.9 1.9 0 0 1-2.7 0L3.5 14a1.9 1.9 0 0 1 0-2.7L11.4 3.4A1.9 1.9 0 0 1 12.8 3H19a2 2 0 0 1 2 2v6.2a1.9 1.9 0 0 1-.4 1.4Z" />
      <circle cx="15.5" cy="8.5" r="1.5" />
    </svg>
  );
}

function IconMovimentacoes() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 3v12M13 11l4 4 4-4" />
      <path d="M7 21V9M3 13l4-4 4 4" />
    </svg>
  );
}

function IconClientes() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-mark">P</div>
            <div className="brand-text">
              <strong>Produsul</strong>
              <span>Cereais</span>
            </div>
          </div>

          <nav>
            <NavLink to="/" end>
              <IconEstoque />
              Estoque
            </NavLink>
            <NavLink to="/produtos/novo">
              <IconNovo />
              Nova Ração
            </NavLink>
            <NavLink to="/movimentacoes">
              <IconMovimentacoes />
              Movimentações
            </NavLink>
            <NavLink to="/clientes">
              <IconClientes />
              Clientes
            </NavLink>
            <NavLink to="/marcas">
              <IconMarcas />
              Marcas
            </NavLink>
          </nav>

          <span className="topbar-tag">Controle de estoque interno</span>
        </div>
      </header>

      <main className="main">
        <div className="content">
          <Routes>
            <Route path="/" element={<Produtos />} />
            <Route path="/produtos/novo" element={<NovoProduto />} />
            <Route path="/produtos/:id/editar" element={<NovoProduto />} />
            <Route path="/movimentacoes" element={<Movimentacoes />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/clientes/:id" element={<ClienteDetalhe />} />
            <Route path="/marcas" element={<Marcas />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
