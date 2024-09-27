from fastapi import APIRouter, HTTPException
from tortoise.exceptions import OperationalError

from backend.models.pydantic import ToolNamesResponse
from backend.models.tortoise import Tool

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/names", response_model=ToolNamesResponse)
async def get_tool_names():
    """Get the human-readable titles of all non-deprecated and non-experimental tools, and their Toolhub names."""
    try:
        tools = await Tool.filter(deprecated=False, experimental=False).values("name", "title")
        title_collection = {
            "all_titles": [],
            "titles": {},
        }
        for tool in tools:
            title = tool["title"]
            name = tool["name"]
            if title not in title_collection["all_titles"]:
                title_collection["all_titles"].append(title)

            if title not in title_collection["titles"]:
                title_collection["titles"][title] = [name]
            else:
                title_collection["titles"][title].append(name)

        return title_collection
    except OperationalError:
        raise HTTPException(
            status_code=503, detail="Database connection failed. Please try again."
        )
