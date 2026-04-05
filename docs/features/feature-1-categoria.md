# Feature 1: CRUD de Categoria

## Contexto

Leia estes arquivos antes de implementar:
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Pre-requisito: Feature 0 (Auth) ja implementada. Todos os endpoints abaixo exigem `Authorization: Bearer <token>`.

## Arquitetura alvo

### Monolito
- Modulo: `src/catalogo/` (mesmo modulo que Produto)
- Entidade Categoria dentro de `src/catalogo/domain/entities/`
- Repository + container no catalogo

### Microsservicos
- Servico: `catalogo-service/`
- Handler Lambda para categorias
- Repository DynamoDB (tabela `tcc-categorias`)

## Endpoints

| Metodo | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/categorias` | `{ "nome": "Eletronicos", "descricao": "Produtos eletronicos" }` | `201` + Categoria |
| GET | `/api/v1/categorias` | — | `200` + Lista |
| GET | `/api/v1/categorias/{id}` | — | `200` + Categoria |

## Modelo: Categoria

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `nome` | string | Obrigatorio, unico, 1-100 caracteres |
| `descricao` | string | Opcional |
| `criado_em` | datetime | Gerado automaticamente |

## Regras de negocio

1. Nome e obrigatorio (1-100 caracteres)
2. Nome e unico no sistema
3. Descricao e opcional

## Erros de dominio

| Codigo | Quando |
|--------|--------|
| `CATEGORIA_NOME_DUPLICADO` | Nome ja existe |
| `CATEGORIA_NAO_ENCONTRADA` | Busca com ID inexistente |

## Response Schema

```json
{
  "id": "uuid",
  "nome": "Eletronicos",
  "descricao": "Produtos eletronicos",
  "criado_em": "2026-04-05T10:00:00Z"
}
```

## Testes esperados (5)

```
test_criar_categoria
  POST /api/v1/categorias com token + dados validos → 201
  Response contem id (UUID), nome, descricao, criado_em

test_criar_categoria_duplicada
  POST duas vezes com mesmo nome → segunda retorna 409
  Response contem code: CATEGORIA_NOME_DUPLICADO

test_listar_categorias
  Criar 2 categorias → GET /api/v1/categorias → 200
  Response contem lista com 2 itens

test_buscar_categoria_por_id
  Criar categoria → GET /api/v1/categorias/{id} → 200
  Response contem dados corretos

test_buscar_categoria_inexistente
  GET /api/v1/categorias/{uuid-aleatorio} → 404
  Response contem code: CATEGORIA_NAO_ENCONTRADA
```

## Estrutura de arquivos esperada (monolito)

```
src/catalogo/
├── domain/
│   ├── entities/categoria.py        # Entidade Categoria
│   ├── exceptions/catalogo.py       # CategoriaNomeDuplicado, CategoriaNaoEncontrada
│   └── repositories/categoria_repository.py  # Interface ABC
├── application/
│   └── use_cases/
│       ├── criar_categoria.py
│       ├── listar_categorias.py
│       └── buscar_categoria.py
├── infrastructure/
│   └── repositories/
│       └── sqlalchemy_categoria_repository.py
├── container.py                     # CatalogoContainer (adicionar providers de categoria)
└── presentation/
    ├── routes.py                    # Rotas /api/v1/categorias
    └── schemas.py                   # Pydantic schemas
```

## Criterio de pronto

- [ ] 5 testes passam
- [ ] `radon cc src/catalogo/ -s -a` sem funcao acima de B
- [ ] `pytest --cov=src.catalogo` >= 70%
- [ ] Endpoints protegidos por JWT (401 sem token)
