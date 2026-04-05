import json


def handler(event, context):
    """Handler para CRUD de produtos e categorias.
    Roteamento por httpMethod + path.
    """
    # TODO: Implementar nas Features 1-2
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Not implemented yet"}),
    }
