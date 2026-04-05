import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

JWT_SECRET = os.environ.get("JWT_SECRET", "")


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
        # TODO: Implementar validacao JWT real na Feature 0
        raise Exception("Auth not implemented yet")
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
