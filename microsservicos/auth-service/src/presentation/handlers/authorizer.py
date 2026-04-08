import logging

from src.container import AuthContainer
from src.domain.exceptions.auth import TokenInvalido
from src.infrastructure.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

container = AuthContainer(
    table_name=settings.usuarios_table,
    jwt_secret=settings.jwt_secret,
    jwt_expiration_hours=settings.jwt_expiration_hours,
)


def handler(event, context):
    """Lambda Authorizer para API Gateway."""
    token = event.get("authorizationToken", "").replace("Bearer ", "")
    if not token:
        raise Exception("Unauthorized")

    try:
        token_service = container.token_service()
        payload = token_service.decode_token(token)
        # Use wildcard resource so cached policy works for all routes
        arn_parts = event["methodArn"].split(":")
        region = arn_parts[3]
        account_id = arn_parts[4]
        api_gw_parts = arn_parts[5].split("/")
        api_id = api_gw_parts[0]
        stage = api_gw_parts[1]
        wildcard_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/{stage}/*"
        return _generate_policy(payload["user_id"], "Allow", wildcard_arn)
    except TokenInvalido:
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
