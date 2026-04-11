# Task: Implementar Auth Service

## Prompt (copiar e colar)

```
Implemente o auth-service para que todos os testes em tests/ passem.

ANTES DE CODAR:
1. Leia microsservicos/tasks/INTEGRATION-CONTRACT.md — regras obrigatorias.
2. Leia CLAUDE.md deste servico para entender a arquitetura (DDD ou MVC).
3. Leia template.yaml e liste TODAS as entradas em Environment.Variables.
   O codigo DEVE ler EXATAMENTE esses nomes (nao inventar DYNAMODB_TABLE etc).
4. Leia os testes em tests/ para entender o comportamento esperado.
5. Use monolito/src/auth/ (DDD) ou monolito-mvc/routes/auth.py (MVC) como referencia.

O servico usa DynamoDB. Os handlers recebem Lambda events (nao FastAPI requests).
Testes invocam handlers diretamente, mas rodam sob mock_aws() via conftest.py
(moto). NAO use repositorios InMemory como fallback selecionado por env var —
em producao, sempre DynamoDB; em teste, moto intercepta.

Para o DDD: copie domain/ e application/ do monolito SEM MODIFICACAO (so ajustar
imports), e implemente uma camada infrastructure com DynamoDBUsuarioRepository
usando boto3. Container instancia SEMPRE a versao DynamoDB.

Para o MVC: reescreva como handlers com queries DynamoDB inline. Sem branch
condicional — boto3 direto. Testes usam moto automaticamente via conftest.py.

Setup:
  cd microsservicos/XXX-service
  pyenv local 3.13.7 && python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt -r requirements-dev.txt
Rodar:
  pytest tests/ -v
```

## Bugs da rodada anterior — NAO REPETIR

A rodada anterior gerou codigo que passou nos testes locais mas falhou
em producao porque:

1. **Desalinhamento de env var**: o container lia `DYNAMODB_TABLE` mas
   `template.yaml` envia `USUARIOS_TABLE`. Resultado: Lambda caia em
   InMemoryRepository a cada cold start e login sempre retornava 401.

   **Evitar**: use EXATAMENTE os nomes do template. O teste-guardiao
   `tests/test_integration_contract.py::test_env_vars_from_template_are_read_by_src_code`
   falha se houver divergencia.

2. **Fallback condicional InMemory**: padrao `if os.environ.get(TABLE):
   return DynamoDB() else: return InMemory()`. Tests passavam sem setar a
   env var → caiam no InMemory.

   **Evitar**: em producao, sempre DynamoDB. O conftest.py usa moto e seta
   as env vars automaticamente. O teste-guardiao
   `test_no_inmemory_fallback_in_production_code` falha se houver if-else.

## Testes que devem passar (6 auth + 2 health + 3 contract = 11)

| Teste | Comportamento |
|-------|-------------|
| test_registrar_sucesso | POST body → 201 + {id, nome, email, criado_em} sem senha |
| test_registrar_email_duplicado | Mesmo email 2x → 409 |
| test_login_sucesso | Registrar → login → 200 + {access_token, token_type: bearer} |
| test_login_senha_errada | Senha errada → 401 |
| test_authorizer_token_valido | Login → authorizer → Allow policy |
| test_authorizer_token_invalido | Token lixo → Exception Unauthorized |
| test_health_returns_200 | GET /health → 200 |
| test_health_body | {status: healthy, service: auth} |
| test_env_vars_from_template_are_read_by_src_code | env vars alinhadas |
| test_no_inmemory_fallback_in_production_code | sem branch InMemory |
| test_event_consumers_do_not_only_log | n/a (sem event consumer) |

## Handlers a implementar

```
src/handlers/
├── health.py        # JA EXISTE — nao alterar
├── auth.py          # registrar_handler(event, context) + login_handler(event, context)
└── authorizer.py    # handler(event, context) → IAM policy com wildcard ARN
```

## DynamoDB (ver template.yaml)

- Tabela: `UsuariosTable` com PK `id` (string/UUID)
- Env var: `USUARIOS_TABLE`
- Buscar por email: Scan com FilterExpression
- Outra env var: `JWT_SECRET` (com default em Parameters)

## Regras de negocio

- Senha: bcrypt hash, minimo 8 chars
- JWT: python-jose, HS256, expira 24h, payload `{sub: user_id}`
- Email case-insensitive (lowercase antes de salvar)
- Resposta de registrar NUNCA contem senha_hash nem senha

## Authorizer — contrato AWS especifico

API Gateway espera que o Lambda Authorizer **lance uma Exception** quando
o token e invalido, NAO retorne `{"statusCode": 401}`. Retornar um JSON
com statusCode causa 500 no API Gateway, nao 401.

```python
def handler(event, context):
    token = event.get("authorizationToken", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        raise Exception("Unauthorized")  # EXACT string — API GW pattern-matches

    return {
        "principalId": payload["sub"],
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "execute-api:Invoke",
                "Resource": "arn:aws:execute-api:*:*:*/*/*/*",  # WILDCARD — cache
            }],
        },
    }
```

- Resource DEVE ser wildcard (`*/*/*/*`) para que o API Gateway faca cache
  da policy (300s). Sem wildcard, cada rota dispara nova invocacao do authorizer.
- A string da Exception tem que conter "Unauthorized" (case-sensitive).

## Checklist de "done"

Marque como feito APENAS se TODOS os items passarem:

- [ ] Venv fresco: `rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt` → sem erros
- [ ] Import sanity: `python -c "from src.handlers.auth import registrar_handler, login_handler; from src.handlers.authorizer import handler"` → sem ModuleNotFoundError (captura dependencias que voce usou mas esqueceu de adicionar em requirements.txt, como `dependency-injector`)
- [ ] `pytest tests/ -v` → **12 passed** (8 comportamento + 4 contract)
- [ ] `test_integration_contract.py` inteiramente verde — sem pulos
- [ ] Nenhum `if os.environ.get(...)` ou `if os.getenv(...)` selecionando InMemory em src/
- [ ] Nenhum `try/except KeyError: InMemory` em src/
- [ ] `grep -rE "os\.(environ|getenv)" src/` lista SOMENTE env vars declaradas em template.yaml
- [ ] Repositorio DynamoDB e instanciado SEM condicional em src/container.py (DDD) ou diretamente em src/handlers/auth.py (MVC)
- [ ] Authorizer LANCA `Exception("Unauthorized")` — nao retorna JSON com 401
- [ ] Nenhuma chamada AWS em nivel de modulo (coluna 0 do arquivo). O teste `test_no_aws_calls_at_module_import_time` valida isso.
- [ ] Diff comparado ao monolito (DDD): domain/ e application/ copiados sem alterar logica (so import paths)
