# Feature 3: Entrada de Estoque

## Contexto

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias (violacoes sao CRITICAL)
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Pre-requisito: Features 0-2 ja implementadas. Produtos e categorias existem no sistema.

## Arquitetura alvo

### Monolito
- Modulo: `src/estoque/`
- ItemEstoque ja foi criado automaticamente quando Produto foi criado (Feature 2)
- Entrada incrementa saldo e cria Movimentacao

### Microsservicos
- Servico: `estoque-service/`
- ItemEstoque existe via evento ProdutoCriado (Feature 5) ou criado manualmente para testes
- Repository DynamoDB (tabelas `tcc-itens-estoque` e `tcc-movimentacoes`)

## Endpoints

| Metodo | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/estoque/{id}/entrada` | `{ "quantidade": 100, "lote": "NF-001", "motivo": "Recebimento" }` | `201` + Movimentacao |
| GET | `/api/v1/estoque` | Query: `?saldo_min=&page=1&size=20` | `200` + Lista paginada |
| GET | `/api/v1/estoque/{id}` | — | `200` + ItemEstoque |
| GET | `/api/v1/estoque/produto/{produto_id}` | — | `200` + ItemEstoque |
| GET | `/api/v1/estoque/{id}/movimentacoes` | Query: `?tipo=&page=1&size=20` | `200` + Lista paginada |

## Modelo: ItemEstoque (Agregado Raiz)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `produto_id` | UUID | Referencia ao produto |
| `sku` | string | Projecao local |
| `nome_produto` | string | Projecao local |
| `categoria_nome` | string | Projecao local |
| `saldo` | int | >= 0 |
| `ativo` | bool | Default: true |
| `criado_em` | datetime | Gerado automaticamente |

## Modelo: Movimentacao (Entidade)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `item_estoque_id` | UUID | Referencia ao agregado raiz |
| `tipo` | enum | `ENTRADA` ou `SAIDA` |
| `quantidade` | int | Maior que zero |
| `lote` | string | Opcional |
| `motivo` | string | Opcional |
| `criado_em` | datetime | Gerado automaticamente |

## Value Objects

### Quantidade
- Imutavel, inteiro positivo (> 0)

### TipoMovimentacao
- Enum: `ENTRADA`, `SAIDA`

## Regras de negocio

1. Quantidade deve ser maior que zero
2. Lote e motivo sao opcionais
3. Entrada incrementa saldo do ItemEstoque
4. Toda entrada gera uma Movimentacao com tipo=ENTRADA
5. Item desativado nao aceita entradas (code: ITEM_INATIVO)

## Erros de dominio

| Codigo | Quando |
|--------|--------|
| `ITEM_NAO_ENCONTRADO` | Busca com ID inexistente |
| `QUANTIDADE_INVALIDA` | Quantidade <= 0 |
| `ITEM_INATIVO` | Entrada em item desativado |

## Response Schemas

**ItemEstoque:**
```json
{
  "id": "uuid",
  "produto_id": "uuid",
  "sku": "ELET-001",
  "nome_produto": "Teclado Mecanico",
  "categoria_nome": "Eletronicos",
  "saldo": 150,
  "ativo": true,
  "criado_em": "2026-04-05T10:00:00Z"
}
```

**Movimentacao:**
```json
{
  "id": "uuid",
  "item_estoque_id": "uuid",
  "tipo": "ENTRADA",
  "quantidade": 100,
  "lote": "NF-2026-001",
  "motivo": "Recebimento fornecedor",
  "criado_em": "2026-04-05T14:00:00Z"
}
```

## Testes esperados (7)

```
test_registrar_entrada
  Criar produto (gera ItemEstoque) → POST /estoque/{id}/entrada quantidade=100 → 201
  Response contem tipo=ENTRADA, quantidade=100

test_saldo_apos_entrada
  Entrada de 100 → GET /estoque/{id} → saldo=100
  Outra entrada de 50 → GET → saldo=150

test_entrada_quantidade_invalida
  POST com quantidade=0 → 422
  code: QUANTIDADE_INVALIDA

test_entrada_item_inexistente
  POST /estoque/{uuid-aleatorio}/entrada → 404
  code: ITEM_NAO_ENCONTRADO

test_listar_itens_estoque
  Criar 2 produtos (gera 2 itens) → GET /estoque → 200, 2 itens

test_buscar_item_por_produto
  Criar produto → GET /estoque/produto/{produto_id} → 200, item correto

test_historico_movimentacoes
  Fazer 3 entradas → GET /estoque/{id}/movimentacoes → 3 registros
```

## Estrutura de arquivos esperada (monolito)

```
src/estoque/
├── domain/
│   ├── entities/
│   │   ├── item_estoque.py          # Agregado ItemEstoque
│   │   └── movimentacao.py          # Entidade Movimentacao
│   ├── value_objects/
│   │   ├── quantidade.py            # Value Object Quantidade
│   │   └── tipo_movimentacao.py     # Enum ENTRADA/SAIDA
│   ├── exceptions/estoque.py        # ItemNaoEncontrado, QuantidadeInvalida, ItemInativo
│   └── repositories/
│       ├── item_estoque_repository.py
│       └── movimentacao_repository.py
├── application/
│   └── use_cases/
│       ├── registrar_entrada.py
│       ├── listar_itens.py
│       ├── buscar_item.py
│       └── listar_movimentacoes.py
├── infrastructure/
│   └── repositories/
│       ├── sqlalchemy_item_estoque_repository.py
│       └── sqlalchemy_movimentacao_repository.py
├── container.py
└── presentation/
    ├── routes.py
    └── schemas.py
```

## Criterio de pronto

- [ ] 7 testes passam
- [ ] `radon cc src/estoque/ -s -a` sem funcao acima de B
- [ ] `pytest --cov=src.estoque` >= 70%
- [ ] Saldo e calculado dentro do agregado ItemEstoque
- [ ] Movimentacao e criada pelo agregado, nao pelo use case
- [ ] Endpoints protegidos por JWT
