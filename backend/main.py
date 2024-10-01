from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.api import auth, field, metrics, schema, task, tool, user
from backend.config import get_settings
from backend.db import register_tortoise
from backend.utils import get_logger, setup_logging

settings = get_settings()

setup_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up...")
    async with register_tortoise(app):
        logger.info("Database registered.")
        yield


def create_app(settings) -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    # Add middleware
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    # Set all CORS enabled origins
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Top-level API router
    api_router = APIRouter(prefix="/api/v1")

    # Include other routers
    api_router.include_router(auth.router)
    api_router.include_router(user.router)
    api_router.include_router(task.router)
    api_router.include_router(field.router)
    api_router.include_router(tool.router)
    api_router.include_router(metrics.router)
    api_router.include_router(schema.router)

    app.include_router(api_router)

    return app


app = create_app(settings)
