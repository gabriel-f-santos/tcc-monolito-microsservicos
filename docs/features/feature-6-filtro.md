# Feature 6: Filtro de Estoque por Categoria

## Contexto

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias (violacoes sao CRITICAL)
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Pre-requisito: Features 0-4 ja implementadas (e Feature 5 nos microsservicos).

**Esta e uma feature transversal** — toca os dois Bounded Contexts. O ponto chave e que o Estoque filtra usando sua **projecao local** (campo `categoria_nome`), sem consultar o Catalogo. Zero acoplamento.

## O que implementar

Adicionar filtro por categoria no endpoint de listagem de estoque.

## Endpoint afetado

| Metodo | Endpoint | Query Param novo | Response |
|--------|----------|-----------------|----------|
| GET | `/api/v1/estoque` | `?categoria=Eletronicos` | `200` + Lista filtrada |

## Regras de negocio

1. Filtro por categoria usa o campo `categoria_nome` do ItemEstoque (projecao local)
2. Nao faz query no Catalogo (zero acoplamento entre BCs)
3. Filtro case-insensitive
4. Categoria inexistente retorna lista vazia (nao erro)
5. Sem filtro retorna todos os itens

## Testes esperados (2)

```
test_filtrar_estoque_por_categoria
  Criar 2 categorias (A, B) + 3 produtos (2 na A, 1 na B) + entrada em todos
  GET /api/v1/estoque?categoria=A → retorna 2 itens
  GET /api/v1/estoque?categoria=B → retorna 1 item

test_filtrar_estoque_categoria_inexistente
  GET /api/v1/estoque?categoria=ZZZ → 200, lista vazia
```

## Arquivos a modificar (monolito)

```
src/estoque/
├── domain/repositories/item_estoque_repository.py  # Adicionar filtro categoria no list
├── infrastructure/repositories/
│   └── sqlalchemy_item_estoque_repository.py       # Implementar filtro SQL
├── application/use_cases/listar_itens.py           # Aceitar param categoria
└── presentation/
    ├── routes.py                                   # Adicionar query param
    └── schemas.py                                  # Atualizar se necessario
```

## Criterio de pronto

- [ ] 2 testes passam
- [ ] Filtro usa projecao local (campo `categoria_nome` no ItemEstoque)
- [ ] ZERO import de `src.catalogo` em `src.estoque`
- [ ] Endpoints protegidos por JWT
