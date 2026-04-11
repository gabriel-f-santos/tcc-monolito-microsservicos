"""Lambda Authorizer para API Gateway.

Valida JWT HS256 e retorna IAM policy com Resource wildcard (para cache
de 300s no API Gateway). Em caso de token invalido, LANCA Exception com
string "Unauthorized" — API Gateway faz pattern-match dessa string para
responder 401.
"""
import os

from jose import jwt, JWTError


def handler(event, context):
    token = event.get("authorizationToken", "") or ""
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    secret = os.environ["JWT_SECRET"]
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        raise Exception("Unauthorized")

    principal_id = payload.get("sub") or "unknown"
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "execute-api:Invoke",
                    "Resource": "arn:aws:execute-api:*:*:*/*/*/*",
                }
            ],
        },
        "context": {
            "user_id": str(principal_id),
            "email": str(payload.get("email", "")),
        },
    }
