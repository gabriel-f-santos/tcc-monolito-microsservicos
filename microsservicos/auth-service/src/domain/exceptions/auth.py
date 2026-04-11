from src.shared.domain.exceptions.base import DomainException


class EmailDuplicado(DomainException):
    def __init__(self) -> None:
        super().__init__(code="EMAIL_DUPLICADO", message="Email ja esta em uso")


class CredenciaisInvalidas(DomainException):
    def __init__(self) -> None:
        super().__init__(code="CREDENCIAIS_INVALIDAS", message="Email ou senha incorretos")


class TokenInvalido(DomainException):
    def __init__(self) -> None:
        super().__init__(code="TOKEN_INVALIDO", message="Token invalido, expirado ou ausente")
