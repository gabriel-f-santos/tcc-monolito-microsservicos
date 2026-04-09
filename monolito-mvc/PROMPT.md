# Prompt para Implementacao do Monolito MVC

## Instrucao

Leia `monolito-mvc/PRD.md` para a especificacao completa de endpoints e regras de negocio.
Leia `monolito-mvc/CLAUDE.md` para as regras de arquitetura MVC (sem DDD, sem camadas).

Implemente TODAS as rotas para que os 31 testes em `monolito-mvc/tests/` passem.
Os testes ja estao escritos com payloads e respostas esperadas — NAO modifique os testes.

## Arquivos existentes (NAO modificar)

- `tests/` — 31 testes prontos (nao alterar)
- `models.py` — SQLAlchemy models ja definidos
- `database.py` — Engine e session
- `docker-compose.yml` — PostgreSQL na porta 5435

## O que implementar

1. **`app.py`** — FastAPI app com middleware JWT, include routers, create_all tables
2. **`schemas.py`** — Pydantic schemas para request/response
3. **`routes/auth.py`** — POST registrar, POST login (bcrypt + JWT)
4. **`routes/categorias.py`** — POST criar, GET listar, GET buscar por ID
5. **`routes/produtos.py`** — POST criar, GET listar (filtros), GET buscar, PUT atualizar, PATCH desativar
6. **`routes/estoque.py`** — POST entrada, POST saida, GET listar, GET buscar, GET por produto, GET movimentacoes

## Regras

- Arquitetura MVC simples: rotas com queries SQL diretas via SQLAlchemy
- Validacao inline nas rotas (sem domain exceptions separadas)
- bcrypt e jose importados diretamente nas rotas (sem interfaces)
- HTTPException para erros (409, 404, 422, 401)
- Depends(get_session) para injecao de sessao do banco
- Ao criar produto, criar item_estoque com saldo=0 na mesma rota
- Saldo nunca negativo (validar na rota de saida)
- JWT middleware protege tudo exceto /health e /api/v1/auth/*

## Ambiente

```bash
cd monolito-mvc
docker compose up -d              # PostgreSQL porta 5435
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v                         # Todos os 31 testes devem passar
```

## Criterio de pronto

- [ ] 31 testes passam sem modificacao
- [ ] uvicorn app:app --port 8001 roda
- [ ] /health retorna {"status": "healthy", "service": "monolito-mvc"}
