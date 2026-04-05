from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/monolito"
    jwt_secret: str = "change-me-in-production"
    jwt_expiration_hours: int = 24
    otel_enabled: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
