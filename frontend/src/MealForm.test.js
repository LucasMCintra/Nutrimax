import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import MealForm from "./MealForm";

const submitMeal = async () => {
  fireEvent.change(screen.getByLabelText("Calorias (kcal)"), { target: { value: "650" } });
  fireEvent.click(screen.getByRole("button", { name: "Registrar refeição" }));
};

describe("MealForm", () => {
  it("envia nutrientes e arquivo de imagem válido", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    const file = new File(["image"], "meal.jpg", { type: "image/jpeg" });
    render(<MealForm onSubmit={onSubmit} onClose={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Foto da refeição opcional"), { target: { files: [file] } });
    await submitMeal();

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({
      meal: expect.objectContaining({ calories: 650 }),
      imageFile: file,
    })));
  });

  it("rejeita tipo de arquivo não suportado", () => {
    render(<MealForm onSubmit={jest.fn()} onClose={jest.fn()} />);
    const file = new File(["text"], "meal.txt", { type: "text/plain" });
    fireEvent.change(screen.getByLabelText("Foto da refeição opcional"), { target: { files: [file], value: "" } });
    expect(screen.getByRole("alert")).toHaveTextContent("JPEG, PNG ou WebP");
  });

  it("preenche dados ao editar uma refeição", () => {
    render(<MealForm meal={{ meal_date: "2026-01-02", calories: 700, protein: 40, carbohydrates: 80, fat: 20 }} onSubmit={jest.fn()} onClose={jest.fn()} />);
    expect(screen.getByRole("heading", { name: "Editar refeição" })).toBeInTheDocument();
    expect(screen.getByLabelText("Calorias (kcal)")).toHaveValue(700);
    expect(screen.getByRole("button", { name: "Salvar alterações" })).toBeInTheDocument();
  });
});
