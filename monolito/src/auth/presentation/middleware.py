from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth.domain.exceptions.auth import TokenInvalido
from src.auth.domain.services.token_service import TokenService

PUBLIC_PATHS = {"/health", "/api/v1/auth/registrar", "/api/v1/auth/login", "/docs", "/openapi.json"}


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token_service: TokenService):
        super().__init__(app)
        self.token_service = token_service

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            exc = TokenInvalido()
            return JSONResponse(
                status_code=401,
                content={"detail": exc.message, "code": exc.code},
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = self.token_service.decode_token(token)
            request.state.user_id = payload["user_id"]
            request.state.user_email = payload["email"]
        except TokenInvalido as exc:
            return JSONResponse(
                status_code=401,
                content={"detail": exc.message, "code": exc.code},
            )

        return await call_next(request)
