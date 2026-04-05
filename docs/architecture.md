# Arquitetura DDD e Clean Architecture

## Visao Geral

O sistema adota **Domain-Driven Design** (Evans, 2003) para modelagem e **Clean Architecture** (Martin, 2017) para estrutura de camadas. A mesma modelagem de dominio e aplicada em duas implantacoes distintas para comparacao.

---

## Bounded Contexts

O sistema possui dois Bounded Contexts claramente delimitados:

```
┌──────────────────────────┐           ┌──────────────────────────┐
│   CATALOGO DE PRODUTOS   │           │   CONTROLE DE ESTOQUE    │
│                          │  Evento   │                          │
│  Produto (Agregado)      │ ───────►  │  ItemEstoque (Agregado)  │
│    ├── SKU (VO)          │ Assinc.   │    ├── Saldo             │
│    ├── Dinheiro (VO)     │           │    └── Projecao local    │
│    └── Categoria (Ent.)  │           │  Movimentacao (Entidade) │
│                          │           │    ├── Quantidade (VO)   │
│  Usuario (Entidade)      │           │    └── TipoMovimentacao  │
│    └── Auth JWT          │           │                          │
└──────────────────────────┘           └──────────────────────────┘
        UPSTREAM                              DOWNSTREAM
     (publica eventos)                    (consome eventos)
```

**Regra fundamental:** O Estoque nunca chama o Catalogo. Toda comunicacao e via eventos de dominio (assincrono nos microsservicos, sincrono no monolito).

---

## Camadas (Clean Architecture)

Cada bounded context segue a mesma estrutura de 4 camadas:

```
src/
├── domain/              # Camada interna — ZERO dependencias externas
│   ├── entities/        # Agregados e entidades (classes Python puras)
│   ├── value_objects/   # Objetos de valor imutaveis (SKU, Dinheiro, Quantidade)
│   ├── repositories/    # Interfaces abstratas (ABC) — nao implementacoes
│   ├── events/          # Eventos de dominio (dataclasses)
│   └── exceptions/      # Excecoes de dominio com codigos da spec
│
├── application/         # Casos de uso — orquestram dominio e repositorios
│   ├── use_cases/       # Um arquivo por caso de uso (CriarProduto, RegistrarSaida)
│   └── dtos/            # Data Transfer Objects (entrada/saida dos use cases)
│
├── infrastructure/      # Implementacoes concretas — depende de frameworks
│   ├── repositories/    # SQLAlchemy (monolito) ou boto3/DynamoDB (microsservicos)
│   ├── database/        # Engine, sessao, conexao
│   └── config/          # Settings via env vars (pydantic-settings ou os.environ)
│
└── presentation/        # Camada externa — recebe requisicoes
    ├── routes/          # FastAPI routes (monolito)
    ├── handlers/        # Lambda handlers puros (microsservicos)
    └── schemas/         # Schemas de request/response (Pydantic)
```

### Direcao da Dependencia

```
Presentation ──► Application ──► Domain ◄── Infrastructure
   (rotas)        (use cases)    (puro)     (repos concretos)
```

- **Domain** nao importa nada de fora. E Python puro.
- **Application** depende apenas de interfaces do Domain.
- **Infrastructure** implementa interfaces do Domain (inversao de dependencia).
- **Presentation** chama Use Cases e mapeia excecoes de dominio para HTTP.

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

## Apresentacao — A Outra Prova

O mesmo Use Case e chamado de formas diferentes:

### Monolito (FastAPI Route)

```python
@router.post("/api/v1/produtos")
def criar_produto(body: CriarProdutoRequest, session = Depends(get_session)):
    repo = SQLAlchemyProdutoRepository(session)
    use_case = CriarProdutoUseCase(repo)
    return use_case.execute(body.to_dto())
```

### Microsservico (Lambda Handler puro — sem FastAPI, sem Mangum)

```python
def handler(event, context):
    body = json.loads(event["body"])
    repo = DynamoDBProdutoRepository(os.environ["PRODUTOS_TABLE"])
    use_case = CriarProdutoUseCase(repo)
    result = use_case.execute(CriarProdutoDTO(**body))
    return {"statusCode": 201, "body": json.dumps(result.to_dict())}
```

**Ponto chave para o artigo:** As camadas de Domain e Application sao identicas. Apenas Presentation e Infrastructure mudam.

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
| Lambda | 3 funcoes (512MB, Python 3.13) | X-Ray ativo |
| DynamoDB | 5 tabelas (PAY_PER_REQUEST) | usuarios, produtos, categorias, itens-estoque, movimentacoes |
| SNS | 1 topico (prod-eventos-dominio) | Fan-out |
| SQS | 1 fila (prod-estoque-eventos) | Visibility 60s |

### Endpoints ao Vivo

| Servico | URL |
|---------|-----|
| Monolito | http://tcc-monolito-alb-1189235770.us-east-1.elb.amazonaws.com |
| Catalogo | https://odkl9vxtd0.execute-api.us-east-1.amazonaws.com/Prod/catalogo |
| Estoque | https://odkl9vxtd0.execute-api.us-east-1.amazonaws.com/Prod/estoque |
