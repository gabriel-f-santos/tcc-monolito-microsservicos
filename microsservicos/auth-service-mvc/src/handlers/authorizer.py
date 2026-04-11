"""Lambda Authorizer — valida JWT e retorna IAM policy."""
import os

from jose import jwt, JWTError


def handler(event, context):
    token = event.get("authorizationToken", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(
            token,
            os.environ["JWT_SECRET"],
            algorithms=["HS256"],
        )
    except JWTError:
        raise Exception("Unauthorized")

    return {
        "principalId": payload["sub"],
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
    }
