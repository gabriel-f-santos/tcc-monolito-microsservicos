# Prompt para Migracao do Monolito MVC para Microsservicos

## Instrucao

Migre o monolito MVC (`monolito-mvc/`) para 3 microsservicos Lambda em `microsservicos-mvc/`.

O monolito MVC e um FastAPI com rotas diretas, queries SQL inline, sem DDD.
Os microsservicos devem ter o MESMO comportamento mas usando DynamoDB e Lambda handlers.

## Referencia

- `monolito-mvc/routes/auth.py` → `microsservicos-mvc/auth-service/src/handlers/auth.py`
- `monolito-mvc/routes/categorias.py` + `monolito-mvc/routes/produtos.py` → `microsservicos-mvc/catalogo-service/src/handlers/catalogo.py`
- `monolito-mvc/routes/estoque.py` → `microsservicos-mvc/estoque-service/src/handlers/estoque.py`

## O que muda

| Monolito MVC | Microsservico MVC |
|-------------|-------------------|
| SQLAlchemy + PostgreSQL | boto3 + DynamoDB |
| FastAPI routes + Depends(get_session) | Lambda handlers (event, context) |
| HTTPException | JSON response com statusCode |
| Middleware JWT no FastAPI | Lambda Authorizer |
| Criar ItemEstoque in-process | Publicar evento SNS → SQS consumer |

## Tabelas DynamoDB (ja existem no template.yaml)

- tcc-usuarios (auth)
- tcc-categorias (catalogo)
- tcc-produtos (catalogo)
- tcc-itens-estoque (estoque)
- tcc-movimentacoes (estoque)

## O que implementar por servico

### auth-service
- `src/handlers/auth.py` — registrar (bcrypt, DynamoDB) + login (JWT)
- `src/handlers/authorizer.py` — validar JWT, retornar IAM policy com wildcard ARN
- Testes: 6

### catalogo-service
- `src/handlers/catalogo.py` — CRUD categorias + CRUD produtos + publicar SNS
- Testes: 14

### estoque-service
- `src/handlers/estoque.py` — entrada, saida, consultas
- `src/handlers/event_consumer.py` — consumir SQS (ProdutoCriado)
- Testes: 14

## Criterio de pronto

- [ ] auth-service: 6+ testes passam
- [ ] catalogo-service: 14+ testes passam
- [ ] estoque-service: 14+ testes passam
- [ ] Mesmos endpoints e respostas do monolito MVC
