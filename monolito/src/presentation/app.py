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

app = FastAPI(
    title="Monolito - Produtos e Estoque",
    version="0.1.0",
)

# --- DI containers ---
auth_container = AuthContainer(
    session_factory=SessionLocal,
    jwt_secret=settings.jwt_secret,
    jwt_expiration_hours=settings.jwt_expiration_hours,
)

# --- Middleware ---
app.add_middleware(JWTMiddleware, token_service=auth_container.token_service())

# --- Routers ---
app.include_router(health_router)
app.include_router(auth_router)

# --- Exception handlers ---
DOMAIN_STATUS_MAP = {
    "EMAIL_DUPLICADO": 409,
    "CREDENCIAIS_INVALIDAS": 401,
    "TOKEN_INVALIDO": 401,
}


@app.exception_handler(DomainException)
async def domain_exception_handler(request, exc: DomainException):
    status = DOMAIN_STATUS_MAP.get(exc.code, 400)
    return JSONResponse(status_code=status, content={"detail": exc.message, "code": exc.code})


setup_telemetry(app)
