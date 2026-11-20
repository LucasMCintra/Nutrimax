import { useState } from "react";
import "./OnboardingForm.css";

function OnboardingForm({ onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: "",
    weight: null,
    height: null,
    age: null,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === "name" ? value : (value ? (name === "age" ? parseInt(value, 10) : parseFloat(value)) : null),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
      <div className="onboarding-card">
        <h2 id="onboarding-title">Complete seu perfil</h2>
        <p className="onboarding-intro">Preencha seus dados para começarmos a acompanhar seu progresso.</p>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Nome completo</label>
            <input
              id="name"
              type="text"
              name="name"
              value={formData.name || ""}
              onChange={handleChange}
              required
              autoComplete="name"
              placeholder="Ex: Lucas Moraes"
            />
          </div>
          <div className="form-group">
            <label htmlFor="weight">Peso (kg)</label>
            <input
              id="weight"
              type="number"
              name="weight"
              value={formData.weight !== null ? formData.weight : ""}
              onChange={handleChange}
              step="0.1"
              min="30"
              max="200"
              placeholder="Ex: 75.5"
            />
          </div>
          <div className="form-group">
            <label htmlFor="height">Altura (cm)</label>
            <input
              id="height"
              type="number"
              name="height"
              value={formData.height !== null ? formData.height : ""}
              onChange={handleChange}
              step="1"
              min="130"
              max="250"
              placeholder="Ex: 175"
            />
          </div>
          <div className="form-group">
            <label htmlFor="age">Idade</label>
            <input
              id="age"
              type="number"
              name="age"
              value={formData.age !== null ? String(formData.age) : ""}
              onChange={handleChange}
              min="13"
              max="99"
              placeholder="Ex: 30"
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? "Salvando..." : "Salvar perfil"}
            </button>
            <button type="button" className="secondary-button" onClick={onClose}>
              Pular
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default OnboardingForm;