import json

def registrar_handler(event, context):
    return {"statusCode": 501, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"message": "Not implemented"})}

def login_handler(event, context):
    return {"statusCode": 501, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"message": "Not implemented"})}
