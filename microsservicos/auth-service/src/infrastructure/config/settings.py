import os


class Settings:
    usuarios_table: str = os.environ.get("USUARIOS_TABLE", "tcc-usuarios")
    jwt_secret: str = os.environ.get("JWT_SECRET", "change-me-in-production")
    jwt_expiration_hours: int = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))


settings = Settings()
