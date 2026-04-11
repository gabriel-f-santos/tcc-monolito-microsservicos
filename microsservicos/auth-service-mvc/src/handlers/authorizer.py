"""Lambda Authorizer — valida JWT e retorna IAM policy."""
import os

from jose import jwt, JWTError

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
ALGORITHM = "HS256"


def handler(event, context):
    token_str = event.get("authorizationToken", "")
    method_arn = event.get("methodArn", "")

    if not token_str.startswith("Bearer "):
        raise Exception("Unauthorized")

    token = token_str[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        principal_id = payload.get("sub", "unknown")
        return _generate_policy(principal_id, "Allow", method_arn)
    except JWTError:
        raise Exception("Unauthorized")


def _generate_policy(principal_id, effect, resource):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        },
    }
