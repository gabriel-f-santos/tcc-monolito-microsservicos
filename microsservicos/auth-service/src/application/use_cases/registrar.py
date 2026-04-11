from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime, timezone

from src.domain.entities.usuario import Usuario
from src.domain.exceptions.auth import EmailDuplicado
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.services.password_hasher import PasswordHasher


@dataclass
class RegistrarDTO:
    nome: str
    email: str
    senha: str


class RegistrarUseCase:
    def __init__(self, repo: UsuarioRepository, hasher: PasswordHasher) -> None:
        self.repo = repo
        self.hasher = hasher

    def execute(self, dados: RegistrarDTO) -> Usuario:
        email_lower = dados.email.lower()
        existente = self.repo.get_by_email(email_lower)
        if existente is not None:
            raise EmailDuplicado()

        usuario = Usuario(
            id=uuid4(),
            nome=dados.nome,
            email=email_lower,
            senha_hash=self.hasher.hash(dados.senha),
            criado_em=datetime.now(timezone.utc),
            atualizado_em=datetime.now(timezone.utc),
        )
        return self.repo.save(usuario)
