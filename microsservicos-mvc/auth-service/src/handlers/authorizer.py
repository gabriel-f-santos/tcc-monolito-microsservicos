"""Lambda authorizer — valida JWT e retorna IAM policy."""
import os

from jose import jwt, JWTError

SECRET_KEY = os.environ.get("JWT_SECRET", "super-secret-key-microsservicos-mvc")
ALGORITHM = "HS256"


def handler(event, context):
    token = event.get("authorizationToken", "")
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        principal_id = payload["sub"]
    except (JWTError, KeyError):
        raise Exception("Unauthorized")

    # Wildcard ARN para cache do API Gateway funcionar
    method_arn = event.get("methodArn", "")
    arn_parts = method_arn.split(":")
    region = arn_parts[3] if len(arn_parts) > 3 else "*"
    account_id = arn_parts[4] if len(arn_parts) > 4 else "*"
    api_gateway_arn = arn_parts[5].split("/") if len(arn_parts) > 5 else ["*", "*"]
    api_id = api_gateway_arn[0] if api_gateway_arn else "*"
    stage = api_gateway_arn[1] if len(api_gateway_arn) > 1 else "*"
    wildcard_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/{stage}/*"

    return _generate_policy(principal_id, "Allow", wildcard_arn)


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
