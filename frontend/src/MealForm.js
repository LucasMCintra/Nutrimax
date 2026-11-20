import { useState } from "react";
import "./OnboardingForm.css";

const initialData = {
  meal_date: new Date().toISOString().slice(0, 10),
  calories: "",
  protein: "",
  carbohydrates: "",
  fat: "",
};

function MealForm({ onSubmit, onClose }) {
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
        meal_date: formData.meal_date,
        calories: Number(formData.calories) || 0,
        protein: Number(formData.protein) || 0,
        carbohydrates: Number(formData.carbohydrates) || 0,
        fat: Number(formData.fat) || 0,
      });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="meal-form-title">
      <div className="onboarding-card meal-form-card">
        <h2 id="meal-form-title">Registrar refeição</h2>
        <p className="onboarding-intro">Adicione os nutrientes consumidos para atualizar seu acompanhamento.</p>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="meal_date">Data</label>
            <input id="meal_date" type="date" name="meal_date" value={formData.meal_date} onChange={handleChange} required />
          </div>
          <div className="meal-nutrients">
            <div className="form-group"><label htmlFor="calories">Calorias (kcal)</label><input id="calories" type="number" name="calories" value={formData.calories} onChange={handleChange} min="0" step="1" required /></div>
            <div className="form-group"><label htmlFor="protein">Proteínas (g)</label><input id="protein" type="number" name="protein" value={formData.protein} onChange={handleChange} min="0" step="0.1" /></div>
            <div className="form-group"><label htmlFor="carbohydrates">Carboidratos (g)</label><input id="carbohydrates" type="number" name="carbohydrates" value={formData.carbohydrates} onChange={handleChange} min="0" step="0.1" /></div>
            <div className="form-group"><label htmlFor="fat">Gorduras (g)</label><input id="fat" type="number" name="fat" value={formData.fat} onChange={handleChange} min="0" step="0.1" /></div>
          </div>
          <div className="form-actions">
            <button type="submit" className="primary-button" disabled={loading}>{loading ? "Salvando..." : "Registrar refeição"}</button>
            <button type="button" className="secondary-button" onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default MealForm;