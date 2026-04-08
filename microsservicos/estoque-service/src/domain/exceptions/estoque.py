from src.shared.domain.exceptions.base import DomainException


class ItemNaoEncontrado(DomainException):
    def __init__(self) -> None:
        super().__init__(
            code="ESTOQUE_ITEM_NAO_ENCONTRADO",
            message="Item de estoque nao encontrado",
        )


class QuantidadeInvalida(DomainException):
    def __init__(self) -> None:
        super().__init__(
            code="ESTOQUE_QUANTIDADE_INVALIDA",
            message="Quantidade deve ser maior que zero",
        )


class EstoqueInsuficiente(DomainException):
    def __init__(self, saldo_atual: int, solicitado: int) -> None:
        super().__init__(
            code="ESTOQUE_INSUFICIENTE",
            message=f"Estoque insuficiente: saldo={saldo_atual}, solicitado={solicitado}",
        )


class ItemInativo(DomainException):
    def __init__(self) -> None:
        super().__init__(
            code="ESTOQUE_ITEM_INATIVO",
            message="Item de estoque esta inativo",
        )
