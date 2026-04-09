# Task: Implementar Catalogo Service

## Prompt (copiar e colar)

```
Implemente o catalogo-service para que todos os testes em tests/ passem.

Leia CLAUDE.md deste servico para entender a arquitetura (DDD ou MVC).
Leia os testes em tests/test_catalogo.py para entender o comportamento esperado.
Use monolito/src/catalogo/ (DDD) ou monolito-mvc/routes/categorias.py + produtos.py (MVC) como referencia.

O servico usa DynamoDB (tabelas definidas no template.yaml).
Os handlers recebem Lambda events, NAO FastAPI requests.
Testes invocam handler() diretamente com event mockado.

Handler unico com roteamento por event["httpMethod"] + event["path"].

Para o DDD: copie domain/ e application/ do monolito, ajuste imports, crie infra DynamoDB.
Para o MVC: reescreva como handler com queries DynamoDB inline.

IMPORTANTE: ao criar produto, publicar evento ProdutoCriado no SNS.
Nos testes, o SNS pode ser mockado/fake (nao precisa de boto3 real).

Setup: cd microsservicos/XXX-service && pyenv local 3.13.7 && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install pytest
Rodar: pytest tests/ -v
```

## Testes que devem passar (14 + 2 health = 16)

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

## Handler a implementar

```
src/handlers/
├── health.py        # JA EXISTE
└── catalogo.py      # handler(event, context) — roteamento por method+path
```

Roteamento:
```
POST  /api/v1/categorias        → criar categoria
GET   /api/v1/categorias        → listar
GET   /api/v1/categorias/{id}   → buscar
POST  /api/v1/produtos          → criar produto + publicar SNS ProdutoCriado
GET   /api/v1/produtos          → listar (query: categoria_id, ativo)
GET   /api/v1/produtos/{id}     → buscar
PUT   /api/v1/produtos/{id}     → atualizar
PATCH /api/v1/produtos/{id}/desativar → desativar
```

## DynamoDB

- Categorias: ver template.yaml (PK: id)
- Produtos: ver template.yaml (PK: id)
- Buscar por nome/SKU: Scan com FilterExpression

## SNS (ao criar produto)

```python
sns.publish(TopicArn=os.environ["EVENTOS_TOPIC_ARN"], Message=json.dumps({
    "evento": "ProdutoCriado",
    "dados": {"produto_id": str(id), "sku": sku, "nome": nome, "categoria_nome": cat_nome}
}))
```

## Regras

- SKU: unico, alfanumerico, 3-50 chars, imutavel
- Preco: > 0
- Categoria referenciada deve existir
- Nome categoria unico
- Paths no handler = paths no template.yaml (/api/v1/*)

## Criterio de pronto

- [ ] `pytest tests/ -v` → 16 passed
- [ ] Ao criar produto, publica ProdutoCriado no SNS (pode ser mockado nos testes)
