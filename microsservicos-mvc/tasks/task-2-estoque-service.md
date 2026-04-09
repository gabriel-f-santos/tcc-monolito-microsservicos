# Task 2: Migrar Estoque para microsservicos-mvc/estoque-service

## Objetivo

Migrar entradas, saidas e consultas de estoque do `monolito-mvc/routes/estoque.py` para Lambda handlers em `microsservicos-mvc/estoque-service/`.

## Referencia (ler antes)

- `monolito-mvc/routes/estoque.py` — rotas de estoque (SQLAlchemy)
- `monolito-mvc/models.py` — modelos ItemEstoque, Movimentacao
- `microsservicos-mvc/CLAUDE.md` — regras (MVC, sem DDD)

## Arquitetura alvo

```
estoque-service/
├── src/
│   ├── handlers/
│   │   ├── health.py           # JA EXISTE
│   │   ├── estoque.py          # REESCREVER — entrada, saida, consultas
│   │   └── event_consumer.py   # REESCREVER — consome SQS (ProdutoCriado)
│   └── __init__.py
├── tests/
│   ├── test_health.py          # JA EXISTE
│   └── test_estoque.py         # CRIAR — 14 testes (11 estoque + 3 eventos)
├── pyproject.toml
└── requirements.txt
```

## DynamoDB

Tabelas:
- `tcc-itens-estoque` (PK: `id` string)
- `tcc-movimentacoes` (PK: `id` string)

Para buscar por produto_id: `Scan` com `FilterExpression`

## O que implementar

### `src/handlers/estoque.py`

Roteamento por method + path:

```python
def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]

    # POST /api/v1/estoque/{id}/entrada
    #   quantidade > 0 senao 422
    #   item deve existir senao 404
    #   item deve estar ativo senao 422
    #   incrementar saldo, criar movimentacao ENTRADA
    #   retornar 201 + movimentacao

    # POST /api/v1/estoque/{id}/saida
    #   quantidade > 0 senao 422
    #   saldo >= quantidade senao 422 (ESTOQUE_INSUFICIENTE)
    #   decrementar saldo, criar movimentacao SAIDA
    #   retornar 201 + movimentacao

    # GET /api/v1/estoque
    #   listar todos os itens de estoque

    # GET /api/v1/estoque/{id}
    #   buscar item por ID, 404 se nao existe

    # GET /api/v1/estoque/produto/{produto_id}
    #   buscar item por produto_id, 404 se nao existe

    # GET /api/v1/estoque/{id}/movimentacoes
    #   listar movimentacoes do item
```

### `src/handlers/event_consumer.py`

Consome eventos SQS do Catalogo:

```python
def handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        message = json.loads(body["Message"])
        evento = message["evento"]

        if evento == "ProdutoCriado":
            # Criar ItemEstoque com saldo=0 no DynamoDB
            # Dados: produto_id, sku, nome, categoria_nome
            # Idempotente: se ja existe item com esse produto_id, ignorar

        elif evento == "ProdutoAtualizado":
            # Atualizar projecao local (nome, categoria_nome)

        elif evento == "ProdutoDesativado":
            # Marcar item como ativo=false
```

### `tests/test_estoque.py` — 14 testes

```python
# Usar dicts in-memory como fake DynamoDB

# Entrada (4)
test_registrar_entrada         # POST entrada → 201 + movimentacao ENTRADA
test_saldo_apos_entrada        # Entrada 100 + 50 → saldo=150
test_entrada_quantidade_invalida  # quantidade=0 → 422
test_entrada_item_inexistente  # uuid aleatorio → 404

# Consultas (3)
test_listar_itens_estoque      # Criar 2 → GET → lista com 2+
test_buscar_item_por_produto   # GET /produto/{id} → 200
test_historico_movimentacoes   # 3 entradas → GET movimentacoes → 3

# Saida (4)
test_registrar_saida           # Entrada 100 + saida 30 → saldo=70
test_saida_estoque_insuficiente  # Entrada 10 + saida 20 → 422
test_saida_zera_estoque        # Entrada 50 + saida 50 → saldo=0
test_multiplas_movimentacoes   # Entrada 100, saida 30, saida 30 → saldo=40

# Eventos (3)
test_evento_produto_criado_cria_item  # Simular SQS event → item criado com saldo=0
test_evento_idempotente        # Mesmo evento 2x → apenas 1 item
test_evento_produto_atualizado # Atualizar projecao local
```

## Environment Variables

- `ITENS_ESTOQUE_TABLE` = "tcc-itens-estoque"
- `MOVIMENTACOES_TABLE` = "tcc-movimentacoes"

## Criterio de pronto

- [ ] 14 testes passam (11 estoque + 3 eventos)
- [ ] 2 testes de health continuam passando
- [ ] Handlers fazem queries DynamoDB diretas
- [ ] Event consumer processa ProdutoCriado, ProdutoAtualizado, ProdutoDesativado
- [ ] Eventos sao idempotentes
- [ ] Saldo nunca negativo (validar no handler)
- [ ] Rodar: `cd microsservicos-mvc/estoque-service && pytest -v`
