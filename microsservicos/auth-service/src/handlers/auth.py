import json

from src.container import registrar_use_case, login_use_case
from src.application.use_cases.registrar import RegistrarDTO
from src.application.use_cases.login import LoginDTO
from src.domain.exceptions.auth import EmailDuplicado, CredenciaisInvalidas
from src.shared.domain.exceptions.base import DomainException

HEADERS = {"Content-Type": "application/json"}


def registrar_handler(event, context):
    body = json.loads(event["body"])
    try:
        usuario = registrar_use_case.execute(
            RegistrarDTO(nome=body["nome"], email=body["email"], senha=body["senha"])
        )
    except EmailDuplicado:
        return {"statusCode": 409, "headers": HEADERS, "body": json.dumps({"error": "EMAIL_DUPLICADO"})}
    except DomainException as e:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": e.code})}

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


def login_handler(event, context):
    body = json.loads(event["body"])
    try:
        result = login_use_case.execute(
            LoginDTO(email=body["email"], senha=body["senha"])
        )
    except CredenciaisInvalidas:
        return {"statusCode": 401, "headers": HEADERS, "body": json.dumps({"error": "CREDENCIAIS_INVALIDAS"})}

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({
            "access_token": result.access_token,
            "token_type": result.token_type,
        }),
    }
