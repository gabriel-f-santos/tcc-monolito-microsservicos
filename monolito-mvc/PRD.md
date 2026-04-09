# PRD — Sistema de Gerenciamento de Produtos e Estoque (MVC)

## Objetivo

Implementar um sistema simples de gerenciamento de produtos e estoque usando FastAPI com arquitetura MVC tradicional (sem DDD, sem Clean Architecture, sem camadas separadas).

**IMPORTANTE:** Este sistema e o grupo de controle do TCC. Deve ter EXATAMENTE a mesma API e comportamento do monolito DDD (`monolito/`), mas com arquitetura proposital mente simples — rotas com queries SQL diretas, validacao inline, sem separacao de camadas.

## Stack

- Python 3.13 / FastAPI / SQLAlchemy 2 / PostgreSQL 16
- Tudo em poucos arquivos (app.py, models.py, routes, schemas)
- Sem dependency-injector, sem containers, sem interfaces ABC
- Sem separacao domain/application/infrastructure

## Endpoints (identicos ao monolito DDD)

### Auth
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | `/api/v1/auth/registrar` | Criar usuario |
| POST | `/api/v1/auth/login` | Login, retorna JWT |

### Categorias
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | `/api/v1/categorias` | Criar categoria |
| GET | `/api/v1/categorias` | Listar |
| GET | `/api/v1/categorias/{id}` | Buscar por ID |

### Produtos
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | `/api/v1/produtos` | Criar produto |
| GET | `/api/v1/produtos` | Listar (filtros: categoria_id, ativo) |
| GET | `/api/v1/produtos/{id}` | Buscar por ID |
| PUT | `/api/v1/produtos/{id}` | Atualizar |
| PATCH | `/api/v1/produtos/{id}/desativar` | Desativar |

### Estoque
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | `/api/v1/estoque/{id}/entrada` | Registrar entrada |
| POST | `/api/v1/estoque/{id}/saida` | Registrar saida |
| GET | `/api/v1/estoque` | Listar itens |
| GET | `/api/v1/estoque/{id}` | Buscar por ID |
| GET | `/api/v1/estoque/produto/{produto_id}` | Buscar por produto |
| GET | `/api/v1/estoque/{id}/movimentacoes` | Historico |

### Health
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET | `/health` | Health check |

## Regras de Negocio (mesmas do monolito DDD)

### Auth
- Senha minimo 8 chars, bcrypt hash
- Email unico, case-insensitive
- JWT expira em 24h
- Todos endpoints exceto /health e /auth/* exigem Bearer token

### Categorias
- Nome unico, 1-100 chars
- Descricao opcional

### Produtos
- SKU unico, alfanumerico, 3-50 chars, imutavel
- Preco > 0
- Categoria deve existir
- Ao criar produto, criar item de estoque com saldo=0

### Estoque
- Quantidade > 0
- Saldo nunca negativo
- Item inativo nao aceita entradas (saidas permitidas)
- Toda movimentacao registrada (auditoria)

## Schemas de Response

(Identicos aos do monolito DDD — ver docs/spec.md secoes 5.1 e 5.2)

## Testes

31 testes — EXATAMENTE os mesmos do monolito DDD. Mesmos nomes, mesmos payloads, mesmos asserts. A unica diferenca e que importam de `app` diferente.
