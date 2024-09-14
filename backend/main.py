import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.api import auth, user
from backend.config import get_settings
from backend.db import register_tortoise

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("Starting up...")
    async with register_tortoise(app):
        log.info("Database registered.")
        yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(lifespan=lifespan)

    # Add middleware
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create a top-level API router
    api_router = APIRouter(prefix="/api/v1")

    # Include other routers
    api_router.include_router(auth.router)
    api_router.include_router(user.router)

    app.include_router(api_router)

    return app


app = create_app()


@app.get("/debug/session")
async def debug_session(request: Request):
    return JSONResponse(
        content={"session": dict(request.session), "cookies": request.cookies}
    )
