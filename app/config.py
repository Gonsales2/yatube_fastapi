"""Configuration settings for the YaTube API application."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "YaTube API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MEDIA_ROOT: str = str(BASE_DIR / "media")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


REFRESH_TOKEN_EXPIRE_DAYS: int = 7

settings = Settings()

Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
