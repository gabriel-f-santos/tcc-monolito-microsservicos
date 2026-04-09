# estoque-service — Controle de Estoque

## Arquitetura: DDD

```
src/
├── handlers/          # Lambda entry points
├── domain/            # Entidades, VOs, interfaces repo, services
├── application/       # Use cases, DTOs
├── infrastructure/    # DynamoDB repos, services concretos
├── shared/            # Base classes (Entity, exceptions)
└── container.py       # dependency-injector DeclarativeContainer
```

Regras DDD:
- domain/ e application/ sao Python puro (ZERO imports de libs externas)
- Leia docs/features/RULES.md para regras completas

## Setup

```bash
cd microsservicos/estoque-service
pyenv local 3.13.7                          # ou versao disponivel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest                           # dev
```

## Testes

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Deploy

```bash
bash deploy.sh
# Ou manualmente:
sam build --use-container
sam deploy --no-confirm-changeset
```

## Recursos AWS (template.yaml)

### DynamoDB
- `tcc-ddd-estoque-itens` (PK: id)
- `tcc-ddd-estoque-movimentacoes` (PK: id)
- SQS: `tcc-ddd-estoque-eventos`

### Cross-Stack References
- `tcc-ddd-auth-authorizer-arn` — Lambda Authorizer
- `tcc-ddd-catalogo-eventos-topic-arn` — Topic SNS para subscription SQS
Nenhum

## Ordem de Deploy

1. auth-service (ou auth-service-mvc) — exporta AuthorizerFunctionArn
2. catalogo-service (ou catalogo-service-mvc) — exporta EventosTopicArn
3. estoque-service (ou estoque-service-mvc) — importa ambos
