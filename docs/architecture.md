# Arquitetura DDD e Clean Architecture

## Visao Geral

O sistema adota **Domain-Driven Design** (Evans, 2003) para modelagem e **Clean Architecture** (Martin, 2017) para estrutura de camadas. A mesma modelagem de dominio e aplicada em duas implantacoes distintas para comparacao.

---

## Bounded Contexts

O sistema possui tres Bounded Contexts:

```
┌──────────────────┐
│   AUTENTICACAO   │   JWT stateless — cada servico valida independente
│                  │   Monolito: middleware FastAPI
│  Usuario (Ent.)  │   Microsservicos: Lambda Authorizer (cache 300s)
└──────────────────┘

┌──────────────────────────┐           ┌──────────────────────────┐
│   CATALOGO DE PRODUTOS   │           │   CONTROLE DE ESTOQUE    │
│                          │  Evento   │                          │
│  Produto (Agregado)      │ ───────►  │  ItemEstoque (Agregado)  │
│    ├── SKU (VO)          │ Assinc.   │    ├── Saldo             │
│    ├── Dinheiro (VO)     │           │    └── Projecao local    │
│    └── Categoria (Ent.)  │           │  Movimentacao (Entidade) │
│                          │           │    ├── Quantidade (VO)   │
│                          │           │    └── TipoMovimentacao  │
└──────────────────────────┘           └──────────────────────────┘
        UPSTREAM                              DOWNSTREAM
     (publica eventos)                    (consome eventos)
```

**Regras fundamentais:**
- O Estoque nunca chama o Catalogo — comunicacao via eventos (assincrono nos microsservicos, sincrono no monolito)
- Auth e independente — JWT e stateless, nenhum servico chama o auth-service para validar token
- Cada BC mapeia 1:1 para um microsservico (auth-service, catalogo-service, estoque-service)

---

## Camadas (Clean Architecture)

Cada bounded context segue a mesma estrutura de 4 camadas:

### Monolito — Organizacao por Dominio

```
monolito/src/
├── shared/                        # Codigo compartilhado entre modulos
│   ├── domain/
│   │   ├── entities/base.py       # BaseEntity (UUID + timestamps)
│   │   ├── exceptions/base.py     # DomainException (code + message)
│   │   └── repositories/base.py   # BaseRepository ABC (get, save, delete)
│   └── infrastructure/
│       ├── config/settings.py     # pydantic-settings (DATABASE_URL, JWT_SECRET)
│       ├── database/session.py    # SQLAlchemy engine + session
│       └── observability.py       # OpenTelemetry setup
│
├── auth/                          # Bounded Context: Autenticacao
│   ├── domain/                    # Usuario entity, excecoes de auth
│   ├── application/               # Login, Registrar use cases
│   ├── infrastructure/            # UsuarioRepository (SQLAlchemy)
│   ├── container.py               # Composition Root — conecta interfaces a implementacoes
│   └── presentation/              # Rotas /api/v1/auth/*, middleware JWT
│
├── catalogo/                      # Bounded Context: Catalogo de Produtos
│   ├── domain/                    # Produto, Categoria, SKU, Dinheiro
│   ├── application/               # CriarProduto, AtualizarProduto, etc.
│   ├── infrastructure/            # ProdutoRepository, CategoriaRepository
│   ├── container.py               # Composition Root
│   └── presentation/              # Rotas /api/v1/produtos, /categorias
│
├── estoque/                       # Bounded Context: Controle de Estoque
│   ├── domain/                    # ItemEstoque, Movimentacao, Quantidade
│   ├── application/               # RegistrarEntrada, RegistrarSaida
│   ├── infrastructure/            # ItemEstoqueRepository, MovimentacaoRepository
│   ├── container.py               # Composition Root
│   └── presentation/              # Rotas /api/v1/estoque/*
│
└── presentation/
    ├── app.py                     # FastAPI app (compoe routers de todos os modulos)
    └── routes/health.py           # GET /health (transversal)
```

**Vantagem da organizacao por dominio:**
- Cada pasta e um Bounded Context autocontido
- Extrair para microsservico = copiar a pasta
- Import entre modulos e explicito (fronteira fisica no filesystem)
- Metricas por modulo: `radon cc src/catalogo/ -s -a`

### Microsservicos — Cada Servico e um Bounded Context

