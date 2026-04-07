import json

from src.application.use_cases.registrar import RegistrarDTO
from src.application.use_cases.login import LoginDTO
from src.container import AuthContainer
from src.infrastructure.config.settings import settings
from src.shared.domain.exceptions.base import DomainException

container = AuthContainer(
    table_name=settings.usuarios_table,
    jwt_secret=settings.jwt_secret,
    jwt_expiration_hours=settings.jwt_expiration_hours,
)

HEADERS = {"Content-Type": "application/json"}

STATUS_MAP = {
    "EMAIL_DUPLICADO": 409,
    "CREDENCIAIS_INVALIDAS": 401,
    "TOKEN_INVALIDO": 401,
}


def registrar_handler(event, context):
    """Handler para POST /api/v1/auth/registrar"""
    try:
        body = json.loads(event["body"])
        use_case = container.registrar()
        usuario = use_case.execute(RegistrarDTO(**body))
        return {
            "statusCode": 201,
            "headers": HEADERS,
            "body": json.dumps({
                "id": str(usuario.id),
                "nome": usuario.nome,
                "email": usuario.email,
                "criado_em": usuario.criado_em.isoformat(),
            }),
        }
    except DomainException as exc:
        return {
            "statusCode": STATUS_MAP.get(exc.code, 400),
            "headers": HEADERS,
            "body": json.dumps({"code": exc.code, "detail": exc.message}),
        }


def login_handler(event, context):
    """Handler para POST /api/v1/auth/login"""
    try:
        body = json.loads(event["body"])
        use_case = container.login()
        result = use_case.execute(LoginDTO(**body))
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({
                "access_token": result.access_token,
                "token_type": result.token_type,
            }),
        }
    except DomainException as exc:
        return {
            "statusCode": STATUS_MAP.get(exc.code, 400),
            "headers": HEADERS,
            "body": json.dumps({"code": exc.code, "detail": exc.message}),
        }
