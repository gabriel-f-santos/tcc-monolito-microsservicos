import json


def handler(event, context):
    """Handler para consulta e movimentacoes de estoque.
    Roteamento por httpMethod + path.
    """
    # TODO: Implementar nas Features 3-4
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Not implemented yet"}),
    }
