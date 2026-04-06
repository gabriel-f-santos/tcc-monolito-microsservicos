from dependency_injector import containers, providers

from src.auth.application.use_cases.login import LoginUseCase
from src.auth.application.use_cases.registrar import RegistrarUseCase
from src.auth.infrastructure.repositories.sqlalchemy_usuario_repository import (
    SQLAlchemyUsuarioRepository,
)
from src.auth.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.auth.infrastructure.services.jose_token_service import JoseTokenService


class AuthContainer(containers.DeclarativeContainer):
    """Composition Root do BC Autenticacao.
    Unico lugar que conhece implementacoes concretas."""

    wiring_config = containers.WiringConfiguration(
        modules=["src.auth.presentation.routes"],
    )

    # External dependencies
    session_factory = providers.Dependency()
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
        SQLAlchemyUsuarioRepository,
        session_factory=session_factory,
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
