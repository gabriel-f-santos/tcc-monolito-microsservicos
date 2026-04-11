from src.container import token_service
from src.domain.exceptions.auth import TokenInvalido


def handler(event, context):
    token_str = event.get("authorizationToken", "")
    if not token_str.startswith("Bearer "):
        raise Exception("Unauthorized")

    token = token_str[7:]
    try:
        payload = token_service.decode_token(token)
    except TokenInvalido:
        raise Exception("Unauthorized")

    return _generate_policy(payload["user_id"], "Allow", event["methodArn"])


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
