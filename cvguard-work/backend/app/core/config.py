from functools import lru_cache
from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://cvguard:cvguard@localhost:5432/cvguard"
    jwt_secret: str = "change-me-in-production"
    access_token_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 10
    storage_dir: str = "./storage"
    ai_provider: str = "deterministic"
    ai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        value = self.cors_origins.strip()
        if not value:
            return []
        if value.startswith("["):
            import json
            parsed = json.loads(value)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("access_token_minutes", "max_upload_mb")
    @classmethod
    def positive_settings(cls, value: int):
        if value <= 0:
            raise ValueError("must be greater than zero")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
