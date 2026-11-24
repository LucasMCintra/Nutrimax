import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import DietForm from "./DietForm";

describe("DietForm", () => {
  it("cria uma dieta com a descrição informada", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<DietForm onSubmit={onSubmit} onClose={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Descrição da dieta"), { target: { value: "Refeições equilibradas com vegetais" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar dieta" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith("Refeições equilibradas com vegetais"));
  });

  it("impede salvar uma dieta vazia", async () => {
    const onSubmit = jest.fn();
    render(<DietForm onSubmit={onSubmit} onClose={jest.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Salvar dieta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Descreva sua dieta");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("preenche e salva uma dieta existente", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<DietForm diet={{ description: "Plano anterior" }} onSubmit={onSubmit} onClose={jest.fn()} />);

    expect(screen.getByRole("heading", { name: "Editar dieta" })).toBeInTheDocument();
    const field = screen.getByLabelText("Descrição da dieta");
    expect(field).toHaveValue("Plano anterior");
    fireEvent.change(field, { target: { value: "Plano atualizado" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar dieta" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith("Plano atualizado"));
  });
});
