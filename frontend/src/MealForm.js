import { useState } from "react";
import "./OnboardingForm.css";

const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

function MealForm({ meal, onSubmit, onClose }) {
  const [formData, setFormData] = useState({
    meal_date: meal?.meal_date || new Date().toISOString().slice(0, 10),
    calories: meal?.calories ?? "",
    protein: meal?.protein ?? "",
    carbohydrates: meal?.carbohydrates ?? "",
    fat: meal?.fat ?? "",
  });
  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const isEditing = Boolean(meal);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleImageChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
      setError("Escolha uma imagem JPEG, PNG ou WebP.");
      event.target.value = "";
      return;
    }
    if (file.size > MAX_IMAGE_SIZE) {
      setError("A imagem deve ter no máximo 5 MB.");
      event.target.value = "";
      return;
    }
    setError("");
    setImageFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onSubmit({
        meal: {
          meal_date: formData.meal_date,
          calories: Number(formData.calories) || 0,
          protein: Number(formData.protein) || 0,
          carbohydrates: Number(formData.carbohydrates) || 0,
          fat: Number(formData.fat) || 0,
        },
        imageFile,
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
        <div className="onboarding-heading">
          <div>
            <p className="onboarding-kicker">REGISTRO NUTRICIONAL</p>
            <h2 id="meal-form-title">{isEditing ? "Editar refeição" : "Registrar refeição"}</h2>
            <p className="onboarding-intro">{isEditing ? "Corrija os dados para manter seu histórico preciso." : "Adicione os nutrientes consumidos para atualizar seu acompanhamento."}</p>
          </div>
          <button type="button" className="onboarding-close" onClick={onClose} aria-label="Fechar formulário">×</button>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="meal_date">Data</label>
            <input id="meal_date" type="date" name="meal_date" value={formData.meal_date} onChange={handleChange} required />
          </div>
          <div className="meal-image-field">
            <label htmlFor="meal-image">Foto da refeição <span>opcional</span></label>
            <input id="meal-image" type="file" accept="image/jpeg,image/png,image/webp" onChange={handleImageChange} />
            {previewUrl && <img className="meal-image-preview" src={previewUrl} alt="Pré-visualização da refeição selecionada" />}
          </div>
          <div className="meal-nutrients">
            <div className="form-group"><label htmlFor="calories">Calorias (kcal)</label><input id="calories" type="number" name="calories" value={formData.calories} onChange={handleChange} min="0" step="1" required /></div>
            <div className="form-group"><label htmlFor="protein">Proteínas (g)</label><input id="protein" type="number" name="protein" value={formData.protein} onChange={handleChange} min="0" step="0.1" /></div>
            <div className="form-group"><label htmlFor="carbohydrates">Carboidratos (g)</label><input id="carbohydrates" type="number" name="carbohydrates" value={formData.carbohydrates} onChange={handleChange} min="0" step="0.1" /></div>
            <div className="form-group"><label htmlFor="fat">Gorduras (g)</label><input id="fat" type="number" name="fat" value={formData.fat} onChange={handleChange} min="0" step="0.1" /></div>
          </div>
          <div className="form-actions">
            <button type="submit" className="primary-button" disabled={loading}>{loading ? "Salvando..." : isEditing ? "Salvar alterações" : "Registrar refeição"}</button>
            <button type="button" className="secondary-button" onClick={onClose}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default MealForm;
