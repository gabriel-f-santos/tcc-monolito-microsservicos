from dataclasses import dataclass

from src.domain.exceptions.auth import CredenciaisInvalidas
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.services.password_hasher import PasswordHasher
from src.domain.services.token_service import TokenService


@dataclass
class LoginDTO:
    email: str
    senha: str


@dataclass
class TokenResult:
    access_token: str
    token_type: str = "bearer"


class LoginUseCase:
    def __init__(
        self,
        repo: UsuarioRepository,
        hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self.repo = repo
        self.hasher = hasher
        self.token_service = token_service

    def execute(self, dados: LoginDTO) -> TokenResult:
        usuario = self.repo.get_by_email(dados.email.lower())
        if usuario is None or not self.hasher.verify(dados.senha, usuario.senha_hash):
            raise CredenciaisInvalidas()

        token = self.token_service.generate_token(usuario.id, usuario.email)
        return TokenResult(access_token=token)
