from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.item_estoque import ItemEstoque
from src.domain.exceptions.estoque import ItemNaoEncontrado
from src.domain.repositories.item_estoque_repository import ItemEstoqueRepository


@dataclass
class ConfigurarAlertaDTO:
    item_estoque_id: UUID
    estoque_minimo: int


class ConfigurarAlertaUseCase:
    def __init__(self, item_repo: ItemEstoqueRepository) -> None:
        self.item_repo = item_repo

    def execute(self, dados: ConfigurarAlertaDTO) -> ItemEstoque:
        if dados.estoque_minimo < 0:
            from src.shared.domain.exceptions.base import DomainException
            raise DomainException(
                "ESTOQUE_MINIMO_INVALIDO",
                "estoque_minimo deve ser >= 0",
            )

        item = self.item_repo.get_by_id(dados.item_estoque_id)
        if item is None:
            raise ItemNaoEncontrado()

        item.estoque_minimo = dados.estoque_minimo
        self.item_repo.save(item)
        return item
