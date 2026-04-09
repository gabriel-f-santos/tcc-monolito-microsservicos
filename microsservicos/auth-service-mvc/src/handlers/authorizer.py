def handler(event, context):
    raise Exception("Unauthorized")

def _generate_policy(principal_id, effect, resource):
    return {"principalId": principal_id, "policyDocument": {"Version": "2012-10-17", "Statement": [{"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}]}}
