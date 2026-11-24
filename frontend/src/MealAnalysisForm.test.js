import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import MealAnalysisForm from "./MealAnalysisForm";

describe("MealAnalysisForm", () => {
  const initialItems = [{
    id: 1,
    food_name: "Arroz integral",
    quantity: 150,
    unit: "g",
    calories: 180,
    protein: 4,
    carbohydrates: 38,
    fat: 1,
    confidence: 0.9,
  }, {
    id: 2,
    food_name: "Molho",
    quantity: 20,
    unit: "g",
    calories: 30,
    protein: 0,
    carbohydrates: 4,
    fat: 1,
    confidence: 0.6,
  }];

  it("envia apenas os itens selecionados", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<MealAnalysisForm meal={{ meal_date: "2026-01-01" }} initialItems={initialItems} onSubmit={onSubmit} onClose={jest.fn()} />);

    const checkboxes = screen.getAllByRole("checkbox");
    fireEvent.click(checkboxes[1]);
    fireEvent.click(screen.getByRole("button", { name: "Confirmar análise" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith([
      expect.objectContaining({ food_name: "Arroz integral", quantity: 150 }),
    ]));
  });

  it("impede confirmação sem itens selecionados", async () => {
    const onSubmit = jest.fn();
    render(<MealAnalysisForm meal={{ meal_date: "2026-01-01" }} initialItems={initialItems} onSubmit={onSubmit} onClose={jest.fn()} />);
    screen.getAllByRole("checkbox").forEach((checkbox) => fireEvent.click(checkbox));
    fireEvent.click(screen.getByRole("button", { name: "Confirmar análise" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Selecione pelo menos um alimento");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("permite adicionar e remover um alimento", () => {
    render(<MealAnalysisForm meal={{ meal_date: "2026-01-01" }} onSubmit={jest.fn()} onClose={jest.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "+ Adicionar alimento" }));
    expect(screen.getByText("Alimento 1")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Remover alimento 1" }));
    expect(screen.queryByText("Alimento 1")).not.toBeInTheDocument();
  });
});
