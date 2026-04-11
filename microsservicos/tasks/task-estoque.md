# Task: Implementar Estoque Service

## Prompt (copiar e colar)

```
Implemente o estoque-service para que todos os testes em tests/ passem.

ANTES DE CODAR:
1. Leia microsservicos/tasks/INTEGRATION-CONTRACT.md — regras obrigatorias.
2. Leia CLAUDE.md deste servico para entender a arquitetura (DDD ou MVC).
3. Leia template.yaml e liste TODAS as entradas em Environment.Variables.
   O codigo DEVE ler EXATAMENTE esses nomes.
4. Leia os testes em tests/ para entender o comportamento esperado.
5. Use monolito/src/estoque/ (DDD) ou monolito-mvc/routes/estoque.py (MVC)
   como referencia.

O servico tem DOIS handlers:
  1. estoque.py — handler(event, context) com roteamento por method+path
  2. event_consumer.py — handler(event, context) consome SQS (eventos de catalogo)

event_consumer DEVE persistir no DynamoDB. Nao pode apenas logar. Os testes
em tests/test_estoque.py criam ItemEstoque via event_consumer (simulando
ProdutoCriado do SQS) e depois verificam via HTTP handler que o item existe.

Testes rodam sob mock_aws() via conftest.py (moto). Nao use repositorios
InMemory como fallback — producao sempre DynamoDB, teste usa moto.

Para o DDD: copie domain/ e application/ do monolito SEM MODIFICACAO (so
ajustar imports). Crie infrastructure com DynamoDBItemEstoqueRepository e
DynamoDBMovimentacaoRepository.

Para o MVC: reescreva como handlers com queries DynamoDB inline.

Setup:
  cd microsservicos/XXX-service
  pyenv local 3.13.7 && python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt -r requirements-dev.txt
Rodar:
  pytest tests/ -v
```

## Bugs da rodada anterior — NAO REPETIR

**Estoque-service foi o servico com MAIS bugs na rodada anterior:**

1. **DDD: nenhum repositorio DynamoDB implementado**. O container so tinha
   `InMemoryItemEstoqueRepository` e `InMemoryMovimentacaoRepository` — a
   IA simplesmente nao criou os arquivos de infra DynamoDB. Testes passaram
   localmente porque sempre usavam InMemory. Em producao, cada Lambda
   invocation era isolada e perdia todo o estado.

2. **MVC: flag `USE_DYNAMO=true` nunca setada no template**. Codigo tinha
   `_USE_DYNAMO = os.environ.get("USE_DYNAMO", "false").lower() == "true"`.
   O template nao enviava essa var → sempre caia no InMemory. Alem disso,
   lia `ITENS_TABLE` mas o template enviava `ITENS_ESTOQUE_TABLE`.

3. **MVC: event_consumer.py sem codigo DynamoDB**. O handler SQS so logava
   o evento e retornava 200 — nunca gravava o ItemEstoque no DynamoDB. Os
   testes passavam porque mutavam um dict in-memory compartilhado entre
   testes do mesmo processo.

**Evitar**:
- O teste `test_env_vars_from_template_are_read_by_src_code` falha se
  voce ler um nome que nao esteja em template.yaml
- O teste `test_no_inmemory_fallback_in_production_code` falha se houver
  `if os.environ.get(...): ... InMemory` ou `_USE_DYNAMO`
- O teste `test_event_consumers_do_not_only_log` falha se event_consumer.py
  nao contem nenhuma chamada de escrita (put_item/update_item/save/Table()).

## Testes que devem passar (14 estoque + 2 health + 3 contract = 19)

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
| test_evento_produto_criado_cria_item | SQS ProdutoCriado → item com saldo=0 persistido no DynamoDB |
| test_evento_idempotente | Mesmo evento 2x → 1 item |
| test_evento_produto_atualizado | ProdutoAtualizado → projecao atualizada |

### Health + Contract
| Teste | Comportamento |
|-------|-------------|
| test_health_returns_200 | GET /health → 200 |
| test_health_body | {status: healthy, service: estoque} |
| test_env_vars_from_template_are_read_by_src_code | env vars alinhadas |
| test_no_inmemory_fallback_in_production_code | sem branch InMemory / USE_DYNAMO |
| test_event_consumers_do_not_only_log | event_consumer.py persiste |

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
                          ProdutoCriado → cria ItemEstoque saldo=0 (PERSISTIR)
                          ProdutoAtualizado → atualiza projecao (nome, categoria)
                          ProdutoDesativado → ativo=false
```

## DynamoDB e SQS (ver template.yaml)

- Tabelas: `ItensEstoqueTable` e `MovimentacoesTable` (PK: id)
- Env vars: `ITENS_ESTOQUE_TABLE`, `MOVIMENTACOES_TABLE`
- SQS: `EstoqueEventosQueue` — subscription automatica no topico SNS do catalogo
- Buscar por produto_id: Scan com FilterExpression

## Regras de negocio

- Quantidade > 0 (senao 422)
- Saldo nunca negativo (saida com saldo < quantidade → 422)
- Item inativo nao aceita entrada (422); saida permitida
- Eventos idempotentes (ProdutoCriado 2x nao duplica — checar antes de criar)
- Movimentacao registra tipo (ENTRADA/SAIDA), quantidade, lote, motivo

## Checklist de "done"

Marque como feito APENAS se TODOS os items passarem:

- [ ] `pytest tests/ -v` → **19 passed** (14 estoque + 2 health + 3 contract)
- [ ] `test_integration_contract.py` inteiramente verde — **incluindo** `test_event_consumers_do_not_only_log`
- [ ] `src/handlers/event_consumer.py` contem `put_item` ou `.save(`
- [ ] Nenhum `if os.environ.get(...): ... InMemory`, nenhum `_USE_DYNAMO`, nenhum `is_aws`
- [ ] `grep -r "os.environ" src/` lista SOMENTE `ITENS_ESTOQUE_TABLE` e `MOVIMENTACOES_TABLE`
- [ ] Arquivos `src/infrastructure/repositories/dynamodb_*.py` EXISTEM e sao usados pelo container (DDD)
- [ ] Teste `test_evento_produto_criado_cria_item` verifica persistencia via boto3.Table(...).scan() ou get_item()
- [ ] Nenhuma chamada DynamoDB em nivel de modulo
- [ ] Diff comparado ao monolito: DDD copiou domain/application SEM alterar logica (so import paths)
