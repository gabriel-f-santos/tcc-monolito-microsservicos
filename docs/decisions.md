# Decisões Arquiteturais

## 1. Banco de Dados: PostgreSQL (Monolito) → DynamoDB (Microsserviços)

- **Monolito** usa PostgreSQL (relacional, familiar, SQL puro)
- **Microsserviços** migram para DynamoDB (serverless puro, elimina NAT Gateway)
- **Justificativa acadêmica:** demonstra na prática o **Repository Pattern** do DDD
  - A interface do repositório (domínio) permanece idêntica
  - Apenas a implementação de infraestrutura muda (SQLAlchemy → boto3)
  - Prova que a separação de camadas funciona: trocar banco não altera regras de negócio
- **Benefício extra:** elimina o problema de custo do NAT Gateway que o professor criticou

## 2. Sem Mangum: Lambda Handler Puro nos Microsserviços

- **Monolito:** FastAPI routes → Use Cases → Repositories
- **Microsserviços:** Lambda handlers puros → Use Cases → Repositories
- **Sem Mangum** — não queremos um adapter que esconda a troca de camada
- **Justificativa acadêmica:** prova que a **camada de aplicação (Use Cases) é agnóstica ao transporte**
  - Mesmos Use Cases funcionam chamados por FastAPI ou por Lambda handler
  - A apresentação é a única camada que muda entre monolito e microsserviços
  - Demonstra Clean Architecture de forma mais explícita do que usando Mangum
- **Impacto no artigo:** seção dedicada mostrando o antes/depois da camada de apresentação sem alterar domínio/aplicação

## 3. Observabilidade: Grafana Cloud (Free Tier)

- Grafana Cloud free tier para dashboards e visualização
- OpenTelemetry para instrumentação
- AWS X-Ray como complemento (Tracing: Active no SAM é uma linha)
- Gera screenshots de alta qualidade para o artigo

## 4. Chaos Engineering: Opcional (Final)

- Prioridade baixa — só implementar se sobrar tempo após os blocos principais
- Se feito: derrubar Produto-service e verificar que Estoque continua via eventos
- Se não feito: discutir teoricamente no artigo como seria implementado

## 5. Estratégia de Desenvolvimento: Walking Skeleton → Features Incrementais

- Toda a infraestrutura (SAM, CI/CD, Grafana, banco) sobe ANTES de medir tempo
- O skeleton tem apenas `/health`
- Cada feature é adicionada uma por vez, medindo tempo com Claude Code e Codex
- O que se mede é estritamente o esforço de codificar a feature, sem ruído de infra
