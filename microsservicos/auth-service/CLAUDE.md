# auth-service — Autenticacao JWT

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
cd microsservicos/auth-service
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
- `tcc-ddd-auth-usuarios` (PK: id)

### Cross-Stack References
Nenhum (primeiro a ser deployado)
- `tcc-ddd-auth-authorizer-arn` — ARN do Lambda Authorizer (usado por catalogo e estoque)

## Ordem de Deploy

1. auth-service (ou auth-service-mvc) — exporta AuthorizerFunctionArn
2. catalogo-service (ou catalogo-service-mvc) — exporta EventosTopicArn
3. estoque-service (ou estoque-service-mvc) — importa ambos
