import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Lambda Authorizer para API Gateway.
    TODO: Implementar na Migration 0
    """
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
