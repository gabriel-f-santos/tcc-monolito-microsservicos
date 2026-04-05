# Monolito — Produtos e Estoque

## Arquitetura

Este projeto segue **DDD** (Domain-Driven Design) e **Clean Architecture**.

### Camadas (direção da dependência: presentation → application → domain ← infrastructure)

- `src/domain/` — Agregados, Entidades, Value Objects, interfaces de Repository, exceções de domínio. **ZERO imports de framework**.
- `src/application/` — Casos de uso. Dependem apenas de interfaces do domínio. Recebem repositórios via construtor.
- `src/infrastructure/` — Implementações de repositório (SQLAlchemy/PostgreSQL), configuração, banco de dados.
- `src/presentation/` — Rotas FastAPI. Apenas delegam aos casos de uso.

### Regras

- Domínio nunca importa de infrastructure ou presentation
- Invariantes de negócio ficam dentro dos agregados (ex: saldo >= 0 no ItemEstoque)
- Exceções são de domínio (DomainException com code), não HTTPException
- Presentation mapeia exceções de domínio para status HTTP
- Repository Pattern: interface abstrata no domínio, implementação concreta na infraestrutura
- Comunicação entre Bounded Contexts (Catálogo e Estoque): apenas eventos assíncronos

## Stack

- Python 3.13 / FastAPI / SQLAlchemy 2 / PostgreSQL 16
- Testes: pytest + httpx (TestClient)
- Métricas: radon (CC), radon (MI), xenon
- Docker: `docker compose up -d` para PostgreSQL

## Especificação

O domínio, contratos de API e eventos estão em `docs/spec.md`. Siga rigorosamente.

## Comandos

```bash
source .venv/bin/activate
docker compose up -d              # PostgreSQL
uvicorn src.presentation.app:app  # Servidor local
pytest -v                         # Testes
radon cc src/ -s -a               # Complexidade ciclomática
radon mi src/ -s                  # Índice de manutenibilidade
```

## Medição de Tempo (para o TCC)

Ao implementar uma feature, registre no final da resposta:
- Tempo estimado de raciocínio/execução
- Número de iterações até testes passarem
- `git diff --stat` da feature
