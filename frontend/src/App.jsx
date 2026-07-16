import { Routes, Route, NavLink } from "react-router-dom";
import Produtos from "./pages/Produtos.jsx";
import NovoProduto from "./pages/NovoProduto.jsx";
import Marcas from "./pages/Marcas.jsx";

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

function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">🌾</div>
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
          <NavLink to="/marcas">
            <IconMarcas />
            Marcas
          </NavLink>
        </nav>

        <div className="sidebar-footer">Controle de estoque interno · Produsul Cereais</div>
      </aside>

      <main className="main">
        <div className="content">
          <Routes>
            <Route path="/" element={<Produtos />} />
            <Route path="/produtos/novo" element={<NovoProduto />} />
            <Route path="/produtos/:id/editar" element={<NovoProduto />} />
            <Route path="/marcas" element={<Marcas />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
