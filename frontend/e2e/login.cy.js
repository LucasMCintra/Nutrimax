// E2E tests for Nutrimax frontend
// /Users/lucasmoraescintra/Documents/Nutrimax/Nutrimax/frontend/e2e/login.cy.js

describe('Login e Cadastro', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('Deve fazer login com credenciais válidas', () => {
    cy.login('test@example.com', 'password123');
    cy.url().should('not.include', '/login');
    cy.contains('Bem-vindo de volta.').should('exist');
  });

  it('Deve cadastrar um novo usuário', () => {
    cy.register('newuser@example.com', 'newpass123', 'New User');
    cy.url().should('not.include', '/register');
    cy.contains('Bem-vindo de volta.').should('exist');
  });

  it('Deve falhar login com credenciais inválidas', () => {
    cy.login('invalid@example.com', 'wrongpass');
    cy.contains('E-mail ou senha inválidos').should('exist');
  });
});