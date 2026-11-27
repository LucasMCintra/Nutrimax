// E2E tests for Nutrimax frontend complete flow
// /frontend/meal-analysis-flow.cy.js

describe('Nutrimax Frontend Complete Flow', () => {
  beforeEach(() => {
    cy.login('testuser@example.com', 'password123');
    cy.viewport(1440, 900); // Desktop view
  });

  it('Deve criar perfil, refeição com foto e analisar nutrientes', () => {
    // 1. Acessar perfil
    cy.visit('/perfil');
    cy.contains('Seu perfil').should('exist');

    // 2. Criar refeição
    cy.visit('/meal');
    cy.get('#create-meal-button').click();
    cy.get('#meal-name').type('Almoço Saudável');
    cy.get('#meal-date').type('2023-10-05');
    cy.uploadPhoto('cypress/fixtures/meal.jpg');
    cy.get('button.confirm-meal').click();
    cy.contains('Refeição criada com sucesso').should('exist');

    // 3. Analisar refeição
    cy.visit('/analysis');
    cy.get('button.analyze-button').click();
    cy.contains('Análise em andamento').should('exist');
    cy.contains('Análise concluída').should('exist');
    cy.contains('Alimentos identificados').should('exist');

    // 4. Editar candidatos
    cy.get('input[placeholder="Alimento"]').type('Quinoa');
    cy.contains('Quinoa').should('exist');
    cy.get('button.edit-item').click();
    cy.get('#food-name').type('Quinoa integral');
    cy.contains('Atualizado com sucesso').should('exist');

    // 5. Selecionar itens e confirmar
    cy.get('input[type="checkbox"]').first().check();
    cy.get('button.primary-button').click();

    // 6. Verificar atualização no dashboard
    cy.visit('/dashboard');
    cy.contains('+1 refeição').should('exist');
    cy.contains('Almoço Saudável').should('exist');
  });

  it('Deve reprocessar análise com falha', () => {
    cy.visit('/analysis');
    cy.get('#reprocess-button').click();
    cy.contains('Reprocessando...').should('exist');
    cy.contains('Análise reprocessada').should('exist');
  });

  it('Deve exibir layout responsivo em 320px e 390px', () => {
    // 320px view
    cy.viewport(320, 600);
    cy.get('.onboarding-card').should('be.visible');
    cy.get('button.primary-button').should('be.visible');

    // 390px view
    cy.viewport(390, 600);
    cy.get('.analysis-items').should('be.visible');
    cy.get('fieldset').should('have.length', 1);
  });
});