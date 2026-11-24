import { useEffect, useState } from "react";
import "./OnboardingForm.css";

function DietForm({ diet, onSubmit, onClose }) {
  const [description, setDescription] = useState(diet?.description || "");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const isEditing = Boolean(diet);

  useEffect(() => {
    setDescription(diet?.description || "");
  }, [diet]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const value = description.trim();
    if (!value) {
      setError("Descreva sua dieta antes de salvar.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await onSubmit(value);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="diet-form-title">
      <div className="onboarding-card diet-form-card">
        <div className="onboarding-heading">
          <div>
            <p className="onboarding-kicker">PLANO ALIMENTAR</p>
            <h2 id="diet-form-title">{isEditing ? "Editar dieta" : "Adicionar dieta"}</h2>
            <p className="onboarding-intro">Descreva a estratégia alimentar que você está seguindo para manter o plano visível.</p>
          </div>
          <button type="button" className="onboarding-close" onClick={onClose} aria-label="Fechar formulário">×</button>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="diet-description">Descrição da dieta</label>
            <textarea id="diet-description" value={description} onChange={(event) => setDescription(event.target.value)} maxLength="2000" rows="6" placeholder="Ex: refeições equilibradas com foco em proteínas e vegetais" />
            <span className="field-counter">{description.length}/2000</span>
          </div>
          <div className="form-actions"><button type="submit" className="primary-button" disabled={loading}>{loading ? "Salvando..." : "Salvar dieta"}</button><button type="button" className="secondary-button" onClick={onClose}>Cancelar</button></div>
        </form>
      </div>
    </div>
  );
}

export default DietForm;
