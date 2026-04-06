# Regras Obrigatorias para Implementacao

Leia ANTES de implementar qualquer feature. Violacoes destas regras sao CRITICAL.

## Camadas — O que pode importar o que

```
domain/         → Python puro. ZERO imports de libs externas. ZERO imports de outros BCs.
application/    → Apenas interfaces do domain/. ZERO imports de libs externas. ZERO imports de outros BCs.
infrastructure/ → Implementa interfaces. UNICA camada que importa libs (SQLAlchemy, bcrypt, jose, boto3).
container.py    → Conecta interfaces → implementacoes. Importa APENAS do PROPRIO BC.
presentation/   → Usa container. Delega aos use cases.
app.py          → UNICO arquivo que conhece TODOS os containers e faz wiring cross-BC.
```

**PROIBIDO em domain/ e application/:**
- `import bcrypt`
- `from jose import jwt`
- `import boto3`
- `from sqlalchemy import ...`
- `from fastapi import ...`
- `from src.estoque import ...` (em catalogo)
- `from src.catalogo import ...` (em estoque)
- Qualquer import de lib externa ou de outro BC

**PROIBIDO em container.py:**
- Imports de OUTRO BC (ex: `from src.estoque.infrastructure import ...` em catalogo/container.py)
- Se precisa de servico cross-BC, receber como `providers.Dependency()` — wiring feito no app.py

## Servicos Externos

Se um use case precisa de hash, JWT, email, HTTP, fila:
1. Criar **interface ABC** em `domain/services/nome_servico.py`
2. Criar **implementacao** em `infrastructure/services/nome_concreto.py`
3. Registrar como `providers.Singleton` no `container.py`
4. Injetar no use case via construtor

## Comunicacao entre Bounded Contexts

- **PROIBIDO** importar de outro BC em domain/, application/ ou container.py
- Se um use case precisa chamar outro BC:
  1. Criar **interface ABC** em `domain/services/` do BC CHAMADOR (ex: `catalogo/domain/services/estoque_service.py`)
  2. Criar **implementacao** no BC CHAMADO (ex: `estoque/infrastructure/services/estoque_service_impl.py`)
  3. A implementacao pode importar do proprio BC (estoque importa de estoque)
  4. O container do BC CHAMADOR recebe o servico como `providers.Dependency()`
  5. **app.py** faz a wiring: instancia a implementacao e injeta no container do chamador
- No monolito: implementacao in-process (app.py wires)
- Nos microsservicos: implementacao via evento (SNS/SQS)

```python
# EXEMPLO CORRETO de cross-BC wiring:

# catalogo/domain/services/estoque_service.py (INTERFACE — Python puro)
class EstoqueService(ABC):
    def inicializar_item(self, produto_id: UUID) -> None: ...

# estoque/infrastructure/services/estoque_service_impl.py (IMPLEMENTACAO — no BC que possui a logica)
class EstoqueServiceImpl(EstoqueService):
    def __init__(self, item_estoque_repo: ItemEstoqueRepository): ...

# catalogo/container.py (recebe como Dependency, NAO importa de estoque)
class CatalogoContainer(DeclarativeContainer):
    estoque_service = providers.Dependency()  # injetado externamente

# app.py (UNICO que conhece os dois BCs)
estoque_container = EstoqueContainer(session_factory=SessionLocal)
_estoque_service = EstoqueServiceImpl(item_estoque_repo=estoque_container.item_estoque_repository())
catalogo_container = CatalogoContainer(session_factory=SessionLocal, estoque_service=_estoque_service)
```

## Entidades e Agregados

- Toda entidade DEVE ter `__post_init__` validando campos obrigatorios
- `__post_init__` DEVE chamar `super().__post_init__()` como primeira linha (incondicional, sem hasattr)
- NUNCA defaults vazios sem validacao (`str = ""` sem check no `__post_init__`)
- Campos opcionais: usar `str | None = None` (nao `str = ""`)
- **Mutacao de estado DENTRO do agregado** — use case NUNCA muta campos diretamente
  - CORRETO: `produto.atualizar(nome=novo_nome)` — agregado valida internamente e atualiza `atualizado_em`
  - ERRADO: `produto.nome = novo_nome` no use case
  - ERRADO: `produto.atualizado_em = datetime.now()` no use case
- Value Objects: `@dataclass(frozen=True)` — imutaveis
- Ao criar Movimentacao/entidade filha dentro do agregado, usar uma unica chamada `datetime.now()` para `criado_em` e `atualizado_em`

## Codigos de Excecao

- DEVEM ser **UNICOS** em todo o sistema
- DEVEM ser **prefixados pelo BC**: `PRODUTO_*`, `CATEGORIA_*`, `ESTOQUE_*`, `AUTH_*`
- NUNCA usar codigos genericos: `NOME_OBRIGATORIO`, `QUANTIDADE_INVALIDA`, `ITEM_NAO_ENCONTRADO`
- SEMPRE usar codigos scopados: `PRODUTO_NOME_OBRIGATORIO`, `ESTOQUE_QUANTIDADE_INVALIDA`, `ESTOQUE_ITEM_NAO_ENCONTRADO`
- Usar exception class do BC (`from src.estoque.domain.exceptions.estoque import QuantidadeInvalida`) em vez de inline `DomainException("QUANTIDADE_INVALIDA", ...)`
- NUNCA definir o mesmo codigo em mais de um arquivo
- Todos os codigos DEVEM estar mapeados no `DOMAIN_STATUS_MAP` em `app.py`

## SQLAlchemy (Infrastructure)

- Usar API moderna SQLAlchemy 2: `select()` + `session.execute()` + `.scalar_one_or_none()` / `.scalars().all()`
- NUNCA usar `session.query()` (API legada 1.x, deprecated)
- Todos os Models herdam de `src.shared.infrastructure.database.base.Base` (Base compartilhado)
- NUNCA criar `registry()` ou `Base` local por BC
- `conftest.py` usa `Base.metadata.create_all()` unico para todas as tabelas

## Container (dependency-injector)

- `providers.Singleton` para repos e servicos (stateless, reutilizaveis)
- `providers.Factory` para use cases (stateless por chamada)
- `wiring_config` no container (nao `wire()` manual no app.py)
- Cross-BC: usar `providers.Dependency()` — NUNCA importar de outro BC no container
- Testes: `container.provider.override()` com fakes

## Testes

- Testes de integracao via TestClient (monolito) ou handler direto (Lambda)
- Cada feature deve ter >= 70% cobertura no modulo
- `radon cc` sem funcao acima de B
- Codigos de erro nos asserts devem usar os codigos scopados (ex: `ESTOQUE_ITEM_NAO_ENCONTRADO`)
