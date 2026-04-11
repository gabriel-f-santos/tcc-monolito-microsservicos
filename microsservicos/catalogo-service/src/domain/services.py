from abc import ABC, abstractmethod
from uuid import UUID


class EventPublisher(ABC):
    """Interface para publicacao de eventos de dominio.
    Implementada no infrastructure via SNS."""

    @abstractmethod
    def publicar_produto_criado(
        self,
        produto_id: UUID,
        sku: str,
        nome: str,
        categoria_nome: str,
    ) -> None:
        ...
