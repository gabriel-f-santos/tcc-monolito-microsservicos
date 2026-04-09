# Task 0: Migrar Auth para microsservicos-mvc/auth-service

## Objetivo

Migrar a autenticacao do `monolito-mvc/routes/auth.py` para Lambda handlers em `microsservicos-mvc/auth-service/`.

## Referencia (ler antes)

- `monolito-mvc/routes/auth.py` — codigo fonte das rotas (SQLAlchemy + FastAPI)
- `monolito-mvc/models.py` — modelo Usuario (SQLAlchemy)
- `monolito-mvc/app.py` — middleware JWT (como funciona)
- `microsservicos-mvc/CLAUDE.md` — regras de arquitetura (MVC, sem DDD)

## Arquitetura alvo

```
auth-service/
├── src/
│   ├── handlers/
│   │   ├── health.py        # JA EXISTE — nao alterar
│   │   ├── auth.py          # REESCREVER — registrar + login com DynamoDB
│   │   └── authorizer.py    # REESCREVER — validar JWT, retornar IAM policy
│   └── __init__.py
├── tests/
│   ├── test_health.py       # JA EXISTE
│   └── test_auth.py         # CRIAR — 6 testes
├── pyproject.toml            # JA EXISTE
└── requirements.txt          # JA EXISTE
```

**SEM domain/, application/, infrastructure/, container.py.** Tudo inline nos handlers.

## DynamoDB

Tabela: `tcc-usuarios` (PK: `id` string)

Para buscar por email: `Scan` com `FilterExpression` (Attr("email").eq(email))

## O que implementar

### `src/handlers/auth.py`

```python
# registrar_handler(event, context):
# 1. Parse body do event
# 2. Scan DynamoDB para verificar email duplicado → 409
# 3. Hash senha com bcrypt
# 4. PutItem no DynamoDB
# 5. Retornar 201 + usuario (sem senha_hash)

# login_handler(event, context):
# 1. Parse body
# 2. Scan DynamoDB por email → 401 se nao encontrar
# 3. Verificar senha com bcrypt → 401 se errada
# 4. Gerar JWT com python-jose (sub=user_id, exp=24h)
# 5. Retornar 200 + { access_token, token_type: "bearer" }
```

### `src/handlers/authorizer.py`

```python
# handler(event, context):
# 1. Extrair token do event["authorizationToken"] (remover "Bearer ")
# 2. Decodificar JWT com python-jose
# 3. Se valido: retornar Allow policy com WILDCARD ARN
# 4. Se invalido: raise Exception("Unauthorized")
#
# IMPORTANTE: usar wildcard ARN para que o cache do API Gateway funcione:
# arn:aws:execute-api:REGION:ACCOUNT:API_ID/STAGE/*
```

### `tests/test_auth.py` — 6 testes

```python
# Usar in-memory dict como fake DynamoDB (nao precisa de boto3 real)

test_registrar_sucesso
  # Invocar registrar_handler com event mockado
  # Body: {"nome": "Admin", "email": "admin@test.com", "senha": "senha12345"}
  # Assert: statusCode 201, response tem id, nome, email, criado_em, sem senha

test_registrar_email_duplicado
  # Registrar duas vezes com mesmo email
  # Assert: segunda retorna statusCode 409

test_login_sucesso
  # Registrar + invocar login_handler
  # Body: {"email": "admin@test.com", "senha": "senha12345"}
  # Assert: statusCode 200, response tem access_token, token_type="bearer"

test_login_senha_errada
  # Registrar + login com senha errada
  # Assert: statusCode 401

test_authorizer_token_valido
  # Login para obter token → invocar authorizer handler
  # Event: {"authorizationToken": "Bearer TOKEN", "methodArn": "arn:..."}
  # Assert: retorna policyDocument com Effect="Allow"

test_authorizer_token_invalido
  # Invocar authorizer com token "lixo"
  # Assert: raise Exception("Unauthorized")
```

## Criterio de pronto

- [ ] 6 testes de auth passam
- [ ] 2 testes de health continuam passando
- [ ] Handlers usam DynamoDB (boto3) direto — sem repository, sem interface
- [ ] bcrypt e jose importados diretamente nos handlers
- [ ] Authorizer retorna wildcard ARN
- [ ] Rodar: `cd microsservicos-mvc/auth-service && pytest -v`
