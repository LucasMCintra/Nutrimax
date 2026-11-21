import { useEffect, useState } from "react";
import "./OnboardingForm.css";

const goals = [
  "Perder peso",
  "Ganhar massa muscular",
  "Manter peso",
  "Perder gordura",
];

function PlanForm({ client, nutritionItems, onSubmit, onClose }) {
  const [formData, setFormData] = useState({
    name: client?.name || "",
    weight: client?.weight ?? "",
    height: client?.height ?? "",
    age: client?.age ?? "",
    goal: client?.goal?.description || "Manter peso",
    calories: nutritionItems.find((item) => item.key === "calories")?.target || 2000,
    protein: nutritionItems.find((item) => item.key === "protein")?.target || 150,
    carbohydrates: nutritionItems.find((item) => item.key === "carbs")?.target || 220,
    fat: nutritionItems.find((item) => item.key === "fat")?.target || 60,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setFormData((current) => ({
      ...current,
      name: client?.name || "",
      weight: client?.weight ?? "",
      height: client?.height ?? "",
      age: client?.age ?? "",
      goal: client?.goal?.description || current.goal,
    }));
  }, [client]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onSubmit({
        client: {
          name: formData.name.trim(),
          weight: formData.weight === "" ? null : Number(formData.weight),
          height: formData.height === "" ? null : Number(formData.height),
          age: formData.age === "" ? null : Number(formData.age),
        },
        goal: formData.goal,
        target: {
          calories: Number(formData.calories),
          protein: Number(formData.protein),
          carbohydrates: Number(formData.carbohydrates),
          fat: Number(formData.fat),
        },
      });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="plan-form-title">
      <div className="onboarding-card onboarding-card-wide">
        <div className="onboarding-heading">
          <div>
            <p className="onboarding-kicker">PLANO PERSONALIZADO</p>
            <h2 id="plan-form-title">Ajuste suas referências</h2>
            <p className="onboarding-intro">Atualize seus dados para manter o acompanhamento alinhado à sua rotina.</p>
          </div>
          <button type="button" className="onboarding-close" onClick={onClose} aria-label="Fechar formulário">×</button>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <fieldset>
            <legend>Seus dados</legend>
            <div className="onboarding-fields onboarding-fields-profile">
              <div className="form-group form-group-wide"><label htmlFor="plan-name">Nome completo</label><input id="plan-name" type="text" name="name" value={formData.name} onChange={handleChange} required /></div>
              <div className="form-group"><label htmlFor="plan-weight">Peso (kg)</label><input id="plan-weight" type="number" name="weight" value={formData.weight} onChange={handleChange} min="30" max="300" step="0.1" /></div>
              <div className="form-group"><label htmlFor="plan-height">Altura (cm)</label><input id="plan-height" type="number" name="height" value={formData.height} onChange={handleChange} min="100" max="250" step="1" /></div>
              <div className="form-group"><label htmlFor="plan-age">Idade</label><input id="plan-age" type="number" name="age" value={formData.age} onChange={handleChange} min="13" max="120" /></div>
            </div>
          </fieldset>
          <fieldset>
            <legend>Seu objetivo</legend>
            <div className="form-group"><label htmlFor="plan-goal">Objetivo principal</label><select id="plan-goal" name="goal" value={formData.goal} onChange={handleChange}>{goals.map((goal) => <option key={goal} value={goal}>{goal}</option>)}</select></div>
          </fieldset>
          <fieldset>
            <legend>Metas diárias</legend>
            <div className="onboarding-fields onboarding-fields-target">
              <div className="form-group"><label htmlFor="plan-calories">Calorias (kcal)</label><input id="plan-calories" type="number" name="calories" value={formData.calories} onChange={handleChange} min="1" step="1" required /></div>
              <div className="form-group"><label htmlFor="plan-protein">Proteínas (g)</label><input id="plan-protein" type="number" name="protein" value={formData.protein} onChange={handleChange} min="0" step="0.1" required /></div>
              <div className="form-group"><label htmlFor="plan-carbohydrates">Carboidratos (g)</label><input id="plan-carbohydrates" type="number" name="carbohydrates" value={formData.carbohydrates} onChange={handleChange} min="0" step="0.1" required /></div>
              <div className="form-group"><label htmlFor="plan-fat">Gorduras (g)</label><input id="plan-fat" type="number" name="fat" value={formData.fat} onChange={handleChange} min="0" step="0.1" required /></div>
            </div>
          </fieldset>
          <div className="form-actions"><button type="submit" className="primary-button" disabled={loading}>{loading ? "Salvando..." : "Salvar alterações"}</button><button type="button" className="secondary-button" onClick={onClose}>Cancelar</button></div>
        </form>
      </div>
    </div>
  );
}

export default PlanForm;
