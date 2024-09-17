import logging
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator

import httpx
import yaml
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.api import auth, field, task, tool, user
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

    app = FastAPI(title="Toolhunt", lifespan=lifespan)

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
    api_router.include_router(task.router)
    api_router.include_router(field.router)
    api_router.include_router(tool.router)

    app.include_router(api_router)

    return app


app = create_app()


@app.get("/debug/session")
async def debug_session(request: Request):
    return JSONResponse(
        content={"session": dict(request.session), "cookies": request.cookies}
    )


@app.get("/api/v1/schema")
async def get_toolhub_schema():
    try:
        schemas = fetch_and_parse_schema()
        return JSONResponse(content=schemas)
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            content={"error": f"HTTP error: {e.response.status_code}"},
            status_code=e.response.status_code,
        )
    except yaml.YAMLError as e:
        return JSONResponse(
            content={"error": f"YAML parsing error: {str(e)}"}, status_code=500
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"An unexpected error occurred: {str(e)}"},
            status_code=500,
        )


@lru_cache(maxsize=1)
def fetch_and_parse_schema():
    url = "https://toolhub-demo.wmcloud.org/api/schema/"
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        yaml_content = yaml.safe_load(response.text)
        full_schema = yaml_content.get("components", {}).get("schemas", {})
        return clean_schema(full_schema)


def clean_schema(full_schema):
    def get_referenced_schemas(schema, all_schemas):
        referenced = set()
        if isinstance(schema, dict):
            for key, value in schema.items():
                if key == "$ref" and isinstance(value, str):
                    ref = value.split("/")[-1]
                    referenced.add(ref)
                    referenced.update(
                        get_referenced_schemas(all_schemas.get(ref, {}), all_schemas)
                    )
                elif isinstance(value, (dict, list)):
                    referenced.update(get_referenced_schemas(value, all_schemas))
        elif isinstance(schema, list):
            for item in schema:
                referenced.update(get_referenced_schemas(item, all_schemas))
        return referenced

    def adjust_references(schema):
        if isinstance(schema, dict):
            for key, value in schema.items():
                if key == "$ref" and isinstance(value, str):
                    schema[key] = re.sub(r"^#/components/schemas/", "#/schemas/", value)
                elif isinstance(value, (dict, list)):
                    adjust_references(value)
        elif isinstance(schema, list):
            for item in schema:
                adjust_references(item)

    cleaned = {"schemas": {}}
    annotations = full_schema.get("Annotations", {})
    cleaned["schemas"]["Annotations"] = annotations

    referenced = get_referenced_schemas(annotations, full_schema)
    for schema in referenced:
        cleaned["schemas"][schema] = full_schema.get(schema, {})

    # Adjust all references in the cleaned schema
    adjust_references(cleaned)

    return cleaned
