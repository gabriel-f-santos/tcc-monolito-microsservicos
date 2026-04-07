from abc import abstractmethod

from src.domain.entities.usuario import Usuario
from src.shared.domain.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    @abstractmethod
    def get_by_email(self, email: str) -> Usuario | None:
        ...
