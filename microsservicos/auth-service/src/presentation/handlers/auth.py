import json

from src.application.use_cases.registrar import RegistrarDTO
from src.application.use_cases.login import LoginDTO
from src.container import AuthContainer
from src.infrastructure.config.settings import settings
from src.shared.domain.exceptions.base import DomainException

DOMAIN_STATUS_MAP = {
    "EMAIL_DUPLICADO": 409,
    "CREDENCIAIS_INVALIDAS": 401,
    "NOME_OBRIGATORIO": 400,
    "EMAIL_OBRIGATORIO": 400,
    "SENHA_OBRIGATORIA": 400,
    "NOME_INVALIDO": 400,
}

container = AuthContainer(
    usuarios_table=settings.usuarios_table,
    jwt_secret=settings.jwt_secret,
    jwt_expiration_hours=settings.jwt_expiration_hours,
)


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _usuario_to_dict(usuario) -> dict:
    return {
        "id": str(usuario.id),
        "nome": usuario.nome,
        "email": usuario.email,
        "criado_em": usuario.criado_em.isoformat(),
        "atualizado_em": usuario.atualizado_em.isoformat(),
    }


def registrar_handler(event, context):
    """Handler para POST /api/v1/auth/registrar"""
    try:
        body = json.loads(event["body"])
        use_case = container.registrar()
        usuario = use_case.execute(RegistrarDTO(**body))
        return _response(201, _usuario_to_dict(usuario))
    except DomainException as e:
        status = DOMAIN_STATUS_MAP.get(e.code, 400)
        return _response(status, {"code": e.code, "message": e.message})


def login_handler(event, context):
    """Handler para POST /api/v1/auth/login"""
    try:
        body = json.loads(event["body"])
        use_case = container.login()
        result = use_case.execute(LoginDTO(**body))
        return _response(200, {"access_token": result.access_token, "token_type": result.token_type})
    except DomainException as e:
        status = DOMAIN_STATUS_MAP.get(e.code, 400)
        return _response(status, {"code": e.code, "message": e.message})
