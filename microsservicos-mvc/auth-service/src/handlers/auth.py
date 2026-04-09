"""Auth handlers — registrar + login com DynamoDB, bcrypt e JWT inline."""
import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import boto3
from boto3.dynamodb.conditions import Attr
from jose import jwt

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "tcc-usuarios")
SECRET_KEY = os.environ.get("JWT_SECRET", "super-secret-key-microsservicos-mvc")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

_table = None


def _get_table():
    global _table
    if _table is None:
        dynamodb = boto3.resource("dynamodb")
        _table = dynamodb.Table(TABLE_NAME)
    return _table


def registrar_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    nome = body.get("nome", "").strip()
    email = body.get("email", "").strip().lower()
    senha = body.get("senha", "")

    if not nome or not email or not senha:
        return _response(400, {"detail": "Campos obrigatorios: nome, email, senha"})

    table = _get_table()

    # Verificar email duplicado via Scan
    resultado = table.scan(FilterExpression=Attr("email").eq(email))
    if resultado.get("Items"):
        return _response(409, {"detail": "Email ja cadastrado"})

    # Criar usuario
    agora = datetime.now(timezone.utc).isoformat()
    usuario_id = str(uuid.uuid4())
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    item = {
        "id": usuario_id,
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash,
        "criado_em": agora,
        "atualizado_em": agora,
    }
    table.put_item(Item=item)

    return _response(201, {
        "id": usuario_id,
        "nome": nome,
        "email": email,
        "criado_em": agora,
    })


def login_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    email = body.get("email", "").strip().lower()
    senha = body.get("senha", "")

    if not email or not senha:
        return _response(400, {"detail": "Campos obrigatorios: email, senha"})

    table = _get_table()
    resultado = table.scan(FilterExpression=Attr("email").eq(email))
    items = resultado.get("Items", [])

    if not items:
        return _response(401, {"detail": "Credenciais invalidas"})

    usuario = items[0]
    if not bcrypt.checkpw(senha.encode(), usuario["senha_hash"].encode()):
        return _response(401, {"detail": "Credenciais invalidas"})

    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    token = jwt.encode({"sub": usuario["id"], "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

    return _response(200, {"access_token": token, "token_type": "bearer"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
