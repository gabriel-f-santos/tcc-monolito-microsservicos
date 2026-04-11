import os

from src.application.use_cases.registrar import RegistrarUseCase
from src.application.use_cases.login import LoginUseCase
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.services.password_hasher import PasswordHasher
from src.domain.services.token_service import TokenService
from src.infrastructure.repositories.in_memory_usuario_repository import InMemoryUsuarioRepository
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.jose_token_service import JoseTokenService

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "")


def _build_repository() -> UsuarioRepository:
    if DYNAMODB_TABLE:
        from src.infrastructure.repositories.dynamodb_usuario_repository import DynamoDBUsuarioRepository
        return DynamoDBUsuarioRepository(DYNAMODB_TABLE)
    return InMemoryUsuarioRepository()


_repo: UsuarioRepository = _build_repository()
_hasher: PasswordHasher = BcryptPasswordHasher()
_token_service: TokenService = JoseTokenService(JWT_SECRET, JWT_EXPIRATION_HOURS)

registrar_use_case = RegistrarUseCase(repo=_repo, hasher=_hasher)
login_use_case = LoginUseCase(repo=_repo, hasher=_hasher, token_service=_token_service)
token_service = _token_service
