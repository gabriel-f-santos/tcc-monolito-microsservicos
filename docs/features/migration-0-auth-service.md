# Migracao: Auth Service (Monolito → Microsservico)

## Contexto

**IMPORTANTE:** Cada microsservico e independente com seu proprio `pyproject.toml`, `tests/` e venv. Rode testes de DENTRO do diretorio do servico: `cd microsservicos/xxx-service && pytest`. Imports usam `src.` (nao `xxx-service.src.`).

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias
- `docs/architecture.md` — padrao DDD, camadas, container DI
- `microsservicos/CLAUDE.md` — regras dos microsservicos
- `monolito/src/auth/` — codigo fonte do monolito (REFERENCIA, nao copiar cegamente)

## Objetivo

Migrar o Bounded Context de Autenticacao do monolito para o `auth-service/` dos microsservicos.
- **Domain e Application devem ser IDENTICOS** ao monolito (copiar)
- **Infrastructure muda:** SQLAlchemy → DynamoDB (boto3)
- **Presentation muda:** FastAPI routes → Lambda handlers puros
- **Container muda:** providers apontam para implementacoes DynamoDB

## O que copiar do monolito (SEM alteracao)

```
monolito/src/auth/domain/          → auth-service/src/domain/
  entities/usuario.py              COPIAR INTEIRO
  exceptions/auth.py               COPIAR INTEIRO
  repositories/usuario_repository.py  COPIAR INTEIRO
  services/password_hasher.py      COPIAR INTEIRO
  services/token_service.py        COPIAR INTEIRO

monolito/src/auth/application/     → auth-service/src/application/
  use_cases/registrar.py           COPIAR INTEIRO
  use_cases/login.py               COPIAR INTEIRO
```

**Estes arquivos NAO devem ser modificados.** Se precisar alterar, e sinal de que a arquitetura falhou.

## O que criar novo (implementacao DynamoDB)

```
auth-service/src/
├── infrastructure/
│   ├── repositories/
│   │   └── dynamodb_usuario_repository.py    # NOVO — implementa UsuarioRepository com boto3
│   └── services/
│       ├── bcrypt_password_hasher.py         # COPIAR do monolito (mesma lib)
│       └── jose_token_service.py             # COPIAR do monolito (mesma lib)
├── container.py                              # NOVO — DeclarativeContainer com providers DynamoDB
└── presentation/
    └── handlers/
        ├── auth.py                           # REESCREVER — Lambda handlers (registrar, login)
        └── authorizer.py                     # REESCREVER — Lambda Authorizer (validar JWT)
```

## DynamoDB — Tabela de Usuarios

```
Tabela: tcc-usuarios
Partition Key: id (S)

Para buscar por email: DynamoDB Scan com FilterExpression
(aceitavel para escala pequena; em producao usaria GSI)
```

## Lambda Handlers

### POST /api/v1/auth/registrar (publico)

```python
def registrar_handler(event, context):
    body = json.loads(event["body"])
    use_case = container.registrar()
    usuario = use_case.execute(RegistrarDTO(**body))
    return {"statusCode": 201, "body": json.dumps(usuario_to_dict(usuario))}
```

### POST /api/v1/auth/login (publico)

```python
def login_handler(event, context):
    body = json.loads(event["body"])
    use_case = container.login()
    result = use_case.execute(LoginDTO(**body))
    return {"statusCode": 200, "body": json.dumps({"access_token": result.access_token, "token_type": result.token_type})}
```

### Lambda Authorizer

```python
def handler(event, context):
    token = event["authorizationToken"].replace("Bearer ", "")
    token_service = container.token_service()
    payload = token_service.decode_token(token)  # raises TokenInvalido
    return generate_allow_policy(payload["user_id"], event["methodArn"])
```

## Testes esperados (6 — mesmos do monolito)

```
test_registrar_sucesso
  Invocar registrar_handler com body valido → statusCode 201

test_registrar_email_duplicado
  Invocar duas vezes com mesmo email → segunda retorna 409

test_login_sucesso
  Registrar → invocar login_handler → statusCode 200, access_token presente

test_login_senha_errada
  Registrar → login com senha errada → statusCode 401

test_authorizer_token_valido
  Login → invocar authorizer com Bearer token → retorna Allow policy

test_authorizer_token_invalido
  Invocar authorizer com token "lixo" → raise Exception("Unauthorized")
```

## Metricas de migracao a coletar

Apos implementar, registrar:

```
Arquivos copiados sem alteracao (domain + application): ___
Arquivos novos (infrastructure + presentation): ___
Arquivos reescritos: ___
Linhas de domain/ inalteradas: ___
Linhas de infrastructure/ novas: ___
Testes que passam: ___/6
```

## Criterio de pronto

- [ ] 6 testes passam
- [ ] domain/ e application/ sao IDENTICOS ao monolito
- [ ] infrastructure/ usa boto3/DynamoDB (nao SQLAlchemy)
- [ ] presentation/ usa Lambda handlers (nao FastAPI)
- [ ] authorizer.py valida JWT e retorna IAM policy
- [ ] Container usa dependency-injector com providers DynamoDB
