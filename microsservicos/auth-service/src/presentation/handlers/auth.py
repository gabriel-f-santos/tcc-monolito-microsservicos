import json


def registrar_handler(event, context):
    """Handler para POST /api/v1/auth/registrar"""
    # TODO: Implementar na Migration 0
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Not implemented yet"}),
    }


def login_handler(event, context):
    """Handler para POST /api/v1/auth/login"""
    # TODO: Implementar na Migration 0
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Not implemented yet"}),
    }
