# Integration Contract — Regras Obrigatorias de Implementacao

Todo servico em `microsservicos/*-service[-mvc]/` DEVE seguir este contrato.
Existe porque, sem ele, ha uma classe comum de bugs em que o codigo passa nos
testes locais mas falha no deploy real (InMemory substituindo DynamoDB,
desalinhamento de nomes de env var, event consumers que nao persistem, etc).

---

## Regra 1 — Leia `template.yaml` ANTES de escrever codigo

Para cada funcao Lambda em `template.yaml`, liste TODAS as entradas em
`Environment.Variables`. Exemplo:

```yaml
RegistrarFunction:
  Environment:
    Variables:
      USUARIOS_TABLE: !Ref UsuariosTable
      JWT_SECRET: !Ref JwtSecret
```

O codigo DEVE ler EXATAMENTE esses nomes. Nao invente variantes como
`DYNAMODB_TABLE`, `TABLE_NAME`, `USER_TABLE`. O teste-guardiao
`tests/test_integration_contract.py` parseia o template e falha se qualquer
env var declarada nao aparecer no codigo.

## Regra 2 — Testes usam `moto` — nunca InMemory oculto

- `conftest.py` abre `mock_aws()` em fixture `autouse=True` e cria as tabelas,
  topicos e filas a partir de `template.yaml`.
- Os testes setam as env vars com os nomes reais e invocam os handlers
  diretamente. boto3 dentro do handler e interceptado pela moto.
- Repositorios InMemory sao permitidos APENAS como fixture de teste
  explicita para dominio/use-cases puros — NUNCA como branch alternativo em
  producao selecionado por env var opcional.

**Antipadrao proibido:**

```python
# ERRADO — cai em InMemory quando env var nao esta setada no teste
if os.environ.get("USUARIOS_TABLE"):
    return DynamoDBRepo()
return InMemoryRepo()
```

**Padrao correto:**

```python
# Producao sempre usa DynamoDB. Moto intercepta as chamadas em teste.
return DynamoDBRepo(os.environ["USUARIOS_TABLE"])
```

## Regra 3 — Persistencia e verificada em todo teste de escrita

Todo teste que faz POST, PUT, PATCH ou processa um evento DEVE verificar
com `boto3.resource(...).scan()` ou `.get_item()` que o registro foi
gravado. Nao confie em `statusCode == 201`.

```python
def test_registrar_persiste_no_dynamodb(dynamodb_tables):
    resp = registrar_handler(_event({"email": "a@b.com", ...}), None)
    assert resp["statusCode"] == 201

    items = dynamodb_tables["USUARIOS_TABLE"].scan()["Items"]
    assert len(items) == 1
    assert items[0]["email"] == "a@b.com"
```

## Regra 4 — Event consumers persistem no DynamoDB

Handlers SQS/SNS que processam eventos de dominio DEVEM gravar o estado
resultante no DynamoDB. Nao apenas logar. Teste verifica o side-effect.

## Regra 5 — Sem chamadas AWS em import time

`boto3.resource("dynamodb").Table(...)` pode ser cacheado em nivel de modulo,
mas operacoes (`get_item`, `scan`, `put_item`) devem rodar DENTRO das funcoes,
nunca no topo do arquivo. Caso contrario pytest/moto nao conseguem interceptar.

## Regra 6 — Handlers nao capturam excecoes genericas

Mantenha `except` especifico para as excecoes de dominio. Excecoes
inesperadas devem subir e virar 500 — isso aparece nos logs do CloudWatch
e permite debug. Um `except Exception: return 500` silencioso mascara bugs.

---

## Artefatos obrigatorios em cada servico

| Caminho | Proposito |
|---|---|
| `conftest.py` na raiz do servico | Fixture `autouse` com `mock_aws()` criando tabelas/topicos/filas do template.yaml |
| `tests/test_integration_contract.py` | Teste-guardiao: env vars alinhadas, ausencia de fallback InMemory |
| `requirements-dev.txt` | pytest + `moto[all]` + pyyaml |

Use `microsservicos/tasks/reference-conftest.py` como ponto de partida —
ele ja parseia `template.yaml` e cria tudo. Basta copiar pra cada servico.

## Checklist antes de considerar "pronto"

- [ ] `pip install -r requirements.txt -r requirements-dev.txt`
- [ ] `pytest tests/ -v` → todos passam, incluindo `test_integration_contract`
- [ ] `grep -rE 'os\.environ(\.get)?\[?["'"'"']' src/` — toda env var citada existe em `template.yaml`
- [ ] Nao ha branch condicional selecionando InMemory em prod
- [ ] Todo POST/evento tem teste que verifica persistencia via boto3
- [ ] Event consumers gravam no DynamoDB
