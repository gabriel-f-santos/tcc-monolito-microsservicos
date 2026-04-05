import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

JWT_SECRET = os.environ.get("JWT_SECRET", "")


def handler(event, context):
    """Lambda Authorizer para API Gateway.

    Valida JWT e retorna IAM policy.
    API Gateway cacheia o resultado por 300s (configurado no template.yaml).

    Fluxo:
    1. API Gateway extrai token do header Authorization
    2. Invoca este authorizer (ou usa cache se mesmo token)
    3. Se policy Allow → encaminha para handler Lambda
    4. Se policy Deny → retorna 401 sem invocar handler
    """
    token = event.get("authorizationToken", "")
    method_arn = event.get("methodArn", "")

    if not token.startswith("Bearer "):
        raise Exception("Unauthorized")

    jwt_token = token[7:]  # Remove "Bearer "

    try:
        # TODO: Implementar validacao JWT real na Feature 0
        # user_id = decode_jwt(jwt_token, JWT_SECRET)
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