```
microsservicos/
├── auth-service/src/              # BC: Autenticacao
│   ├── shared/domain/             # BaseEntity, DomainException, BaseRepository
│   ├── domain/                    # Usuario
│   ├── application/               # Login, Registrar use cases
│   ├── infrastructure/            # DynamoDB repos (boto3)
│   └── presentation/handlers/     # Lambda handlers + Lambda Authorizer
│
├── catalogo-service/src/          # BC: Catalogo de Produtos
│   ├── shared/domain/             # BaseEntity, DomainException, BaseRepository
│   ├── domain/                    # Produto, Categoria, SKU, Dinheiro
│   ├── application/               # Use cases (identicos ao monolito)
│   ├── infrastructure/            # DynamoDB repos (boto3)
│   └── presentation/handlers/     # Lambda handlers puros
│
└── estoque-service/src/           # BC: Controle de Estoque
    ├── shared/domain/             # BaseEntity, DomainException, BaseRepository
    ├── domain/                    # ItemEstoque, Movimentacao, Quantidade
    ├── application/               # Use cases (identicos ao monolito)
    ├── infrastructure/            # DynamoDB repos (boto3)
    └── presentation/handlers/     # Lambda handlers puros + event consumer
```

### Direcao da Dependencia (dentro de cada modulo)

```
presentation/ ──► application/ ──► domain/ ◄── infrastructure/
   (rotas)        (use cases)      (puro)      (repos concretos)
```

