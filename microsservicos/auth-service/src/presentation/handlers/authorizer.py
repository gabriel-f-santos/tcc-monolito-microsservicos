import logging

from src.container import AuthContainer
from src.infrastructure.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

container = AuthContainer(
    usuarios_table=settings.usuarios_table,
    jwt_secret=settings.jwt_secret,
    jwt_expiration_hours=settings.jwt_expiration_hours,
)


def handler(event, context):
    """Lambda Authorizer para API Gateway.

    Valida JWT e retorna IAM policy.
    API Gateway cacheia o resultado por 300s (configurado no template.yaml).
    """
    token = event.get("authorizationToken", "")
    method_arn = event.get("methodArn", "")

    if not token.startswith("Bearer "):
        raise Exception("Unauthorized")

    jwt_token = token[7:]

    try:
        token_service = container.token_service()
        payload = token_service.decode_token(jwt_token)
        return _generate_policy(payload["user_id"], "Allow", method_arn)
    except Exception:
        raise Exception("Unauthorized")


def _generate_policy(principal_id, effect, resource):
    """Gera IAM policy para API Gateway."""
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resource,
            }],
        },
    }
