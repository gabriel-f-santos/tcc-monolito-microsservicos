from abc import ABC, abstractmethod
from uuid import UUID


class TokenService(ABC):
    @abstractmethod
    def generate_token(self, user_id: UUID, email: str) -> str:
        ...

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Returns payload dict with 'user_id' and 'email' keys.
        Raises TokenInvalido if token is invalid or expired."""
        ...
