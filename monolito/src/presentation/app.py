from fastapi import FastAPI

from src.infrastructure.observability import setup_telemetry
from src.presentation.routes.health import router as health_router

app = FastAPI(
    title="Monolito - Produtos e Estoque",
    version="0.1.0",
)

app.include_router(health_router)

setup_telemetry(app)
