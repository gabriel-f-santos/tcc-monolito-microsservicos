# Monolito — Produtos e Estoque

## Arquitetura

DDD (Domain-Driven Design) + Clean Architecture, **organizado por domínio**.

### Estrutura

```
src/
├── shared/          # BaseEntity, DomainException, BaseRepository, Settings, DB session
├── auth/            # BC: Autenticação (Usuario, JWT)
├── catalogo/        # BC: Catálogo de Produtos (Produto, Categoria, SKU, Dinheiro)
├── estoque/         # BC: Controle de Estoque (ItemEstoque, Movimentacao, Quantidade)
└── presentation/    # FastAPI app + health check
```

Cada módulo (auth, catalogo, estoque) tem: `domain/`, `application/`, `infrastructure/`, `container.py`, `presentation/`.

### Injeção de Dependência (dependency-injector)

- Cada BC tem um `container.py` com `DeclarativeContainer` — **Composition Root**
- É o ÚNICO arquivo que conhece implementações concretas (SQLAlchemy)
- Use Cases recebem repos via construtor (`providers.Factory`)
- Rotas usam `@inject` + `Provide[]` para receber use cases
- Testes usam `container.provider.override()` com repos in-memory
- **NÃO usar FastAPI Depends() para DI** — acopla ao framework
- Container é wired no startup do app via `container.wire(modules=[...])`

### Regras de Dependência

- `domain/` é Python puro — ZERO imports de framework
- `application/` depende apenas de interfaces do `domain/`
- `infrastructure/` implementa interfaces do `domain/` (SQLAlchemy)
- `container.py` conecta interfaces → implementações (único ponto de acoplamento)
- `presentation/` usa container, delega aos use cases
- **Import entre módulos PROIBIDO** — apenas `shared/` é compartilhado
- `catalogo/` NÃO importa de `estoque/` e vice-versa
- Comunicação entre BCs: in-process (chamada direta no use case, sem evento)

### Invariantes

- Regras de negócio DENTRO dos agregados (ex: `saldo >= 0` no ItemEstoque)
- Exceções de domínio (DomainException com code), não HTTPException
- Presentation mapeia exceções de domínio para status HTTP

## Stack

- Python 3.13 / FastAPI / SQLAlchemy 2 / PostgreSQL 16
- Testes: pytest + httpx (TestClient)
- Métricas: radon (CC/MI), xenon
- Docker: `docker compose up -d` para PostgreSQL

## Especificação

`docs/spec.md` — domínio, contratos de API, eventos, testes por feature. Siga rigorosamente.

## Comandos

```bash
source .venv/bin/activate
docker compose up -d              # PostgreSQL
uvicorn src.presentation.app:app  # Servidor local
pytest -v                         # Testes
radon cc src/ -s -a               # Complexidade ciclomática
radon mi src/ -s                  # Índice de manutenibilidade
radon cc src/catalogo/ -s -a      # CC por módulo
```

## Medição de Tempo (para o TCC)

Ao implementar uma feature, registre no final da resposta:
- Tempo estimado de raciocínio/execução
- Número de iterações até testes passarem
- `git diff --stat` da feature
