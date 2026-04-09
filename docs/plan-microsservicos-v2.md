# Plano: 6 Microsservicos Independentes

## Arquitetura

```
microsservicos/
├── auth-service/           # DDD — migrado do monolito/src/auth/
├── catalogo-service/       # DDD — migrado do monolito/src/catalogo/
├── estoque-service/        # DDD — migrado do monolito/src/estoque/ (modelo ja criado)
├── auth-service-mvc/       # MVC — migrado do monolito-mvc/routes/auth.py
├── catalogo-service-mvc/   # MVC — migrado do monolito-mvc/routes/categorias+produtos
└── estoque-service-mvc/    # MVC — migrado do monolito-mvc/routes/estoque
```

## Cada servico tem

```
xxx-service/
├── src/
│   ├── handlers/           # Lambda handlers
│   │   ├── health.py
│   │   └── xxx.py
│   └── __init__.py
├── tests/                  # Testes (mesmos comportamentos DDD vs MVC)
├── template.yaml           # SAM stack PROPRIO (API GW, DynamoDB, IAM)
├── samconfig.toml          # Config de deploy
├── deploy.sh               # Script de deploy
├── requirements.txt        # Deps
├── CLAUDE.md               # Regras + como configurar
└── .gitignore
```

## Recursos por servico

### auth-service / auth-service-mvc
- API Gateway proprio
- Lambda: health, registrar, login, authorizer
- DynamoDB: {prefix}-usuarios
- Exporta: AuthorizerFunctionArn (outros servicos importam)

### catalogo-service / catalogo-service-mvc
- API Gateway proprio
- Lambda: health, catalogo (CRUD categorias + produtos)
- DynamoDB: {prefix}-categorias, {prefix}-produtos
- SNS: {prefix}-eventos-dominio (publica ProdutoCriado)
- Importa: AuthorizerFunctionArn do auth-service

### estoque-service / estoque-service-mvc
- API Gateway proprio
- Lambda: health, estoque (entrada, saida, consultas), event_consumer
- DynamoDB: {prefix}-itens-estoque, {prefix}-movimentacoes
- SQS: {prefix}-estoque-eventos (consome do SNS do catalogo)
- Importa: AuthorizerFunctionArn do auth-service

## Prefixos DynamoDB (evitar colisao)

| Servico | Prefixo tabelas |
|---------|----------------|
| auth-service | tcc-ddd-auth |
| catalogo-service | tcc-ddd-catalogo |
| estoque-service | tcc-ddd-estoque |
| auth-service-mvc | tcc-mvc-auth |
| catalogo-service-mvc | tcc-mvc-catalogo |
| estoque-service-mvc | tcc-mvc-estoque |

## Cross-stack references

```yaml
# auth-service/template.yaml — Exporta
Outputs:
  AuthorizerFunctionArn:
    Value: !GetAtt AuthorizerFunction.Arn
    Export:
      Name: tcc-ddd-auth-authorizer-arn  # ou tcc-mvc-auth-authorizer-arn

# catalogo-service/template.yaml — Importa
EstoqueApi:
  Auth:
    Authorizers:
      JwtAuthorizer:
        FunctionArn: !ImportValue tcc-ddd-auth-authorizer-arn

# catalogo-service/template.yaml — Exporta SNS
Outputs:
  EventosTopicArn:
    Value: !Ref EventosDominioTopic
    Export:
      Name: tcc-ddd-catalogo-eventos-topic-arn

# estoque-service/template.yaml — Importa SNS para subscription
EstoqueEventosSubscription:
  Properties:
    TopicArn: !ImportValue tcc-ddd-catalogo-eventos-topic-arn
```

## Ordem de deploy

1. auth-service (exporta authorizer ARN)
2. catalogo-service (importa authorizer, exporta SNS topic)
3. estoque-service (importa authorizer + SNS topic)

Mesma ordem para MVC.

## CLAUDE.md padrao (dentro de cada servico)

Conteudo:
- Arquitetura do servico (DDD ou MVC)
- Como fazer setup (.venv, pyenv local 3.13.7, pip install)
- Como rodar testes
- Como fazer deploy (deploy.sh)
- Cross-stack: o que importa, o que exporta
- Tabelas DynamoDB que usa
- Filas SNS/SQS (se aplicavel)

## Testes (identicos entre DDD e MVC)

Mesmos testes, mesmos payloads, mesmos asserts:
- auth: 6 testes
- catalogo: 14 testes
- estoque: 14 testes (11 estoque + 3 eventos)

## Tasks de migracao

Uma task por servico (6 total), cada uma com:
- Qual monolito referenciar
- O que copiar (DDD) ou reescrever (MVC)
- Testes que devem passar
- Criterio de pronto
- Diagrama de arquitetura do servico

## Proximos passos

1. Criar estrutura base dos 6 servicos (skeleton com health)
2. CLAUDE.md em cada um
3. template.yaml com recursos proprios
4. samconfig.toml + deploy.sh
5. Testes skeleton
6. Tasks de migracao
7. Deploy auth-services primeiro (exportam authorizer)
8. Deploy catalogo e estoque
9. Validar health checks em todos
10. Medir migracao com IA
