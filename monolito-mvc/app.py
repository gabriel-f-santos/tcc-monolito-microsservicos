"""FastAPI app — MVC monolito com middleware JWT."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from database import Base, engine
from routes import auth, categorias, estoque, produtos

SECRET_KEY = "super-secret-key-monolito-mvc"
ALGORITHM = "HS256"


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for health and auth routes
        if path == "/health" or path.startswith("/api/v1/auth"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Token ausente"})

        token = auth_header.split(" ", 1)[1]
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Token invalido"})

        return await call_next(request)


app = FastAPI(title="Monolito MVC - Produtos e Estoque", version="0.1.0")
app.add_middleware(JWTMiddleware)

# Create tables on startup
Base.metadata.create_all(engine)

# Routers
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(estoque.router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "monolito-mvc"}
