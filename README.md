# Nutrimax

Sistema de controle de refeições com IA integrada para ajudar usuários a manter uma dieta saudável e monitorar seu progresso.

## Características

- **Dashboard de progresso**: Acompanhe metas diárias, semanais e mensais
- **Analisador de refeições**: Identifique alimentos e quantidades a partir de fotos
- **Recomendação de dieta**: Gere planos alimentares personalizados com base no perfil e objetivos do usuário
- **Sistema seguro e intuitivo**: Proteja dados sensíveis dos usuários enquanto mantém alta usabilidade

## Stack Tecnológico

- **Frontend**: React (TypeScript)
- **Backend**: FastAPI (Python)
- **Banco de Dados**: PostgreSQL
- **Docker**: Para ambientes de desenvolvimento e produção reprodutíveis

## Estrutura do Projeto

```bash
frontend/           # Aplicação React
├── src/             # Código fonte React
├── public/          # Arquivos estáticos

backend/            # Servidor FastAPI
├── app/             # Aplicação FastAPI principal
├── docker/          # Dockerfiles e docker-compose.yml
```

Para mais detalhes, consulte a `docs/` pasta.

## Getting Started

### Desenvolvimento Local

```bash
# Iniciar bancos de dados e serviços auxiliares
docker-compose up -d

# Clonar e instalar dependencies do backend
./scripts/setup.sh

# Instalar dependencies do frontend
cd frontend && npm install

# Executar migrations do banco de dados
# (depende do modelo do seu ORM favorito)
```

### Executando a Aplicação

```bash
# Backend
python -m pytest  # Run tests
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm start
```

### Testes

```bash
# Tests do backend (usando pytest)
pytest backend/app/tests/

# Tests de integração/cobertura
pytest -v

# Frontend
cd frontend
npm test
```

## Contribuição

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Execute os testes
4. Commite e envie suas mudanças
5. Crie um Pull Request

## Documentação

- [Especificação do Projeto](docs/spec.md)
- [Documentação da API](docs/api.md)
- [Diagramas de Arquitetura](docs/architecture.md)

## Licença

Este projeto está sob a licença MIT.