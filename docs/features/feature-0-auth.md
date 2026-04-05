# Feature 0: Autenticacao JWT

## Contexto

Leia estes arquivos antes de implementar:
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Voce esta implementando autenticacao com JWT para proteger os endpoints da API.

## Arquitetura alvo

### Monolito
- Modulo: `src/auth/`
- Camadas: `domain/` → `application/` → `infrastructure/` → `container.py` → `presentation/`
- Middleware FastAPI que valida JWT em todas as rotas exceto /health e /auth/*
- Repository: SQLAlchemy + PostgreSQL (tabela `usuarios`)
- Container: `dependency-injector` DeclarativeContainer

### Microsservicos
- Servico: `auth-service/`
- Lambda Authorizer: valida JWT, API Gateway cacheia por 300s
- Lambda handlers para registrar e login
- Repository: DynamoDB (tabela `tcc-usuarios`)
- Container: `dependency-injector` DeclarativeContainer

## Endpoints

| Metodo | Endpoint | Request Body | Response | Auth |
|--------|----------|-------------|----------|------|
| POST | `/api/v1/auth/registrar` | `{ "nome": "Admin", "email": "admin@test.com", "senha": "minimo8chars" }` | `201` + Usuario (sem senha) | Publico |
| POST | `/api/v1/auth/login` | `{ "email": "admin@test.com", "senha": "minimo8chars" }` | `200` + `{ "access_token": "jwt...", "token_type": "bearer" }` | Publico |

## Modelo: Usuario

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | Gerado automaticamente |
| `nome` | string | Obrigatorio, 1-200 caracteres |
| `email` | string | Obrigatorio, unico, formato valido |
| `senha_hash` | string | bcrypt hash, nunca retornado na API |
| `criado_em` | datetime | Gerado automaticamente |

## Regras de negocio

1. Senha: minimo 8 caracteres, armazenada como hash bcrypt
2. Email: unico no sistema (case-insensitive)
3. JWT: expira em 24h, payload contem `user_id` e `email`
4. Todos os endpoints exceto `/health`, `/api/v1/auth/registrar` e `/api/v1/auth/login` exigem header `Authorization: Bearer <token>`
5. Token invalido ou expirado retorna 401
6. Sem sistema de roles/permissoes — todo usuario autenticado tem acesso total

## Erros de dominio

| Codigo | Quando |
|--------|--------|
| `EMAIL_DUPLICADO` | Registro com email ja existente |
| `CREDENCIAIS_INVALIDAS` | Email ou senha incorretos no login |
| `TOKEN_INVALIDO` | JWT invalido, expirado ou ausente |

## Dependencias a adicionar

- `python-jose[cryptography]` (JWT encode/decode)
- `passlib[bcrypt]` (hash de senha)

## Testes esperados (6)

```
test_registrar_sucesso
  POST /api/v1/auth/registrar com dados validos → 201
  Response contem id, nome, email, criado_em (sem senha_hash)

test_registrar_email_duplicado
  POST registrar duas vezes com mesmo email → segunda retorna 409
  Response contem code: EMAIL_DUPLICADO

test_login_sucesso
  Registrar usuario → POST /api/v1/auth/login com credenciais corretas → 200
  Response contem access_token e token_type=bearer

test_login_senha_errada
  Registrar → POST login com senha errada → 401
  Response contem code: CREDENCIAIS_INVALIDAS

test_rota_protegida_sem_token
  GET /api/v1/categorias sem header Authorization → 401

test_rota_protegida_com_token
  Registrar + Login → GET /api/v1/categorias com Bearer token → 200 (ou 404, mas nao 401)
```

## Estrutura de arquivos esperada (monolito)

```
src/auth/
├── domain/
│   ├── entities/usuario.py        # Entidade Usuario
│   ├── exceptions/auth.py         # EmailDuplicado, CredenciaisInvalidas, TokenInvalido
│   └── repositories/usuario_repository.py  # Interface ABC
├── application/
│   └── use_cases/
│       ├── registrar.py           # RegistrarUseCase
│       └── login.py               # LoginUseCase
├── infrastructure/
│   └── repositories/
│       └── sqlalchemy_usuario_repository.py
├── container.py                   # AuthContainer (DeclarativeContainer)
└── presentation/
    ├── routes.py                  # Rotas /api/v1/auth/*
    ├── middleware.py              # Middleware JWT (valida token)
    └── schemas.py                 # Pydantic schemas request/response
```

## Criterio de pronto

- [ ] 6 testes passam
- [ ] `radon cc src/auth/ -s -a` sem funcao acima de B
- [ ] `pytest --cov=src.auth` >= 70%
- [ ] Senha NUNCA aparece em response JSON
- [ ] JWT funciona com secret da env var `JWT_SECRET`
- [ ] Rotas de auth sao publicas, demais protegidas
