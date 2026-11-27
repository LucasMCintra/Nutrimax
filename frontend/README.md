## Instruções para executar os testes E2E

Para validar o fluxo completo de análise nutricional, siga estes passos:

1. Instale o Cypress (se ainda não estiver instalado):
```bash
cd frontend
npm install cypress --save-dev
```

2. Execute os testes:
```bash
npm run test:e2e
```

3. Para visualizar os testes interativamente:
```bash
npm run test:e2e:open
```

Os testes cobrem:
- Login e cadastro de usuário
- Criação de perfil
- Upload de foto de refeição
- Análise nutricional com validação de itens
- Edição de candidatos alimentares
- Seleção e confirmação de análise
- Atualização do dashboard
- Reprocessamento de análise
- Layout responsivo em 320px e 390px

Os testes utilizam fixtures localizadas em `/frontend/cypress/fixtures/meal.jpg` para simular o fluxo completo.