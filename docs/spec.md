# Especificação de Domínio — Sistema de Gerenciamento de Produtos e Estoque

## 1. Linguagem Ubíqua (Glossário)

| Termo | Definição | Contexto |
|-------|-----------|----------|
| **Produto** | Item catalogado para venda ou uso, identificado por um SKU único | Catálogo |
| **SKU** | Stock Keeping Unit — código alfanumérico único que identifica um produto | Catálogo |
| **Categoria** | Classificação que agrupa produtos por tipo (ex: Eletrônicos, Alimentos) | Catálogo |
| **Item de Estoque** | Representação de um produto dentro do contexto de estoque, com saldo e rastreabilidade | Estoque |
| **Movimentação** | Registro de entrada ou saída de quantidade de um item no estoque | Estoque |
| **Entrada** | Movimentação que incrementa o saldo (recebimento de mercadoria, devolução) | Estoque |
| **Saída** | Movimentação que decrementa o saldo (venda, consumo, perda) | Estoque |
| **Saldo** | Quantidade atual disponível de um item de estoque | Estoque |
| **Lote** | Identificador opcional que agrupa uma entrada específica (ex: nota fiscal, fornecedor) | Estoque |
| **Usuário** | Pessoa autenticada que opera o sistema, identificada por email | Autenticação |
| **Token** | JWT que comprova a identidade do usuário em cada requisição | Autenticação |

---

## 2. Bounded Contexts

### 2.1 Catálogo de Produtos

**Responsabilidade:** Gerenciar o ciclo de vida dos produtos — criação, atualização, categorização e consulta.

**O que NÃO faz:** Não sabe nada sobre quantidades, movimentações ou saldos. Não conhece o conceito de estoque.

### 2.2 Controle de Estoque

**Responsabilidade:** Rastrear quantidades, registrar movimentações (entradas e saídas) e manter o saldo atualizado.

**O que NÃO faz:** Não cria nem edita produtos. Mantém apenas uma **projeção local** com os dados mínimos que precisa (SKU, nome) — recebidos via evento.

### 2.3 Mapa de Contextos

```
┌─────────────────────┐         Evento Assíncrono          ┌─────────────────────┐
│                     │  ProdutoCriado / ProdutoAtualizado  │                     │
│  Catálogo de        │ ──────────────────────────────────► │  Controle de        │
│  Produtos           │         (SNS → SQS)                │  Estoque            │
│                     │                                     │                     │
│  - Produto (CRUD)   │                                     │  - Item de Estoque  │
│  - Categoria        │                                     │  - Movimentação     │
│                     │                                     │  - Saldo            │
└─────────────────────┘                                     └─────────────────────┘
       PostgreSQL                                                DynamoDB
      (monolito)                                            (microsserviços)
```

**Relação:** Upstream-Downstream (Catálogo publica, Estoque consome).
O Estoque nunca chama o Catálogo. Se o Catálogo estiver fora do ar, o Estoque continua operando com os dados da projeção local.

---

## 3. Agregados, Entidades e Value Objects

### 3.1 Contexto: Catálogo de Produtos

#### Agregado Raiz: Produto

| Campo | Tipo | Classificação | Regras |
|-------|------|---------------|--------|
| `id` | UUID | Identidade | Gerado automaticamente, imutável |
| `sku` | string | Value Object | Único no sistema, alfanumérico, 3-50 caracteres |
| `nome` | string | Atributo | Obrigatório, 1-200 caracteres |
| `descricao` | string | Atributo | Opcional, até 1000 caracteres |
| `preco` | Dinheiro | Value Object | Maior que zero |
| `categoria_id` | UUID | Referência | Referência à entidade Categoria |
| `ativo` | bool | Atributo | Default: true |
| `criado_em` | datetime | Atributo | Gerado automaticamente |
| `atualizado_em` | datetime | Atributo | Atualizado automaticamente |

#### Entidade: Categoria

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `nome` | string | Único, 1-100 caracteres |
| `descricao` | string | Opcional |

