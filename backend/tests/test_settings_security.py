import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_signing_key():
    with pytest.raises(ValidationError, match="Production JWT_SECRET"):
        Settings(app_env="production", jwt_secret="change-me-in-production",
                 database_url="postgresql+psycopg://app:strongpass@localhost:5432/app")


def test_production_rejects_short_signing_key():
    with pytest.raises(ValidationError, match="Production JWT_SECRET"):
        Settings(app_env="production", jwt_secret="short",
                 database_url="postgresql+psycopg://app:strongpass@localhost:5432/app")


def test_production_rejects_example_database_password():
    with pytest.raises(ValidationError, match="example database password"):
        Settings(app_env="production", jwt_secret="a" * 40,
                 database_url="postgresql+psycopg://cvguard:cvguard@localhost:5432/app")


def test_production_accepts_nondefault_credentials():
    settings = Settings(app_env="production", jwt_secret="b" * 40,
                        database_url="postgresql+psycopg://app:strongpass@localhost:5432/app")
    assert settings.app_env == "production"
