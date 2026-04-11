# Task: Implementar Catalogo Service

## Prompt (copiar e colar)

```
Implemente o catalogo-service para que todos os testes em tests/ passem.

ANTES DE CODAR:
1. Leia microsservicos/tasks/INTEGRATION-CONTRACT.md — regras obrigatorias.
2. Leia CLAUDE.md deste servico para entender a arquitetura (DDD ou MVC).
3. Leia template.yaml e liste TODAS as entradas em Environment.Variables.
   O codigo DEVE ler EXATAMENTE esses nomes.
4. Leia os testes em tests/ para entender o comportamento esperado.
5. Use monolito/src/catalogo/ (DDD) ou monolito-mvc/routes/categorias.py +
   produtos.py (MVC) como referencia.

O servico usa DynamoDB (duas tabelas) + SNS (publica ProdutoCriado).
Handlers recebem Lambda events. Handler unico com roteamento por
event["httpMethod"] + event["path"].

Testes rodam sob mock_aws() via conftest.py (moto). Nao use repositorios
InMemory como fallback — producao sempre DynamoDB/SNS reais, teste usa moto.

Para o DDD: copie domain/ e application/ do monolito SEM MODIFICACAO (so
ajustar imports). Implemente infrastructure com DynamoDBCategoriaRepository,
DynamoDBProdutoRepository e SnsEventPublisher.

Para o MVC: reescreva como handler com queries DynamoDB e sns.publish inline.

Setup:
  cd microsservicos/XXX-service
  pyenv local 3.13.7 && python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt -r requirements-dev.txt
Rodar:
  pytest tests/ -v
```

## Bugs da rodada anterior — NAO REPETIR

Embora catalogo-service nao tenha tido bug grave na rodada anterior, outros
servicos falharam por:
- Ler `DYNAMODB_TABLE` quando o template enviava o nome real (`USUARIOS_TABLE`/`CATEGORIAS_TABLE`)
- Criar fallback `if env_var: DynamoDB else: InMemory`
- Publicar evento e esquecer de persistir (ou vice-versa)

**Evitar**: os testes-guardiao em `tests/test_integration_contract.py`
falham se voce cair em qualquer um desses padroes.

## Testes que devem passar (14 catalogo + 2 health + 3 contract = 19)

| Teste | Comportamento |
|-------|-------------|
| test_criar_categoria | POST → 201 + {id, nome, criado_em} |
| test_criar_categoria_duplicada | Mesmo nome → 409 |
| test_listar_categorias | Criar 2 → GET → lista >= 2 |
| test_buscar_categoria_por_id | GET /{id} → 200 |
| test_buscar_categoria_inexistente | GET /{uuid} → 404 |
| test_criar_produto | POST → 201 + {id, sku, ativo: true} |
| test_criar_produto_sku_duplicado | Mesmo SKU → 409 |
| test_criar_produto_preco_invalido | preco=0 → 422 |
| test_criar_produto_categoria_inexistente | cat_id invalido → 404 |
| test_listar_produtos | Criar 3 → GET → lista >= 3 |
| test_listar_produtos_filtro_categoria | Filtrar por categoria_id |
| test_buscar_produto_por_id | GET /{id} → 200 |
| test_atualizar_produto | PUT → 200 + nome atualizado |
| test_desativar_produto | PATCH /desativar → 200 + ativo=false |
| test_health_returns_200 | GET /health → 200 |
| test_health_body | {status: healthy, service: catalogo} |
| test_env_vars_from_template_are_read_by_src_code | env vars alinhadas |
| test_no_inmemory_fallback_in_production_code | sem branch InMemory |
| test_event_consumers_do_not_only_log | n/a (sem event consumer) |

## Handler a implementar

```
src/handlers/
├── health.py        # JA EXISTE
└── catalogo.py      # handler(event, context) — roteamento por method+path
```

Roteamento:
```
POST  /api/v1/categorias              → criar categoria
GET   /api/v1/categorias              → listar
GET   /api/v1/categorias/{id}         → buscar
POST  /api/v1/produtos                → criar produto + publicar SNS ProdutoCriado
GET   /api/v1/produtos                → listar (query: categoria_id, ativo)
GET   /api/v1/produtos/{id}           → buscar
PUT   /api/v1/produtos/{id}           → atualizar
PATCH /api/v1/produtos/{id}/desativar → desativar
```

## DynamoDB e SNS (ver template.yaml)

- Tabelas: `CategoriasTable` e `ProdutosTable` com PK `id`
- Env vars: `CATEGORIAS_TABLE`, `PRODUTOS_TABLE`, `EVENTOS_TOPIC_ARN`
- SNS topic: `EventosDominioTopic` — usado para publicar `ProdutoCriado`
- Buscar por nome/SKU: Scan com FilterExpression

Ao criar produto, publicar:
```python
sns.publish(TopicArn=os.environ["EVENTOS_TOPIC_ARN"], Message=json.dumps({
    "evento": "ProdutoCriado",
    "dados": {"produto_id": str(id), "sku": sku, "nome": nome, "categoria_nome": cat_nome}
}))
```

## Regras de negocio

- SKU: unico, alfanumerico, 3-50 chars, imutavel
- Preco: > 0 (422 caso contrario)
- Categoria referenciada deve existir (404 caso contrario)
- Nome de categoria unico (409 caso contrario)
- Paths no handler = paths no template.yaml (/api/v1/*)

## Checklist de "done"

Marque como feito APENAS se TODOS os items passarem:

- [ ] `pytest tests/ -v` → **19 passed** (14 catalogo + 2 health + 3 contract)
- [ ] `test_integration_contract.py` inteiramente verde
- [ ] Nenhum `if os.environ.get(...): ... InMemory ... else: ...` em src/
- [ ] `grep -r "os.environ" src/` lista SOMENTE env vars declaradas no template
- [ ] Ao criar produto, handler publica no SNS (moto intercepta — verificar com `boto3.client('sns').list_subscriptions()` se quiser garantir)
- [ ] Nenhuma chamada DynamoDB/SNS em nivel de modulo (so dentro de funcoes)
- [ ] Diff comparado ao monolito: DDD copiou domain/application SEM alterar logica (so import paths)
