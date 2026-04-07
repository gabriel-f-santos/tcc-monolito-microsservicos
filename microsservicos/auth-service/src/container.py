from dependency_injector import containers, providers

from src.application.use_cases.login import LoginUseCase
from src.application.use_cases.registrar import RegistrarUseCase
from src.infrastructure.repositories.dynamodb_usuario_repository import (
    DynamoDBUsuarioRepository,
)
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.jose_token_service import JoseTokenService


class AuthContainer(containers.DeclarativeContainer):
    """Composition Root do BC Autenticacao (Microsservico).
    Unico lugar que conhece implementacoes concretas."""

    # External dependencies
    usuarios_table = providers.Dependency(instance_of=str)
    jwt_secret = providers.Dependency(instance_of=str)
    jwt_expiration_hours = providers.Dependency(instance_of=int)

    # Infrastructure services
    password_hasher = providers.Singleton(BcryptPasswordHasher)

    token_service = providers.Singleton(
        JoseTokenService,
        secret=jwt_secret,
        expiration_hours=jwt_expiration_hours,
    )

    # Repository
    usuario_repository = providers.Singleton(
        DynamoDBUsuarioRepository,
        table_name=usuarios_table,
    )

    # Use Cases
    registrar = providers.Factory(
        RegistrarUseCase,
        repo=usuario_repository,
        hasher=password_hasher,
    )

    login = providers.Factory(
        LoginUseCase,
        repo=usuario_repository,
        hasher=password_hasher,
        token_service=token_service,
    )
