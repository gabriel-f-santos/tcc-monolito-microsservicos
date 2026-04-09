# Task: Implementar Estoque Service

## Prompt (copiar e colar)

```
Implemente o estoque-service para que todos os testes em tests/ passem.

Leia CLAUDE.md deste servico para entender a arquitetura (DDD ou MVC).
Leia os testes em tests/test_estoque.py para entender o comportamento esperado.
Use monolito/src/estoque/ (DDD) ou monolito-mvc/routes/estoque.py (MVC) como referencia.

O servico usa DynamoDB (tabelas definidas no template.yaml).
Handlers recebem Lambda events. Testes invocam handlers diretamente.

Dois handlers:
1. estoque.py — handler(event, context) com roteamento por method+path
2. event_consumer.py — handler(event, context) consome SQS (eventos do catalogo)

Os testes criam ItemEstoque via event_consumer (simulando ProdutoCriado do SQS).
Use in-memory storage (dict) nos testes — NAO precisa de DynamoDB real.

Para o DDD: copie domain/ e application/ do monolito, ajuste imports, crie infra DynamoDB.
Para o MVC: reescreva como handlers com queries DynamoDB inline.

Setup: cd microsservicos/XXX-service && pyenv local 3.13.7 && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install pytest
Rodar: pytest tests/ -v
```

## Testes que devem passar (14 + 2 health = 16)

### Entrada (4)
| Teste | Comportamento |
|-------|-------------|
| test_registrar_entrada | POST entrada 100 → 201 + {tipo: ENTRADA, quantidade: 100} |
| test_saldo_apos_entrada | Entrada 100 + 50 → saldo=150 |
| test_entrada_quantidade_invalida | quantidade=0 → 422 |
| test_entrada_item_inexistente | uuid aleatorio → 404 |

### Consultas (3)
| Teste | Comportamento |
|-------|-------------|
| test_listar_itens_estoque | Criar 2 → GET → lista >= 2 |
| test_buscar_item_por_produto | GET /produto/{id} → 200 + produto_id correto |
| test_historico_movimentacoes | 3 entradas → GET movimentacoes → 3 |

### Saida (4)
| Teste | Comportamento |
|-------|-------------|
| test_registrar_saida | Entrada 100 + Saida 30 → saldo=70 |
| test_saida_estoque_insuficiente | Entrada 10 + Saida 20 → 422 |
| test_saida_zera_estoque | Entrada 50 + Saida 50 → saldo=0 |
| test_multiplas_movimentacoes | Entrada 100, Saida 30, Saida 30 → saldo=40, 3 movimentacoes |

### Eventos (3)
| Teste | Comportamento |
|-------|-------------|
| test_evento_produto_criado_cria_item | SQS ProdutoCriado → item com saldo=0 |
| test_evento_idempotente | Mesmo evento 2x → 1 item |
| test_evento_produto_atualizado | ProdutoAtualizado → projecao atualizada |

## Handlers a implementar

```
src/handlers/
├── health.py           # JA EXISTE
├── estoque.py          # handler(event, context) — roteamento:
│                         POST /api/v1/estoque/{id}/entrada
│                         POST /api/v1/estoque/{id}/saida
│                         GET  /api/v1/estoque
│                         GET  /api/v1/estoque/{id}
│                         GET  /api/v1/estoque/produto/{produto_id}
│                         GET  /api/v1/estoque/{id}/movimentacoes
└── event_consumer.py   # handler(event, context) — consome SQS:
                          ProdutoCriado → cria ItemEstoque saldo=0
                          ProdutoAtualizado → atualiza projecao (nome, categoria)
                          ProdutoDesativado → ativo=false
```

## DynamoDB

- Itens Estoque: ver template.yaml (PK: id)
- Movimentacoes: ver template.yaml (PK: id)
- Buscar por produto_id: Scan com FilterExpression

## Regras

- Quantidade > 0 (senao 422)
- Saldo nunca negativo (saida com saldo < quantidade → 422)
- Item inativo nao aceita entrada (422), saida permitida
- Eventos idempotentes (ProdutoCriado 2x nao duplica)
- Movimentacao registra tipo (ENTRADA/SAIDA), quantidade, lote, motivo
- Paths no handler = paths no template.yaml (/api/v1/*)

## Criterio de pronto

- [ ] `pytest tests/ -v` → 16 passed
- [ ] Event consumer processa ProdutoCriado, ProdutoAtualizado, ProdutoDesativado
- [ ] Eventos idempotentes
- [ ] Saldo nunca negativo
