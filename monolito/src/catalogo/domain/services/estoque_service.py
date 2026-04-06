from abc import ABC, abstractmethod
from uuid import UUID


class EstoqueService(ABC):
    """Interface para comunicacao com o BC de Estoque.
    No monolito, implementado in-process.
    Nos microsservicos, publicaria evento no SNS."""

    @abstractmethod
    def inicializar_item(
        self,
        produto_id: UUID,
        sku: str,
        nome_produto: str,
        categoria_nome: str,
    ) -> None:
        """Cria ItemEstoque com saldo=0 para um produto recem-criado."""
        ...
