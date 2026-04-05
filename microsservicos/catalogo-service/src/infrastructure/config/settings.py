import os


class Settings:
    produtos_table: str = os.environ.get("PRODUTOS_TABLE", "dev-produtos")
    categorias_table: str = os.environ.get("CATEGORIAS_TABLE", "dev-categorias")
    eventos_topic_arn: str = os.environ.get("EVENTOS_TOPIC_ARN", "")
    environment: str = os.environ.get("ENVIRONMENT", "dev")


settings = Settings()
