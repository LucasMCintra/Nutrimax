import { useEffect, useMemo, useState } from "react";
import {
  createClient,
  createGoal,
  createMeal,
  getClient,
  getClientFull,
  getCurrentUser,
  getDashboardSummary,
  getMeals,
  getProgress,
  getMealImage,
  setNutritionTarget,
  updateClient,
  updateMeal,
  deleteMeal,
  uploadMealImage,
  updateGoal,
} from "./api";
import { clearToken, getToken } from "./auth";
import Login from "./Login";
import OnboardingForm from "./OnboardingForm";
import MealForm from "./MealForm";
import PlanForm from "./PlanForm";
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

const navItems = [
  { label: "Visão geral", glyph: "⌂" },
  { label: "Refeições", glyph: "◉" },
  { label: "Progresso", glyph: "↗" },
  { label: "Meu plano", glyph: "▤" },
];

function formatNumber(value, maximumFractionDigits = 0) {
  return new Intl.NumberFormat("pt-BR", { maximumFractionDigits }).format(Number(value) || 0);
}

function formatMealDate(value) {
  if (!value) return "Data não informada";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T12:00:00`)).replace(".", "");
}

function MetricCard({ item }) {
  const percentage = Math.min(Math.round((item.value / item.target) * 100), 100);

  return (
    <article className={`metric-card metric-${item.color}`}>
      <div className="metric-topline">
        <span className="metric-icon" aria-hidden="true">{item.icon}</span>
        <span className="metric-label">{item.label}</span>
      </div>
      <div className="metric-value">
        {formatNumber(item.value, item.unit === "kcal" ? 0 : 1)}
        <span>{item.unit}</span>
      </div>
      <div className="metric-progress" aria-label={`${percentage}% da meta de ${item.label}`}>
        <span style={{ width: `${percentage}%` }} />
      </div>
      <div className="metric-foot">
        <span>{percentage}% da meta</span>
        <strong>{formatNumber(item.target, item.unit === "kcal" ? 0 : 1)}{item.unit}</strong>
      </div>
    </article>
  );
}

function CaloriesChart({ points }) {
  const [activePoint, setActivePoint] = useState(null);
  const maxValue = 2500;
  const target = points[0]?.target || 2000;
  const targetPosition = 100 - (target / maxValue) * 100;

  return (
    <article className="chart-card" id="progress-chart">
      <div className="section-heading">
        <div>
          <p className="section-kicker">ÚLTIMOS 7 DIAS</p>
          <h2>Consumo de calorias</h2>
        </div>
        <div className="legend" aria-label={`Meta diária de ${formatNumber(target)} kcal`}>
          <span />
          <small>Meta diária</small>
        </div>
      </div>
      <div className="chart-wrap" aria-label="Consumo de calorias nos últimos sete dias">
        <div className="y-axis" aria-hidden="true">
          <span>2.500</span>
          <span>2.000</span>
          <span>1.500</span>
          <span>1.000</span>
          <span>0</span>
        </div>
        <div className="chart-area" role="list" aria-label="Barras de consumo por dia">
          <div className="target-line" style={{ top: `${targetPosition}%` }} aria-hidden="true" />
          {activePoint && (
            <div className="chart-tooltip" role="status">
              <strong>{formatNumber(activePoint.calories)} kcal</strong>
              <span>{activePoint.day} · meta {formatNumber(activePoint.target)} kcal</span>
            </div>
          )}
          <div className="bars">
            {points.map((item) => {
              const height = Math.max((item.calories / maxValue) * 100, 3);
              const hasData = item.calories > 0;

              return (
                <div className="bar-column" key={`${item.day}-${item.calories}`} role="listitem">
                  <button
                    type="button"
                    className="bar-hit"
                    onMouseEnter={() => setActivePoint(item)}
                    onMouseLeave={() => setActivePoint(null)}
                    onFocus={() => setActivePoint(item)}
                    onBlur={() => setActivePoint(null)}
                    aria-label={`${item.day}: ${hasData ? `${formatNumber(item.calories)} quilocalorias` : "sem registro"}. Meta de ${formatNumber(item.target)} quilocalorias.`}
                  >
                    <span className={`bar ${hasData ? "" : "empty"}`} style={{ height: `${height}%` }} aria-hidden="true" />
                  </button>
                  <small>{item.day}</small>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <details className="data-table">
        <summary>Ver dados em tabela</summary>
        <table>
          <thead>
            <tr><th>Dia</th><th>Calorias</th><th>Meta</th></tr>
          </thead>
          <tbody>
            {points.map((item) => (
              <tr key={`${item.day}-table-${item.calories}`}>
                <td>{item.day}</td>
                <td>{formatNumber(item.calories)} kcal</td>
                <td>{formatNumber(item.target)} kcal</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </article>
  );
}

function GoalBanner({ title, progress, mealCount }) {
  return (
    <section className="goal-banner" aria-labelledby="goal-title">
      <div className="goal-copy">
        <span className="goal-icon" aria-hidden="true">✦</span>
        <div>
          <span className="section-kicker">OBJETIVO ATUAL</span>
          <h2 id="goal-title">{title}</h2>
          <p>Continue acompanhando sua rotina com consistência.</p>
        </div>
      </div>
      <div className="goal-stats">
        <div>
          <strong>{progress}%</strong>
          <span>da meta diária</span>
        </div>
        <div className="goal-ring" aria-label={`${mealCount} refeições registradas`}>
          <span>{mealCount}</span>
          <small>refeições</small>
        </div>
      </div>
    </section>
  );
}

function MealsView({ meals, images, onAddMeal, onEditMeal, onDeleteMeal }) {
  const sortedMeals = useMemo(
    () => [...meals].sort((first, second) => new Date(second.meal_date) - new Date(first.meal_date)),
    [meals],
  );

  return (
    <section className="page-view" aria-labelledby="meals-title" data-enter>
      <div className="page-view-header">
        <div>
          <p className="eyebrow">REGISTRO NUTRICIONAL</p>
          <h1 id="meals-title">Suas refeições</h1>
          <p className="intro">Veja o que já foi registrado e mantenha seu acompanhamento em dia.</p>
        </div>
        <button className="primary-button" type="button" onClick={onAddMeal}>+ Registrar refeição</button>
      </div>

      {sortedMeals.length > 0 ? (
        <div className="meal-list" aria-label="Refeições registradas">
          {sortedMeals.map((meal) => (
            <article className="meal-row" key={meal.id}>
              {images[meal.id] ? <img className="meal-image-thumb" src={images[meal.id]} alt="Refeição registrada" /> : <div className="meal-date-mark" aria-hidden="true">◒</div>}
              <div className="meal-row-main">
                <strong>{formatMealDate(meal.meal_date)}</strong>
                <span>{formatNumber(meal.calories)} kcal registradas</span>
              </div>
              <div className="meal-nutrient-list" aria-label="Nutrientes da refeição">
                <span><b>{formatNumber(meal.protein, 1)}g</b> proteína</span>
                <span><b>{formatNumber(meal.carbohydrates, 1)}g</b> carboidratos</span>
                <span><b>{formatNumber(meal.fat, 1)}g</b> gorduras</span>
              </div>
              <div className="meal-row-actions">
                <button type="button" className="meal-action" onClick={() => onEditMeal(meal)} aria-label={`Editar refeição de ${formatMealDate(meal.meal_date)}`}>Editar</button>
                <button type="button" className="meal-action meal-action-danger" onClick={() => onDeleteMeal(meal)} aria-label={`Excluir refeição de ${formatMealDate(meal.meal_date)}`}>Excluir</button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <span className="empty-state-icon" aria-hidden="true">◌</span>
          <h2>Nenhuma refeição registrada</h2>
          <p>Registre sua primeira refeição para começar a acompanhar seu consumo.</p>
          <button className="secondary-button" type="button" onClick={onAddMeal}>Registrar primeira refeição <span>→</span></button>
        </div>
      )}
    </section>
  );
}

function ProgressView({ points, nutritionItems }) {
  const registeredDays = points.filter((point) => point.calories > 0);
  const averageCalories = registeredDays.length
    ? registeredDays.reduce((total, point) => total + point.calories, 0) / registeredDays.length
    : 0;
  const daysOnTarget = registeredDays.filter((point) => point.calories <= point.target).length;

  return (
    <section className="page-view progress-view" aria-labelledby="progress-title" data-enter>
      <div className="page-view-header">
        <div>
          <p className="eyebrow">HISTÓRICO DE 7 DIAS</p>
          <h1 id="progress-title">Seu progresso</h1>
          <p className="intro">Compare seu consumo recente com a meta diária.</p>
        </div>
      </div>
      <div className="progress-stat-grid" aria-label="Resumo do progresso">
        <article className="progress-stat"><span>Média diária</span><strong>{formatNumber(averageCalories)} <small>kcal</small></strong></article>
        <article className="progress-stat"><span>Dias dentro da meta</span><strong>{daysOnTarget}<small> de {registeredDays.length || points.length}</small></strong></article>
        <article className="progress-stat"><span>Dias registrados</span><strong>{registeredDays.length}<small> de {points.length}</small></strong></article>
      </div>
      <CaloriesChart points={points} />
      <p className="progress-note">Os dados são atualizados sempre que você registra uma nova refeição.</p>
      <div className="progress-nutrition-row">
        {nutritionItems.slice(0, 2).map((item) => (
          <div className={`progress-nutrition progress-${item.color}`} key={item.key}>
            <span>{item.label}</span>
            <strong>{formatNumber(item.value, item.unit === "kcal" ? 0 : 1)}{item.unit}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function PlanView({ goalTitle, nutritionItems, hasTarget, onAddMeal, onEditPlan }) {
  return (
    <section className="page-view plan-view" aria-labelledby="plan-title" data-enter>
      <div className="page-view-header">
        <div>
          <p className="eyebrow">ACOMPANHAMENTO PERSONALIZADO</p>
          <h1 id="plan-title">Meu plano</h1>
          <p className="intro">Seu objetivo e suas referências nutricionais em um só lugar.</p>
        </div>
        <div className="page-view-actions"><button className="secondary-button" type="button" onClick={onEditPlan}>Editar plano</button><button className="primary-button" type="button" onClick={onAddMeal}>+ Registrar refeição</button></div>
      </div>
      <div className="plan-grid">
        <article className="plan-card plan-card-featured">
          <span className="section-kicker">OBJETIVO</span>
          <h2>{goalTitle}</h2>
          <p>Seu acompanhamento diário parte deste objetivo. Registre as refeições para construir um histórico mais preciso.</p>
          <span className="plan-card-mark" aria-hidden="true">✦</span>
        </article>
        <article className="plan-card">
          <span className="section-kicker">METAS NUTRICIONAIS</span>
          <h2>{hasTarget ? "Referências do dia" : "Metas ainda não configuradas"}</h2>
          <div className="plan-target-list">
            {nutritionItems.map((item) => (
              <div className="plan-target" key={item.key}>
                <span className={`target-dot target-${item.color}`} aria-hidden="true" />
                <span>{item.label}</span>
                <strong>{formatNumber(item.target, item.unit === "kcal" ? 0 : 1)}{item.unit}</strong>
              </div>
            ))}
          </div>
          {!hasTarget && <p className="plan-helper">As referências exibidas são uma base inicial para o acompanhamento.</p>}
        </article>
      </div>
      <div className="plan-tip">
        <span className="tip-icon" aria-hidden="true">↗</span>
        <div><strong>O histórico fica melhor com constância.</strong><p>Registre mesmo quando o dia não sair como planejado. Isso também faz parte do progresso.</p></div>
      </div>
    </section>
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
  const [showPlanForm, setShowPlanForm] = useState(false);
  const [showMealForm, setShowMealForm] = useState(false);
  const [editingMeal, setEditingMeal] = useState(null);
  const [mealImages, setMealImages] = useState({});
  const [menuOpen, setMenuOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  const themeLabel = dark ? "Ativar modo claro" : "Ativar modo escuro";
  const todayLabel = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" }).format(new Date()).replace(".", "");
  const weekdayLabel = new Intl.DateTimeFormat("pt-BR", { weekday: "long" }).format(new Date()).toUpperCase();
  const profileName = client?.name?.split(" ")[0] || user?.email?.split("@")[0] || "você";
  const profileInitials = profileName.slice(0, 2).toUpperCase();
  const liveNutrition = summary?.day ? [
    { key: "calories", label: "Calorias", value: summary.day.calories, target: summary.target?.calories || 2000, unit: "kcal", color: "coral", icon: "◒" },
    { key: "protein", label: "Proteínas", value: summary.day.protein, target: summary.target?.protein || 150, unit: "g", color: "blue", icon: "◆" },
    { key: "carbs", label: "Carboidratos", value: summary.day.carbohydrates, target: summary.target?.carbohydrates || 220, unit: "g", color: "amber", icon: "▦" },
    { key: "fat", label: "Gorduras", value: summary.day.fat, target: summary.target?.fat || 60, unit: "g", color: "green", icon: "✦" },
  ] : nutrition;
  const liveWeek = progress?.points?.map((point) => ({
    day: new Date(`${point.date}T12:00:00`).toLocaleDateString("pt-BR", { weekday: "short" }).replace(".", ""),
    calories: point.calories,
    target: progress.target?.calories || 2000,
  })) || week;
  const goalTitle = client?.goal?.description || "Acompanhar meu progresso";
  const goalProgress = summary?.target?.calories ? Math.min(Math.round((summary.day.calories / summary.target.calories) * 100), 100) : 0;

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    window.localStorage.setItem("nutrimax-theme", next ? "dark" : "light");
  };

  const handleLogout = () => {
    clearToken();
    setToken(null);
    setUser(null);
    setClient(null);
    setSummary(null);
    setProgress(null);
    setMeals([]);
    setMealImages({});
  };

  const handleNavChange = (item) => {
    setActiveNav(item);
    setMenuOpen(false);
    setNotificationOpen(false);
    setHelpOpen(false);
  };

  const refreshTrackingData = async () => {
    const today = new Date().toISOString().slice(0, 10);
    const start = new Date();
    start.setDate(start.getDate() - 6);
    const startDate = start.toISOString().slice(0, 10);
    const [dashboard, progressData, clientMeals] = await Promise.all([
      getDashboardSummary(token, today),
      getProgress(token, startDate, today),
      getMeals(token, client.id),
    ]);
    setSummary(dashboard);
    setProgress(progressData);
    setMeals(clientMeals);
    const imageEntries = await Promise.all(clientMeals.map(async (meal) => [meal.id, await getMealImage(token, client.id, meal.id)]));
    setMealImages(Object.fromEntries(imageEntries.filter(([, image]) => image)));
  };

  const handleMealSubmit = async (data) => {
    const savedMeal = editingMeal
      ? await updateMeal(token, client.id, editingMeal.id, data.meal)
      : await createMeal(token, client.id, data.meal);
    if (data.imageFile) await uploadMealImage(token, client.id, savedMeal.id, data.imageFile);
    await refreshTrackingData();
    setEditingMeal(null);
    setShowMealForm(false);
  };

  const handleDeleteMeal = async (meal) => {
    const confirmed = window.confirm(`Excluir a refeição de ${formatMealDate(meal.meal_date)}?`);
    if (!confirmed) return;
    setError("");
    try {
      await deleteMeal(token, client.id, meal.id);
      await refreshTrackingData();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const refreshClientData = async () => {
    const today = new Date().toISOString().slice(0, 10);
    const start = new Date();
    start.setDate(start.getDate() - 6);
    const startDate = start.toISOString().slice(0, 10);
    const [dashboard, progressData, clientDetails] = await Promise.all([
      getDashboardSummary(token, today),
      getProgress(token, startDate, today),
      getClientFull(token, client.id),
    ]);
    setSummary(dashboard);
    setProgress(progressData);
    setClient(clientDetails);
  };

  const handleOnboardingSubmit = async (data) => {
    const createdClient = await createClient(token, data.client);
    await Promise.all([
      createGoal(token, createdClient.id, data.goal),
      setNutritionTarget(token, data.target),
    ]);
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

  const handlePlanSubmit = async (data) => {
    await Promise.all([
      updateClient(token, client.id, data.client),
      updateGoal(token, client.id, data.goal),
      setNutritionTarget(token, data.target),
    ]);
    await refreshClientData();
    setShowPlanForm(false);
  };

  useEffect(() => {
    if (!token) return undefined;

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

        const [dashboard, progressData, clientDetails] = await Promise.all([
          getDashboardSummary(token, today),
          getProgress(token, startDate, today),
          getClientFull(token, clients[0].id),
        ]);
        const clientMeals = await getMeals(token, clients[0].id);

        setUser(currentUser);
        setClient(clientDetails || clients[0]);
        setSummary(dashboard);
        setProgress(progressData);
        setMeals(clientMeals);
        const imageEntries = await Promise.all(clientMeals.map(async (meal) => [meal.id, await getMealImage(token, clients[0].id, meal.id)]));
        setMealImages(Object.fromEntries(imageEntries.filter(([, image]) => image)));
      } catch (requestError) {
        clearToken();
        setToken(null);
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
    return undefined;
  }, [token]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setMenuOpen(false);
        setNotificationOpen(false);
        setHelpOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (!token) return <Login onAuthenticated={setToken} />;
  if (loading) return <main className="loading-screen"><span className="brand-mark">N</span><p>Preparando seu dia...</p></main>;

  const renderActiveView = () => {
    if (activeNav === "Refeições") {
      return <MealsView
        meals={meals}
        images={mealImages}
        onAddMeal={() => { setEditingMeal(null); setShowMealForm(true); }}
        onEditMeal={(meal) => { setEditingMeal(meal); setShowMealForm(true); }}
        onDeleteMeal={handleDeleteMeal}
      />;
    }

    if (activeNav === "Progresso") {
      return <ProgressView points={liveWeek} nutritionItems={liveNutrition} />;
    }

    if (activeNav === "Meu plano") {
      return <PlanView goalTitle={goalTitle} nutritionItems={liveNutrition} hasTarget={Boolean(summary?.target)} onAddMeal={() => setShowMealForm(true)} onEditPlan={() => setShowPlanForm(true)} />;
    }

    return (
      <>
        <section className="welcome" data-enter>
          <div>
            <p className="eyebrow">{weekdayLabel}, {todayLabel.toUpperCase()}</p>
            <h1>Seu dia, em equilíbrio.</h1>
            <p className="intro">Acompanhe seu progresso, {profileName}.</p>
          </div>
          <button className="primary-button" type="button" onClick={() => setShowMealForm(true)} disabled={!client}>+ Registrar refeição</button>
        </section>

        <GoalBanner title={goalTitle} progress={goalProgress} mealCount={meals.length} />

        <section className="section-block" aria-labelledby="consumption-title">
          <div className="section-heading">
            <div>
              <p className="section-kicker">ACOMPANHAMENTO DE HOJE</p>
              <h2 id="consumption-title">Seu consumo</h2>
            </div>
            <button className="text-button" type="button" onClick={() => handleNavChange("Progresso")}>Ver detalhes <span>→</span></button>
          </div>
          <div className="metrics-grid">{liveNutrition.map((item) => <MetricCard key={item.key} item={item} />)}</div>
        </section>

        <section className="section-block lower-grid" aria-label="Histórico e insight">
          <CaloriesChart points={liveWeek} />
          <aside className="insight-card">
            <div className="insight-header"><span className="spark" aria-hidden="true">✦</span><span className="section-kicker">INSIGHT DO DIA</span></div>
            <h2>Pequenos passos fazem grandes mudanças.</h2>
            <p>Você já atingiu {liveNutrition[1] ? Math.min(Math.round((liveNutrition[1].value / liveNutrition[1].target) * 100), 100) : 0}% da sua meta de proteína. Continue registrando suas refeições para manter o equilíbrio.</p>
            <button className="secondary-button" type="button" onClick={() => setShowMealForm(true)} disabled={!client}>Registrar agora <span>→</span></button>
            <div className="insight-art" aria-hidden="true"><span>✦</span><span>•</span><span>✦</span></div>
          </aside>
        </section>
      </>
    );
  };

  return (
    <div className={dark ? "app-shell dark" : "app-shell"}>
      <aside className={menuOpen ? "sidebar menu-open" : "sidebar"}>
        <div className="sidebar-header">
          <div className="brand"><span className="brand-mark">N</span><span>Nutrimax</span></div>
          <button
            className="mobile-menu-toggle"
            type="button"
            onClick={() => setMenuOpen((current) => !current)}
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={menuOpen}
            aria-controls="primary-navigation"
          >
            <span aria-hidden="true">{menuOpen ? "×" : "☰"}</span>
          </button>
        </div>
        <div className="sidebar-content" id="primary-navigation">
          <div className="profile-card">
            <div className="avatar">{profileInitials}</div>
            <div><strong>Olá, {profileName}</strong><span>Meta em andamento</span></div>
            <button className="icon-button" type="button" onClick={handleLogout} aria-label="Sair da conta" title="Sair da conta">↪</button>
          </div>
          <nav aria-label="Navegação principal">
            {navItems.map((item) => (
              <button
                key={item.label}
                type="button"
                className={activeNav === item.label ? "nav-item active" : "nav-item"}
                onClick={() => handleNavChange(item.label)}
                aria-current={activeNav === item.label ? "page" : undefined}
              >
                <span className="nav-glyph" aria-hidden="true">{item.glyph}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
          <div className="sidebar-bottom">
            <div className="help-wrap">
              <button className="nav-item" type="button" onClick={() => setHelpOpen((current) => !current)} aria-expanded={helpOpen}>
                <span className="nav-glyph" aria-hidden="true">?</span>Ajuda
              </button>
              {helpOpen && <div className="help-popover" role="status">Registre suas refeições todos os dias para acompanhar mudanças com mais clareza.</div>}
            </div>
            <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={themeLabel}>
              <span aria-hidden="true">{dark ? "☼" : "◐"}</span>{dark ? "Modo claro" : "Modo escuro"}
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Dashboard</span><b>/</b><strong>{activeNav}</strong></div>
          <div className="top-actions">
            <span className="date-display">Hoje, {todayLabel}</span>
            <div className="notification-wrap">
              <button className="notification" type="button" onClick={() => setNotificationOpen((current) => !current)} aria-label="Notificações" aria-expanded={notificationOpen} aria-controls="notification-panel">
                <span aria-hidden="true">♢</span><i />
              </button>
              {notificationOpen && (
                <div className="notification-popover" id="notification-panel" role="status">
                  <strong>{meals.length ? "Acompanhamento atualizado" : "Comece seu acompanhamento"}</strong>
                  <span>{meals.length ? "Sua última atualização já está refletida no painel." : "Registre sua primeira refeição para acompanhar seu dia."}</span>
                </div>
              )}
            </div>
            <div className="top-avatar" aria-label={`Perfil de ${profileName}`}>{profileInitials}</div>
          </div>
        </header>

        {error && <p className="global-error" role="status">{error}</p>}
        <div className="view-container">{renderActiveView()}</div>

        <footer><span>© {new Date().getFullYear()} Nutrimax</span><span>Feito para uma rotina mais leve.</span></footer>
      </main>
      {showOnboarding && <OnboardingForm onSubmit={handleOnboardingSubmit} onClose={() => setShowOnboarding(false)} />}
      {showPlanForm && <PlanForm client={client} nutritionItems={liveNutrition} onSubmit={handlePlanSubmit} onClose={() => setShowPlanForm(false)} />}
      {showMealForm && <MealForm meal={editingMeal} onSubmit={handleMealSubmit} onClose={() => { setEditingMeal(null); setShowMealForm(false); }} />}
    </div>
  );
}

export default App;
