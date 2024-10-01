import re
from functools import lru_cache

import httpx
import yaml
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.config import get_settings

router = APIRouter(prefix="/schema", tags=["schema"])

settings = get_settings()


@router.get("")
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
    url = f"{settings.TOOLHUB_API_BASE_URL}/schema/"
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

    adjust_references(cleaned)

    return cleaned
