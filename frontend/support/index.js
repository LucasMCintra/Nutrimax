// Cypress custom commands for Nutrimax frontend
// /Users/lucasmoraescintra/Documents/Nutrimax/Nutrimax/frontend/support/index.js

// Custom commands
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login');
  cy.get('#email').type(email);
  cy.get('#password').type(password);
  cy.get('button.primary-button').click();
  cy.url().should('not.include', '/login');
});

Cypress.Commands.add('createProfile', (name, email, password) => {
  cy.visit('/register');
  cy.get('#name').type(name);
  cy.get('#email').type(email);
  cy.get('#password').type(password);
  cy.get('button.primary-button').click();
  cy.url().should('not.include', '/register');
  cy.contains('Bem-vindo de volta.').should('exist');
});

Cypress.Commands.add('createMeal', (mealData) => {
  cy.visit('/meal');
  cy.get('#create-meal-button').click();
  cy.get('#meal-name').type(mealData.name);
  cy.get('#meal-date').type(mealData.date);
  cy.get('button.confirm-meal').click();
  cy.contains('Refeição criada').should('exist');
});

Cypress.Commands.add('uploadPhoto', (filePath) => {
  cy.get('input[type="file"]').attachFile(filePath);
  cy.contains('Upload concluído').should('exist');
});

Cypress.Commands.add('selectFoodItem', (index) => {
  cy.get(`input[type="checkbox"]`).eq(index).check();
});

Cypress.Commands.add('confirmAnalysis', () => {
  cy.get('button.primary-button').click();
  cy.contains('Análise confirmada').should('exist');
});

Cypress.Commands.add('reprocessAnalysis', () => {
  cy.get('button.reprocess-button').click();
  cy.contains('Reprocessando...').should('exist');
  cy.contains('Análise reprocessada').should('exist');
});

Cypress.Commands.add('viewDashboard', () => {
  cy.get('header').contains('Dashboard').click();
  cy.url().should('include', '/dashboard');
});

Cypress.Commands.add('loginAsAdmin', (email, password) => {
  cy.visit('/login');
  cy.get('#email').type(email);
  cy.get('#password').type(password);
  cy.get('button.primary-button').click();
  cy.url().should('not.include', '/login');
});