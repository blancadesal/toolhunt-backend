import logging

from api import auth, user
from config import get_settings
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI()

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