#### Value Objects

- **SKU**: string imutável, validada (alfanumérico, 3-50 chars). Dois SKUs são iguais se o valor é igual.
- **Dinheiro**: decimal com 2 casas, sempre positivo. Comparação por valor.

### 3.2 Contexto: Controle de Estoque

#### Agregado Raiz: ItemEstoque

| Campo | Tipo | Classificação | Regras |
|-------|------|---------------|--------|
| `id` | UUID | Identidade | Gerado automaticamente |
| `produto_id` | UUID | Referência externa | Vem do evento ProdutoCriado |
| `sku` | string | Projeção | Cópia local, atualizada via evento |
| `nome_produto` | string | Projeção | Cópia local, atualizada via evento |
| `categoria_nome` | string | Projeção | Cópia local, atualizada via evento |
| `saldo` | int | Atributo | >= 0, calculado a partir das movimentações |
| `criado_em` | datetime | Atributo | Quando o item foi registrado no estoque |

**Invariante:** `saldo` nunca pode ser negativo. Uma saída que resulte em saldo < 0 deve ser rejeitada.

#### Entidade: Movimentacao

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `item_estoque_id` | UUID | Referência ao agregado raiz |
| `tipo` | enum | `ENTRADA` ou `SAIDA` |
| `quantidade` | int | Maior que zero |
| `lote` | string | Opcional, identificador do lote |
| `motivo` | string | Opcional, descrição da movimentação |
| `criado_em` | datetime | Gerado automaticamente |

#### Value Objects

- **TipoMovimentacao**: enum (`ENTRADA`, `SAIDA`). Imutável.
- **Quantidade**: inteiro positivo, nunca zero.

---

## 4. Eventos de Domínio

### 4.1 Eventos emitidos pelo Catálogo de Produtos

#### ProdutoCriado

```json
{
  "evento": "ProdutoCriado",
  "timestamp": "2026-04-03T10:00:00Z",
  "dados": {
    "produto_id": "uuid",
    "sku": "ELET-001",
    "nome": "Teclado Mecânico",
    "categoria_nome": "Eletrônicos",
    "preco": 299.90
  }
}
```

**Consumidor:** Estoque cria um `ItemEstoque` com saldo 0.

#### ProdutoAtualizado

```json
{
  "evento": "ProdutoAtualizado",
  "timestamp": "2026-04-03T11:00:00Z",
  "dados": {
    "produto_id": "uuid",
    "sku": "ELET-001",
    "nome": "Teclado Mecânico RGB",
    "categoria_nome": "Eletrônicos",
    "preco": 349.90
  }
}
```

**Consumidor:** Estoque atualiza a projeção local (nome, categoria_nome).

#### ProdutoDesativado

```json
{
  "evento": "ProdutoDesativado",
  "timestamp": "2026-04-03T12:00:00Z",
  "dados": {
    "produto_id": "uuid"
  }
}
```

**Consumidor:** Estoque marca o item como inativo (não aceita novas entradas).

### 4.2 Eventos emitidos pelo Controle de Estoque

#### EstoqueMovimentado

```json
{
  "evento": "EstoqueMovimentado",
  "timestamp": "2026-04-03T14:00:00Z",
  "dados": {
    "item_estoque_id": "uuid",
    "produto_id": "uuid",
    "tipo": "ENTRADA",
    "quantidade": 100,
    "saldo_atual": 100
  }
}
```

**Consumidor potencial:** Nenhum por enquanto (extensível para notificações, analytics).

#### EstoqueInsuficiente

```json
{
  "evento": "EstoqueInsuficiente",
  "timestamp": "2026-04-03T15:00:00Z",
  "dados": {
    "item_estoque_id": "uuid",
    "produto_id": "uuid",
    "quantidade_solicitada": 50,
    "saldo_atual": 10
  }
}
```

**Consumidor potencial:** Alertas, reposição automática (fora do escopo).

---

## 5. Contratos de API (Endpoints REST)

### 5.1 Catálogo de Produtos

Base path: `/api/v1`

#### Categorias

| Método | Endpoint | Descrição | Request Body | Response |
|--------|----------|-----------|-------------|----------|
| POST | `/categorias` | Criar categoria | `{ nome, descricao? }` | `201` + Categoria |
| GET | `/categorias` | Listar categorias | — | `200` + Lista |
| GET | `/categorias/{id}` | Buscar por ID | — | `200` + Categoria |

#### Produtos

| Método | Endpoint | Descrição | Request Body | Response |
|--------|----------|-----------|-------------|----------|
| POST | `/produtos` | Criar produto | `{ sku, nome, descricao?, preco, categoria_id }` | `201` + Produto |
| GET | `/produtos` | Listar produtos | Query: `?categoria_id=&ativo=&page=&size=` | `200` + Lista paginada |
| GET | `/produtos/{id}` | Buscar por ID | — | `200` + Produto |
| PUT | `/produtos/{id}` | Atualizar produto | `{ nome?, descricao?, preco?, categoria_id? }` | `200` + Produto |
| PATCH | `/produtos/{id}/desativar` | Desativar produto | — | `200` + Produto |

#### Schemas de Response

**Produto:**
```json
{
  "id": "uuid",
  "sku": "ELET-001",
  "nome": "Teclado Mecânico",
  "descricao": "Teclado com switches blue",
  "preco": 299.90,
  "categoria": {
    "id": "uuid",
    "nome": "Eletrônicos"
  },
  "ativo": true,
  "criado_em": "2026-04-03T10:00:00Z",
  "atualizado_em": "2026-04-03T10:00:00Z"
}
```

**Erro:**
```json
{
  "detail": {
    "code": "PRODUTO_SKU_DUPLICADO",
    "message": "Já existe um produto com o SKU 'ELET-001'"
  }
}
```

### 5.2 Controle de Estoque

Base path: `/api/v1`

#### Itens de Estoque

| Método | Endpoint | Descrição | Request Body | Response |
|--------|----------|-----------|-------------|----------|
| GET | `/estoque` | Listar itens | Query: `?categoria=&saldo_min=&page=&size=` | `200` + Lista paginada |
| GET | `/estoque/{id}` | Buscar item por ID | — | `200` + ItemEstoque |
| GET | `/estoque/produto/{produto_id}` | Buscar por produto | — | `200` + ItemEstoque |

#### Movimentações

| Método | Endpoint | Descrição | Request Body | Response |
|--------|----------|-----------|-------------|----------|
| POST | `/estoque/{id}/entrada` | Registrar entrada | `{ quantidade, lote?, motivo? }` | `201` + Movimentacao |
| POST | `/estoque/{id}/saida` | Registrar saída | `{ quantidade, motivo? }` | `201` + Movimentacao |
| GET | `/estoque/{id}/movimentacoes` | Histórico | Query: `?tipo=&page=&size=` | `200` + Lista paginada |

#### Schemas de Response

**ItemEstoque:**
```json
{
  "id": "uuid",
  "produto_id": "uuid",
  "sku": "ELET-001",
  "nome_produto": "Teclado Mecânico",
  "categoria_nome": "Eletrônicos",
  "saldo": 150,
  "criado_em": "2026-04-03T10:00:00Z"
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
  "criado_em": "2026-04-03T14:00:00Z"
}
```

### 5.3 Health Check (ambos os serviços)

| Método | Endpoint | Response |
|--------|----------|----------|
| GET | `/health` | `200` + `{ "status": "healthy", "service": "catalogo" }` |

---

## 6. Erros de Domínio

| Código | Contexto | Quando |
|--------|----------|--------|
| `EMAIL_DUPLICADO` | Auth | Tentativa de registrar com email já existente |
| `CREDENCIAIS_INVALIDAS` | Auth | Email ou senha incorretos no login |
| `TOKEN_INVALIDO` | Auth | JWT inválido, expirado ou ausente |
| `PRODUTO_SKU_DUPLICADO` | Catálogo | Tentativa de criar produto com SKU existente |
| `PRODUTO_NAO_ENCONTRADO` | Catálogo | Busca/atualização com ID inexistente |
| `CATEGORIA_NAO_ENCONTRADA` | Catálogo | Referência a categoria inexistente |
| `PRECO_INVALIDO` | Catálogo | Preço <= 0 |
| `SKU_INVALIDO` | Catálogo | SKU fora do formato permitido |
| `ITEM_NAO_ENCONTRADO` | Estoque | Busca com ID inexistente |
| `ESTOQUE_INSUFICIENTE` | Estoque | Saída com quantidade > saldo atual |
| `QUANTIDADE_INVALIDA` | Estoque | Quantidade <= 0 |
| `ITEM_INATIVO` | Estoque | Tentativa de entrada em item desativado |

---

## 7. Regras de Negócio Consolidadas

### Catálogo
1. SKU é único no sistema e imutável após criação
2. Preço deve ser maior que zero
3. Produto desativado não pode ser reativado (simplificação do escopo)
4. Ao criar produto, emite evento `ProdutoCriado`
5. Ao atualizar produto, emite evento `ProdutoAtualizado`
6. Ao desativar produto, emite evento `ProdutoDesativado`

### Estoque
1. `ItemEstoque` é criado automaticamente ao consumir evento `ProdutoCriado` (saldo inicial = 0)
2. Saldo nunca pode ser negativo
3. Toda alteração de saldo gera uma `Movimentacao` (auditoria)
4. Item desativado não aceita novas entradas (saídas são permitidas para zerar estoque)
5. Ao registrar movimentação, emite evento `EstoqueMovimentado`
6. Se saída é rejeitada por saldo insuficiente, emite evento `EstoqueInsuficiente`

### Comunicação entre Contextos
1. **Zero chamadas síncronas** entre Catálogo e Estoque
2. Catálogo publica eventos em tópico SNS
3. Estoque consome eventos via fila SQS
4. Consistência eventual: pode haver delay entre criar produto e ele aparecer no estoque
5. Eventos devem ser idempotentes (processar o mesmo evento duas vezes não causa efeito colateral)

---

## 8. Features (Spec-Driven — cada feature é um prompt para a IA)

Cada feature abaixo é autocontida: escopo, endpoints, regras e critérios de aceite (testes).
A IA recebe apenas a feature e a arquitetura base. O cronômetro começa no prompt.

---

### Feature 0: Autenticação (JWT)

**Contexto:** Transversal (protege todos os endpoints)
**Pré-requisito:** Nenhum (primeira feature a implementar)

