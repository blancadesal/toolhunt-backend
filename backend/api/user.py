from fastapi import APIRouter, Depends
from models.pydantic import User
from security import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user
