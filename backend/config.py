import secrets
from functools import lru_cache
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.utils import get_logger

logger = get_logger(__name__)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", case_sensitive=True)
    PROJECT_NAME: str = "Toolhunt"
    FRONTEND_HOST: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # FastAPI configuration
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str
    TOOLHUB_API_BASE_URL: str = "https://toolhub-demo.wmcloud.org/api"

    # OAuth2 configuration
    TOOLHUB_AUTH_URL: str
    TOOLHUB_TOKEN_URL: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ENCRYPTION_KEY: str

    # Annotations to include
    ANNOTATIONS: dict[str, bool] = {
        "audiences": True,
        "content_types": True,
        "tasks": True,
        "subject_domains": True,
        "wikidata_qid": True,
        "icon": True,
        "tool_type": True,
        "repository": True,
        "api_url": True,
        "translate_url": True,
        "bugtracker_url": True,
        "deprecated": False,
        "replaced_by": False,
        "experimental": False,
        "for_wikis": False,
        "available_ui_languages": False,
        "developer_docs_url": True,
        "user_docs_url": True,
        "feedback_url": False,
        "privacy_policy_url": False,
    }

    @property
    def active_annotations(self) -> set[str]:
        return {k for k, v in self.ANNOTATIONS.items() if v}


@lru_cache()
def get_settings() -> Settings:
    logger.info("Loading settings from the environment...")
    return Settings()
