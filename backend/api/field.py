from fastapi import APIRouter, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError

from backend.config import get_settings

router = APIRouter(prefix="/fields", tags=["fields"])
settings = get_settings()


@router.get(
    "",
    response_model=list[str],
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_fields():
    fields = list(settings.active_annotations)
    if not fields:
        raise HTTPException(status_code=404, detail="No fields found")
    return fields