**Escopo:**
- Criar conta de administrador (registro)
- Login (gera JWT)
- Proteger todos os endpoints (exceto /health e /auth/*) com Bearer token
- Identificar usuário logado

**Endpoints:**

| Método | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/auth/registrar` | `{ "nome": "Admin", "email": "admin@test.com", "senha": "minimo8chars" }` | `201` + Usuario (sem senha) |
| POST | `/api/v1/auth/login` | `{ "email": "admin@test.com", "senha": "minimo8chars" }` | `200` + `{ "access_token": "jwt...", "token_type": "bearer" }` |

**Modelo: Usuario**

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `nome` | string | Obrigatório, 1-200 caracteres |
| `email` | string | Obrigatório, único, formato válido |
| `senha_hash` | string | bcrypt hash, nunca retornado na API |
| `criado_em` | datetime | Gerado automaticamente |

**Regras:**
- Senha: mínimo 8 caracteres, armazenada como hash bcrypt
- JWT: expira em 24h, contém user_id e email no payload
- Todos os endpoints exceto `/health`, `/api/v1/auth/registrar` e `/api/v1/auth/login` exigem header `Authorization: Bearer <token>`
- Token inválido ou expirado retorna 401
- Sem token retorna 401
- Sem sistema de roles/permissões (todo usuário autenticado tem acesso total)

**Schema de Response:**

**Usuario:**
```json
{
  "id": "uuid",
  "nome": "Admin",
  "email": "admin@test.com",
  "criado_em": "2026-04-04T10:00:00Z"
}
```

**Login:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Erro de autenticação:**
```json
{
  "detail": {
    "code": "CREDENCIAIS_INVALIDAS",
    "message": "Email ou senha incorretos"
  }
}
```

**Critérios de aceite (testes):**

```
test_registrar_usuario_sucesso
  POST /api/v1/auth/registrar → 201
  Response contém id, nome, email, criado_em (sem senha)

test_registrar_email_duplicado
  POST duas vezes com mesmo email → segundo retorna 409
  code: EMAIL_DUPLICADO

test_registrar_senha_curta
  POST com senha "123" → 422
  Validação: mínimo 8 caracteres

test_registrar_email_invalido
  POST com email "nao-e-email" → 422

test_login_sucesso
  Registrar → POST /api/v1/auth/login → 200
  Response contém access_token e token_type=bearer

test_login_email_inexistente
  POST login com email não registrado → 401
  code: CREDENCIAIS_INVALIDAS

test_login_senha_errada
  Registrar → login com senha errada → 401
  code: CREDENCIAIS_INVALIDAS

test_endpoint_protegido_sem_token
  GET /api/v1/categorias sem header Authorization → 401

test_endpoint_protegido_com_token_valido
  Login → GET /api/v1/categorias com Bearer token → 200

test_endpoint_protegido_token_invalido
  GET /api/v1/categorias com token "lixo" → 401

test_health_nao_exige_auth
  GET /health sem token → 200
```

**Cobertura mínima:** 11 testes

**Dependências adicionais:**
- `python-jose[cryptography]` (JWT)
- `passlib[bcrypt]` (hash de senha)

---

### Feature 1: CRUD de Categoria

**Contexto:** Catálogo de Produtos
**Pré-requisito:** Feature 0 (endpoints protegidos por JWT)

**Escopo:**
- Criar categoria
- Listar categorias
- Buscar categoria por ID

**Endpoints:**

| Método | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/categorias` | `{ "nome": "Eletrônicos", "descricao": "Produtos eletrônicos" }` | `201` + Categoria |
| GET | `/api/v1/categorias` | — | `200` + Lista |
| GET | `/api/v1/categorias/{id}` | — | `200` + Categoria |

**Regras:**
- Nome é obrigatório (1-100 caracteres)
- Nome é único (case-insensitive)
- Descrição é opcional

**Critérios de aceite (testes):**

```
test_criar_categoria_sucesso
  POST /api/v1/categorias {"nome": "Eletrônicos"} → 201
  Response contém id (UUID), nome, descricao

test_criar_categoria_nome_duplicado
  POST duas vezes com mesmo nome → segunda retorna 422 ou 409
  Response contém code: CATEGORIA_NOME_DUPLICADO

test_criar_categoria_nome_vazio
  POST com nome "" → 422
  Validação de input

test_listar_categorias
  Criar 3 categorias → GET /api/v1/categorias → 200
  Response contém lista com 3 itens

test_buscar_categoria_por_id
  Criar categoria → GET /api/v1/categorias/{id} → 200
  Response contém dados corretos

test_buscar_categoria_inexistente
  GET /api/v1/categorias/{uuid-random} → 404
  Response contém code: CATEGORIA_NAO_ENCONTRADA
```

**Cobertura mínima:** 6 testes

---

### Feature 2: CRUD de Produto

**Contexto:** Catálogo de Produtos
**Pré-requisito:** Feature 1 (Categoria deve existir)

**Escopo:**
- Criar produto (com categoria)
- Listar produtos (com filtros e paginação)
- Buscar produto por ID
- Atualizar produto
- Desativar produto

**Endpoints:**

| Método | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/produtos` | `{ "sku": "ELET-001", "nome": "Teclado", "preco": 299.90, "categoria_id": "uuid" }` | `201` + Produto |
| GET | `/api/v1/produtos` | Query: `?categoria_id=&ativo=&page=1&size=20` | `200` + Lista paginada |
| GET | `/api/v1/produtos/{id}` | — | `200` + Produto |
| PUT | `/api/v1/produtos/{id}` | `{ "nome": "Teclado RGB", "preco": 349.90 }` | `200` + Produto |
| PATCH | `/api/v1/produtos/{id}/desativar` | — | `200` + Produto |

**Regras:**
- SKU: alfanumérico, 3-50 caracteres, único, imutável após criação
- Nome: obrigatório, 1-200 caracteres
- Preço: maior que zero (Dinheiro VO, decimal 2 casas)
- Categoria deve existir
- Produto desativado não pode ser reativado
- Ao criar: emite evento ProdutoCriado (no monolito apenas loga, nos microsserviços publica SNS)
- Ao atualizar: emite evento ProdutoAtualizado
- Ao desativar: emite evento ProdutoDesativado

**Critérios de aceite (testes):**

```
test_criar_produto_sucesso
  Criar categoria → POST produto com categoria_id → 201
  Response contém id, sku, nome, preco, categoria (nested), ativo=true

test_criar_produto_sku_duplicado
  POST dois produtos com mesmo SKU → segundo retorna 409
  code: PRODUTO_SKU_DUPLICADO

test_criar_produto_sku_invalido
  POST com sku "AB" (muito curto) → 422
  code: SKU_INVALIDO

test_criar_produto_preco_zero
  POST com preco=0 → 422
  code: PRECO_INVALIDO

test_criar_produto_preco_negativo
  POST com preco=-10 → 422
  code: PRECO_INVALIDO

test_criar_produto_categoria_inexistente
  POST com categoria_id=uuid-random → 404
  code: CATEGORIA_NAO_ENCONTRADA

test_listar_produtos_vazio
  GET /api/v1/produtos → 200, lista vazia

test_listar_produtos_com_filtro_categoria
  Criar 2 categorias, 3 produtos (2 na cat A, 1 na cat B)
  GET ?categoria_id=catA → retorna 2 produtos

test_listar_produtos_paginacao
  Criar 25 produtos → GET ?page=1&size=10 → 10 itens
  GET ?page=3&size=10 → 5 itens

test_buscar_produto_por_id
  Criar produto → GET /api/v1/produtos/{id} → 200, dados corretos

test_buscar_produto_inexistente
  GET /api/v1/produtos/{uuid-random} → 404
  code: PRODUTO_NAO_ENCONTRADO

test_atualizar_produto_sucesso
  Criar produto → PUT com nome novo → 200
  nome atualizado, sku inalterado, atualizado_em mudou

test_atualizar_produto_preco
  PUT com preco=0 → 422
  code: PRECO_INVALIDO

test_desativar_produto
  Criar produto → PATCH /desativar → 200
  ativo=false

test_desativar_produto_ja_inativo
  Desativar duas vezes → segunda retorna 200 (idempotente) ou 409
```

**Cobertura mínima:** 15 testes

---

### Feature 3: Entrada de Estoque

**Contexto:** Controle de Estoque
**Pré-requisito:** Feature 2 (Produto deve existir no monolito; nos microsserviços, ItemEstoque criado via evento)

**Escopo:**
- Registrar entrada de estoque (incrementa saldo)
- Consultar item de estoque
- Consultar histórico de movimentações

**Endpoints:**

| Método | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/estoque/{id}/entrada` | `{ "quantidade": 100, "lote": "NF-001", "motivo": "Recebimento" }` | `201` + Movimentacao |
| GET | `/api/v1/estoque` | Query: `?saldo_min=&page=&size=` | `200` + Lista paginada |
| GET | `/api/v1/estoque/{id}` | — | `200` + ItemEstoque |
| GET | `/api/v1/estoque/produto/{produto_id}` | — | `200` + ItemEstoque |
| GET | `/api/v1/estoque/{id}/movimentacoes` | Query: `?tipo=&page=&size=` | `200` + Lista paginada |

**Regras:**
- Quantidade deve ser maior que zero
- Lote e motivo são opcionais
- Entrada incrementa saldo do ItemEstoque
- Toda entrada gera uma Movimentacao (tipo=ENTRADA)
- Emite evento EstoqueMovimentado
- Item desativado não aceita entradas (code: ITEM_INATIVO)

**Nota para monolito:** O ItemEstoque precisa ser criado manualmente ou via seed quando o produto é criado. No monolito, ao criar produto, crie automaticamente o ItemEstoque com saldo=0 (simulando o que o evento faria nos microsserviços).

**Critérios de aceite (testes):**

```
test_registrar_entrada_sucesso
  Criar produto + item estoque → POST entrada com quantidade=100 → 201
  Response contém tipo=ENTRADA, quantidade=100

test_verificar_saldo_apos_entrada
  Entrada de 100 → GET item → saldo=100
  Outra entrada de 50 → GET item → saldo=150

test_entrada_quantidade_zero
  POST com quantidade=0 → 422
  code: QUANTIDADE_INVALIDA

test_entrada_quantidade_negativa
  POST com quantidade=-5 → 422
  code: QUANTIDADE_INVALIDA

test_entrada_item_inexistente
  POST /api/v1/estoque/{uuid-random}/entrada → 404
  code: ITEM_NAO_ENCONTRADO

test_entrada_item_inativo
  Desativar produto → POST entrada → 422
  code: ITEM_INATIVO

test_listar_itens_estoque
  Criar 3 itens → GET /api/v1/estoque → 200, 3 itens

test_buscar_item_por_produto_id
  GET /api/v1/estoque/produto/{produto_id} → 200, item correto

test_historico_movimentacoes
  Fazer 3 entradas → GET movimentacoes → 3 registros, tipo=ENTRADA

test_historico_filtro_tipo
  Fazer entradas e saídas → GET ?tipo=ENTRADA → só entradas
```

**Cobertura mínima:** 10 testes

---

### Feature 4: Saída de Estoque

**Contexto:** Controle de Estoque
**Pré-requisito:** Feature 3 (precisa ter saldo para sair)

**Escopo:**
- Registrar saída de estoque (decrementa saldo)
- Rejeitar saída se saldo insuficiente

**Endpoints:**

| Método | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/estoque/{id}/saida` | `{ "quantidade": 30, "motivo": "Venda" }` | `201` + Movimentacao |

**Regras:**
- Quantidade deve ser maior que zero
- Saldo resultante não pode ser negativo (invariante do agregado)
- Se saldo insuficiente: rejeitar e emitir evento EstoqueInsuficiente
- Saída permitida mesmo em item desativado (para zerar estoque)
- Emite evento EstoqueMovimentado após saída bem-sucedida

**Critérios de aceite (testes):**

```
test_registrar_saida_sucesso
  Entrada de 100 → Saída de 30 → 201
  Response contém tipo=SAIDA, quantidade=30

test_verificar_saldo_apos_saida
  Entrada 100, saída 30 → GET item → saldo=70

test_saida_estoque_insuficiente
  Entrada 10 → Saída 20 → 422
  code: ESTOQUE_INSUFICIENTE, saldo não alterado

test_saida_zera_estoque
  Entrada 50 → Saída 50 → 201
  saldo=0

test_saida_quantidade_invalida
  POST com quantidade=0 → 422
  code: QUANTIDADE_INVALIDA

test_saida_item_inexistente
  POST /api/v1/estoque/{uuid-random}/saida → 404
  code: ITEM_NAO_ENCONTRADO

test_saida_item_inativo_permitida
  Desativar produto → Saída do estoque restante → 201
  (saída permitida em item inativo para zerar)

test_multiplas_saidas_consecutivas
  Entrada 100 → Saída 30 → Saída 30 → Saída 30 → saldo=10
  Saída 20 → 422 (insuficiente)
```

**Cobertura mínima:** 8 testes

---

### Feature 5: Eventos de Domínio (Microsserviços)

**Contexto:** Comunicação entre Catálogo e Estoque
**Pré-requisito:** Features 1-4
**Nota:** Esta feature só se aplica aos microsserviços. No monolito, a criação do ItemEstoque é síncrona.

**Escopo:**
- Catálogo publica evento ProdutoCriado no SNS ao criar produto
- Estoque consome evento via SQS e cria ItemEstoque com saldo=0
- Catálogo publica ProdutoAtualizado ao atualizar
- Estoque atualiza projeção local (nome, categoria)
- Catálogo publica ProdutoDesativado ao desativar
- Estoque marca item como inativo

**Regras:**
- Eventos são idempotentes (reprocessar não duplica dados)
- Consistência eventual (delay aceitável)
- Estoque opera independente se Catálogo estiver fora do ar

**Critérios de aceite (testes):**

```
test_evento_produto_criado_cria_item_estoque
  Simular evento ProdutoCriado → ItemEstoque criado com saldo=0

test_evento_produto_criado_idempotente
  Enviar mesmo evento duas vezes → apenas 1 ItemEstoque

test_evento_produto_atualizado_atualiza_projecao
  Criar item via evento → Enviar ProdutoAtualizado com nome novo
  → nome_produto atualizado na projeção local

test_evento_produto_desativado_marca_inativo
  Criar item via evento → Enviar ProdutoDesativado
  → item marcado como inativo

test_evento_formato_invalido_nao_quebra
  Enviar mensagem mal formada → consumer não quebra, loga erro

test_evento_produto_desconhecido_ignora
  Enviar evento com tipo desconhecido → consumer ignora
```

**Cobertura mínima:** 6 testes

---

### Feature 6: Categoria de Produto + Filtro de Estoque por Categoria

**Contexto:** Transversal (Catálogo + Estoque)
**Pré-requisito:** Features 1-4 (e 5 nos microsserviços)

**Escopo:**
- Filtrar produtos por categoria (já existe no CRUD)
- Filtrar itens de estoque por categoria_nome
- Projeção de categoria_nome no ItemEstoque vem do evento

**Endpoints afetados:**

| Método | Endpoint | Filtro novo |
|--------|----------|------------|
| GET | `/api/v1/estoque` | `?categoria=Eletrônicos` |

**Regras:**
- Filtro por categoria no estoque usa a projeção local (categoria_nome)
- Não faz query no Catálogo (zero acoplamento)

**Critérios de aceite (testes):**

```
test_filtrar_estoque_por_categoria
  Criar 2 categorias (A, B), 3 produtos (2xA, 1xB), entradas em todos
  GET /api/v1/estoque?categoria=A → retorna 2 itens

test_filtrar_estoque_categoria_inexistente
  GET /api/v1/estoque?categoria=XYZ → 200, lista vazia

test_filtrar_estoque_sem_filtro_retorna_todos
  GET /api/v1/estoque → retorna todos os itens

test_projecao_categoria_atualizada_via_evento
  (microsserviços) Atualizar categoria do produto → evento → projeção atualizada
  Filtro reflete nova categoria
```

**Cobertura mínima:** 4 testes

---

## 9. Resumo de Features e Cobertura

| # | Feature | Contexto | Testes mínimos | Pré-requisito |
|---|---------|----------|---------------|---------------|
| 0 | Autenticação (JWT) | Transversal | 11 | — |
| 1 | CRUD Categoria | Catálogo | 6 | Feature 0 |
| 2 | CRUD Produto | Catálogo | 15 | Feature 1 |
| 3 | Entrada de Estoque | Estoque | 10 | Feature 2 |
| 4 | Saída de Estoque | Estoque | 8 | Feature 3 |
| 5 | Eventos de Domínio | Transversal | 6 | Features 1-4 |
| 6 | Filtro por Categoria | Transversal | 4 | Features 1-4 |
| **Total** | | | **60 testes** | |

**Meta de cobertura por feature:** >= 70% das linhas do código novo (medido com `pytest --cov`)
