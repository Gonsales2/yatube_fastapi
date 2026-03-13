"""Configuration settings for the YaTube API application."""

from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "YaTube API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/db.sqlite3"

    SECRET_KEY: str = "m%(5u7nv9j2%@3xb%#c3p-$9&0$kq$j6l@9+@ogairu48a+dy+"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        """Pydantic configuration class."""

        env_file = ".env"


settings = Settings()
