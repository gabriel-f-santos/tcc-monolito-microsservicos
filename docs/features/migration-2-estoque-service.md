# Migracao: Estoque Service (Monolito → Microsservico)

## Contexto

**IMPORTANTE:** Cada microsservico e independente com seu proprio `pyproject.toml`, `tests/` e venv. Rode testes de DENTRO do diretorio do servico: `cd microsservicos/xxx-service && pytest`. Imports usam `src.` (nao `xxx-service.src.`).

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias
- `docs/architecture.md` — padrao DDD, camadas, container DI
- `microsservicos/CLAUDE.md` — regras dos microsservicos
- `monolito/src/estoque/` — codigo fonte do monolito (REFERENCIA)
- `microsservicos/template.yaml` — recursos SAM ja provisionados
- `docs/features/feature-5-eventos.md` — spec dos eventos de dominio

## Objetivo

Migrar o Bounded Context de Controle de Estoque do monolito para o `estoque-service/`.
- **Domain e Application: IDENTICOS** ao monolito
- **Infrastructure: DynamoDB** (tabelas `tcc-itens-estoque`, `tcc-movimentacoes`)
- **Presentation: Lambda handlers** puros
- **Event Consumer:** Lambda que consome SQS e cria/atualiza ItemEstoque via projecao

## O que copiar do monolito (SEM alteracao)

```
monolito/src/estoque/domain/          → estoque-service/src/domain/
  entities/item_estoque.py            COPIAR INTEIRO
  entities/movimentacao.py            COPIAR INTEIRO
  value_objects/quantidade.py         COPIAR INTEIRO
  value_objects/tipo_movimentacao.py  COPIAR INTEIRO
  exceptions/estoque.py              COPIAR INTEIRO
  repositories/item_estoque_repository.py   COPIAR INTEIRO
  repositories/movimentacao_repository.py   COPIAR INTEIRO

monolito/src/estoque/application/     → estoque-service/src/application/
  use_cases/registrar_entrada.py      COPIAR INTEIRO
  use_cases/registrar_saida.py        COPIAR INTEIRO
  use_cases/listar_itens.py           COPIAR INTEIRO
  use_cases/buscar_item.py            COPIAR INTEIRO
  use_cases/listar_movimentacoes.py   COPIAR INTEIRO
```

## O que criar novo

```
estoque-service/src/
├── infrastructure/
│   ├── repositories/
│   │   ├── dynamodb_item_estoque_repository.py    # NOVO
│   │   └── dynamodb_movimentacao_repository.py    # NOVO
├── container.py                                    # NOVO
├── application/
│   └── use_cases/
│       ├── criar_item_estoque.py                  # NOVO — cria item a partir de evento
│       └── atualizar_projecao.py                  # NOVO — atualiza nome/categoria via evento
└── presentation/
    └── handlers/
        ├── estoque.py                             # REESCREVER — Lambda handler
        └── event_consumer.py                      # REESCREVER — consome SQS, delega a use cases
```

## DynamoDB — Tabelas

```
tcc-itens-estoque:   PK = id (S)
tcc-movimentacoes:   PK = id (S)

Para buscar por produto_id: Scan com FilterExpression
Para filtrar por categoria: Scan com FilterExpression no campo categoria_nome
```

## Event Consumer — SQS

O consumer Lambda e disparado pelo SQS (configurado no template.yaml, BatchSize=1).
Recebe mensagens do SNS com eventos de dominio do Catalogo:

```python
def handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        message = json.loads(body["Message"])
        evento = message["evento"]

        if evento == "ProdutoCriado":
            use_case = container.criar_item_estoque()
            use_case.execute(message["dados"])
        elif evento == "ProdutoAtualizado":
            use_case = container.atualizar_projecao()
            use_case.execute(message["dados"])
        elif evento == "ProdutoDesativado":
            # marcar item como inativo
            ...
```

### Regras de eventos

1. Idempotente: reprocessar nao duplica ItemEstoque
2. ProdutoCriado → cria ItemEstoque com saldo=0
3. ProdutoAtualizado → atualiza projecao local (nome, categoria)
4. ProdutoDesativado → marca item como inativo
5. Evento invalido → logar e descartar (nao quebrar consumer)

## Testes esperados (14 — estoque + eventos)

### Estoque (11 — entrada + saida)
```
test_registrar_entrada
test_saldo_apos_entrada
test_entrada_quantidade_invalida
test_entrada_item_inexistente
test_listar_itens_estoque
test_buscar_item_por_produto
test_historico_movimentacoes
test_registrar_saida
test_saida_estoque_insuficiente
test_saida_zera_estoque
test_multiplas_movimentacoes
```

### Eventos (3)
```
test_evento_produto_criado_cria_item
test_evento_idempotente
test_evento_produto_atualizado
```

## Metricas de migracao a coletar

```
Arquivos copiados sem alteracao (domain + application): ___
Arquivos novos (infrastructure + presentation + eventos): ___
Linhas de domain/ inalteradas: ___
Linhas de infrastructure/ novas: ___
Testes que passam: ___/14
```

## Criterio de pronto

- [ ] 14 testes passam (11 estoque + 3 eventos)
- [ ] domain/ e application/ IDENTICOS ao monolito (exceto use cases de evento que sao novos)
- [ ] Repos usam DynamoDB (boto3), nao SQLAlchemy
- [ ] Event consumer processa ProdutoCriado, ProdutoAtualizado, ProdutoDesativado
- [ ] Eventos sao idempotentes
- [ ] Container usa dependency-injector
