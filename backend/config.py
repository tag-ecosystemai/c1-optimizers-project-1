"""Settings loaded from environment via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/tickets"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"

    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    app_name: str = "Customer Intelligence Classifier"
    api_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
