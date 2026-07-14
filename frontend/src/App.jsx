import { Routes, Route, NavLink } from "react-router-dom";
import Produtos from "./pages/Produtos.jsx";
import NovoProduto from "./pages/NovoProduto.jsx";
import Marcas from "./pages/Marcas.jsx";

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <h1>Produsul Cereais</h1>
        <nav>
          <NavLink to="/" end>
            Estoque
          </NavLink>
          <NavLink to="/produtos/novo">Nova Ração</NavLink>
          <NavLink to="/marcas">Marcas</NavLink>
        </nav>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<Produtos />} />
          <Route path="/produtos/novo" element={<NovoProduto />} />
          <Route path="/produtos/:id/editar" element={<NovoProduto />} />
          <Route path="/marcas" element={<Marcas />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
