"""Composition Root do auth-service.

Producao SEMPRE usa DynamoDB. Testes rodam sob moto (mock_aws) via conftest.py,
que intercepta as chamadas boto3. Nao ha fallback InMemory por env var.
"""
import os

from src.application.use_cases.login import LoginUseCase
from src.application.use_cases.registrar import RegistrarUseCase
from src.infrastructure.repositories.dynamodb_usuario_repository import (
    DynamoDBUsuarioRepository,
)
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.jose_token_service import JoseTokenService


def _usuarios_table_name() -> str:
    return os.environ["USUARIOS_TABLE"]


def _jwt_secret() -> str:
    return os.environ["JWT_SECRET"]


def build_usuario_repository() -> DynamoDBUsuarioRepository:
    return DynamoDBUsuarioRepository(table_name=_usuarios_table_name())


def build_password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


def build_token_service() -> JoseTokenService:
    return JoseTokenService(secret=_jwt_secret(), expiration_hours=24)


def build_registrar_use_case() -> RegistrarUseCase:
    return RegistrarUseCase(
        repo=build_usuario_repository(),
        hasher=build_password_hasher(),
    )


def build_login_use_case() -> LoginUseCase:
    return LoginUseCase(
        repo=build_usuario_repository(),
        hasher=build_password_hasher(),
        token_service=build_token_service(),
    )
