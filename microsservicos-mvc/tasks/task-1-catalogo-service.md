# Task 1: Migrar Catalogo para microsservicos-mvc/catalogo-service

## Objetivo

Migrar CRUD de categorias e produtos do `monolito-mvc/routes/categorias.py` e `monolito-mvc/routes/produtos.py` para Lambda handler em `microsservicos-mvc/catalogo-service/`.

## Referencia (ler antes)

- `monolito-mvc/routes/categorias.py` — CRUD categorias (SQLAlchemy)
- `monolito-mvc/routes/produtos.py` — CRUD produtos (SQLAlchemy)
- `monolito-mvc/models.py` — modelos Categoria, Produto, ItemEstoque
- `monolito-mvc/schemas.py` — schemas de request/response
- `microsservicos-mvc/CLAUDE.md` — regras (MVC, sem DDD)

## Arquitetura alvo

```
catalogo-service/
├── src/
│   ├── handlers/
│   │   ├── health.py        # JA EXISTE
│   │   └── catalogo.py      # REESCREVER — roteamento por method+path
│   └── __init__.py
├── tests/
│   ├── test_health.py       # JA EXISTE
│   └── test_catalogo.py     # CRIAR — 14 testes
├── pyproject.toml
└── requirements.txt
```

## DynamoDB

Tabelas:
- `tcc-categorias` (PK: `id` string)
- `tcc-produtos` (PK: `id` string)

Para buscar por nome/SKU: `Scan` com `FilterExpression`
Para filtrar por categoria_id: `Scan` com `FilterExpression`

## O que implementar

### `src/handlers/catalogo.py`

Handler unico com roteamento por `event["httpMethod"]` + `event["path"]`:

```python
def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]

    # Categorias
    # POST /api/v1/categorias → criar (nome unico, 409 se duplicado)
    # GET  /api/v1/categorias → listar
    # GET  /api/v1/categorias/{id} → buscar por ID (404 se nao existe)

    # Produtos
    # POST  /api/v1/produtos → criar (SKU unico, preco>0, categoria deve existir)
    #   IMPORTANTE: ao criar produto, publicar evento ProdutoCriado no SNS
    #   Topic ARN via env var EVENTOS_TOPIC_ARN
    # GET   /api/v1/produtos → listar (filtros: categoria_id, ativo)
    # GET   /api/v1/produtos/{id} → buscar
    # PUT   /api/v1/produtos/{id} → atualizar (nome, descricao, preco)
    # PATCH /api/v1/produtos/{id}/desativar → ativo=false
```

### Publicacao de evento SNS (ao criar produto)

```python
import boto3, json, os
sns = boto3.client("sns")
sns.publish(
    TopicArn=os.environ["EVENTOS_TOPIC_ARN"],
    Message=json.dumps({
        "evento": "ProdutoCriado",
        "dados": {"produto_id": str(id), "sku": sku, "nome": nome, "categoria_nome": cat_nome}
    })
)
```

### `tests/test_catalogo.py` — 14 testes

```python
# Usar dicts in-memory como fake DynamoDB e fake SNS

# Categorias (5)
test_criar_categoria           # POST → 201 + id, nome, criado_em
test_criar_categoria_duplicada # POST mesmo nome → 409
test_listar_categorias         # Criar 2 → GET → lista com 2+
test_buscar_categoria_por_id   # Criar → GET /{id} → 200
test_buscar_categoria_inexistente  # GET /{uuid} → 404

# Produtos (9)
test_criar_produto             # POST → 201 + sku, nome, preco, categoria nested
test_criar_produto_sku_duplicado   # POST mesmo SKU → 409
test_criar_produto_preco_invalido  # POST preco=0 → 422
test_criar_produto_categoria_inexistente  # POST cat_id invalido → 404
test_listar_produtos           # Criar 3 → GET → lista com 3+
test_listar_produtos_filtro_categoria  # Filtrar por categoria_id
test_buscar_produto_por_id     # GET /{id} → 200
test_atualizar_produto         # PUT → 200 + dados atualizados
test_desativar_produto         # PATCH /desativar → 200 + ativo=false
```

## Environment Variables (handler lê de os.environ)

- `CATEGORIAS_TABLE` = "tcc-categorias"
- `PRODUTOS_TABLE` = "tcc-produtos"
- `EVENTOS_TOPIC_ARN` = "arn:aws:sns:us-east-1:537124970335:tcc-eventos-dominio"

## Criterio de pronto

- [ ] 14 testes de catalogo passam
- [ ] 2 testes de health continuam passando
- [ ] Handler faz queries DynamoDB diretas (sem repository)
- [ ] Ao criar produto, publica ProdutoCriado no SNS
- [ ] Paths no handler correspondem ao template.yaml (/api/v1/categorias, /api/v1/produtos)
- [ ] Rodar: `cd microsservicos-mvc/catalogo-service && pytest -v`
