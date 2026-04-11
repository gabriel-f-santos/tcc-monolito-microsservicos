"""Auth handlers — MVC inline (bcrypt + JWT + DynamoDB direto)."""
import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import boto3
from boto3.dynamodb.conditions import Attr
from jose import jwt

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def _table():
    """Lazy singleton do Table — evita chamada AWS em import time."""
    return boto3.resource("dynamodb").Table(os.environ["USUARIOS_TABLE"])


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        os.environ["JWT_SECRET"],
        algorithm=ALGORITHM,
    )


def _find_by_email(email: str):
    items = _table().scan(
        FilterExpression=Attr("email").eq(email)
    ).get("Items", [])
    return items[0] if items else None


def registrar_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    nome = body.get("nome")
    email = (body.get("email") or "").lower()
    senha = body.get("senha") or ""

    if not nome or not email or len(senha) < 8:
        return _response(400, {"message": "Dados invalidos"})

    if _find_by_email(email):
        return _response(409, {"message": "Email ja cadastrado"})

    usuario_id = str(uuid.uuid4())
    criado_em = datetime.now(timezone.utc).isoformat()
    item = {
        "id": usuario_id,
        "nome": nome,
        "email": email,
        "senha_hash": _hash_password(senha),
        "criado_em": criado_em,
    }
    _table().put_item(Item=item)

    return _response(201, {
        "id": usuario_id,
        "nome": nome,
        "email": email,
        "criado_em": criado_em,
    })


def login_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    email = (body.get("email") or "").lower()
    senha = body.get("senha") or ""

    usuario = _find_by_email(email)
    if not usuario or not _verify_password(senha, usuario["senha_hash"]):
        return _response(401, {"message": "Credenciais invalidas"})

    token = _create_token(usuario["id"])
    return _response(200, {"access_token": token, "token_type": "bearer"})
