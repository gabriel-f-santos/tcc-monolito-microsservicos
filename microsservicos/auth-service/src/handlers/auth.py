"""Lambda handlers para Registrar e Login.

Cada invocacao monta o use case via container (sem cache de modulo que
faria chamadas AWS em import-time — Regra 5 do INTEGRATION-CONTRACT).
"""
import json

from src.application.use_cases.login import LoginDTO
from src.application.use_cases.registrar import RegistrarDTO
from src.container import build_login_use_case, build_registrar_use_case
from src.domain.exceptions.auth import CredenciaisInvalidas, EmailDuplicado


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _parse_body(event: dict) -> dict:
    raw = event.get("body") or "{}"
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode()
    if isinstance(raw, dict):
        return raw
    return json.loads(raw)


def registrar_handler(event, context):
    data = _parse_body(event)
    nome = data.get("nome", "")
    email = data.get("email", "")
    senha = data.get("senha", "")

    if len(senha) < 8:
        return _response(400, {"code": "SENHA_INVALIDA", "message": "Senha deve ter ao menos 8 caracteres"})

    use_case = build_registrar_use_case()
    try:
        usuario = use_case.execute(RegistrarDTO(nome=nome, email=email, senha=senha))
    except EmailDuplicado as e:
        return _response(409, {"code": e.code, "message": e.message})

    return _response(
        201,
        {
            "id": str(usuario.id),
            "nome": usuario.nome,
            "email": usuario.email,
            "criado_em": usuario.criado_em.isoformat(),
        },
    )


def login_handler(event, context):
    data = _parse_body(event)
    email = data.get("email", "")
    senha = data.get("senha", "")

    use_case = build_login_use_case()
    try:
        result = use_case.execute(LoginDTO(email=email, senha=senha))
    except CredenciaisInvalidas as e:
        return _response(401, {"code": e.code, "message": e.message})

    return _response(
        200,
        {
            "access_token": result.access_token,
            "token_type": result.token_type,
        },
    )
