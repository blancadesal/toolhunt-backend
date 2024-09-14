from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from backend.config import get_settings

settings = get_settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["backend.models.tortoise", "aerich.models"],
            "default_connection": "default",
        }
    },
}


def register_tortoise(app: FastAPI) -> RegisterTortoise:
    return RegisterTortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["backend.models.tortoise", "aerich.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )
