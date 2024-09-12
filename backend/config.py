import logging
import secrets
from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", case_sensitive=True)

    # MariaDB
    MARIADB_USER: str
    MARIADB_PASSWORD: str
    MARIADB_ROOT_PASSWORD: str
    MARIADB_DATABASE: str

    # FastAPI configuration
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    DATABASE_URL: str
    TOOLHUB_API_ENDPOINT: str

    # OAuth2 configuration
    TOOLHUB_AUTH_URL: str
    TOOLHUB_TOKEN_URL: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading settings from the environment...")
    return Settings()
