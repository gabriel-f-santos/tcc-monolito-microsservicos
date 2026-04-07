# Microsservicos Serverless — Produtos e Estoque

## Arquitetura

Dois servicos independentes seguindo **DDD** e **Clean Architecture**, deployados como AWS Lambda.

### Servicos

- `catalogo-service/` — Bounded Context de Catalogo de Produtos
- `estoque-service/` — Bounded Context de Controle de Estoque

### Camadas (cada servico)

- `src/domain/` — Agregados, Entidades, Value Objects, interfaces de Repository, excecoes. **ZERO imports de framework**.
- `src/application/` — Casos de uso. Identicos aos do monolito.
- `src/infrastructure/` — Implementacoes de repositorio (DynamoDB/boto3), config.
- `src/presentation/handlers/` — Lambda handlers puros (sem Mangum, sem FastAPI).

### Regras

- Lambda handlers delegam imediatamente ao caso de uso (zero logica de negocio no handler)
- Dominio nunca importa de infrastructure ou presentation
- Casos de uso sao identicos aos do monolito (mesma camada de aplicacao)
- Repository Pattern: mesma interface do monolito, implementacao com boto3/DynamoDB
- Comunicacao entre BCs: eventos via SNS/SQS apenas (zero chamadas HTTP sincronas)
- Estoque consome eventos do Catalogo e mantem projecao local

## Stack

- Python 3.13 / AWS Lambda / API Gateway / DynamoDB / SNS / SQS
- Infraestrutura: AWS SAM (template.yaml)
- Testes: pytest
- Metricas: radon (CC/MI)

## Especificacao

O dominio, contratos de API e eventos estao em `docs/spec.md`. Siga rigorosamente.

## Estrutura Independente

Cada microsservico e **independente** com seu proprio:
- `pyproject.toml` — dependencias
- `tests/` — testes
- `.venv/` — virtual environment (nao commitado)

**NUNCA** usar pyproject.toml ou venv compartilhado entre servicos.

## Comandos

```bash
# Por servico (rodar de DENTRO do diretorio)
cd microsservicos/auth-service
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
pytest -v                         # Testes
radon cc src/ -s -a               # CC

# SAM (rodar da raiz microsservicos/)
cd microsservicos
sam build                         # Build
sam deploy --no-confirm-changeset # Deploy
```

## Medicao de Tempo (para o TCC)

Ao implementar uma feature, registre no final da resposta:
- Tempo estimado de raciocinio/execucao
- Numero de iteracoes ate testes passarem
- `git diff --stat` da feature
# Microsservicos - Produtos e Estoque
