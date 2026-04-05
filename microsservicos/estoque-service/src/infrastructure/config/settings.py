import os


class Settings:
    itens_estoque_table: str = os.environ.get("ITENS_ESTOQUE_TABLE", "dev-itens-estoque")
    movimentacoes_table: str = os.environ.get("MOVIMENTACOES_TABLE", "dev-movimentacoes")
    environment: str = os.environ.get("ENVIRONMENT", "dev")


settings = Settings()
