import { useEffect, useState } from "react";
import { createClient, createMeal, getClient, getClientFull, getCurrentUser, getDashboardSummary, getMeals, getProgress } from "./api";
import { clearToken, getToken } from "./auth";
import Login from "./Login";
import OnboardingForm from "./OnboardingForm";
import MealForm from "./MealForm";
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
  const [token, setToken] = useState(getToken);
  const [dark, setDark] = useState(() => window.localStorage.getItem("nutrimax-theme") === "dark");
  const [activeNav, setActiveNav] = useState("Visão geral");
  const [user, setUser] = useState(null);
  const [client, setClient] = useState(null);
  const [summary, setSummary] = useState(null);
  const [progress, setProgress] = useState(null);
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(Boolean(token));
  const [error, setError] = useState("");
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showMealForm, setShowMealForm] = useState(false);

  const themeLabel = dark ? "Ativar modo claro" : "Ativar modo escuro";
  const liveNutrition = summary?.day ? [
    { key: "calories", label: "Calorias", value: summary.day.calories, target: summary.target?.calories || 2000, unit: "kcal", color: "coral", icon: "◒" },
    { key: "protein", label: "Proteínas", value: summary.day.protein, target: summary.target?.protein || 150, unit: "g", color: "blue", icon: "◆" },
    { key: "carbs", label: "Carboidratos", value: summary.day.carbohydrates, target: summary.target?.carbohydrates || 220, unit: "g", color: "amber", icon: "▦" },
    { key: "fat", label: "Gorduras", value: summary.day.fat, target: summary.target?.fat || 60, unit: "g", color: "green", icon: "✦" },
  ] : nutrition;
  const liveWeek = progress?.points?.map((point) => ({
    day: new Date(`${point.date}T12:00:00`).toLocaleDateString("pt-BR", { weekday: "short" }).replace(".", ""),
    calories: point.calories,
    target: progress.target?.calories || 2000
  })) || week;
  const goalTitle = client?.goal?.description || "Acompanhar meu progresso";
  const goalProgress = summary?.target?.calories ? Math.min(Math.round((summary.day.calories / summary.target.calories) * 100), 100) : 0;
  const profileName = client?.name?.split(" ")[0] || user?.email?.split("@")[0] || "você";

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    window.localStorage.setItem("nutrimax-theme", next ? "dark" : "light");
  };

  const handleMealSubmit = async (data) => {
    const savedMeal = await createMeal(token, client.id, data);
    setMeals((currentMeals) => [...currentMeals, savedMeal]);
    const today = new Date().toISOString().slice(0, 10);
    const start = new Date();
    start.setDate(start.getDate() - 6);
    const startDate = start.toISOString().slice(0, 10);
    const [dashboard, progressData] = await Promise.all([
      getDashboardSummary(token, today),
      getProgress(token, startDate, today),
    ]);
    setSummary(dashboard);
    setProgress(progressData);
    setShowMealForm(false);
  };

  const handleOnboardingSubmit = async (data) => {
    await createClient(token, data);
    const currentUser = await getCurrentUser(token);
    const today = new Date().toISOString().slice(0, 10);
    const start = new Date();
    start.setDate(start.getDate() - 6);
    const startDate = start.toISOString().slice(0, 10);

    const [dashboard, progressData, clientList] = await Promise.all([
      getDashboardSummary(token, today),
      getProgress(token, startDate, today),
      getClient(token),
    ]);

    const currentClient = clientList[0];
    const clientMeals = currentClient ? await getMeals(token, currentClient.id) : [];
    const clientDetails = currentClient ? await getClientFull(token, currentClient.id) : null;
    setUser(currentUser);
    setClient(clientDetails || currentClient);
    setSummary(dashboard);
    setProgress(progressData);
    setMeals(clientMeals);
    setShowOnboarding(false);
  };

  useEffect(() => {
    if (!token) return;

    async function loadDashboard() {
      try {
        const today = new Date().toISOString().slice(0, 10);
        const start = new Date();
        start.setDate(start.getDate() - 6);
        const startDate = start.toISOString().slice(0, 10);

        const [currentUser, clients] = await Promise.all([
          getCurrentUser(token),
          getClient(token),
        ]);

        if (clients.length === 0) {
          setShowOnboarding(true);
          return;
        }

        const [dashboard, progressData] = await Promise.all([
          getDashboardSummary(token, today),
          getProgress(token, startDate, today),
        ]);
        const clientMeals = await getMeals(token, clients[0].id);

        setUser(currentUser);
        setClient(clients[0]);
        setSummary(dashboard);
        setProgress(progressData);
        setMeals(clientMeals);
      } catch (requestError) {
        clearToken();
        setToken(null);
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [token]);

  if (!token) return <Login onAuthenticated={setToken} />;
  if (loading) return <main className="loading-screen"><span className="brand-mark">N</span><p>Preparando seu dia...</p></main>;

  return (
    <div className={dark ? "app-shell dark" : "app-shell"}>
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">N</span><span>Nutrimax</span></div>
        <div className="profile-card">
          <div className="avatar">LM</div>
          <div><strong>Olá, {profileName}</strong><span>Meta em andamento</span></div>
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
          <div><p className="eyebrow">SEXTA-FEIRA, 20 DE NOVEMBRO</p><h1>Seu dia, em equilíbrio.</h1><p className="intro">Acompanhe seu progresso, {profileName}.</p>{error && <p className="inline-error" role="status">{error}</p>}</div>
          <button className="primary-button" onClick={() => setShowMealForm(true)} disabled={!client}>+ Registrar refeição</button>
        </section>

        <section className="goal-banner">
          <div className="goal-copy"><span className="goal-icon">✦</span><div><span className="section-kicker">OBJETIVO ATUAL</span><h2>{goalTitle}</h2><p>Continue acompanhando sua rotina com consistência.</p></div></div>
          <div className="goal-stats"><div><strong>{goalProgress}%</strong><span>da meta diária</span></div><div className="goal-ring"><span>{meals.length}</span><small>refeições</small></div></div>
        </section>

        <section className="section-block">
          <div className="section-heading"><div><p className="section-kicker">ACOMPANHAMENTO DE HOJE</p><h2>Seu consumo</h2></div><button className="text-button">Ver detalhes <span>→</span></button></div>
          <div className="metrics-grid">{liveNutrition.map((item) => <MetricCard key={item.key} item={item} />)}</div>
        </section>

        <section className="section-block lower-grid">
          <div className="chart-card">
            <div className="section-heading"><div><p className="section-kicker">ÚLTIMOS 7 DIAS</p><h2>Consumo de calorias</h2></div><div className="legend"><span /><small>Meta diária</small></div></div>
            <div className="chart-wrap" role="img" aria-label="Gráfico de barras do consumo de calorias nos últimos sete dias">
              <div className="y-axis"><span>2.500</span><span>2.000</span><span>1.500</span><span>1.000</span><span>0</span></div>
              <div className="chart-area"><div className="target-line" /><div className="bars">{liveWeek.map((item) => <div className="bar-column" key={`${item.day}-${item.calories}`}><div className={`bar ${item.calories === 0 ? "empty" : ""}`} style={{ height: `${Math.max((item.calories / 2500) * 100, 3)}%` }}><span>{item.calories || "—"}</span></div><small>{item.day}</small></div>)}</div></div>
            </div>
            <details className="data-table"><summary>Ver dados em tabela</summary><table><thead><tr><th>Dia</th><th>Calorias</th><th>Meta</th></tr></thead><tbody>{liveWeek.map((item) => <tr key={`${item.day}-${item.calories}`}><td>{item.day}</td><td>{item.calories || 0} kcal</td><td>{item.target} kcal</td></tr>)}</tbody></table></details>
          </div>
          <aside className="insight-card"><div className="insight-header"><span className="spark">✦</span><span className="section-kicker">INSIGHT DO DIA</span></div><h2>Pequenos passos fazem grandes mudanças.</h2><p>Você já atingiu {liveNutrition[1] ? Math.min(Math.round((liveNutrition[1].value / liveNutrition[1].target) * 100), 100) : 0}% da sua meta de proteína. Continue registrando suas refeições para manter o equilíbrio.</p><button className="secondary-button" onClick={() => setShowMealForm(true)} disabled={!client}>Registrar agora <span>→</span></button><div className="insight-art" aria-hidden="true"><span>✦</span><span>•</span><span>✦</span></div></aside>
        </section>

        <footer><span>© 2026 Nutrimax</span><span>Feito para uma rotina mais leve.</span></footer>
      </main>
      {showOnboarding && <OnboardingForm onSubmit={handleOnboardingSubmit} onClose={() => setShowOnboarding(false)} />}
      {showMealForm && <MealForm onSubmit={handleMealSubmit} onClose={() => setShowMealForm(false)} />}
    </div>
  );
}

export default App;