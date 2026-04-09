# Task: Implementar Auth Service

## Prompt (copiar e colar)

```
Implemente o auth-service para que todos os testes em tests/ passem.

Leia CLAUDE.md deste servico para entender a arquitetura (DDD ou MVC).
Leia os testes em tests/test_auth.py para entender o comportamento esperado.
Use monolito/src/auth/ (DDD) ou monolito-mvc/routes/auth.py (MVC) como referencia.

O servico usa DynamoDB (tabela definida no template.yaml).
Os handlers recebem Lambda events, NAO FastAPI requests.
Testes invocam handlers diretamente — nao precisa de HTTP server.

Para o DDD: copie domain/ e application/ do monolito, ajuste imports, crie infra DynamoDB.
Para o MVC: reescreva as rotas como handlers com queries DynamoDB inline.

Setup: cd microsservicos/XXX-service && pyenv local 3.13.7 && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install pytest
Rodar: pytest tests/ -v
```

## Testes que devem passar (6 + 2 health = 8)

| Teste | Comportamento |
|-------|-------------|
| test_registrar_sucesso | POST body → 201 + {id, nome, email, criado_em} sem senha |
| test_registrar_email_duplicado | Mesmo email 2x → 409 |
| test_login_sucesso | Registrar → login → 200 + {access_token, token_type: bearer} |
| test_login_senha_errada | Senha errada → 401 |
| test_authorizer_token_valido | Login → authorizer → Allow policy |
| test_authorizer_token_invalido | Token lixo → Exception Unauthorized |
| test_health_returns_200 | 200 |
| test_health_body | {status: healthy, service: auth} |

## Handlers a implementar

```
src/handlers/
├── health.py        # JA EXISTE — nao alterar
├── auth.py          # registrar_handler(event, context) + login_handler(event, context)
└── authorizer.py    # handler(event, context) → IAM policy com wildcard ARN
```

## DynamoDB

- Tabela: ver template.yaml (campo TableName)
- PK: `id` (string/UUID)
- Buscar por email: Scan com FilterExpression

## Regras

- Senha: bcrypt hash, minimo 8 chars
- JWT: python-jose, HS256, expira 24h, payload {sub: user_id}
- Authorizer: wildcard ARN no Resource da policy (cache API GW)
- Email case-insensitive (lowercase antes de salvar)
- Resposta de registrar NUNCA contem senha_hash

## Criterio de pronto

- [ ] `pytest tests/ -v` → 8 passed
- [ ] Handlers usam DynamoDB (boto3)
- [ ] Authorizer retorna wildcard ARN
