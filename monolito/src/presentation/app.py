from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.shared.domain.exceptions.base import DomainException
from src.shared.infrastructure.config.settings import settings
from src.shared.infrastructure.database.session import SessionLocal
from src.shared.infrastructure.observability import setup_telemetry
from src.presentation.routes.health import router as health_router
from src.auth.container import AuthContainer
from src.auth.presentation.routes import router as auth_router
from src.auth.presentation.middleware import JWTMiddleware
from src.catalogo.container import CatalogoContainer
from src.catalogo.presentation.routes import router as catalogo_router
from src.estoque.container import EstoqueContainer
from src.estoque.presentation.routes import router as estoque_router

# Cross-BC service: implementation lives in estoque BC, interface in catalogo BC
from src.estoque.infrastructure.services.estoque_service_impl import EstoqueServiceImpl

app = FastAPI(
    title="Monolito - Produtos e Estoque",
    version="0.1.0",
)

# --- DI containers ---
# app.py is the ONLY file that knows all containers and cross-BC wiring.

auth_container = AuthContainer(
    session_factory=SessionLocal,
    jwt_secret=settings.jwt_secret,
    jwt_expiration_hours=settings.jwt_expiration_hours,
)

estoque_container = EstoqueContainer(
    session_factory=SessionLocal,
)

# Cross-BC wiring: build estoque service using estoque's repo, inject into catalogo
_estoque_service = EstoqueServiceImpl(
    item_estoque_repo=estoque_container.item_estoque_repository(),
)

catalogo_container = CatalogoContainer(
    session_factory=SessionLocal,
    estoque_service=_estoque_service,
)

# --- Middleware ---
app.add_middleware(JWTMiddleware, token_service=auth_container.token_service())

# --- Routers ---
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(catalogo_router)
app.include_router(estoque_router)

# --- Exception handlers ---
DOMAIN_STATUS_MAP = {
    # Auth
    "EMAIL_DUPLICADO": 409,
    "CREDENCIAIS_INVALIDAS": 401,
    "TOKEN_INVALIDO": 401,
    # Catalogo
    "CATEGORIA_NOME_DUPLICADO": 409,
    "CATEGORIA_NAO_ENCONTRADA": 404,
    "CATEGORIA_NOME_OBRIGATORIO": 422,
    "PRODUTO_SKU_DUPLICADO": 409,
    "PRODUTO_NAO_ENCONTRADO": 404,
    "PRODUTO_SKU_OBRIGATORIO": 422,
    "PRODUTO_NOME_OBRIGATORIO": 422,
    "PRODUTO_PRECO_OBRIGATORIO": 422,
    "PRODUTO_CATEGORIA_OBRIGATORIA": 422,
    "PRECO_INVALIDO": 422,
    "SKU_INVALIDO": 422,
    # Estoque
    "ESTOQUE_ITEM_NAO_ENCONTRADO": 404,
    "ESTOQUE_QUANTIDADE_INVALIDA": 422,
    "ESTOQUE_ITEM_INATIVO": 422,
    "ESTOQUE_INSUFICIENTE": 422,
    "ESTOQUE_SALDO_NEGATIVO": 422,
}


@app.exception_handler(DomainException)
async def domain_exception_handler(request, exc: DomainException):
    status = DOMAIN_STATUS_MAP.get(exc.code, 400)
    return JSONResponse(status_code=status, content={"detail": exc.message, "code": exc.code})


# --- Create tables on startup (no Alembic for TCC simplicity) ---
from src.shared.infrastructure.database.base import Base
from src.shared.infrastructure.database.session import engine
import src.auth.infrastructure.repositories.sqlalchemy_usuario_repository  # noqa: F401
import src.catalogo.infrastructure.repositories.sqlalchemy_categoria_repository  # noqa: F401
import src.catalogo.infrastructure.repositories.sqlalchemy_produto_repository  # noqa: F401
import src.estoque.infrastructure.repositories.sqlalchemy_item_estoque_repository  # noqa: F401
import src.estoque.infrastructure.repositories.sqlalchemy_movimentacao_repository  # noqa: F401
Base.metadata.create_all(engine)

setup_telemetry(app)