- **domain/** nao importa nada de fora. E Python puro. Apenas herda de `shared/`.
- **application/** depende apenas de interfaces do domain/.
- **infrastructure/** implementa interfaces do domain/ (inversao de dependencia).
- **presentation/** chama Use Cases e mapeia excecoes de dominio para HTTP.

### Regra de Import entre Modulos

```
auth/       → shared/ (apenas)
catalogo/   → shared/ (apenas)
estoque/    → shared/ (apenas)
catalogo/ ✗ estoque/  (PROIBIDO — comunicacao via eventos)
estoque/  ✗ catalogo/ (PROIBIDO — usa projecao local)
```

---

## Repository Pattern — A Prova da Arquitetura

O mesmo caso de uso funciona com dois bancos diferentes sem alteracao:

### Interface (Domain — igual nos dois)

```python
class ProdutoRepository(ABC):
    @abstractmethod
    def get_by_id(self, produto_id: UUID) -> Produto | None: ...

    @abstractmethod
    def save(self, produto: Produto) -> Produto: ...

    @abstractmethod
    def list_all(self, filtros: dict) -> list[Produto]: ...
```

### Implementacao Monolito (Infrastructure — SQLAlchemy)

```python
class SQLAlchemyProdutoRepository(ProdutoRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, produto: Produto) -> Produto:
        model = ProdutoModel.from_domain(produto)
        self.session.add(model)
        self.session.commit()
        return model.to_domain()
```

### Implementacao Microsservicos (Infrastructure — DynamoDB)

```python
class DynamoDBProdutoRepository(ProdutoRepository):
    def __init__(self, table_name: str):
        self.table = boto3.resource('dynamodb').Table(table_name)

    def save(self, produto: Produto) -> Produto:
        self.table.put_item(Item=produto.to_dict())
        return produto
```

### Use Case (Application — identico nos dois)

```python
class CriarProdutoUseCase:
    def __init__(self, repo: ProdutoRepository):  # recebe interface, nao implementacao
        self.repo = repo

    def execute(self, dados: CriarProdutoDTO) -> Produto:
        produto = Produto.criar(...)  # dominio valida
        return self.repo.save(produto)  # persiste via interface
```

---

## Injecao de Dependencia — Composition Root

### Problema

Use Cases dependem de interfaces (Repository). Alguem precisa decidir qual implementacao concreta usar (SQLAlchemy ou DynamoDB). Onde colocar essa decisao?

**Errado:** no Use Case (acoplaria ao framework)
**Errado:** no FastAPI `Depends()` (acoplaria a composicao ao framework — violacao de Clean Architecture)
**Correto:** em um **Composition Root** (container) por Bounded Context

### Padrao: Container Manual

Cada BC tem um `container.py` que e o **unico arquivo que conhece implementacoes concretas**. Domain e Application nunca importam de Infrastructure diretamente.

```
domain/         → Python puro (interfaces)
application/    → Python puro (usa interfaces via construtor)
infrastructure/ → Implementa interfaces
container.py    → UNICO lugar que conecta interface → implementacao
presentation/   → Usa container para obter use cases prontos
```

### Monolito — Container com SQLAlchemy

```python
# src/catalogo/container.py
class CatalogoContainer:
    """Composition Root do BC Catalogo.
    Unico lugar que sabe que ProdutoRepository = SQLAlchemy."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def produto_repository(self) -> ProdutoRepository:
        return SQLAlchemyProdutoRepository(self._session_factory())

    def categoria_repository(self) -> CategoriaRepository:
        return SQLAlchemyCategoriaRepository(self._session_factory())

    def criar_produto_use_case(self) -> CriarProdutoUseCase:
        return CriarProdutoUseCase(repo=self.produto_repository())
```

```python
# src/catalogo/presentation/routes.py
# A rota NAO sabe qual implementacao de repo esta usando
@router.post("/api/v1/produtos")
def criar_produto(body: CriarProdutoRequest):
    use_case = container.criar_produto_use_case()
    return use_case.execute(body.to_dto())
```

### Microsservicos — Container com DynamoDB

```python
# catalogo-service/src/container.py
class CatalogoContainer:
    """Mesmo contrato, implementacao diferente."""

    def produto_repository(self) -> ProdutoRepository:
        return DynamoDBProdutoRepository(os.environ["PRODUTOS_TABLE"])

    def criar_produto_use_case(self) -> CriarProdutoUseCase:
        return CriarProdutoUseCase(repo=self.produto_repository())
```

```python
# catalogo-service/src/presentation/handlers/catalogo.py
def handler(event, context):
    body = json.loads(event["body"])
    use_case = container.criar_produto_use_case()
    result = use_case.execute(CriarProdutoDTO(**body))
    return {"statusCode": 201, "body": json.dumps(result.to_dict())}
```

### Testes — Container com Fake/InMemory

```python
# tests/conftest.py
class FakeCatalogoContainer:
    def produto_repository(self):
        return InMemoryProdutoRepository()

    def criar_produto_use_case(self):
        return CriarProdutoUseCase(repo=self.produto_repository())

# Injeta o container fake antes dos testes
app.state.catalogo_container = FakeCatalogoContainer()
```

### Por que NAO usar FastAPI Depends()

| Aspecto | `Depends()` | Container manual |
|---------|-------------|-----------------|
| Acoplamento ao framework | Sim — DI vive no FastAPI | Nao — container e Python puro |
| Lambda handlers | Nao funciona (sem FastAPI) | Funciona igual |
| Testabilidade | `dependency_overrides` (API do FastAPI) | Trocar container (Python puro) |
| Clean Architecture | Viola — framework controla composicao | Respeita — composicao e independente |
| Para o artigo | Superficial | Demonstra inversao de dependencia real |

**Ponto chave:** O Use Case nao sabe se esta rodando no FastAPI ou Lambda, nao sabe se o banco e PostgreSQL ou DynamoDB. O container e o unico ponto que sabe. Isso e Clean Architecture de verdade.

### Fluxo de Dependencia Completo

```
presentation/routes.py          presentation/handlers/catalogo.py
         │                                   │
         ▼                                   ▼
    container.py (SQLAlchemy)          container.py (DynamoDB)
         │                                   │
         ▼                                   ▼
    CriarProdutoUseCase ◄──── IDENTICO ────► CriarProdutoUseCase
         │                                   │
         ▼                                   ▼
    ProdutoRepository (interface)      ProdutoRepository (interface)
         │                                   │
         ▼                                   ▼
    SQLAlchemyProdutoRepo            DynamoDBProdutoRepo
         │                                   │
         ▼                                   ▼
    PostgreSQL                         DynamoDB
```

---

## Comunicacao entre Bounded Contexts

### Monolito: Sincrona (in-process)

Ao criar um Produto, o mesmo Use Case cria o ItemEstoque diretamente:

```python
class CriarProdutoUseCase:
    def __init__(self, produto_repo, item_estoque_repo):
        ...
    def execute(self, dados):
        produto = Produto.criar(...)
        self.produto_repo.save(produto)
        # Chamada direta — mesmo processo, mesmo banco
        item = ItemEstoque.criar_para_produto(produto)
        self.item_estoque_repo.save(item)
```

### Microsservicos: Assincrona (SNS → SQS → Lambda)

```
CriarProdutoUseCase → SNS (ProdutoCriado) → SQS → Lambda Consumer → CriarItemEstoqueUseCase
```

- Consistencia eventual (delay de ~100ms a ~2s)
- Idempotente (reprocessar o mesmo evento nao duplica)
- Resiliente (se Estoque esta fora, SQS retenta automaticamente)
- Desacoplado (Catalogo nao sabe que Estoque existe)

---

## Invariantes de Dominio

Regras de negocio ficam **dentro dos agregados**, nao nos use cases:

```python
@dataclass
class ItemEstoque:
    saldo: int = 0

    def registrar_saida(self, quantidade: int) -> Movimentacao:
        if quantidade <= 0:
            raise QuantidadeInvalida()
        if self.saldo < quantidade:
            raise EstoqueInsuficiente(saldo_atual=self.saldo, solicitado=quantidade)
        self.saldo -= quantidade
        return Movimentacao(tipo=TipoMovimentacao.SAIDA, quantidade=quantidade)
```

O Use Case nao valida o saldo — apenas chama `item.registrar_saida()` e o agregado protege sua propria invariante.

---

## Diagramas

| Arquivo | Tipo | Descricao |
|---------|------|-----------|
| `c4-context.puml` | C4 Nivel 1 | Sistema completo: operador, monolito, microsservicos, Grafana |
| `c4-container-monolith.puml` | C4 Nivel 2 | ALB → Docker → camadas DDD → PostgreSQL |
| `c4-container-microservices.puml` | C4 Nivel 2 | API GW → Lambdas → camadas DDD → DynamoDB + SNS/SQS |
| `sequence-create-product-monolith.puml` | Sequencia | Criar produto no monolito (sincrono) |
| `sequence-create-product-microservices.puml` | Sequencia | Criar produto nos microsservicos (assincrono) |
| `sequence-stock-exit.puml` | Sequencia | Saida de estoque com invariante de saldo |

Gerar imagens: `plantuml docs/diagrams/*.puml`

---

## CI/CD — Tempos Medidos

GitHub Actions mede automaticamente o tempo de cada job. Dados do ultimo deploy bem-sucedido:

### Monolito (push → ALB respondendo)

| Job | Duracao |
|-----|---------|
| Test & Quality (pytest + radon + xenon) | 23s |
| Build & Deploy (Docker + ECR + Instance Refresh) | 6min 51s |
| **Total push-to-live** | **~7min 14s** |

### Microsservicos (push → API Gateway respondendo)

| Job | Duracao |
|-----|---------|
| Test & Quality (pytest + radon + xenon) | 11s |
| SAM Build & Deploy | 17s |
| **Total push-to-live** | **~28s** |

**Insight para o artigo:** Deploy serverless e ~15x mais rapido que deploy em EC2/ASG. O Instance Refresh (rolling) do ASG domina o tempo do monolito (espera instancia nova ficar healthy).

---

## Infraestrutura Atual

### Monolito

| Recurso | Tipo | Config |
|---------|------|--------|
| ALB | Application Load Balancer | HTTP :80, health check /health |
| EC2 | t3.micro (1GB, ASG 1-2) | Docker container com 512MB limit |
| RDS | db.t4g.micro (PostgreSQL 16) | Subnet privada, SG restritivo |
| ECR | tcc-monolito | Ultimas 5 imagens |

### Microsservicos

| Recurso | Tipo | Config |
|---------|------|--------|
| API Gateway | REST | /catalogo/* e /estoque/* |
| Lambda | ~8 funcoes (512MB, Python 3.13) + 1 authorizer (256MB) | X-Ray ativo |
| DynamoDB | 5 tabelas (PAY_PER_REQUEST) | usuarios, produtos, categorias, itens-estoque, movimentacoes |
| SNS | 1 topico (prod-eventos-dominio) | Fan-out |
| SQS | 1 fila (prod-estoque-eventos) | Visibility 60s |

### Endpoints ao Vivo

| Servico | URL |
|---------|-----|
| Monolito | http://tcc-monolito-alb-1189235770.us-east-1.elb.amazonaws.com |
| Catalogo | https://odkl9vxtd0.execute-api.us-east-1.amazonaws.com/Prod/catalogo |
| Estoque | https://odkl9vxtd0.execute-api.us-east-1.amazonaws.com/Prod/estoque |
