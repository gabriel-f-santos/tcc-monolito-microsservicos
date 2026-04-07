# Migracao: Catalogo Service (Monolito → Microsservico)

## Contexto

**IMPORTANTE:** Cada microsservico e independente com seu proprio `pyproject.toml`, `tests/` e venv. Rode testes de DENTRO do diretorio do servico: `cd microsservicos/xxx-service && pytest`. Imports usam `src.` (nao `xxx-service.src.`).

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias
- `docs/architecture.md` — padrao DDD, camadas, container DI
- `microsservicos/CLAUDE.md` — regras dos microsservicos
- `monolito/src/catalogo/` — codigo fonte do monolito (REFERENCIA)
- `microsservicos/template.yaml` — recursos SAM ja provisionados

## Objetivo

Migrar o Bounded Context de Catalogo de Produtos do monolito para o `catalogo-service/`.
- **Domain e Application: IDENTICOS** ao monolito
- **Infrastructure: DynamoDB** (tabelas `tcc-produtos`, `tcc-categorias`)
- **Presentation: Lambda handlers** puros
- **Cross-BC:** ao criar produto, publica evento ProdutoCriado no SNS (em vez de chamar EstoqueService in-process)

## O que copiar do monolito (SEM alteracao)

```
monolito/src/catalogo/domain/         → catalogo-service/src/domain/
  entities/produto.py                 COPIAR INTEIRO
  entities/categoria.py               COPIAR INTEIRO
  value_objects/sku.py                COPIAR INTEIRO
  value_objects/dinheiro.py           COPIAR INTEIRO
  exceptions/catalogo.py              COPIAR INTEIRO
  repositories/produto_repository.py  COPIAR INTEIRO
  repositories/categoria_repository.py COPIAR INTEIRO

monolito/src/shared/domain/services/
  estoque_service.py                  COPIAR para shared/domain/services/

monolito/src/catalogo/application/    → catalogo-service/src/application/
  use_cases/criar_produto.py          COPIAR INTEIRO
  use_cases/criar_categoria.py        COPIAR INTEIRO
  use_cases/listar_produtos.py        COPIAR INTEIRO
  use_cases/listar_categorias.py      COPIAR INTEIRO
  use_cases/buscar_produto.py         COPIAR INTEIRO
  use_cases/buscar_categoria.py       COPIAR INTEIRO
  use_cases/atualizar_produto.py      COPIAR INTEIRO
  use_cases/desativar_produto.py      COPIAR INTEIRO
```

## O que criar novo

```
catalogo-service/src/
├── infrastructure/
│   ├── repositories/
│   │   ├── dynamodb_produto_repository.py      # NOVO
│   │   └── dynamodb_categoria_repository.py    # NOVO
│   └── services/
│       └── sns_estoque_service.py              # NOVO — publica ProdutoCriado no SNS
├── container.py                                # NOVO — providers DynamoDB + SNS
└── presentation/
    └── handlers/
        └── catalogo.py                         # REESCREVER — Lambda handler com roteamento
```

## DynamoDB — Tabelas

```
tcc-produtos:     PK = id (S)
tcc-categorias:   PK = id (S)

Para buscar por SKU: Scan com FilterExpression (escala pequena)
Para filtrar por categoria_id: Scan com FilterExpression
```

## Cross-BC: SNS em vez de in-process

No monolito, `CriarProdutoUseCase` chama `estoque_service.inicializar_item()` in-process.
Nos microsservicos, a implementacao de `EstoqueService` publica no SNS:

```python
# catalogo-service/src/infrastructure/services/sns_estoque_service.py
class SNSEstoqueService(EstoqueService):
    def __init__(self, topic_arn: str):
        self.sns = boto3.client("sns")
        self.topic_arn = topic_arn

    def inicializar_item(self, produto_id, sku, nome_produto, categoria_nome):
        self.sns.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps({
                "evento": "ProdutoCriado",
                "dados": {"produto_id": str(produto_id), "sku": sku, "nome": nome_produto, "categoria_nome": categoria_nome}
            })
        )
```

**O use case NAO muda** — ele chama `self.estoque_service.inicializar_item()` como antes. So a implementacao e diferente.

## Lambda Handler — Roteamento

```python
def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]
    # Rotear por method + path para o use case correto
    # O user_id vem do Lambda Authorizer context:
    user_id = event["requestContext"]["authorizer"]["principalId"]
```

## Testes esperados (14 — categoria + produto)

Mesmos testes do monolito, adaptados para invocar Lambda handler com event mockado:

```
# Categoria (5)
test_criar_categoria
test_criar_categoria_duplicada
test_listar_categorias
test_buscar_categoria_por_id
test_buscar_categoria_inexistente

# Produto (9)
test_criar_produto
test_criar_produto_sku_duplicado
test_criar_produto_preco_invalido
test_criar_produto_categoria_inexistente
test_listar_produtos
test_listar_produtos_filtro_categoria
test_buscar_produto_por_id
test_atualizar_produto
test_desativar_produto
```

## Metricas de migracao a coletar

```
Arquivos copiados sem alteracao (domain + application): ___
Arquivos novos (infrastructure + presentation): ___
Linhas de domain/ inalteradas: ___
Linhas de infrastructure/ novas: ___
Testes que passam: ___/14
```

## Criterio de pronto

- [ ] 14 testes passam
- [ ] domain/ e application/ IDENTICOS ao monolito
- [ ] Repos usam DynamoDB (boto3), nao SQLAlchemy
- [ ] CriarProduto publica evento ProdutoCriado no SNS
- [ ] Handler faz roteamento por httpMethod + path
- [ ] Container usa dependency-injector
