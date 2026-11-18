#### O Problema:

A Nutrimax foi pensado para que o usuario consiga estar mantendo uma dieta controlada e saiba o seu progresso e pontos de observação, é indicado para todos aqueles que querem manter uma vida mais saudável e controlada.
Será um sistema de controle de refeiçoes com IA integrada. 
Área de exercicios ou atividades fisicas não será integrado no sistema.

#### **Requisitos Funcionais:**

1.O cliente irá preencher um formulário com o seu perfil e objetivo e o sistema indicará a dieta ideal para o perfil do usuario.

2.O cliente vai registrar as refeiçoes da sua dieta e o sistema deve armazenar os nutrientes presentes nessa refeiçao.

3.O sistema deve ter um dashboard com o progresso do usuario até o objetivo dele.

4.O sistema tem que ter um dashboard para registrar as metas diárias, semanais e mensais.

#### **Requisitos Não Funcionais:**

O sistema deve ter uma margem de erro muito baixa de quantidade de nutrientes.
O sistema deve ser intuitivo e com alta usabilidade.
O sistema deve ser seguro com dados sensíveis, para proteção do cliente.

#### MVP:

O sistema deverá ter as seguintes funcionalidades:
Dashboard da meta do dia, semana e mês.
Um analista de Refeiçoes que vai analisar a foto da refeiçao identificar cada alimento e quantidade e estipular a quantidade de nutrientes de cada alimentos.
Deve ter uma área de objetivos onde será analisado o perfil do usuario e indicado a melhor dieta para ele alcaçar esse objetivo.

#### Arquitetura e Stack:

O sistema deve ter um banco de dados para armazenar as refeiçoes, deve ter uma API para manter dashboards atualizados.

#### **Modelo de dados básico:**

Cliente(id, nome, peso, altura, idade) 
objetivo(id, perda de peso, ganho de massa muscular, manter peso, perca de gordura.)
dieta(id) 
refeições(id, data-da-refeiçao, imagem)

cliente-refeiçao: 1:N
cliente-objetivo:1:1
cliente-dieta: 1:1

Stack:
front-end: React
Back-end: Python e FastApi
DataBase: PostgreSQL
