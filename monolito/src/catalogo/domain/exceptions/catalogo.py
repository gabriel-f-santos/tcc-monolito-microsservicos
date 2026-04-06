from src.shared.domain.exceptions.base import DomainException


class CategoriaNomeDuplicado(DomainException):
    def __init__(self) -> None:
        super().__init__(code="CATEGORIA_NOME_DUPLICADO", message="Nome de categoria ja existe")


class CategoriaNaoEncontrada(DomainException):
    def __init__(self) -> None:
        super().__init__(code="CATEGORIA_NAO_ENCONTRADA", message="Categoria nao encontrada")
