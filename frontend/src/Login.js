import { useState } from "react";
import { login, register } from "./api";
import { saveToken } from "./auth";
import "./Login.css";

function Login({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(email, password);
      }
      const token = await login(email, password);
      saveToken(token.access_token);
      onAuthenticated(token.access_token);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand"><span className="brand-mark">N</span><span>Nutrimax</span></div>
        <p className="eyebrow">SUA ROTINA, EM EQUILÍBRIO</p>
        <h1>{mode === "login" ? "Bem-vindo de volta." : "Comece seu equilíbrio."}</h1>
        <p className="auth-intro">{mode === "login" ? "Acesse seu acompanhamento nutricional." : "Crie sua conta e acompanhe seu progresso."}</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" />
          <label htmlFor="password">Senha</label>
          <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength="8" required autoComplete={mode === "login" ? "current-password" : "new-password"} />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-button" disabled={loading}>{loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta"}</button>
        </form>
        <button className="auth-switch" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>{mode === "login" ? "Ainda não tenho uma conta" : "Já tenho uma conta"}</button>
      </section>
      <aside className="auth-aside"><span className="auth-orbit orbit-one" /><span className="auth-orbit orbit-two" /><span className="auth-spark">✦</span><p>Clareza para suas escolhas.<br /><strong>Consistência para seus objetivos.</strong></p></aside>
    </main>
  );
}

export default Login;
