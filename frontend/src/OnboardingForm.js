import { useState } from "react";
import "./OnboardingForm.css";

const initialData = {
  name: "",
  weight: "",
  height: "",
  age: "",
  goal: "Manter peso",
  calories: "2000",
  protein: "150",
  carbohydrates: "220",
  fat: "60",
};

const goalOptions = [
  "Perder peso",
  "Ganhar massa muscular",
  "Manter peso",
  "Perder gordura",
];

function OnboardingForm({ onClose, onSubmit }) {
  const [formData, setFormData] = useState(initialData);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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
          weight: formData.weight ? Number(formData.weight) : null,
          height: formData.height ? Number(formData.height) : null,
          age: formData.age ? Number(formData.age) : null,
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
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
      <div className="onboarding-card onboarding-card-wide">
        <div className="onboarding-heading">
          <div>
            <p className="onboarding-kicker">PRIMEIRO PASSO</p>
            <h2 id="onboarding-title">Complete seu perfil</h2>
            <p className="onboarding-intro">Defina seu objetivo e suas referências diárias para personalizar o acompanhamento.</p>
          </div>
          <button type="button" className="onboarding-close" onClick={onClose} aria-label="Fechar formulário">×</button>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <fieldset>
            <legend>Seus dados</legend>
            <div className="onboarding-fields onboarding-fields-profile">
              <div className="form-group form-group-wide">
                <label htmlFor="name">Nome completo</label>
                <input id="name" type="text" name="name" value={formData.name} onChange={handleChange} required autoComplete="name" placeholder="Ex: Lucas Moraes" />
              </div>
              <div className="form-group">
                <label htmlFor="weight">Peso (kg)</label>
                <input id="weight" type="number" name="weight" value={formData.weight} onChange={handleChange} step="0.1" min="30" max="300" placeholder="75,5" />
              </div>
              <div className="form-group">
                <label htmlFor="height">Altura (cm)</label>
                <input id="height" type="number" name="height" value={formData.height} onChange={handleChange} step="1" min="100" max="250" placeholder="175" />
              </div>
              <div className="form-group">
                <label htmlFor="age">Idade</label>
                <input id="age" type="number" name="age" value={formData.age} onChange={handleChange} min="13" max="120" placeholder="30" />
              </div>
            </div>
          </fieldset>

          <fieldset>
            <legend>Seu objetivo</legend>
            <div className="form-group">
              <label htmlFor="goal">Objetivo principal</label>
              <select id="goal" name="goal" value={formData.goal} onChange={handleChange}>
                {goalOptions.map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
            </div>
          </fieldset>

          <fieldset>
            <legend>Metas diárias</legend>
            <div className="onboarding-fields onboarding-fields-target">
              <div className="form-group">
                <label htmlFor="calories">Calorias (kcal)</label>
                <input id="calories" type="number" name="calories" value={formData.calories} onChange={handleChange} min="1" step="1" required />
              </div>
              <div className="form-group">
                <label htmlFor="protein">Proteínas (g)</label>
                <input id="protein" type="number" name="protein" value={formData.protein} onChange={handleChange} min="0" step="0.1" required />
              </div>
              <div className="form-group">
                <label htmlFor="carbohydrates">Carboidratos (g)</label>
                <input id="carbohydrates" type="number" name="carbohydrates" value={formData.carbohydrates} onChange={handleChange} min="0" step="0.1" required />
              </div>
              <div className="form-group">
                <label htmlFor="fat">Gorduras (g)</label>
                <input id="fat" type="number" name="fat" value={formData.fat} onChange={handleChange} min="0" step="0.1" required />
              </div>
            </div>
          </fieldset>

          <div className="form-actions">
            <button type="submit" className="primary-button" disabled={loading}>{loading ? "Salvando..." : "Salvar meu plano"}</button>
            <button type="button" className="secondary-button" onClick={onClose}>Fazer depois</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default OnboardingForm;
