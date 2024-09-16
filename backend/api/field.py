from typing import List

from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError

from backend.config import get_settings
from backend.models.tortoise import Field

router = APIRouter(prefix="/fields", tags=["fields"])
settings = get_settings()


@router.get(
    "",
    response_model=List[str],
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_fields():
    fields = await Field.filter(name__in=settings.active_annotations).values_list(
        "name", flat=True
    )
    if not fields:
        raise HTTPException(status_code=404, detail="No fields found")
    return list(fields)
