import { useMemo, useState } from "react";
import "./App.css";

const nutrition = [
  { key: "calories", label: "Calorias", value: 1420, target: 2000, unit: "kcal", color: "coral", icon: "◒" },
  { key: "protein", label: "Proteínas", value: 98, target: 150, unit: "g", color: "blue", icon: "◆" },
  { key: "carbs", label: "Carboidratos", value: 164, target: 220, unit: "g", color: "amber", icon: "▦" },
  { key: "fat", label: "Gorduras", value: 42, target: 60, unit: "g", color: "green", icon: "✦" },
];

const week = [
  { day: "Seg", calories: 1840, target: 2000 },
  { day: "Ter", calories: 2050, target: 2000 },
  { day: "Qua", calories: 1720, target: 2000 },
  { day: "Qui", calories: 2210, target: 2000 },
  { day: "Sex", calories: 1420, target: 2000 },
  { day: "Sáb", calories: 0, target: 2000 },
  { day: "Dom", calories: 0, target: 2000 },
];

function MetricCard({ item }) {
  const percentage = Math.min(Math.round((item.value / item.target) * 100), 100);
  return (
    <article className={`metric-card metric-${item.color}`}>
      <div className="metric-topline">
        <span className="metric-icon" aria-hidden="true">{item.icon}</span>
        <span className="metric-label">{item.label}</span>
        <button className="icon-button" aria-label={`Mais opções de ${item.label}`}>•••</button>
      </div>
      <div className="metric-value">{item.value}<span>{item.unit}</span></div>
      <div className="metric-progress" aria-label={`${percentage}% da meta de ${item.label}`}>
        <span style={{ width: `${percentage}%` }} />
      </div>
      <div className="metric-foot"><span>{percentage}% da meta</span><strong>{item.target}{item.unit}</strong></div>
    </article>
  );
}

function App() {
  const [dark, setDark] = useState(() => window.localStorage.getItem("nutrimax-theme") === "dark");
  const [activeNav, setActiveNav] = useState("Visão geral");

  const themeLabel = dark ? "Ativar modo claro" : "Ativar modo escuro";
  const total = useMemo(() => nutrition.reduce((sum, item) => sum + item.value, 0), []);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    window.localStorage.setItem("nutrimax-theme", next ? "dark" : "light");
  };

  return (
    <div className={dark ? "app-shell dark" : "app-shell"}>
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">N</span><span>Nutrimax</span></div>
        <div className="profile-card">
          <div className="avatar">LM</div>
          <div><strong>Olá, Lucas</strong><span>Meta em andamento</span></div>
          <button className="icon-button" aria-label="Abrir menu do perfil">⌄</button>
        </div>
        <nav aria-label="Navegação principal">
          {["Visão geral", "Refeições", "Progresso", "Meu plano"].map((item, index) => (
            <button key={item} className={activeNav === item ? "nav-item active" : "nav-item"} onClick={() => setActiveNav(item)}>
              <span className="nav-glyph" aria-hidden="true">{["⌂", "◉", "↗", "▤"][index]}</span>{item}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button className="nav-item"><span className="nav-glyph">?</span>Ajuda</button>
          <button className="theme-toggle" onClick={toggleTheme} aria-label={themeLabel}><span>{dark ? "☼" : "◐"}</span>{dark ? "Modo claro" : "Modo escuro"}<b>{dark ? "" : ""}</b></button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Dashboard</span><b>/</b><strong>{activeNav}</strong></div>
          <div className="top-actions"><button className="date-button">Hoje, 20 de nov <span>⌄</span></button><button className="notification" aria-label="Notificações"><span>♢</span><i /></button><div className="top-avatar">LM</div></div>
        </header>

        <section className="welcome" data-enter>
          <div><p className="eyebrow">SEXTA-FEIRA, 20 DE NOVEMBRO</p><h1>Seu dia, em equilíbrio.</h1><p className="intro">Acompanhe o que importa e faça escolhas que aproximam você do seu objetivo.</p></div>
          <button className="primary-button">+ Registrar refeição</button>
        </section>

        <section className="goal-banner">
          <div className="goal-copy"><span className="goal-icon">✦</span><div><span className="section-kicker">OBJETIVO ATUAL</span><h2>Manter o peso</h2><p>Você está no ritmo certo. Continue assim!</p></div></div>
          <div className="goal-stats"><div><strong>68%</strong><span>do plano concluído</span></div><div className="goal-ring"><span>12</span><small>dias</small></div></div>
        </section>

        <section className="section-block">
          <div className="section-heading"><div><p className="section-kicker">ACOMPANHAMENTO DE HOJE</p><h2>Seu consumo</h2></div><button className="text-button">Ver detalhes <span>→</span></button></div>
          <div className="metrics-grid">{nutrition.map((item) => <MetricCard key={item.key} item={item} />)}</div>
        </section>

        <section className="section-block lower-grid">
          <div className="chart-card">
            <div className="section-heading"><div><p className="section-kicker">ÚLTIMOS 7 DIAS</p><h2>Consumo de calorias</h2></div><div className="legend"><span /><small>Meta diária</small></div></div>
            <div className="chart-wrap" role="img" aria-label="Gráfico de barras do consumo de calorias nos últimos sete dias">
              <div className="y-axis"><span>2.500</span><span>2.000</span><span>1.500</span><span>1.000</span><span>0</span></div>
              <div className="chart-area"><div className="target-line" /><div className="bars">{week.map((item) => <div className="bar-column" key={item.day}><div className={`bar ${item.calories === 0 ? "empty" : ""}`} style={{ height: `${Math.max((item.calories / 2500) * 100, 3)}%` }}><span>{item.calories || "—"}</span></div><small>{item.day}</small></div>)}</div></div>
            </div>
            <details className="data-table"><summary>Ver dados em tabela</summary><table><thead><tr><th>Dia</th><th>Calorias</th><th>Meta</th></tr></thead><tbody>{week.map((item) => <tr key={item.day}><td>{item.day}</td><td>{item.calories || 0} kcal</td><td>{item.target} kcal</td></tr>)}</tbody></table></details>
          </div>
          <aside className="insight-card"><div className="insight-header"><span className="spark">✦</span><span className="section-kicker">INSIGHT DO DIA</span></div><h2>Pequenos passos fazem grandes mudanças.</h2><p>Você já atingiu 71% da sua meta de proteína. Um lanche rico em proteína pode fechar o dia com equilíbrio.</p><button className="secondary-button">Ver sugestões <span>→</span></button><div className="insight-art" aria-hidden="true"><span>✦</span><span>•</span><span>✦</span></div></aside>
        </section>

        <footer><span>© 2026 Nutrimax</span><span>Feito para uma rotina mais leve.</span></footer>
      </main>
    </div>
  );
}

export default App;
