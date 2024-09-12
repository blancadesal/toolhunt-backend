import logging
import secrets
from functools import lru_cache

from pydantic import AnyUrl
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
    ENVIRONMENT: str = "dev"
    DATABASE_URL: AnyUrl
    TOOLHUB_API_ENDPOINT: AnyUrl

    # OAuth2 configuration
    TOOLHUB_AUTH_URL: AnyUrl
    TOOLHUB_TOKEN_URL: AnyUrl
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: AnyUrl
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
