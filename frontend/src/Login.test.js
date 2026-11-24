import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import Login from "./Login";
import { login, register } from "./api";
import { saveToken } from "./auth";

jest.mock("./api", () => ({
  login: jest.fn(),
  register: jest.fn(),
}));
jest.mock("./auth", () => ({ saveToken: jest.fn() }));

describe("Login", () => {
  beforeEach(() => jest.clearAllMocks());

  it("autentica uma conta existente e salva o token", async () => {
    login.mockResolvedValue({ access_token: "token-de-teste" });
    const onAuthenticated = jest.fn();
    render(<Login onAuthenticated={onAuthenticated} />);

    fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: "user@example.com" } });
    fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "StrongPassword123" } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    await waitFor(() => expect(onAuthenticated).toHaveBeenCalledWith("token-de-teste"));
    expect(saveToken).toHaveBeenCalledWith("token-de-teste");
    expect(login).toHaveBeenCalledWith("user@example.com", "StrongPassword123");
  });

  it("exibe erro retornado pela API", async () => {
    login.mockRejectedValue(new Error("Credenciais inválidas"));
    render(<Login onAuthenticated={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: "user@example.com" } });
    fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "StrongPassword123" } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Credenciais inválidas");
  });

  it("registra uma conta antes de fazer login", async () => {
    register.mockResolvedValue({});
    login.mockResolvedValue({ access_token: "novo-token" });
    render(<Login onAuthenticated={jest.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Ainda não tenho uma conta" }));
    fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: "new@example.com" } });
    fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "StrongPassword123" } });
    fireEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    await waitFor(() => expect(register).toHaveBeenCalledWith("new@example.com", "StrongPassword123"));
    expect(login).toHaveBeenCalledWith("new@example.com", "StrongPassword123");
  });
});
