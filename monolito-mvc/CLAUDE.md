# Monolito MVC — Produtos e Estoque (Grupo de Controle)

## IMPORTANTE

Este projeto e o **grupo de controle** do TCC. Implementa EXATAMENTE a mesma API do monolito DDD (`monolito/`), mas com arquitetura MVC tradicional — SEM DDD, SEM Clean Architecture, SEM separacao de camadas.

O objetivo e comparar:
- Tempo de implementacao (IA)
- Tempo de migracao para microsservicos
- % codigo reutilizado na migracao
- Complexidade ciclomatica

## Arquitetura (propositalmente simples)

```
monolito-mvc/
├── app.py              # FastAPI app + middleware JWT
├── models.py           # SQLAlchemy models (todas as tabelas)
├── schemas.py          # Pydantic schemas (request/response)
├── routes/
│   ├── auth.py         # Rotas de auth (registrar, login)
│   ├── categorias.py   # CRUD categorias
│   ├── produtos.py     # CRUD produtos
│   └── estoque.py      # Entrada, saida, consultas
├── database.py         # Engine, session, Base
├── docker-compose.yml
├── pyproject.toml
└── tests/              # Mesmos 31 testes do monolito DDD
```

## Regras (anti-DDD de proposito)

- **Tudo junto** — rotas fazem query SQL direto, validacao inline
- **Sem interfaces** — sem ABC, sem Repository Pattern
- **Sem containers** — sem dependency-injector, instancia direto
- **Sem camadas** — sem domain/, application/, infrastructure/
- **Models = entidades** — SQLAlchemy models sao usados diretamente nas rotas
- **Validacao nas rotas** — nao em entidades separadas
- **Queries diretas** — `session.execute(select(...))` dentro da rota

## Exemplo de como uma rota deve ser

```python
# routes/categorias.py
@router.post("/api/v1/categorias")
def criar_categoria(body: CriarCategoriaRequest, session: Session = Depends(get_session)):
    # Validacao inline
    existente = session.execute(
        select(Categoria).where(Categoria.nome == body.nome)
    ).scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=409, detail="Categoria ja existe")

    categoria = Categoria(nome=body.nome, descricao=body.descricao)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return CategoriaResponse.model_validate(categoria)
```

**Note:** sem use case, sem repository, sem domain exception. Tudo na rota.

## Stack

- Python 3.13 / FastAPI / SQLAlchemy 2 / PostgreSQL 16
- bcrypt + python-jose (direto nas rotas, sem interface)
- pytest + httpx

## Comandos

```bash
docker compose up -d
source .venv/bin/activate
uvicorn app:app --port 8001    # Porta diferente do monolito DDD
pytest -v
radon cc . -s -a
```

## Especificacao

Ver `monolito-mvc/PRD.md` para endpoints e regras. Os testes sao identicos ao `monolito/tests/`.
