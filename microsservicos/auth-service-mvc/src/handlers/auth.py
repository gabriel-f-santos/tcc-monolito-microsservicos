"""Auth handlers — registrar + login (bcrypt + JWT, DynamoDB inline)."""
import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24
USUARIOS_TABLE = os.environ.get("USUARIOS_TABLE", "")

# In-memory store for local/test execution (no DynamoDB)
_local_store: dict[str, dict] = {}


def _get_table():
    if USUARIOS_TABLE:
        import boto3
        return boto3.resource("dynamodb").Table(USUARIOS_TABLE)
    return None


def _find_by_email(email: str) -> dict | None:
    table = _get_table()
    if table:
        resp = table.scan(FilterExpression="email = :e", ExpressionAttributeValues={":e": email})
        items = resp.get("Items", [])
        return items[0] if items else None
    # local mode
    for u in _local_store.values():
        if u["email"] == email:
            return u
    return None


def _put_user(user: dict):
    table = _get_table()
    if table:
        table.put_item(Item=user)
    else:
        _local_store[user["id"]] = user


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def registrar_handler(event, context):
    body = json.loads(event["body"])
    nome = body.get("nome", "")
    email = body.get("email", "").lower()
    senha = body.get("senha", "")

    if _find_by_email(email):
        return _response(409, {"message": "Email ja cadastrado"})

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user = {
        "id": user_id,
        "nome": nome,
        "email": email,
        "senha_hash": _hash_password(senha),
        "criado_em": now,
    }
    _put_user(user)

    return _response(201, {
        "id": user_id,
        "nome": nome,
        "email": email,
        "criado_em": now,
    })


def login_handler(event, context):
    body = json.loads(event["body"])
    email = body.get("email", "").lower()
    senha = body.get("senha", "")

    user = _find_by_email(email)
    if not user or not _verify_password(senha, user["senha_hash"]):
        return _response(401, {"message": "Credenciais invalidas"})

    token = _create_token(user["id"])
    return _response(200, {"access_token": token, "token_type": "bearer"})
