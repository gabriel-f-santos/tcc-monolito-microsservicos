---
name: ddd-review
description: Use when reviewing Python code for DDD compliance, Clean Architecture violations, coupling between bounded contexts, or aggregate boundary issues. Triggers on code review requests involving domain modeling.
---

# DDD and Clean Architecture Review Checklist

## Overview

Checklist for reviewing code against Domain-Driven Design and Clean Architecture principles as defined in this project's `docs/spec.md`.

## Review Checklist

### 1. Layer Separation (Clean Architecture)

- [ ] **Domain layer has ZERO imports from infrastructure or presentation**
  - No SQLAlchemy, boto3, FastAPI, or framework imports in `domain/`
  - Repository interfaces defined in domain as abstract classes
- [ ] **Application layer (use cases) depends only on domain interfaces**
  - Use cases receive repositories via constructor injection
  - No direct database calls in use cases
- [ ] **Infrastructure implements domain interfaces**
  - `infrastructure/repositories/` implements interfaces from `domain/repositories/`
  - Framework-specific code stays in infrastructure
- [ ] **Presentation layer only calls use cases**
  - FastAPI routes or Lambda handlers delegate to use cases immediately
  - No business logic in routes/handlers

### 2. Aggregate Boundaries

- [ ] **Each aggregate has a single root entity**
  - Produto is root of Catalogo aggregate
  - ItemEstoque is root of Estoque aggregate
- [ ] **Value Objects are immutable**
  - SKU, Dinheiro, TipoMovimentacao, Quantidade have no setters
  - Equality by value, not by identity
- [ ] **Invariants enforced inside the aggregate**
  - Saldo >= 0 checked inside ItemEstoque, not in use case or route
  - Preco > 0 checked inside Produto or Dinheiro VO

### 3. Bounded Context Independence

- [ ] **ZERO sync calls between Catalogo and Estoque**
  - No HTTP calls, no shared database, no direct imports
- [ ] **Estoque does NOT import from Catalogo domain**
  - Estoque has its own projecao local (sku, nome_produto, categoria_nome)
  - Data comes exclusively via domain events
- [ ] **Events are the only communication**
  - ProdutoCriado, ProdutoAtualizado, ProdutoDesativado published by Catalogo
  - Consumed by Estoque to maintain local projection
- [ ] **Events are idempotent**
  - Processing same event twice has no side effect

### 4. Repository Pattern

- [ ] **Interface in domain, implementation in infrastructure**
  - `domain/repositories/produto_repository.py` = abstract class
  - `infrastructure/repositories/sqlalchemy_produto_repository.py` = implementation
- [ ] **Same interface for both PostgreSQL and DynamoDB**
  - Method signatures identical
  - Only internal implementation differs
- [ ] **No ORM/database leakage into domain**
  - Domain entities are plain Python classes, not ORM models
  - Mapping between ORM model and domain entity happens in repository

### 5. Dependency Injection (Container)

- [ ] **Each BC has a `container.py`**
  - It is the ONLY file that imports from infrastructure
  - Creates concrete repos and injects into use cases
- [ ] **Use Cases receive repos via constructor**
  - `def __init__(self, repo: ProdutoRepository)` — interface, not implementation
  - NEVER `from infrastructure.repositories import ...` in use case
- [ ] **Presentation uses container, not direct instantiation**
  - `container.criar_produto_use_case()` — not `CriarProdutoUseCase(SQLAlchemyRepo(...))`
- [ ] **No FastAPI Depends() for DI**
  - `Depends()` couples DI to the framework
  - Container is plain Python, works in FastAPI and Lambda
- [ ] **Tests use fake container**
  - `FakeContainer` with in-memory repos, no DB needed

### 6. Domain Events

- [ ] **Events are simple data classes**
  - No logic, no methods beyond serialization
  - Contain only primitive types and timestamps
- [ ] **Published after successful persistence**
  - Use case: save entity first, then publish event
  - Never publish event if save failed
- [ ] **Event names use past tense**
  - ProdutoCriado (not CriarProduto), EstoqueMovimentado (not MovimentarEstoque)

### 6. Domain Errors

- [ ] **Domain exceptions, not HTTP exceptions**
  - `ProdutoNaoEncontrado`, not `HTTPException(404)`
  - Presentation layer maps domain exceptions to HTTP status codes
- [ ] **Specific error codes from spec**
  - Use codes from `docs/spec.md` section 6

## Red Flags

| Smell | Problem | Fix |
|-------|---------|-----|
| `from infrastructure import` in domain/ | Layer violation | Invert dependency with interface |
| `from infrastructure import` in use case | DI violation | Use constructor injection via container |
| `Depends()` for use case/repo creation | Framework coupling | Use container.py instead |
| `import requests` or `httpx` in use case | Sync coupling | Use event via SNS/SQS |
| Business rule in route/handler | Logic leak | Move to aggregate or use case |
| `session.query()` in use case | ORM leak | Use repository interface |
| Estoque importing Produto entity | BC coupling | Use local projection |
| `if saldo < quantidade` outside aggregate | Invariant leak | Move check into ItemEstoque |
| Use case instantiating repo directly | Missing DI | Wire via container.py |
