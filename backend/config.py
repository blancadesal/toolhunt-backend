import logging
import secrets
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", case_sensitive=True)

    # FastAPI configuration
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
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

    # Annotations to update
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
    log.info("Loading settings from the environment...")
    return Settings()
