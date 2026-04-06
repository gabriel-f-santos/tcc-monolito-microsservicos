# Feature 2: CRUD de Produto

## Contexto

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias (violacoes sao CRITICAL)
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Pre-requisito: Features 0 (Auth) e 1 (Categoria) ja implementadas.

## Arquitetura alvo

### Monolito
- Modulo: `src/catalogo/` (mesmo modulo que Categoria)
- Agregado Produto com Value Objects SKU e Dinheiro
- Ao criar produto, criar ItemEstoque com saldo=0 no mesmo use case (in-process)

### Microsservicos
- Servico: `catalogo-service/`
- Ao criar produto, publicar evento ProdutoCriado no SNS
- Estoque cria ItemEstoque via consumer (Feature 5)

## Endpoints

| Metodo | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/produtos` | `{ "sku": "ELET-001", "nome": "Teclado", "descricao": "Mecanico", "preco": 299.90, "categoria_id": "uuid" }` | `201` + Produto |
| GET | `/api/v1/produtos` | Query: `?categoria_id=&ativo=&page=1&size=20` | `200` + Lista paginada |
| GET | `/api/v1/produtos/{id}` | — | `200` + Produto |
| PUT | `/api/v1/produtos/{id}` | `{ "nome": "Teclado RGB", "preco": 349.90 }` | `200` + Produto |
| PATCH | `/api/v1/produtos/{id}/desativar` | — | `200` + Produto |

## Modelo: Produto (Agregado Raiz)

| Campo | Tipo | Classificacao | Regras |
|-------|------|---------------|--------|
| `id` | UUID | Identidade | Gerado automaticamente |
| `sku` | SKU (VO) | Value Object | Unico, alfanumerico, 3-50 chars, imutavel |
| `nome` | string | Atributo | Obrigatorio, 1-200 caracteres |
| `descricao` | string | Atributo | Opcional, ate 1000 caracteres |
| `preco` | Dinheiro (VO) | Value Object | Maior que zero, decimal 2 casas |
| `categoria_id` | UUID | Referencia | Categoria deve existir |
| `ativo` | bool | Atributo | Default: true |
| `criado_em` | datetime | Atributo | Gerado automaticamente |
| `atualizado_em` | datetime | Atributo | Atualizado automaticamente |

## Value Objects (implementar em `domain/value_objects/`)

### SKU
- Imutavel (`frozen=True`)
- Validacao: alfanumerico + hifen, 3-50 caracteres, regex `^[A-Za-z0-9-]{3,50}$`
- Igualdade por valor

### Dinheiro
- Imutavel (`frozen=True`)
- Validacao: valor > 0, Decimal com 2 casas
- Igualdade por valor

## Regras de negocio

1. SKU e unico no sistema e imutavel apos criacao
2. Preco deve ser maior que zero
3. Categoria referenciada deve existir
4. Produto desativado nao pode ser reativado
5. **Monolito:** ao criar produto, criar ItemEstoque com saldo=0 automaticamente
6. **Microsservicos:** ao criar produto, publicar evento ProdutoCriado no SNS

## Erros de dominio

| Codigo | Quando |
|--------|--------|
| `PRODUTO_SKU_DUPLICADO` | SKU ja existe |
| `PRODUTO_NAO_ENCONTRADO` | Busca/atualizacao com ID inexistente |
| `CATEGORIA_NAO_ENCONTRADA` | categoria_id invalido |
| `PRECO_INVALIDO` | Preco <= 0 |
| `SKU_INVALIDO` | SKU fora do formato |

## Response Schema

```json
{
  "id": "uuid",
  "sku": "ELET-001",
  "nome": "Teclado Mecanico",
  "descricao": "Teclado com switches blue",
  "preco": 299.90,
  "categoria": {
    "id": "uuid",
    "nome": "Eletronicos"
  },
  "ativo": true,
  "criado_em": "2026-04-05T10:00:00Z",
  "atualizado_em": "2026-04-05T10:00:00Z"
}
```

## Testes esperados (9)

```
test_criar_produto
  Criar categoria → POST /api/v1/produtos com dados validos → 201
  Response contem id, sku, nome, preco, categoria (nested), ativo=true

test_criar_produto_sku_duplicado
  POST dois produtos com mesmo SKU → segundo retorna 409
  code: PRODUTO_SKU_DUPLICADO

test_criar_produto_preco_invalido
  POST com preco=0 → 422
  code: PRECO_INVALIDO

test_criar_produto_categoria_inexistente
  POST com categoria_id=uuid-aleatorio → 404
  code: CATEGORIA_NAO_ENCONTRADA

test_listar_produtos
  Criar 3 produtos → GET /api/v1/produtos → 200, 3 itens

test_listar_produtos_filtro_categoria
  Criar 2 categorias, 3 produtos (2 na cat A, 1 na cat B)
  GET ?categoria_id=catA → retorna 2 produtos

test_buscar_produto_por_id
  Criar produto → GET /api/v1/produtos/{id} → 200

test_atualizar_produto
  Criar produto → PUT /{id} com nome novo → 200
  nome atualizado, sku inalterado, atualizado_em mudou

test_desativar_produto
  Criar produto → PATCH /{id}/desativar → 200, ativo=false
```

## Estrutura de arquivos esperada (monolito, adicionar ao catalogo existente)

```
src/catalogo/
├── domain/
│   ├── entities/produto.py          # Agregado Produto
│   ├── value_objects/
│   │   ├── sku.py                   # Value Object SKU
│   │   └── dinheiro.py              # Value Object Dinheiro
│   ├── exceptions/catalogo.py       # Adicionar erros de produto
│   └── repositories/produto_repository.py  # Interface ABC
├── application/
│   └── use_cases/
│       ├── criar_produto.py
│       ├── listar_produtos.py
│       ├── buscar_produto.py
│       ├── atualizar_produto.py
│       └── desativar_produto.py
├── infrastructure/
│   └── repositories/
│       └── sqlalchemy_produto_repository.py
├── container.py                     # Adicionar providers de produto
└── presentation/
    ├── routes.py                    # Adicionar rotas de produto
    └── schemas.py                   # Adicionar schemas de produto
```

## Criterio de pronto

- [ ] 9 testes passam
- [ ] `radon cc src/catalogo/ -s -a` sem funcao acima de B
- [ ] `pytest --cov=src.catalogo` >= 70%
- [ ] Value Objects SKU e Dinheiro sao imutaveis (frozen dataclass)
- [ ] Invariantes validadas dentro do agregado Produto
- [ ] Endpoints protegidos por JWT
