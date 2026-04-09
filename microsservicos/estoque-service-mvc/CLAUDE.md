# estoque-service-mvc — Controle de Estoque

## Arquitetura: MVC

```
src/
├── handlers/          # Lambda handlers com queries DynamoDB inline
└── __init__.py
```

Regras MVC:
- Tudo inline nos handlers (sem camadas, sem interfaces)
- boto3/bcrypt/jose importados diretamente

## Setup

```bash
cd microsservicos/estoque-service-mvc
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
- `tcc-mvc-estoque-itens` (PK: id)
- `tcc-mvc-estoque-movimentacoes` (PK: id)
- SQS: `tcc-mvc-estoque-eventos`

### Cross-Stack References
- `tcc-mvc-auth-authorizer-arn` — Lambda Authorizer
- `tcc-mvc-catalogo-eventos-topic-arn` — Topic SNS
Nenhum

## Ordem de Deploy

1. auth-service (ou auth-service-mvc) — exporta AuthorizerFunctionArn
2. catalogo-service (ou catalogo-service-mvc) — exporta EventosTopicArn
3. estoque-service (ou estoque-service-mvc) — importa ambos
