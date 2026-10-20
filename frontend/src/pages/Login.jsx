import { useState } from "react";
import { api, salvarToken } from "../api/client.js";

export default function Login({ onEntrar }) {
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function entrar(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      const { token } = await api.login(senha);
      salvarToken(token);
      onEntrar();
    } catch (e2) {
      setErro(e2.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login">
      <form className="form" onSubmit={entrar}>
        <div className="brand">
          <div className="brand-mark">P</div>
          <div className="brand-text">
            <strong>Produsul</strong>
            <span>Cereais</span>
          </div>
        </div>
        <strong>Acesso do administrador</strong>
        {erro && <p className="erro">{erro}</p>}
        <label>
          Senha
          <input
            type="password"
            required
            autoFocus
            autoComplete="current-password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
        </label>
        <button type="submit" disabled={enviando}>
          {enviando ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
