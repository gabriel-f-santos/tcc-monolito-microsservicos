from fastapi import FastAPI

from database import Base, engine

app = FastAPI(title="Monolito MVC - Produtos e Estoque", version="0.1.0")

# Create tables on startup
Base.metadata.create_all(engine)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "monolito-mvc"}


# TODO: Adicionar rotas de auth, categorias, produtos, estoque
# TODO: Adicionar middleware JWT
