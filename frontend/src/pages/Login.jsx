import { useState } from "react";
import { api } from "../api/client.js";

export default function Login({ aoLogar }) {
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");

  async function entrar(e) {
    e.preventDefault();
    setErro("");
    try {
      const { token } = await api.login(usuario, senha);
      localStorage.setItem("token", token);
      aoLogar();
    } catch (e2) {
      setErro(e2.message);
    }
  }

  return (
    <div className="login-page">
      <form className="form" onSubmit={entrar}>
        <div className="brand">
          <div className="brand-mark">P</div>
          <div className="brand-text">
            <strong>Produsul</strong>
            <span>Cereais</span>
          </div>
        </div>

        <label>
          Usuário
          <input
            required
            autoFocus
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
          />
        </label>

        <label>
          Senha
          <input
            required
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
        </label>

        {erro && <p className="erro">{erro}</p>}

        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}
