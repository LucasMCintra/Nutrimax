import { useState } from "react";
import "./OnboardingForm.css";

const emptyItem = {
  food_name: "",
  quantity: "",
  unit: "g",
  calories: "",
  protein: "",
  carbohydrates: "",
  fat: "",
  confidence: null,
  selected: true,
};

function MealAnalysisForm({ meal, onSubmit, onClose }) {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const addItem = () => setItems((current) => [...current, { ...emptyItem }]);

  const updateItem = (index, field, value) => {
    setItems((current) => current.map((item, itemIndex) => (
      itemIndex === index ? { ...item, [field]: value } : item
    )));
  };

  const removeItem = (index) => setItems((current) => current.filter((_, itemIndex) => itemIndex !== index));

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!items.length) {
      setError("Adicione pelo menos um alimento antes de confirmar.");
      return;
    }
    if (!items.some((item) => item.selected)) {
      setError("Selecione pelo menos um alimento para confirmar.");
      return;
    }
    if (items.some((item) => item.selected && (!item.food_name.trim() || Number(item.quantity) <= 0))) {
      setError("Preencha o nome e a quantidade de todos os alimentos.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await onSubmit(items.filter((item) => item.selected).map((item) => ({
        ...item,
        food_name: item.food_name.trim(),
        quantity: Number(item.quantity),
        calories: Number(item.calories) || 0,
        protein: Number(item.protein) || 0,
        carbohydrates: Number(item.carbohydrates) || 0,
        fat: Number(item.fat) || 0,
      })));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="analysis-title">
      <div className="onboarding-card onboarding-card-wide analysis-card">
        <div className="onboarding-heading">
          <div>
            <p className="onboarding-kicker">REVISÃO NUTRICIONAL</p>
            <h2 id="analysis-title">Revise sua refeição</h2>
            <p className="onboarding-intro">Revise os alimentos identificados e confirme os nutrientes antes de atualizar seu acompanhamento.</p>
          </div>
          <button type="button" className="onboarding-close" onClick={onClose} aria-label="Fechar análise">×</button>
        </div>
        <div className="analysis-meal-context"><span>REFEIÇÃO</span><strong>{new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${meal.meal_date}T12:00:00`)).replace(".", "")}</strong></div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="analysis-items">
            {items.map((item, index) => (
              <fieldset className="analysis-item" key={`analysis-item-${index}`}>
                <legend><label className="analysis-select-label"><input type="checkbox" checked={item.selected} onChange={(event) => updateItem(index, "selected", event.target.checked)} /> Alimento {index + 1}</label></legend>
                <div className="analysis-item-grid">
                  <div className="form-group analysis-food-name"><label htmlFor={`analysis-food-${index}`}>Alimento</label><input id={`analysis-food-${index}`} value={item.food_name} onChange={(event) => updateItem(index, "food_name", event.target.value)} placeholder="Ex: arroz integral" /></div>
                  <div className="form-group"><label htmlFor={`analysis-quantity-${index}`}>Quantidade</label><input id={`analysis-quantity-${index}`} type="number" min="0.1" step="0.1" value={item.quantity} onChange={(event) => updateItem(index, "quantity", event.target.value)} placeholder="150" /></div>
                  <div className="form-group"><label htmlFor={`analysis-unit-${index}`}>Unidade</label><select id={`analysis-unit-${index}`} value={item.unit} onChange={(event) => updateItem(index, "unit", event.target.value)}><option value="g">g</option><option value="ml">ml</option><option value="unidade">unidade</option><option value="colher">colher</option></select></div>
                  <button type="button" className="analysis-remove" onClick={() => removeItem(index)} aria-label={`Remover alimento ${index + 1}`}>Remover</button>
                </div>
                <div className="analysis-nutrients-grid">
                  <div className="form-group"><label htmlFor={`analysis-calories-${index}`}>Calorias</label><input id={`analysis-calories-${index}`} type="number" min="0" step="0.1" value={item.calories} onChange={(event) => updateItem(index, "calories", event.target.value)} /></div>
                  <div className="form-group"><label htmlFor={`analysis-protein-${index}`}>Proteínas (g)</label><input id={`analysis-protein-${index}`} type="number" min="0" step="0.1" value={item.protein} onChange={(event) => updateItem(index, "protein", event.target.value)} /></div>
                  <div className="form-group"><label htmlFor={`analysis-carbs-${index}`}>Carboidratos (g)</label><input id={`analysis-carbs-${index}`} type="number" min="0" step="0.1" value={item.carbohydrates} onChange={(event) => updateItem(index, "carbohydrates", event.target.value)} /></div>
                  <div className="form-group"><label htmlFor={`analysis-fat-${index}`}>Gorduras (g)</label><input id={`analysis-fat-${index}`} type="number" min="0" step="0.1" value={item.fat} onChange={(event) => updateItem(index, "fat", event.target.value)} /></div>
                </div>
              </fieldset>
            ))}
          </div>
          <button type="button" className="analysis-add" onClick={addItem}>+ Adicionar alimento</button>
          <div className="form-actions"><button type="submit" className="primary-button" disabled={loading}>{loading ? "Confirmando..." : "Confirmar análise"}</button><button type="button" className="secondary-button" onClick={onClose}>Cancelar</button></div>
        </form>
      </div>
    </div>
  );
}

export default MealAnalysisForm;
